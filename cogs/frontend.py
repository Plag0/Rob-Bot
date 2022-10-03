from discord.ext import commands
import discord
import time
from datetime import datetime, timedelta
from backports.zoneinfo import ZoneInfo
from cogs.utility import Utility as util
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pyimgur
import json
import os
import asyncio
from typing import Union

client_id = os.environ['Imgur_CLIENT_ID']

class Frontend(commands.Cog):
  def __init__(self, client):
    self.client = client


  async def help_steal(self,ctx):
    desc=""
    desc+="__*24h Cooldown*__"
    desc+="```$steal (@mention/username/ID) ($amount = optional)```"
    desc+="*Leaving the amount field empty will default to the maximum safe amount for your level.\nEntering a value in the place of the mention field will simulate your odds of success.*\n\n"
    desc+="📖 **Description**\n"
    desc+="The Steal command allows you to take Sloans from others without their consent.\n"
    desc+="The maximum amount of Sloans you can safely take depends on your level. Anything above that maximum safe amount will quickly become a gamble as your odds of success exponentially decrease.\n"
    desc+="Some users may also own the Protection upgrade, giving them a 5-90% chance (based on level) to automatically interrupt your thieving attempt.\n\n"
    desc+="The stealing process takes a total of 21 seconds. The first seven seconds are spent trying to break through the target's Protection upgrade. The following seven seconds are dedicated to attempting the collection of funds from the target's balance. The remaining seconds are the home stretch where time is your only obstacle.\n\n"
    desc+="If you get caught or something goes wrong during this 15-second window, the steal will fail, and you'll be fined for 50% of your safe max. This fine is added to your account as a 5% interest debt that you must repay to the target within two weeks.\n"
    desc+="Each day, you are given three attempts to reach at least the equivalent of your safe max in profits. If you run out of attempts or exceed your profit limit the command will go on cooldown. If you don't use all your attempts they will reset 24 hours after your first attempt.\n\n"
    desc+='There are no fines for stealing from users that are no longer in any Rob supported servers. These users are known as "Deserters" and can be identified by using the `$total` command.'

    rules =""
    rules+="• Requires at least **Steal Level 1** to use.\n"
    rules+="• Can't be used while ROB Banned.\n"
    rules ="• You can only have one Steal in progress at a time.\n"
    rules+="• Must have under 3 unpaid fines from the target.\n"
    rules+="• Can't use Steal in Rob's DMs.\n"
    rules+="• You can only steal from users in the same server.\n"
    rules+="• Stealing from Rob will apply 2x the normal fine.\n"
    rules+="• Your daily attempts and profit limit will reset if a day* passes since your first attempt.\n"
    rules+="**Cooldown reduction applies.*"
    
    with open("upgrades.json","r") as f:
      d = json.load(f)
    data = d["upgrade_steal"]
    values = "**Level  |  Safe Max  |  Price**\n"
    for i in range(10):
      amount = data["amounts"][str(i+1)]
      price = data["prices"][str(i)]
      values += f"`{i+1}    ${amount:,}    ${price:,}`\n"
    
    embed = discord.Embed(
      title = "❔ Help | 🕵️‍♂️ Steal",
      description = desc,
      colour = discord.Colour.magenta()
      )
    embed.add_field(name = "📜 **Rules**", value = rules, inline = True)
    embed.add_field(name = "📊 **Values**", value = values, inline = True)
    await ctx.channel.send(embed=embed)
  
  @commands.command(aliases = ["commands"])
  @commands.is_owner()
  async def help(self, ctx, category:str = None):

    if category == None:
      embed = discord.Embed(
        title = "Categories",
        description = "Choose a category by typing `$help category`",
        colour = discord.Colour.magenta()
      )
      embed.add_field(name = "Community", value = "Server wide trading and shop.", inline = True)
      embed.add_field(name = "Information", value = "Display profiles and statistics.", inline = True)
      embed.add_field(name = "Gambling", value = "Various risky games to play.", inline = True)
      embed.add_field(name = "Transactions", value = "Send Sloans and give out loans.", inline = True)
      embed.add_field(name = "Rewards", value = "Free Sloans.", inline = True)
      embed.add_field(name = "Versus", value = "Challenge others.", inline = True)
    elif category == "community":
      embed = discord.Embed(
        title = "Community",
        description = "Server wide trading and shop.",
        colour = discord.Colour.magenta())
      embed.add_field(name = "`$loan (@mention) ($amount) (#days) (%interest = optional)`", value = "*If days is entered as `0` the expiry period is infinite.*", inline = True)
      embed.add_field(name = "`$buy (upgrade) (#quantity = optional)`", value = "*Quantity defaults to `1`*```fix\n1 ROB Ban on record```", inline = True)
      embed.add_field(name = "`$shop (@mention = optional)`", value = "*Mentioning a user allows you to view their shop prices.*", inline = False)
    
    await ctx.channel.send(embed=embed)


  @commands.command(aliases = ["inflation"])
  @commands.cooldown(1, 30, commands.BucketType.user)
  async def total(self, ctx):
    guild_name = ""
    
    total = 0
    local_total = 0
    deserter_total = 0
    
    global_users = []
    local_users = []
    outlaws = []
    user_dict = await util.get_user_data()

    try:
      guild_name = ctx.guild.name
      async for user in ctx.guild.fetch_members(limit=None):
        local_users.append(str(user.id))
    except:
      guild_name = ctx.author.name
      local_users.append(str(ctx.author.id))
      
    for guild in self.client.guilds:
      async for user in guild.fetch_members(limit=None):
        global_users.append(str(user.id))
    
    for user in user_dict:
      if user not in global_users and user_dict[user]["balance"] > 0:
        deserter_total += user_dict[user]["balance"]
        outlaws.append(user)
      elif user in local_users:
        local_total += user_dict[user]["balance"]
      total += user_dict[user]["balance"]
    
    outlaw_str = ""
    for o in outlaws:
      user = await self.client.fetch_user(o)
      outlaw_str += f"• `${user_dict[o]['balance']:,}` {user.mention}\n"

    embed = discord.Embed(
      title = "⚖ Global Inflation",
      description = f"There are **${total:,}** Sloans in global circulation.\nThere are **${local_total:,}** Sloans in **{guild_name}**.\nThere are **${deserter_total:,}** Sloans missing."
    )
    embed.add_field(name="📌 Deserters Bounty Board", value = f"There are no consequences for stealing from a deserter.\n{outlaw_str}")
      
    await ctx.channel.send(embed=embed)


  @commands.command(aliases = ["statistics","info","stats"])
  async def stat(self, ctx, stat_name:str, scope: Union[int, discord.User] = 0, mention:discord.User = None, mention2:discord.User = None):
    if isinstance(scope, discord.User) or isinstance(scope, discord.ClientUser):
      if mention != None:
        mention2 = mention
        mention = scope
      else:
        mention = scope
      scope = 0
    mention = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(mention.id)]
    if mention2 != None:
      user2 = user_dict[str(mention2.id)]

    if "flip" in stat_name:
      stat = user["average_flip_balance"]
      stat_name = "Coin Flips"
      if mention2 != None:
        stat2 = user2["average_flip_balance"]
    elif "bal" in stat_name:
      stat_name = "Hours"
      scope *= 24
      stat = []
      stat2 = []
      for bal in user["hourly_balance"]:
        stat.append(bal[0])
      if mention2 != None:
        for bal in user2["hourly_balance"]:
          stat2.append(bal[0])  
    else:
      await util.embed_error(ctx, f"Unsupported stat: `{stat}`")
      return
    
    data = []
    data2 = []
    scope2 = scope
    if scope >= len(stat) -1 or scope == 0:
      scope = len(stat) - 1
    for i in range(scope):
      i+=1
      data.append( stat[-i] )
    data.reverse()
    
    if mention2 != None:
      if scope2 >= len(stat2) -1 or scope2 == 0:
        scope = len(stat2) - 1
      for i in range(scope):
        i+=1
        data2.append( stat2[-i] )
      data2.reverse()

    try:
      if data[0] < data[len(data)-1]:
        #red
        colour = '#2ECC70'
      else:
        #green
        colour = '#E74D3C'
    except:
      colour = 'white'
      
    fig, ax = plt.subplots()
    ax.plot(data, color = colour, linewidth=3, markersize=12, antialiased=True)[0]
    ax.set_title(f"{mention.name}'s Balance Over {scope:,} {stat_name}", color='white')
    if mention2 != None:
      ax.plot(data2, color = '#3498DB', linewidth=3, markersize=12, antialiased=True)[0]
      ax.set_title(f"{mention.name} vs {mention2.name}'s Balance Over {scope:,} {stat_name}", color='white')
      
    for axis in [ax.xaxis, ax.yaxis]:
      axis.set_major_locator(ticker.MaxNLocator(integer=True))
    
    #ax.xaxis.set_visible(False)
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white')
    ax.yaxis.set_major_formatter('${x:1.0f}')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    path = 'graphics//trend.png'
    fig.savefig(path, bbox_inches='tight', transparent=True) #facecolor='#2e3136'
    plt.close(fig)
    
    #im = pyimgur.Imgur(client_id)
    #image = im.upload_image(path, title="trend")
    #link = image.link
    file = discord.File('graphics//trend.png')

    await ctx.channel.send(file=file)
      

  @commands.command(aliases = ["loans","sheet","owed","debts"])
  async def debt(self, ctx, mention:discord.User = None, simple = None):
    mention = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(mention.id)]
    FMT = "%Y-%m-%d"
    tz = ZoneInfo("Australia/Sydney")
    time_now = datetime.now(tz).strftime(FMT)

    
    debt = user["debt"]
    owed = user["owed"]
    debt.sort()
    owed.sort()
    
    if simple == None:
      debt_string = ""
      total_debt = 0
      d_tomorrow = 0
      for d in debt:
        owed_user = await self.client.fetch_user(d[2])
        days = datetime.strptime(d[0], FMT) - datetime.strptime(time_now, FMT)
        if str(days) == "0:00:00":
          debt_string += f"• **${d[1]:,}** at **{d[5]}%** to **{owed_user.name}** due **{d[0]}** *(Today at 12:00am AEST)*\n"
        elif int(str(days).split(' ')[0]) > 365:
          debt_string += f"• **${d[1]:,}** at **{d[5]}%** to **{owed_user.name}** due **∞**\n"
        else:
          debt_string += f"• **${d[1]:,}** at **{d[5]}%** to **{owed_user.name}** due **{d[0]}** *({str(days).split(',')[0]})*\n"
        if d[1] < d[4]*2:
          d_tomorrow += d[1] + int(d[1]*(d[5]*0.01))
        total_debt += d[1]
      if debt_string == "":
        debt_string = "*None!*"
  
      owed_string = ""
      total_owed = 0
      o_tomorrow = 0
      for d in owed:
        loaned_user = await self.client.fetch_user(d[2])
        days = datetime.strptime(d[0], FMT) - datetime.strptime(time_now, FMT)
        if str(days) == "0:00:00":
          owed_string += f"• **${d[1]:,}** at **{d[5]}%** from **{loaned_user.name}** due **{d[0]}** *(Today at 12:00am AEST)*\n"
        elif int(str(days).split(' ')[0]) > 365:
          owed_string += f"• **${d[1]:,}** at **{d[5]}%** from **{loaned_user.name}** due **∞**\n"
        else:
          owed_string += f"• **${d[1]:,}** at **{d[5]}%** from **{loaned_user.name}** due **{d[0]}** *({str(days).split(',')[0]})*\n"
        if d[1] < d[4]*2:
          o_tomorrow += d[1] + int(d[1]*(d[5]*0.01))
        total_owed += d[1]
      if owed_string == "":
        owed_string = "*None!*"
    
    
    
    else:
      debt_string = ""
      total_debt = 0
      d_tomorrow = 0
      for d in debt:
        owed_user = await self.client.fetch_user(d[2])
        days = datetime.strptime(d[0], FMT) - datetime.strptime(time_now, FMT)
        if str(days) == "0:00:00":
          debt_string += f"${d[1]:,} {d[5]}% {owed_user.name} {d[0][5:]}\n"
        elif int(str(days).split(' ')[0]) > 365:
          debt_string += f"${d[1]:,} {d[5]}% {owed_user.name} ∞\n"
        else:
          debt_string += f"${d[1]:,} {d[5]}% {owed_user.name} {d[0][5:]}\n"
        if d[1] < d[4]*2:
          d_tomorrow += d[1] + int(d[1]*(d[5]*0.01))
        total_debt += d[1]
      if debt_string == "":
        debt_string = "*None!*"
  
      owed_string = ""
      total_owed = 0
      o_tomorrow = 0
      for d in owed:
        loaned_user = await self.client.fetch_user(d[2])
        days = datetime.strptime(d[0], FMT) - datetime.strptime(time_now, FMT)
        if str(days) == "0:00:00":
          owed_string += f"${d[1]:,} {d[5]}% {loaned_user.name} {d[0][5:]}\n"
        elif int(str(days).split(' ')[0]) > 365:
          owed_string += f"${d[1]:,} {d[5]}% {loaned_user.name} ∞\n"
        else:
          owed_string += f"${d[1]:,} {d[5]}% {loaned_user.name} {d[0][5:]}\n"
        if d[1] < d[4]*2:
          o_tomorrow += d[1] + int(d[1]*(d[5]*0.01))
        total_owed += d[1]
      if owed_string == "":
        owed_string = "*None!*"
      

    embed = discord.Embed(
      title = f"📜 {mention.name}'s Balance Sheet",
    )
    
    if total_owed >= total_debt:
      embed.color = discord.Colour.green()
    else:
      embed.color = discord.Colour.red()

    total_debt = f"**-${total_debt:,}** *(-${d_tomorrow:,} by tomorrow)*"
    total_owed = f"**+${total_owed:,}** *(+${o_tomorrow:,} by tomorrow)*"
    if len(debt) < 2:
      total_debt = ""
    if len(owed) < 2:
      total_owed = ""
    embed.add_field(name = f"**Debt** {total_debt}", value = debt_string)
    embed.add_field(name = f"**Owed** {total_owed}", value = owed_string, inline=False)
    embed.set_footer(text = f"{mention.name}", icon_url = mention.display_avatar.url)
    try:
      await ctx.channel.send(embed=embed)
    except discord.errors.HTTPException:
      await util.embed_error(ctx, "Your debt exceeds the Discord character limit.")
      

    
  
  @commands.command(aliases = ["cooldown","cd","cds","time"])
  async def cooldowns(self, ctx, mention:discord.User = None):
    mention = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(mention.id)]
    FMT = "%Y-%m-%d-%H:%M:%S"
    time_now = datetime.now()
    total_cooldowns = 0
    ready_cooldowns = 0

    ready = "<:ready:997527681333727253>"
    unavailable = "<:unavailable:997530299376341092>"
    

    embed = discord.Embed(
      description = f"You have a cooldown level of **{user['upgrade_cooldown']['level']}**\nYour cooldowns are reduced by **{user['upgrade_cooldown']['amount']}%**"
      )
                             
    # Daily.
    total_cooldowns += 1
    last_use = datetime.strptime(user["last_daily"], FMT)
    raw_cooldown = timedelta(hours = 24).total_seconds()
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    #Too Early
    if time_now < last_use + cooldown: 
      difference = time_now - last_use
      time_remaining = cooldown - difference
      time_remaining_str = str(time_remaining).split(".")[0]
      embed.add_field(name = "⏫ Daily", value = f"{unavailable}`{time_remaining_str}`")
    else:
      embed.add_field(name = "⏫ Daily", value = f"{ready}*Ready!*")
      ready_cooldowns += 1


    # Weekly.
    total_cooldowns += 1
    last_use = datetime.strptime(user["last_weekly"], FMT)
    raw_cooldown = timedelta(days = 7).total_seconds()
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    #Too Early
    if time_now < last_use + cooldown:
      difference = time_now - last_use
      time_remaining = cooldown - difference
      time_remaining_str = str(time_remaining).split(".")[0]
      embed.add_field(name = "📅 Weekly", value = f"{unavailable}`{time_remaining_str}`")
    else:
      embed.add_field(name = "📅 Weekly", value = f"{ready}*Ready!*")
      ready_cooldowns += 1

    # Steal.
    name = "🕵️‍♂️ Steal"
    if user["upgrade_steal"]["level"] <= 0:
      embed.add_field(name = name, value = f"{unavailable}`Locked!`")
    else:
      total_cooldowns += 1
      last_use = datetime.strptime(user["last_steal"], FMT)
      raw_cooldown = timedelta(hours = 24).total_seconds()
      cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
      # Too Early.
      if time_now < last_use + cooldown:
        difference = time_now - last_use
        time_remaining = cooldown - difference
        time_remaining_str = str(time_remaining).split(".")[0]
        embed.add_field(name = name, value = f"{unavailable}`{time_remaining_str}`")
      else:
        embed.add_field(name = name, value = f"{ready}*Ready!*")
        ready_cooldowns += 1

    # Gambling Addict.
    if user["upgrade_gambling_addict"]["level"] <= 0:
      embed.add_field(name = "🏓 Rebound", value = f"{unavailable}`Locked!`")
      embed.add_field(name = "🎯 Focus", value = f"{unavailable}`Locked!`")
    else:
      total_cooldowns += 2
      # Rebound.
      last_use = datetime.strptime(user["last_gambling_addict_passive"], FMT)
      raw_cooldown = timedelta(hours = 24).total_seconds()
      cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
      # Too Early.
      if time_now < last_use + cooldown:
        difference = time_now - last_use
        time_remaining = cooldown - difference
        time_remaining_str = str(time_remaining).split(".")[0]
        embed.add_field(name = "🏓 Rebound", value = f"{unavailable}`{time_remaining_str}`")
      else:
        embed.add_field(name = "🏓 Rebound", value = f"{ready}*Ready!*")
        ready_cooldowns += 1

      # Focus.
      last_use = datetime.strptime(user["last_gambling_addict_active"], FMT)
      raw_cooldown = timedelta(hours = 24).total_seconds()
      cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
      # Too Early.
      if time_now < last_use + cooldown:
        difference = time_now - last_use
        time_remaining = cooldown - difference
        time_remaining_str = str(time_remaining).split(".")[0]
        embed.add_field(name = "🎯 Focus", value = f"{unavailable}`{time_remaining_str}`")
      else:
        embed.add_field(name = "🎯 Focus", value = f"{ready}*Ready!*")
        ready_cooldowns += 1
    
    # Miner.
    name = "👨‍🏭 Miner"
    if user["upgrade_miner"]["level"] <= 0:
      embed.add_field(name = name, value = f"{unavailable}`Locked!`")
    else:
      total_cooldowns += 1
      last_use = datetime.strptime(user["last_mine"], FMT)
      raw_cooldown = timedelta(hours = 48).total_seconds()
      cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
      # Too Early.
      if time_now < last_use + cooldown:
        difference = time_now - last_use
        time_remaining = cooldown - difference
        time_remaining_str = str(time_remaining).split(".")[0]
        embed.add_field(name = name, value = f"{unavailable}`{time_remaining_str}`")
      else:
        embed.add_field(name = name, value = f"{ready}*Ready!*")
        ready_cooldowns += 1

    embed.title = f"⌛ {mention.name}'s Cooldowns | *{ready_cooldowns}/{total_cooldowns}*"
    embed.set_footer(text = f"{mention.name} has saved {str(timedelta(seconds=user['stat_time_saved']))} total.", icon_url = mention.display_avatar.url)
    
    if ready_cooldowns <= 0:
      embed.color = discord.Colour.red()
    elif ready_cooldowns < total_cooldowns:
      embed.color = discord.Colour.orange()
    else:
      embed.color = discord.Colour.green()
      
    await ctx.channel.send(embed=embed)
    




  @commands.command(aliases = ["board","scoreboard","rank"])
  async def leaderboard(self, ctx, *variable):
    user_dict = await util.get_user_data()
    data = []
    words = []
    stat_name = None
  
    for word in variable:
      words.append(word.lower().strip())
  
    for key in user_dict[str(ctx.author.id)]:
      if all(word in key for word in words):
        stat_name = key
        break
    member_amount = 0
    async for user in ctx.guild.fetch_members(limit=None):
      member_amount +=1
      if "upgrade" not in stat_name or "stat_upgrade_loss" in stat_name:
        user = (user_dict[str(user.id)][stat_name],user.mention)
      else:
        user = (user_dict[str(user.id)][stat_name]["level"],user.mention,user_dict[str(user.id)][stat_name]["amount"])
      data.append(user)
    
    if "loss" in words or "lowest" in words:
      data.sort(reverse=False)
    else:
      data.sort(reverse=True)
  
    symbol = ""
    if "profit" in stat_name or "loss" in stat_name:
      symbol += "$"
  
    output = ""
    i=0
    while i < 10 and i < member_amount:
      if len(data[i]) < 3:
        output+= f"**{i+1}. {data[i][1]}**: {symbol}{data[i][0]:,}\n"
      else:
        output+= f"**{i+1}. {data[i][1]}**: Level {symbol}{data[i][0]:,} | {data[i][2]:,}\n"
      i+=1
    stat_name = stat_name.replace("stat_","")
    embed = discord.Embed(
    colour = discord.Colour.magenta(),
    title = f"Top 10 {stat_name.replace('_',' ').title()} Leaderboard",
    description = output)
    await ctx.channel.send(embed=embed)


  @commands.command(aliases = ["inv","items"])
  async def inventory(self, ctx, mention:discord.User = None):
    account = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(account.id)]
    with open("upgrades.json","r") as f:
      d = json.load(f)
    upgrades = ""
    for key in user:
      if key.startswith("upgrade_"):
        if user[key]["level"] >= 1 and d[key]["single_use"] == True:
          upgrade_name = key.split("_")
          upgrades += f'{d[key]["emoji"]} {upgrade_name[1].capitalize()}: **{user[key]["level"]}**\n'
    if upgrades == "":
      upgrades += "**Empty!**"
      desc = f"{upgrades}\nYou can purchase items from the $shop."
    else:
      desc = f"{upgrades}\nTo use an item in your inventory, type `$use` followed by the item name."
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = f"{account.name}'s Inventory",
    description = desc)
    await ctx.channel.send(embed=embed)
  
  
  
  @commands.command(aliases = ["sloan","balance","bal","robcoins","robux","slons","slon",""])
  async def sloans(self, ctx, mention:discord.User = None, chart = None, mention2:discord.User = None):
    mention = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(mention.id)]
    balance = user["balance"]

    # Debt calculation.
    future_str = ""
    if len(user["owed"]) >= 1 or len(user["debt"]) >= 1:
      future_bal = 0
      op = "+"
      for o in user["owed"]:
        future_bal += o[1]
      for d in user["debt"]:
        future_bal -= d[1]
      if future_bal < 0:
        future_bal = -future_bal
        op = "-"
      future_str = f" *({op}${future_bal:,})*"
    
    embed = discord.Embed(
      title = "<:heads:981507458944098345> Sloans",
      description = f"{mention.name} has **${balance:,}**{future_str} Sloans.")
    
    # % Change.
    old = user["last_balance"]
    new = balance
    if old == 0:
      old = 1
    pc = (new - old) / old * 100
    
    status = "▲"
    embed.color = discord.Colour.green()
    if pc < 0:
      embed.color = discord.Colour.red()
      status = "▼"
    embed.set_footer(text = f"{status} {round(pc,2):,}% today", icon_url = mention.display_avatar.url)
    await ctx.channel.send(embed=embed)

  

  @commands.command(aliases = ["prof","account","whois","acc","p"])
  async def profile(self, ctx, mention:discord.User = None):
  
    account = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(account.id)]
    save = False
  
    if ctx.author.id != account.id:
      user["stat_profile_views"] += 1
      save = True

    total_flips = user["stat_flip_victory"] + user["stat_flip_defeat"]
    if total_flips != 0:
      winrate = round((user["stat_flip_victory"] / total_flips) * 100, 2)
    else:
      winrate = 0
  
    balance = user["balance"]
    highest_balance = user["stat_highest_balance"]
    total_given = user["stat_give_loss"]
    total_received = user["stat_give_profit"]
    total_daily = user["stat_daily_quantity"]
    total_weekly = user["stat_weekly_quantity"]
    #could show redeemed sloans next to the activity e.g. Dailys Done: 5 (+$500)
    redeemed_sloans = user["stat_daily_profit"] + user["stat_weekly_profit"]
    total_flips = user["stat_flip_quantity"]
    highest_daily_streak = user["stat_highest_daily_streak"]
    flip_profit = user["stat_flip_profit"]
    flip_loss = user["stat_flip_loss"]
    flip_streak = user["stat_highest_flip_win_streak"]
    views = user["stat_profile_views"]
    total_claims = user["stat_claim_quantity"]
    claim_profit = user["stat_claim_profit"]
    upgrade_loss = user["stat_upgrade_loss"]

    gambling_profit = flip_profit + user["stat_jackpot_profit"] + user["stat_mystery_box_profit"]
    gambling_loss = flip_loss + user["stat_mystery_box_loss"] + user["stat_jackpot_loss"]
    vs_profit = user["stat_trivia_profit"]

    # Deprecated.
    #if user["stat_last_active"] != "":
      #FMT = "%Y-%m-%d-%H:%M:%S"
      #last_active = datetime.strptime(user["stat_last_active"], FMT)
      #time_passed = datetime.now() - last_active
      #time_since_last_active = str(time_passed).split(".")[0]
    #else:
      #time_since_last_active = ":skull: Unknown"
    
    favourite_charity_text = ""
    if user["stat_highest_give_sent_user"] != "":
      charity = await self.client.fetch_user(user["stat_highest_give_sent_user"])
      favourite_charity_text = f"Favourite Charity: **{charity.mention}**\n"
    
    richest_benefactor_text = ""
    if user["stat_highest_give_received_user"] != "": 
      benefactor = await self.client.fetch_user(user["stat_highest_give_received_user"])
      richest_benefactor_text = f"Richest Benefactor: **{benefactor.mention}**\n"
    
    with open("upgrades.json","r") as f:
      d = json.load(f)
    
    upgrade_emojis = ""
    for key in user:
      if key.startswith("upgrade_"):
        if user[key]["level"] >= 1 and key != "upgrade_loan":
          upgrade_name = key.split("_")
          upgrade_emojis += f'{d[key]["emoji"]} {upgrade_name[1].capitalize()}: **{user[key]["level"]}**\n'
    if upgrade_emojis == "":
      upgrade_emojis += "*None*"

    desc = ""
    if user["rob_banned"] == True:
      desc += "🚫 "
    if user["upgrade_gambling_addict"]["amount"] == True:
      desc += "🎯 "
    # Curse Check.
    if user["cursed"]:
      FMT = "%Y-%m-%d-%H:%M:%S"
      curses = len(user["cursed"])
      expired = []
      for curse in user["cursed"]:
        if datetime.utcnow() > datetime.strptime(curse[0], FMT):
          user["luck"] = user["luck"]/curse[1]
          expired.append(curse)
          curses -= 1
          save = True
      if curses > 0:
        desc += "😈 "
      for curse in expired:
        user["cursed"].remove(curse)

    #  Saves user data if a view has been added or a curse has been removed.
    if save == True:
      await util.save_user_data(user_dict)

    future_str = ""
    if len(user["owed"]) >= 1 or len(user["debt"]) >= 1:
      future_bal = 0
      op = "+"
      for o in user["owed"]:
        future_bal += o[1]
      for d in user["debt"]:
        future_bal -= d[1]
      if future_bal < 0:
        future_bal = -future_bal
        op = "-"
      future_str = f" *({op}${future_bal:,})*"

    rel = "*Unknown*"
    if user['stat_loan_quantity_taken'] > 0:
      rel = f"**{round(( ( user['stat_loan_quantity_paid'] - user['stat_loan_quantity_paid_late'] ) / user['stat_loan_quantity_taken']) * 100, 2):,}%**"

    title = ""
    #  This whole title system needs a rework for it to be actually interesting.
    incomes = [ 
              (redeemed_sloans,"👨‍🌾 Farmer", "👨‍🌾 Apprentice Farmer", "👨‍🌾 Formidable Farmer", "👨‍🌾 Full-Time Farmer", "👨‍🌾 Turbo Farmer", "👨‍🌾 Legendary Farmer"), 
              (gambling_profit, "🃏 Gambler", "🃏 Dabbling Gambler", "🃏 Degenerate Gambler", "🃏 Fanatical Gambler", "🃏 Genius Gambler", "🃏 God-Tier Gambler"), 
              (vs_profit, "⚔ Challenger", "⚔ Crazed Challenger", "⚔ Proficient Challenger", "⚔ Dangerous Challenger", "⚔ Unstoppable Challenger", "⚔ Legendary Challenger"), 
              (total_received, "🏳 Beggar", "🏳 Homeless Beggar", "🏳 Scheming Beggar", "🏳 Dexterous Beggar", "🏳 Turbo Beggar", "🏳 Professional Beggar"),
              (claim_profit + user["stat_turf_war_profit"],"🦅 Hunter","🦅 Keen Hunter","🦅 Skilled Hunter","🦅 Proficient Hunter","🦅 Elite Hunter","🦅 Master Hunter"),
              (user["stat_loan_profit"],"📊 Investor", "📊 Avid Investor", "📊 Smart Investor", "📊 Qualified Investor", "📊 Genius Investor", "📊 Terminal Investor"),
              (user["stat_gold_transmutation_profit"], "🎮 Gamer", "🎮 Gold Gamer", "🎮 Platinum Gamer", "🎮 Diamond Gamer", "🎮 Master Gamer", "🎮 Grandmaster Gamer"),
              (0, "🕵️‍♂️ Thief", "🕵️‍♂️ Small-Time Thief", "🕵️‍♂️ Mischievous Thief", "🕵️‍♂️ Wanted Thief", "🕵️‍♂️ Master Thief", "🕵️‍♂️ Ultimate Thief")
              ]
    situational_titles = (total_received, "⚖ Trader", "⚖ Amatuer Trader", "⚖ Experienced Trader", "⚖ Devious Trader", "⚖ Turbo Trader", "⚖ Professional Trader")
    incomes.sort(reverse=True)
    if incomes[0][0] > 0:
      if incomes[0][0] < 1000:
        title = f"*{incomes[0][1]}*"
      elif incomes[0][0] >= 1000 and incomes[0][0] < 100000000:
        title = f"*{incomes[0][len(str(int(incomes[0][0]/100)))]}*"
        if "Beggar" in title:
          tg = total_given * -1
          if tg <= total_received * 1.2 and tg >= total_received * 0.8:
            title = f"*{situational_titles[len(str(int(situational_titles[0]/100)))]}*"
            
          
      else:
        title = f"*{incomes[0][6]}*"
        
        

    bw = [ (user["stat_highest_flip"], "Coin Flip"), (user["stat_mystery_box_highest_win"], "Mystery Box"), (user["stat_jackpot_highest_win"], "Jackpot")]
    bw.sort(reverse=True)
    biggest_win = f"**${bw[0][0]:,}**"
    biggest_win_game = bw[0][1]

    gambling_desc = ""
    fav_game = "Unknown"
    gamemodes = [  (total_flips, "Coin Flip"),(user["stat_mystery_box_quantity"], "Mystery Box"),(user["stat_jackpot_quantity"], "Jackpot")  ]
    gamemodes.sort(reverse=True)
    if gamemodes[0][0] > 0:
      fav_game = gamemodes[0][1]
      if fav_game != biggest_win_game:
        biggest_win += f" *({biggest_win_game})*"

    
    bal_sum = 0
    for bal in user["average_balance"]:
      bal_sum += bal[1]
    length = 1
    if len(user["average_balance"]) > 1:
      length = len(user["average_balance"])
    average_bal = round(bal_sum/length)

    length = 1
    if len(user["average_loan_repay_time"]) > 1:
      length = len(user["average_loan_repay_time"])
    avg_repay_time = round( sum(user["average_loan_repay_time"])/length, 1)
        
    if fav_game == "Coin Flip":
      gambling_desc = f"\nWinrate: **{winrate}%**\nFlips: **{total_flips:,}**\nBest Streak: **{flip_streak}**\nBiggest Win: {biggest_win}\n────────────"
    elif fav_game == "Mystery Box":
      gambling_desc = f"\nProfitability: **{round((user['stat_mystery_box_profit'] / (user['stat_mystery_box_loss'] * -1)) * 100, 2)}%**\nOpened: **{user['stat_mystery_box_quantity']:,}**\nBiggest Win: {biggest_win}\n────────────"
    elif fav_game == "Jackpot":
      gambling_desc = f"\nWinrate: **{round(user['stat_jackpot_quantity'] / user['stat_jackpot_victory'] * 100, 2)}%**\nLuckiest Win: **{round(user['stat_jackpot_lowest_odds_victory'],2)}%**\nPots Joined: **{user['stat_jackpot_quantity']:,}**\nBiggest Win: {biggest_win}\n────────────"

    status = f"*Good Standing*"
    if user["rob_banned"] == True:
      status = f"```diff\n- 🚫 Rob Banned!```"
    elif user['stat_rob_banned_quantity'] > 0:
      status = f"```fix\n{user['stat_rob_banned_quantity']} ROB Bans on record```"
      
    embed = discord.Embed(
    colour = discord.Colour.magenta(),
    title = f"{account.name}'s Profile",
    description = f"{title}\n{desc}\n{account.mention}\n{status}")
    embed.add_field(name = "<:heads:981507458944098345> Sloans", value = f"Balance: **${balance:,}**{future_str}\nAverage: **${average_bal:,}**\nHighest: **${highest_balance:,}**\nSpent: **${upgrade_loss:,}**\nCash Flow: **${user['total_cash_flow']:,}**", inline = True)
    embed.add_field(name = ":tickets: Rewards", value = f"Highest Streak: **{highest_daily_streak:,}**\nDaily: **{total_daily:,}** +${user['stat_daily_profit']:,}\nWeekly: **{total_weekly:,}** +${user['stat_weekly_profit']:,}\nWhacks: **{total_claims:,}** +${claim_profit:,}\nTotal: **${redeemed_sloans+claim_profit:,}**", inline = True)
    embed.add_field(name = '\u200b', value = '\u200b', inline = True)
    embed.add_field(name = ":incoming_envelope: Transactions", value = f"Reliability: {rel}\nRepay Time: **{avg_repay_time}d**\nGiven: **${total_given:,}**\nReceived: **${total_received:,}**\nNet Gain: **${total_given + total_received:,}**\n{favourite_charity_text}{richest_benefactor_text}", inline = True)
    embed.add_field(name = ":game_die: Gambling", value = f"Favourite: **{fav_game}**{gambling_desc}\nWon: **${gambling_profit:,}**\nLost: **${gambling_loss:,}**\nNet Gain: **${gambling_profit + gambling_loss:,}**", inline = True)
    embed.add_field(name = ":star2: Upgrades", value = upgrade_emojis)
    embed.set_thumbnail(url = account.display_avatar.url)
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"{views:,} Views - Requested by {ctx.author.name}")
    await ctx.channel.send(embed=embed)
  
  
  
  async def get_shop_values(self, user, upgrade, single_use = False):
    with open("upgrades.json","r") as f:
      d = json.load(f)
    price = 'MAX'
    if single_use == False:
      next_amount = d[upgrade]["amounts"][str( user[upgrade]["level"] )]
      if user[upgrade]["level"] < d[upgrade]["max_level"]:
        next_amount = d[upgrade]["amounts"][str( user[upgrade]["level"] + 1)]
        price = f'${user[upgrade]["price"]:,}'
    
    else:
      next_amount = None
      if user[upgrade]["level"] < d[upgrade]["max_level"]:
        price = f'${user[upgrade]["price"]:,}'
        
    level = await util.superscript(user[upgrade]["level"])
    return level, price, next_amount
  
  @commands.command(aliases = ["upgrades","perks","upgrade","store","$","s"])
  async def shop(self, ctx, mention:discord.User = None):
    mention = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(mention.id)]
    with open("upgrades.json","r") as f:
      d = json.load(f)
    max = 'MAX'
      
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = f":star2: {mention.name}'s Shop",
    description = f"**Current Balance: ${user['balance']:,}**\nPurchase upgrades by typing: `$buy name`\nNot all upgrades are currently available to purchase, dysfunctional upgrades are marked by `*`")

    #Apocalypse
    embed.add_field(name = ":comet: *Apocalypse", value = "**$50M**\nSingle use, bans 50% of the server for 30 minutes.", inline = True)

    #Bankrupt
    embed.add_field(name = ":boom: *Bankrupt", value = "**$10M**\nSingle use, blow up someone's bank account and spread the wealth.", inline = True)

    #Ban
    level, price, next_amount = await self.get_shop_values(user, "upgrade_ban", single_use = True)
    embed.add_field(name = f":hammer: Ban {level}", value = f"**{price}**\nSingle use, ban someome temporarily.", inline = True)

    #Kick
    level, price, next_amount = await self.get_shop_values(user, "upgrade_kick", single_use = True)
    embed.add_field(name = f":foot: Kick {level}", value = f"**{price}**\nSingle use, kicks someone random.", inline = True)

    #Miner
    level, price, next_amount = await self.get_shop_values(user, "upgrade_miner")
    embed.add_field(name = f"{d['upgrade_miner']['emoji']} Miner {level}", value = f"**{price}**\nOnce every two days, illegally mine `${next_amount}` a minute until you get caught or choose to stop.", inline = True)

    #Gambling Addict
    level, price, next_amount = await self.get_shop_values(user, "upgrade_gambling_addict")
    embed.add_field(name = f":game_die: Gambling Addict {level}", value = f"**{price}**\nWin more often and get rewarded for losing it all.", inline = True)

    #Steal
    level, price, next_amount = await self.get_shop_values(user, "upgrade_steal")
    embed.add_field(name = f":detective: Steal {level}", value = f"**{price}**\nSteal upwards of `${next_amount:,}` from your friends every day.", inline = True)

    #Sabotage
    level, price, next_amount = await self.get_shop_values(user, "upgrade_sabotage", single_use = True)
    embed.add_field(name = f":smiling_imp: Sabotage {level}", value = f"**{price}**\nSingle use, dramatically decrease someone's coin flip odds by `50%` for 24 hours.", inline = True)

    #Cooldown
    level, price, next_amount = await self.get_shop_values(user, "upgrade_cooldown")
    embed.add_field(name = f":hourglass_flowing_sand: Cooldown {level}", value = f"**{price}**\nPermanently reduce all cooldowns by `{next_amount}%`.", inline = True)

    #Protection
    level, price, next_amount = await self.get_shop_values(user, "upgrade_protection")
    embed.add_field(name = f":shield: Protection {level}", value = f"**{price}**\nMore time can pass before you lose your daily streak, gain `{next_amount}%` protection from Sabotage & Steal.", inline = True)

    #Weekly
    level, price, next_amount = await self.get_shop_values(user, "upgrade_weekly")
    next_amount += 1000
    embed.add_field(name = f":date: Weekly {level}", value = f"**{price}**\nPermanently increase weekly reward to `+${next_amount:,}`.", inline = True)

    #Opportunist
    extra = ""
    if user["upgrade_opportunist"]["level"] > 4:
      extra = "\nGet notified of events before they happen."
    level, price, next_amount = await self.get_shop_values(user, "upgrade_opportunist")
    embed.add_field(name = f"🦊 Opportunist {level}", value = f"**{price}**\nGain `+{next_amount:,}%` more Sloans from all events.{extra}", inline = True)

    #Passive Income
    level, price, next_amount = await self.get_shop_values(user, "upgrade_passive_income")
    next_amount = d["upgrade_passive_income"]["amounts"][str( user["upgrade_passive_income"]["level"]+1 )]
    
    embed.add_field(name = f":chart_with_upwards_trend: Passive Income {level}", value = f"**{price}**\nOnce a minute, have a 50% chance to gain `+${next_amount:,}` from any message.", inline = True)
    
    #Mystery Box
    level, price, next_amount = await self.get_shop_values(user, "upgrade_mystery_box", single_use = True)
    embed.add_field(name = f":gift: Mystery Box {level}", value = f"**{price}**\nMysterious.", inline = True)

    #Streak
    level, price, next_amount = await self.get_shop_values(user, "upgrade_streak")
    embed.add_field(name = f":tada: Streak {level}", value = f"**{price}**\nGain `{next_amount}%` more from your daily streak.", inline = True)

    #Daily
    level, price, next_amount = await self.get_shop_values(user, "upgrade_daily")
    next_amount += 100
    embed.add_field(name = f":arrow_double_up: Daily {level}", value = f"**{price}**\nPermanently increase daily reward to `+${next_amount:,}`.", inline = True)
  
    #Mail
    level, price, next_amount = await self.get_shop_values(user, "upgrade_mail", single_use = True)
    embed.add_field(name = f":mailbox: Mail {level}", value = f"**{price}**\nAnonymously DM someone a custom message through Rob.", inline = True)

    #Gold Transmutation
    level = user["upgrade_gold_transmutation"]["level"]
    price = user["upgrade_gold_transmutation"]["price"]
    next_amount = d["upgrade_gold_transmutation"]["amounts"][str( user["upgrade_gold_transmutation"]["level"]+1 )]
    games_remaining = f"${price:,}"
    if level >= 1:
      total_games = user["stat_league_games_quantity"]
      level_req = [0,15,20,30,40,60,85,120,175,250]
      games=0
      for i in range(level):
        games += level_req[i]
      games_remaining = f"{level_req[level]-(total_games-games)} Games"
    elif level >= 10:
      games_remaining = "MAX"
    level = await util.superscript(level)
    embed.add_field(name = f"<:lol_passive:957853326626656307> Gold Transmutation {level}", value = f"**{games_remaining}**\nTransform `{next_amount}%` of the gold you earn in League of Legends into Sloans", inline = True)

    #Restore Streak
    streak = user["stat_highest_daily_streak"]
    percent = user["upgrade_streak"]["amount"]
    amount = streak*(streak+1)/2 * 10  +  streak*(streak+1)/2 * 10 * percent*0.01
    price = await util.round_number(amount+amount*.25, 10)
    level = await util.superscript(user["upgrade_restore"]["level"])
    embed.add_field(name = f":confetti_ball: Restore Streak {level}", value = f"**${price:,}**\nSingle use, restores your current daily streak to `{streak:,}`", inline = True)

    #Change Summoner Name
    level, price, next_amount = await self.get_shop_values(user, "upgrade_change_lol", single_use = True)
    embed.add_field(name = f"👤 Change Summoner Name {level}", value = f"**{price}**\nUpdate your League of Legends summoner name & region in the database.", inline = True)

    #Banker
    min_cf = d["upgrade_banker"]["prices"][str( user["upgrade_banker"]["level"] )]
    if len(user["weekly_cash_flow"]) < 7:
      price = f"{7 - len(user['weekly_cash_flow'])} Days"

    elif sum(user["12_week_average_cash_flow"]) < min_cf*len(user["12_week_average_cash_flow"]):
      days_this_week = user['day_counter']%7
      cash_flow_this_week = 0
      for i in range(days_this_week):
        i+=1
        cash_flow_this_week += user["weekly_cash_flow"][len(user["weekly_cash_flow"])-i][1]
      cash_flow_this_week += user["daily_cash_flow"]
      price = f"Transact ${(min_cf + min_cf*len(user['12_week_average_cash_flow']) - sum(user['12_week_average_cash_flow'])) - cash_flow_this_week:,}"
    else:
      price = f'${int(await util.round_number( sum(user["12_week_average_cash_flow"]) / len(user["12_week_average_cash_flow"])  ,1000) * 0.1):,}'
    
    level = await util.superscript(user["upgrade_banker"]["level"])
    next_amount = d["upgrade_banker"]["amounts"][str( user["upgrade_banker"]["level"]+1 )]
    embed.add_field(name = f"💵 Banker {level}", value = f"**{price}**\nOffer up to `{next_amount:,}%` of your balance as a compound interest loan.", inline = True)
    
    #Loan
    price = "FREE"
    level = await util.superscript(user["upgrade_loan"]["level"])
    embed.add_field(name = f"🏦 Loan {level}", value = f"**{price}**\nTake out a `5%` interest loan of up to `$20,000` which must be repaid within two weeks.", inline = True)
    
    embed.set_footer(text=f"{mention.name} has spent ${abs(user['stat_upgrade_loss']):,} on upgrades in total.", icon_url = mention.display_avatar.url)
    await ctx.channel.send(embed=embed)







  #second shop maybe coming in future
