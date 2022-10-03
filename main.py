import os
import sys
import asyncio
from os import system 
import discord
from discord.ext import commands

print(f"Running on Discord.py version {discord.__version__}")
print(f"Python version {sys.version}")

intents = discord.Intents.all()
bot_prefix = "$"
client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="the bongos"))
  print(f"Successfully logged in as {client.user}")
  for fn in os.listdir(f"./cogs"):
    if fn.endswith(".py"):
      await client.load_extension(f"cogs.{fn[:-3]}")
      print(f"Loaded {fn}")
  print("Finished")
  
  from cogs.timer import Timer as timer
  guilds = []
  for guild in client.guilds:
    guilds.append(guild)
    
    # This doesn't work as user.activities just returns an empty tuple despite intents.
    # Could be achieved by adding everyone online with the League upgrade into a role, 1 second at a time, then removing them.
    """    
    async for user in guild.fetch_members(limit=None):
      for item in user.activities:
        if item.name == "League of Legends":
          if item.application_id == 401518684763586560 and item.state == "In Game":
            if item.details == "Summoner's Rift (Normal)":
              await user.edit(nick=f"{user.name}.")
              await user.edit(nick=user.name[:-1])
    """
  
  await asyncio.gather(
    timer.claim_timer(client, guilds[0])
    #more guilds here
                      )
@client.command()
@commands.is_owner()
async def load(ctx, extension):
  await client.load_extension(f"cogs.{extension}")
  print(f"Loaded {extension}.py!")

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
  await client.unload_extension(f"cogs.{extension}")
  print(f"Unloaded {extension}.py!")

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
  await client.reload_extension(f"cogs.{extension}")
  print(f"Reloaded {extension}.py!")

from cogs.utility import Utility as util

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await util.embed_error_cooldown(ctx,"This command is on cooldown for", f"{int(error.retry_after):,} seconds")
  else:
    raise(error)

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
    system('kill 1')