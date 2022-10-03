import os
from discord.ext import commands
import discord
from datetime import datetime, timedelta
import asyncio
import random
from cogs.rewards import Rewards as rewards
from cogs.utility import Utility as util
from cogs.interactions import Interactions as inter
from backports.zoneinfo import ZoneInfo
import json



class Timer(commands.Cog):
  def __init__(self, client):
    self.client = client

  last_hour = None 
  async def claim_timer(client, guild):
    print(f"Starting event timer for {guild.name}...")
    tz = ZoneInfo("Australia/Sydney")
    FMT = "%Y-%m-%d-%H:%M:%S"
    print(datetime.now(tz))
    while True:
      hours = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,0]
      if Timer.last_hour != None:
        hours.remove(Timer.last_hour)
      while hours:
        t = datetime.now(tz)
        if t.hour not in hours:
          pass
        else:
          await util.backup_user_data(client,title="hourly")
          user_dict = await util.get_user_data()
          for key in user_dict:
            user = user_dict[str(key)]
            if user["hourly_balance"][len(user["hourly_balance"])-1][1] != t.hour:
              user["hourly_balance"].append( (user["balance"], t.hour) )
              if len(user["hourly_balance"]) > 168:
                user["hourly_balance"].pop(0)
          await util.save_user_data(user_dict)

          update_mins = [0,1,2,3,4,5]
          # Updates data for statistical trends.
          if t.hour == 0 and t.minute in update_mins:
            print("Updating daily trends...")
            await util.backup_user_data(client,title="daily")
            user_dict = await util.get_user_data()
            time = datetime.now(tz).strftime(FMT)
            for key in user_dict:
              user = user_dict[str(key)]

              # Day Counter.
              user["day_counter"] += 1

              # Average Bal.
              user["last_balance"] = user["balance"]
              user["average_balance"].append( (time, user["balance"]) )
              if len(user["average_balance"]) > 7:
                user["average_balance"].pop(0)

              # Weekly Cash Flow.
              user["weekly_cash_flow"].append( (time, user["daily_cash_flow"]) )
              if user["stat_highest_daily_cash_flow"] < user["daily_cash_flow"]:
                user["stat_highest_daily_cash_flow"] = user["daily_cash_flow"]
              user["daily_cash_flow"] = 0
              if len(user["weekly_cash_flow"]) > 7:
                user["weekly_cash_flow"].pop(0)

              # 12 Week Average Cash Flow.
              if user["day_counter"] != 0  and  user["day_counter"] % 7 == 0:
                weekly_cash_flow = 0
                for day in user["weekly_cash_flow"]:
                  weekly_cash_flow += day[1]
                user["12_week_average_cash_flow"].append( weekly_cash_flow )
                if len(user["12_week_average_cash_flow"]) > 12:
                  user["12_week_average_cash_flow"].pop(0)

              cFMT = "%Y-%m-%d"
              time_now = t.strftime(cFMT)
              overdue = 0
              for d in user["debt"]:
                # If debt is overdue.
                if datetime.strptime(d[0], cFMT) < datetime.strptime(time_now, cFMT):
                  overdue += 1
                # If repay amount is less than twice the original amount, compound interest.
                if d[1] < d[4]*2:
                  d[1] += int(d[1]*(d[5]*0.01))
                  owed_user = user_dict[d[2]]
                  for o in owed_user["owed"]:
                    # If IDs match, adjust values for owed party.
                    if d[3] == o[3]:
                      o[1] += int(d[1]*(d[5]*0.01))
              if overdue > 0:
                if user["rob_banned"] == False:
                  user["rob_banned"] = True
                  user["stat_rob_banned_quantity"] += 1
                  user["last_rob_banned"] = time_now
                  print(f"ROB Banned {key}")
              else:
                user["rob_banned"] = False

              #Cursing for each overdue payment.
              with open("upgrades.json","r") as f:
                d = json.load(f)
              prot_chance = d["upgrade_protection"]["amounts"][ str(user["upgrade_protection"]["level"]) ]
              base = 0.5
              luck = base * (100 + prot_chance) * 0.01
              for i in range(overdue):
                user["luck"] = user["luck"] * luck
                expire_date = datetime.utcnow() + timedelta(hours = 24)
                user["cursed"].append( (expire_date.strftime(FMT), luck) )
              
                
            await util.save_user_data(user_dict)
            print("Daily trends updated successfully!")
                
          for channel in guild.voice_channels:
            if len(channel.members) >= 3:
              success = random.choices([True,False],[5,95])
              if success[0] == False:
                print(f"{t.hour} - No Drop Party")
                break
              else:
                print(f"{t.hour} - Drop Party Triggered")
                text_channel = await client.fetch_channel("241507995614183424")
                await text_channel.send("Something is coming...")
                await asyncio.sleep(120)
                for i in range(len(channel.members) * random.randrange(2,6)):
                  await rewards.whack_a_rob(client, drop_party = True)
                  wait = random.choices([0,1,2,5,8],[60,20,10,5,5])[0]
                  await asyncio.sleep(wait)

          #Time: 12am, 4am, 8am, 12pm, 4pm, 8pm
          whack_a_rob_hours = [0, 4, 8, 12, 16, 20]
          if t.hour in whack_a_rob_hours:
            minute = random.randrange(t.minute, 60)
            print(f"{t.hour}:{t.minute}:{t.second} -- Minute has been selected as: {minute}")
            while True:
              t = datetime.now(tz)
              if t.minute == minute:
                await rewards.whack_a_rob(client)
                break
              await asyncio.sleep(1)
          
          # Testing in private server.
          #if guild.id == 957393064157139004:
            #await rewards.turf_war(client, guild)
          
          turf_war_hours = [19]
          if t.hour in turf_war_hours:
            #if random.randrange(1,101) <= 14:
            if random.randrange(1,101) <= 14:
              
              # Allows me to cancel if caused by a restart.
              print("Turf War starting in 5 seconds")
              await asyncio.sleep(5)
              
              text_channel = await client.fetch_channel("241507995614183424") # Change for multi-server update.
              await text_channel.send("Something is coming...")
              await asyncio.sleep(120)
              await inter.turf_war(client, guild)

          # Removes an hour after each iteration. If it's the last hour; removes all of them, resetting the loop.
          #if t.hour != hours[len(hours)-1]:
          Timer.last_hour = t.hour
          hours.remove(t.hour)
          
          #else:
            #hours = []
        #waits 10 seconds between each 'while hours:' iteration
        await asyncio.sleep(10)

async def setup(client):
    await client.add_cog(Timer(client))