"""@commands.command(aliases = ["quest","quests","questshop","$","upgradeq","upgradeother"])
async def quest_shop(ctx):
  user_dict = await get_user_data()
  user = user_dict[str(ctx.author.id)]

  embed = discord.Embed(
  colour = (discord.Colour.blue(),
  title = f":sparkles: {ctx.author.name}'s Quest Upgrades",
  description = "Purchase upgrades by typing: `$buy name`!\nFunctional upgrades are marked by an *asterisk")
  
  embed.add_field(name = ":comet: Apocalypse", value = "**$50M**\nSingle use, bans 50% of the server for 30 minutes.", inline = True)
  embed.add_field(name = ":boom: Bankrupt", value = "**$10M**\nSingle use, blow up someone's bank account and spread the wealth.", inline = True)
  upgrade_price = user["upgrade_ban"][2]
  upgrade_quantity = await superscript(user["upgrade_ban"][1])
  embed.add_field(name = f":hammer: *Ban {upgrade_quantity}", value = f"**${upgrade_price:,}**\nSingle use, ban someome temporarily.", inline = True)

 
  embed.add_field(name = ":game_die: Gambling Addict", value = "**$200k^**\nPermanently gain %5 more from non 50/50 bets.", inline = True)
  embed.add_field(name = ":detective: Steal", value = "**$100k^**\nPermanently unlock the $steal command.", inline = True)

  embed.add_field(name = ":smiling_imp: Sabotage", value = "**$50k**\nSingle use, dramatically decrease someone's win chance for 24 hours.", inline = True)

  embed.add_field(name = ":shield: Protection", value = "**$25k^**\n+10% chance to parry $steal, even when offline.", inline = True)


  await ctx.channel.send(embed=embed)"""
  

async def setup(client):
  await client.add_cog(Frontend(client))