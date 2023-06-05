import discord
from discord import Intents
from google.cloud import compute_v1
from CloudFlare import CloudFlare

bot_TOKEN = 'Discord bot token'
PROJECT_ID = 'GCP PROJECT_ID'
ZONE = 'GCP_ZONE'
INSTANCE_NAME = 'instance Name'
CLOUDFLARE_EMAIL = 'example@gmail.com'
CLOUDFLARE_API_TOKEN = 'TOken'
CLOUDFLARE_ZONE_ID = 'Zone ID'
CLOUDFLARE_RECORD_NAME = 'Record-Name=aka-Prefix'

intents = Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
cloudflare = CloudFlare(email=CLOUDFLARE_EMAIL, token=CLOUDFLARE_API_TOKEN)
compute_client = compute_v1.InstancesClient()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!gcpstart':
        start_instance()
        await message.channel.send('GCP instance starting...')

    elif message.content == '!gcpstop':
        stop_instance()
        await message.channel.send('GCP instance stopped.')

def start_instance():
    request = compute_client.start(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME).result()
    instance = compute_client.get(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME).result()
    external_ip = instance.network_interfaces[0].access_configs[0].nat_ip
    update_cloudflare_ip(external_ip)

def stop_instance():
    request = compute_client.stop(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME).result()

def update_cloudflare_ip(ip_address):
    cf = CloudFlare(email=CLOUDFLARE_EMAIL, token=CLOUDFLARE_API_TOKEN)
    dns_records = cf.zones.dns_records.get(CLOUDFLARE_ZONE_ID)
    record_id = None

    for record in dns_records:
        if record['name'] == CLOUDFLARE_RECORD_NAME:
            record_id = record['id']
            break

    if record_id:
        cf.zones.dns_records.put(CLOUDFLARE_ZONE_ID, record_id, data={'content': ip_address})
        print(f'Updated Cloudflare DNS record with IP: {ip_address}')

client.run(bot_TOKEN)
