#!/usr/bin/env python3
import smtplib
import json
import sqlite3
import logging
import socket
import dns.resolver
import os
import sys
import CloudFlare
import CloudFlare.exceptions
from datetime import datetime
from email.mime.text import MIMEText
from contextlib import closing

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
    return resolver.query('myip.opendns.com')[0]

#def GetLastKnownIP():
    #try:
        #con = sqlite3.connect(os.path.join(dir_path, 'cloudflareDNS.sqlite'))
        #with closing(con.cursor()) as cur:
            #cur.execute('SELECT ip FROM currentIP')
            #return cur.fetchone()[0]
    #except sqlite3.Error as e:
        #if con:
            #con.rollback()
        #log('Error {0}:'.format(e.args[0]))
    #finally:
        #if con:
            #con.close()

def GetRecordIDs(cf, zone_id):
    try:
        dns_records = []
        for record in required["record_names"]:
            params = {'name':record, 'match':'all', 'type':'A'}
            dns_records.append(cf.zones.dns_records.get(zone_id, params=params))
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones/dns_records %s - %d %s - api call failed' % (dns_name, e, e))
    
    return dns_records

def GetZoneID(cf):
    try:
        params = {'name':required["zone_name"]}
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        log('/zones %d %s - api call failed' % (e, e))
        exit
    except Exception as e:
        log('/zones.get - %s - api call failed' % (e))
        exit

    if len(zones) == 0:
        log('/zones.get - %s - zone not found' % (zone_name))
        exit
    if len(zones) != 1:
        log('/zones.get - %s - api call returned %d items' % (zone_name, len(zones)))
        exit

    return zones[0]["id"]

def UpdateRecord(cf, ids, currentIP):
    for dns_record in ids:
            knownIP = dns_record[0]['content']
            host = dns_record[0]["name"]
            print currentIP
            print knownIP
            print("{0} {1} {2} {3}".format(host, dns_record[0]["id"], dns_record[0]["content"], dns_record[0]["type"]))
            if currentIP == knownIP:
                log("IP, {0}, has not changed for {1}.".format(knownIP, host))
                exit

    



if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logging.basicConfig(filename=os.path.join(dir_path, 'cloudflare.log'),level=logging.DEBUG)
    log('Check Initiated')
    #print(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
    #print(sys.path.insert(0, os.path.abspath('..')))
    required = GetRequired()
    currentIP = GetCurrentIP()
    #knownIP = GetLastKnownIP()
    #if currentIP == knownIP:
        #log("IP, {0}, has not changed.".format(knownIP))
        #exit
    #else:
    #print(required["auth_email"])
    #print(required["auth_key"])
    cf = CloudFlare.CloudFlare(email=required["auth_email"], token=required["auth_key"])
    zone_id = GetZoneID(cf)
    #print(required["zone_name"])
    #print(zone_id)
    ids = GetRecordIDs(cf, zone_id)
    UpdateRecord(cf, ids, currentIP)

    
    #SetOutageInfo(now)
    #SendGmailMsg(required, now)



