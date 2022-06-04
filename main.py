import os
from os import system
try:
  import nacl
except ImportError:
  print("Failed to import nacl, installing from system.")
  try:
    os.system("pip install pynacl")
  except Exception as e:
    print("Error:", e)
    exit()
try:
  import discord_components
except ImportError:
  print("Failed to import discord_components, installing from system.")
  try:
    os.system("pip install discord-components")
  except Exception as e:
    print("Error:", e)
    exit()
    
from discord_components import DiscordComponents, ComponentsBot, Button, SelectOption, Select
import discord
import asyncio
from discord.ext import commands
#import tracemalloc


#tracemalloc.start()
intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot_prefix = "$"
client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True, intents=intents)
DiscordComponents(client)

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="the bongos"))
  print(f"Successfully logged in as {client.user}")

  for fn in os.listdir(f"./cogs"):
    if fn.endswith(".py"):
      client.load_extension(f"cogs.{fn[:-3]}")
      print(f"Loaded {fn}")
  print("Finished")

  from cogs.timer import Timer as timer
  for guild in client.guilds:
    await timer.claim_timer(client, guild)

@client.command()
@commands.is_owner()
async def load(ctx, extension):
  client.load_extension(f"cogs.{extension}")
  print("Loaded cog!")

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
  client.unload_extension(f"cogs.{extension}")
  print("Unloaded cog!")

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
  client.reload_extension(f"cogs.{extension}")
  print("Reloaded cog!")

from cogs.interactions import Interactions as inter

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  await client.process_commands(message)
  await inter.check_message(client, message)

try:
  client.run(os.environ['TOKEN'])
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    system("server_restarter.py")
    system('kill 1')