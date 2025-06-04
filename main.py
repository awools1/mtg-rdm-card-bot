from keep_alive import keep_alive
import os
import discord
import aiohttp
import asyncio
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz

TOKEN = os.getenv("TOKEN")

CHANNEL_ID = 714943990855762001

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

scheduler = AsyncIOScheduler()

async def fetch_random_card():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.scryfall.com/cards/random") as resp:
            data = await resp.json()
            return data.get("image_uris", {}).get("normal", ""), data.get("name", "Unknown Card")

async def send_daily_card():
    print("Running daily card job...")  # 👈 This prints when the job runs (extra debug!)
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        image_url, card_name = await fetch_random_card()
        if image_url:
            await channel.send(f"Today's Magic card: **{card_name}**\n{image_url}")
        else:
            await channel.send("Couldn't fetch a card today, sorry!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Schedule for 11AM Eastern Time
    eastern = pytz.timezone("US/Eastern")
    scheduler.add_job(send_daily_card, 'cron', hour=11, minute=0, timezone=eastern)
    scheduler.start()
    print("Scheduled daily Magic card job at 11AM Eastern.")  # 👈 This confirms scheduling

@bot.command(name="card")
async def card(ctx):
    image_url, card_name = await fetch_random_card()
    if image_url:
        await ctx.send(f"Here's a random Magic card: **{card_name}**\n{image_url}")
    else:
        await ctx.send("Oops, couldn't fetch a card right now!")

keep_alive()
bot.run(TOKEN)
