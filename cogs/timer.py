from discord.ext import commands
import discord
import datetime
import asyncio
import random
from cogs.rewards import Rewards as rewards
from cogs.utility import Utility as util


class Timer(commands.Cog):
  def __init__(self, client):
    self.client = client

        
  async def claim_timer(client, guild):
    print(f"Starting event timer for {guild.name}...")
    while True:
      hours = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
      while hours:
        t = datetime.datetime.utcnow()
        if t.hour not in hours:
          pass
        else:
          await util.backup_user_data(client,"hourly")
          for channel in guild.voice_channels:
            if len(channel.members) >= 3:
              success = random.choices([True,False],[5,95])
              if success[0] == False:
                print(f"{t.hour} - No drop party")
                #old hour remove
                break
              else:
                print(f"{t.hour} - Drop Party Triggered")
                text_channel = await client.fetch_channel("241507995614183424")
                embed = discord.Embed(
                colour = discord.Colour.magenta(),
                title = f"👀 SOMETHING BIG IS COMING...",
                description= "I smell sloans...")
                await text_channel.send(embed=embed)
                await asyncio.sleep(120)
                for i in range(len(channel.members) * random.randrange(2,6)):
                  await rewards.whack_a_rob(client)
                  wait = random.choices([0,1,2,5,8],[60,20,10,5,5])[0]
                  await asyncio.sleep(wait)
                #old hour remove
          whack_a_rob_hours = [0, 4, 8, 12, 16, 20]
          if t.hour in whack_a_rob_hours:
            minute = random.randrange(t.minute, 60)
            print(f"{t.hour}:{t.minute}:{t.second} -- Minute has been selected as: {minute}")
            while True:
              t = datetime.datetime.utcnow()
              if t.minute == minute:
                #old hour remove
                await rewards.whack_a_rob(client)
                break
              await asyncio.sleep(1)
          #removes an hour after each iteration. If it's the last hour; removes all of them, resetting the loop.
          if t.hour != hours[len(hours)-1]:
            hours.remove(t.hour)
          else:
            hours = []
        #waits 10 seconds between each 'while hours:' iteration
        await asyncio.sleep(10)

def setup(client):
    client.add_cog(Timer(client))
