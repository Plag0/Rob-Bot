from discord.ext import commands
import discord
from datetime import datetime
from replit import db
from cogs.utility import Utility as util

class Frontend(commands.Cog):
  def __init__(self, client):
    self.client = client



  @commands.command(aliases = ["board","scoreboard","rank"])
  async def leaderboard(self, ctx, *variable):
    data = []
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    words = []
    stat_name = None
  
    for word in variable:
      words.append(word.lower().strip())
  
    print(f"string is {words}")
  
    for key in user_dict[str(ctx.author.id)]:
      print(f"comparing {key}")
      if all(word in key for word in words):
        print(f"match found, assigning var as {key}")
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
    
    if "loss" in words:
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
        output+= f"**{i+1}. {data[i][1]}**: Level {symbol}{data[i][0]:,} + ${data[i][2]:,}\n"
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
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(account.id)]
    upgrades = ""
    for key in user:
      if key.startswith("upgrade_"):
        if user[key]["level"] >= 1 and user[key]["single_use"] == True:
          upgrade_name = key.split("_")
          upgrades += f'{user[key]["emoji"]} {upgrade_name[1].capitalize()}: **{user[key]["level"]}**\n'
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
  async def sloans(self, ctx, mention:discord.User = None):
    mention = mention or ctx.author
  
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    balance = user_dict[str(mention.id)]["balance"]
  
    embed = discord.Embed(
      colour = (discord.Colour.magenta()),
      title = ":coin: Sloans",
      description = f"{mention.name} has **${balance:,}** sloans."
      )
    await ctx.channel.send(embed=embed)


  @commands.command(aliases = ["prof","account","whois","acc","p"])
  async def profile(self, ctx, mention:discord.User = None):
  
    account = mention or ctx.author
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(account.id)]
  
    if ctx.author.id != account.id:
      user["stat_profile_views"] += 1
      #await util.save_user_data(user_dict)

    total_flips = user["stat_flip_victory"] + user["stat_flip_defeat"]
    if total_flips != 0:
      winrate = round((user["stat_flip_victory"] / total_flips) * 100, 2)
    else:
      winrate = 0
  
    balance = user["balance"]
    highest_balance = user["stat_highest_balance"]
    rep = user["rep"]
    total_given = user["stat_give_loss"]
    total_received = user["stat_give_profit"]
    total_daily = user["stat_daily_quantity"]
    total_weekly = user["stat_weekly_quantity"]
    #could show redeemed sloans next to the activity e.g. Dailys Done: 5 (+$500)
    redeemed_sloans = user["stat_daily_profit"] + user["stat_weekly_profit"]
    total_flips = user["stat_flip_quantity"]
    highest_flip = user["stat_highest_flip"]
    highest_daily_streak = user["stat_highest_daily_streak"]
    flip_profit = user["stat_flip_profit"]
    flip_loss = user["stat_flip_loss"]
    flip_streak = user["stat_highest_flip_win_streak"]
    views = user["stat_profile_views"]
    total_claims = user["stat_claim_quantity"]
    claim_profit = user["stat_claim_profit"]
    upgrade_loss = user["stat_upgrade_loss"]

    if user["stat_last_active"] != "":
      FMT = "%Y-%m-%d-%H:%M:%S"
      last_active = datetime.strptime(user["stat_last_active"], FMT)
      time_passed = datetime.now() - last_active
      time_since_last_active = str(time_passed).split(".")[0]
    else:
      time_since_last_active = ":skull: Unknown"
    
  
    if user["stat_highest_give_sent_user"] != "":
      charity = await self.client.fetch_user(user["stat_highest_give_sent_user"])
      favourite_charity_text = f"Favourite Charity: **{charity.mention}**"
    else:
      favourite_charity_text = ""
    if user["stat_highest_give_received_user"] != "": 
      benefactor = await self.client.fetch_user(user["stat_highest_give_received_user"])
      richest_benefactor_text = f"Richest Benefactor: **{benefactor.mention}**"
    else:
      richest_benefactor_text = ""
    
    upgrade_emojis = ""
    for key in user:
      if key.startswith("upgrade_"):
        if user[key]["level"] >= 1:
          upgrade_name = key.split("_")
          upgrade_emojis += f'{user[key]["emoji"]} {upgrade_name[1].capitalize()}: **{user[key]["level"]}**\n'
    if upgrade_emojis == "":
      upgrade_emojis += "No Upgrades!"
  
    embed = discord.Embed(
    colour = discord.Colour.magenta(),
    title = f"{account.name}'s Profile",
    description = f"{account.mention}\nLast Active: {time_since_last_active}")
    embed.add_field(name = ":coin: Sloans", value = f"Balance: **${balance:,}**\nHighest: **${highest_balance:,}**\nSpent: **${upgrade_loss:,}**", inline = True)
    embed.add_field(name = ":tickets: Rewards", value = f"Dailys Done: **{total_daily:,}**\nHighest Streak: **{highest_daily_streak:,}**\nWeeklys Done: **{total_weekly:,}**\nRobs Caught: **{total_claims:,}**\nProfit: **${redeemed_sloans+claim_profit:,}**", inline = True)
    embed.add_field(name = ":arrow_up_small: Rob Points", value = f"**{rep}**", inline = True)
    embed.add_field(name = ":incoming_envelope: Transactions", value = f"Given: **${total_given:,}**\nReceived: **${total_received:,}**\nNet Gain: **${total_given + total_received:,}**\n{favourite_charity_text}\n{richest_benefactor_text}", inline = True)
    embed.add_field(name = ":game_die: Gambling", value = f"Flip Winrate: **{winrate}%**\nTotal Flips: **{total_flips:,}**\nBiggest Flip: **${highest_flip:,}**\nHighest Win Streak: **{flip_streak}**\nWon: **${flip_profit:,}**\nLost: **${flip_loss:,}**\nNet Gain: **${flip_loss + flip_profit:,}**", inline = True)
    embed.add_field(name = ":star2: Upgrades", value = upgrade_emojis)
    embed.set_thumbnail(url = account.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"{views:,} Views - Requested by {ctx.author.name}")
    await ctx.channel.send(embed=embed)
  
  
  
  
  
  #Come back later and future proof the dictionary so amounts["10"] dosn't cause problems.
  @commands.command(aliases = ["upgrades","perks","upgrade","store","$"])
  async def shop(self, ctx):
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    balance = user["balance"]
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = f":star2: {ctx.author.name}'s Shop",
    description = f"**Current Balance: ${balance:,}**\nPurchase upgrades by typing: `$buy name`\nNot all upgrades are currently available to purchase, dysfunctional upgrades are marked by `*`")

    #Apocalypse
    embed.add_field(name = ":comet: *Apocalypse", value = "**$50M**\nSingle use, bans 50% of the server for 30 minutes.", inline = True)

    #Bankrupt
    embed.add_field(name = ":boom: *Bankrupt", value = "**$10M**\nSingle use, blow up someone's bank account and spread the wealth.", inline = True)

    #Ban
    level = await util.superscript(user["upgrade_ban"]["level"])
    price = user["upgrade_ban"]["price"]
    embed.add_field(name = f":hammer: Ban {level}", value = f"**${price:,}**\nSingle use, ban someome temporarily.", inline = True)

    #Kick
    level = await util.superscript(user["upgrade_kick"]["level"])
    price = user["upgrade_kick"]["price"]
    embed.add_field(name = f":foot: Kick {level}", value = f"**${price:,}**\nSingle use, kicks someone random.", inline = True)

    #Gambling Addict
    embed.add_field(name = ":game_die: *Gambling Addict", value = "**$200k^**\nPermanently gain more from all-in bets.", inline = True)

    #Steal
    embed.add_field(name = ":detective: *Steal", value = "**$100k^**\nPermanently unlock the $steal command.", inline = True)

    #Sabotage
    embed.add_field(name = ":smiling_imp: *Sabotage", value = "**$50k**\nSingle use, dramatically decrease someone's win chance for 24 hours.", inline = True)

    #Cooldown
    level = await util.superscript(user["upgrade_cooldown"]["level"])
    price = user["upgrade_cooldown"]["price"]
    next_amount = user["upgrade_cooldown"]["amounts"][str( user["upgrade_cooldown"]["level"]+1 )]
    embed.add_field(name = f":hourglass_flowing_sand: Cooldown {level}", value = f"**${price:,}**\nPermanently reduce all cooldowns by `{next_amount}%`.", inline = True)

    #Protection
    embed.add_field(name = ":shield: *Protection", value = "**$25k^**\n+10% chance to parry $steal, even when offline.", inline = True)

    #Rename
    embed.add_field(name = ":name_badge: *Rename", value = "**$20k**\nSingle use, set someone's nickname for a day.", inline = True)

    #Weekly
    level = await util.superscript(user["upgrade_weekly"]["level"])
    price = user["upgrade_weekly"]["price"]
    next_amount = user["upgrade_weekly"]["amounts"][str( user["upgrade_weekly"]["level"]+1 )]
    embed.add_field(name = f":date: Weekly {level}", value = f"**${price:,}**\nPermanently increase weekly reward by `+${next_amount:,}`.", inline = True)

    #Passive Income
    level = await util.superscript(user["upgrade_passive_income"]["level"])
    price = user["upgrade_passive_income"]["price"]
    next_amount = user["upgrade_passive_income"]["amounts"][str( user["upgrade_passive_income"]["level"]+1 )]
    
    embed.add_field(name = f":chart_with_upwards_trend: Passive Income {level}", value = f"**${price:,}**\nOnce a minute, have a 50% chance to gain `+${next_amount:,}` from any message.", inline = True)
    
    #Mystery Box
    level = await util.superscript(user["upgrade_mystery_box"]["level"])
    price = user["upgrade_mystery_box"]["price"]
    embed.add_field(name = f":gift: Mystery Box {level}", value = f"**${price:,}**\nMysterious.", inline = True)

    #Streak
    level = await util.superscript(user["upgrade_streak"]["level"])
    price = user["upgrade_streak"]["price"]
    next_amount = user["upgrade_streak"]["amounts"][str( user["upgrade_streak"]["level"]+1 )]
    embed.add_field(name = f":tada: Streak {level}", value = f"**${price:,}**\nGain `{next_amount}%` more from your daily streak.", inline = True)

    #Daily
    level = await util.superscript(user["upgrade_daily"]["level"])
    price = user["upgrade_daily"]["price"]
    next_amount = user["upgrade_daily"]["amounts"][str( user["upgrade_daily"]["level"]+1 )]
    embed.add_field(name = f":arrow_double_up: Daily {level}", value = f"**${price:,}**\nPermanently increase daily reward by `+${next_amount:,}`.", inline = True)
  
    #Mail
    level = await util.superscript(user["upgrade_mail"]["level"])
    price = user["upgrade_mail"]["price"]
    embed.add_field(name = f":mailbox: Mail {level}", value = f"**${price:,}**\nAnonymously DM someone a custom message through Rob.", inline = True)

    #Gold Transmutation
    level = user["upgrade_gold_transmutation"]["level"]
    price = user["upgrade_gold_transmutation"]["price"]
    next_amount = user["upgrade_gold_transmutation"]["amounts"][str( user["upgrade_gold_transmutation"]["level"]+1 )]
    games_remaining = f"${price:,}"
    if level >= 1:
      total_games = user["stat_league_games_quantity"]
      level_req = [0,15,20,30,40,60,85,120,175,250]
      games=0
      for i in range(level):
        games += level_req[i]
      games_remaining = f"{level_req[level]-(total_games-games)} Games"
    level = await util.superscript(level)
    embed.add_field(name = f"<:lol_passive:957853326626656307> Gold Transmutation {level}", value = f"**{games_remaining}**\nTransform `{next_amount}%` of the gold you earn in League of Legends into Sloans", inline = True)

    #Restore Streak
    streak = user["stat_highest_daily_streak"]
    streak_percent_bonus = user["upgrade_streak"]["amount"]
    price = streak*(streak+1)/2*10 + streak*(streak+1)/2*1 * streak_percent_bonus*0.01
    price = round(price + price*.5)
    level = await util.superscript(user["upgrade_restore"]["level"])
    embed.add_field(name = f":confetti_ball: Restore Streak {level}", value = f"**${price:,}**\nSingle use, restores your current daily streak to `{streak:,}`", inline = True)

    #Change Summoner Name
    price = user["upgrade_change_lol"]["price"]
    level = await util.superscript(user["upgrade_change_lol"]["level"])
    embed.add_field(name = f"👤 Change Summoner Name {level}", value = f"**${price:,}**\nUpdate your League of Legends summoner name & region in the database.", inline = True)

    #Loan
    embed.add_field(name = ":bank: *Loan", value = "**$FREE**\nTake out a loan which has to be repaid before any upgrades are purchased.", inline = True)
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
  

def setup(client):
  client.add_cog(Frontend(client))