
import discord
import asyncio
from google.cloud import compute_v1
from CloudFlare import CloudFlare

bot_TOKEN = 'x'
PROJECT_ID = 'x'

ZONE = 'xa'
INSTANCE_NAME = 'x-1'
CLOUDFLARE_EMAIL = 'x@gmail.com'
CLOUDFLARE_API_TOKEN = 'x'
CLOUDFLARE_ZONE_ID = 'x'
CLOUDFLARE_RECORD_NAME = 'x'

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.content.startswith('!gcpstart'):
        await gcp_start_function(message.channel)
    elif message.content.startswith('!gcpstop'):
        await gcp_stop_function(message.channel)

async def gcp_start_function(channel):
    await channel.send('GCP instance starting...')
    await asyncio.sleep(1)  # Do any additional processing if required
    start_instance()
    await channel.send('GCP instance started.')

async def gcp_stop_function(channel):
    await channel.send('GCP instance stopping...')
    await asyncio.sleep(1)  # Do any additional processing if required
    stop_instance()
    await channel.send('GCP instance stopped.')

def start_instance():
    compute_client = compute_v1.InstancesClient()
    request = compute_client.start(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME).result()
    instance = compute_client.get(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME)
    external_ip = instance.network_interfaces[0].access_configs[0].nat_i_p
    update_cloudflare_ip(external_ip)
    print('GCP instance starting...')

def stop_instance():
    compute_client = compute_v1.InstancesClient()
    request = compute_client.stop(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME).result()
    print('GCP instance stopped.')

def update_cloudflare_ip(ip_address):
    cloudflare = CloudFlare(email=CLOUDFLARE_EMAIL, token=CLOUDFLARE_API_TOKEN)
    dns_records = cloudflare.zones.dns_records.get(CLOUDFLARE_ZONE_ID)
    record_id = None

    for record in dns_records:
        if record['name'] == CLOUDFLARE_RECORD_NAME:
            record_id = record['id']
            break

    if record_id:
        cloudflare.zones.dns_records.put(CLOUDFLARE_ZONE_ID, record_id, data={'content': ip_address})
        print(f'Updated Cloudflare DNS record with IP: {ip_address}')

bot.run(bot_TOKEN)
