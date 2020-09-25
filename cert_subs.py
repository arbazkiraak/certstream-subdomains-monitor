import certstream,requests,os
import time as t
import tldextract
import logging
import sys
import datetime
from discord_webhook import DiscordWebhook,DiscordEmbed

BOUNTY_LIST = [line.strip() for line in open('bug-bounty-list.txt')]
DUPS_LIST = [line.strip() for line in open('dups.txt')]
discord_webhook_url = "https://discordapp.com/api/webhooks/527730436005298187/xXxxxxxxxxxxxxxxxxx"

def Discord_Push(message):
    try:
        webhook = DiscordWebhook(url=str(discord_webhook_url))
        embed = DiscordEmbed(title="[CERTSTEAM] NEW SUBDOMAIN", description=str(message), color=242424)
        webhook.add_embed(embed)
        resp = webhook.execute()
    except Exception as e:
        print("[*] EXCEPTION IN NOTIFY PUSH : {}".format(e))
        return True

def dupe_write(subdomain):
    with open("dups.txt",'a') as f:
        f.write(subdomain+'\n')
    f.close()

def monitor(message, context):
    logging.debug("Message -> {}".format(message))

    all_domains = ""

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

    for subdomain in set(all_domains):
        if subdomain.count(".") > 1 and not subdomain.startswith("*."):
            ext = tldextract.extract(subdomain)
            domain_ext = '.'.join(ext[1:])
            if domain_ext in BOUNTY_LIST:
                if subdomain not in DUPS_LIST:
                    DUPS_LIST.append(subdomain)
                    dupe_write(subdomain)
                    Discord_Push(subdomain)

logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

certstream.listen_for_events(monitor, url='wss://certstream.calidog.io/')
