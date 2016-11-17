#!/usr/bin/env python2
import smtplib
import json
import logging
import socket
import dns.resolver
import os
import CloudFlare
import CloudFlare.exceptions
from datetime import datetime
from email.mime.text import MIMEText

def GetRequired():
    with open(os.path.join(dir_path, 'required.json'), 'r') as fin:
        return json.loads(fin.read())

def log(msg):
    if msg:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        logging.info("[{0}] {1}".format(now,msg))

def GetCurrentIP():
    # Use opendns "myip" function to query current IP.
    resolver = dns.resolver.Resolver()
    resolver.nameservers=[socket.gethostbyname('resolver1.opendns.com')]
    return resolver.query('myip.opendns.com')[0].address

def GetRecordIDs(cf, zone_id):
    try:
        dns_records = []
        for record in required["record_names"]:
            params = {'name':record, 'match':'all', 'type':'A'}
            dns_records.append(cf.zones.dns_records.get(zone_id, params=params))
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        log("/zones/dns_records {0} - {1} {2} - api call failed".format(dns_name, e, e))
        exit(0)

    return dns_records

def GetZoneID(cf):
    try:
        params = {'name':required["zone_name"]}
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        log("/zones {0} {1} - api call failed".format(e, e))
        exit
    except Exception as e:
        log("/zones.get - {0} - api call failed".format(e))
        exit(0)

    if len(zones) == 0:
        log("/zones.get - {0} - zone not found".format(zone_name))
        exit(0)
    if len(zones) != 1:
        log("/zones.get - {0} - api call returned %d items".format(zone_name, len(zones)))
        exit(0)

    return zones[0]["id"]

def SendUpdateEmail(msg):
    gmailAddress = required['sender']
    gmailPassword = required['password'] #App Specific Password

    fromSender = gmailAddress
    toRecipients = required['recipients']

    msg_subject = 'DNS UPDATE:'
    msg_text = msg

    msg = MIMEText(msg_text)
    msg['Subject'] = msg_subject
    msg['From'] = fromSender
    msg['To'] = ", ".join(toRecipients)
    s = smtplib.SMTP_SSL('smtp.gmail.com', '465')
    s.login(gmailAddress, gmailPassword)
    s.sendmail(fromSender, toRecipients, msg.as_string())
    s.quit()

def UpdateRecord(cf, ids, currentIP):
    for dns_record in ids:
        knownIP = dns_record[0]['content']
        dns_name = dns_record[0]["name"]
        dns_record_id = dns_record[0]["id"]
        ip_address_type = dns_record[0]["type"]
        zone_id = dns_record[0]["zone_id"]
        #print("{0} {1} {2} {3}".format(dns_name, dns_record_id, ip_address, ip_address_type))
        if currentIP == knownIP:
            log("IP, {0}, has not changed for {1}.".format(knownIP, dns_name))
            continue
        else:
            dns_record[0]['content'] = currentIP
            try:
                #dns_record = cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record[0])
                msg = "UPDATED: {0} {1} -> {2}".format(dns_name, knownIP, currentIP)
                log(msg)
                SendUpdateEmail(msg)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                log("/zones.dns_records.put {0} - {1} {2} - api call failed".format(dns_name, e, e))
                exit                

#Main
if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logging.basicConfig(filename=os.path.join(dir_path, 'cloudflare.log'),level=logging.DEBUG)
    log('DNS Check Initiated')
    required = GetRequired()
    currentIP = GetCurrentIP()
    cf = CloudFlare.CloudFlare(email=required["auth_email"], token=required["auth_key"])
    zone_id = GetZoneID(cf)
    ids = GetRecordIDs(cf, zone_id)
    UpdateRecord(cf, ids, currentIP)
    log('DNS Check Complete')
