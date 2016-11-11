#!/usr/bin/env python3
import smtplib
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from contextlib import closing

## CHANGE THESE
#auth_email="bzsparks@gmail.com"
#auth_key="79a5d70cf6263c3d36eb2c1a736a5afe7a88d" # found in cloudflare account settings
#zone_name="bzsprks.com"
#record_name="vpn.bzsprks.com"
#
## MAYBE CHANGE THESE
#ip=$(dig @resolver1.opendns.com +short myip.opendns.com)
#ip_file="ip.txt"
#id_file="cloudflare.ids"
#log_file="cloudflare.log"

def GetRequired():
    with open('required.json', 'r') as fin:
        return json.loads(fin.read())

# LOGGER
def log(msg):
    if msg:
        #echo -e "[$(date)] - $1" >> $log_file
        now = datetime.now()
        logging.info("[{0}] {1}".format(now,msg))

#if [ -f $ip_file ]; then
#    old_ip=$(cat $ip_file)
#    if [ $ip == $old_ip ]; then
#        echo "IP has not changed."
#        exit 0
#    fi
#fi
#
#if [ -f $id_file ] && [ $(wc -l $id_file | cut -d " " -f 1) == 2 ]; then
#    zone_identifier=$(head -1 $id_file)
#    record_identifier=$(tail -1 $id_file)
#else
#    zone_identifier=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$zone_name" -H "X-Auth-Email: $auth_email" -H "X-Auth-Key: $auth_key" -H "Content-Type: application/json" | grep -Po '(?<="id":")[^"]*' | head -1 )
#    record_identifier=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$zone_identifier/dns_records?name=$record_name" -H "X-Auth-Email: $auth_email" -H "X-Auth-Key: $auth_key" -H "Content-Type: application/json"  | grep -Po '(?<="id":")[^"]*')
#    echo "$zone_identifier" > $id_file
#    echo "$record_identifier" >> $id_file
#fi
#
#update=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zone_identifier/dns_records/$record_identifier" -H "X-Auth-Email: $auth_email" -H "X-Auth-Key: $auth_key" -H "Content-Type: application/json" --data "{\"id\":\"$zone_identifier\",\"type\":\"A\",\"name\":\"$record_name\",#\"content\":\"$ip\"}")
#
#if [[ $update == *"\"success\":false"* ]]; then
#    message="API UPDATE FAILED. DUMPING RESULTS:\n$update"
#    log "$message"
#    echo -e "$message"
#    exit 1 
#else
#    message="IP changed to: $ip"
#    echo "$ip" > $ip_file
#    log "$message"
#    echo "$message"
#fi



if __name__ == "__main__":
    logging.basicConfig(filename='cloudflare.log',level=logging.DEBUG)
    log("Check Initiated")
    required = GetRequired()
    #SetOutageInfo(now)
    #SendGmailMsg(required, now)



