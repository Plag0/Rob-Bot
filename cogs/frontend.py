from discord.ext import commands
import discord
from datetime import datetime
from cogs.utility import Utility as util

class Frontend(commands.Cog):
  def __init__(self, client):
    self.client = client



  @commands.command(aliases = ["board","scoreboard","rank"])
  async def leaderboard(self, ctx, *variable):
    data = []
    user_dict = await util.get_user_data()
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
        user = (user_dict[str(user.id)][stat_name][1],user.mention,user_dict[str(user.id)][stat_name][0])
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
  
  
  
  @commands.command(aliases = ["sloan","balance","bal","robcoins","robux","slons","slon",""])
  async def sloans(self, ctx, mention:discord.User = None):
    mention = mention or ctx.author
  
    users = await util.get_user_data()
    balance = users[str(mention.id)]["balance"]
  
    embed = discord.Embed(
      colour = (discord.Colour.magenta()),
      title = ":coin: Sloans",
      description = f"{mention.name} has **${balance:,}** sloans."
      )
    await ctx.channel.send(embed=embed)


  @commands.command(aliases = ["prof","account","whois","acc","p"])
  async def profile(self, ctx, mention:discord.User = None):
  
    account = mention or ctx.author
    user_dict = await util.get_user_data()
    user = user_dict[str(account.id)]
  
    if ctx.author.id != account.id:
      user["stat_profile_views"] += 1
      await util.save_user_data(user_dict)

    total_flips = user["stat_flip_victory"] + user["stat_flip_defeat"]
    if total_flips != 0:
      winrate = round((user["stat_flip_victory"] / total_flips) * 100, 1)
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
        if user[key][1] >= 1:
          upgrade_name = key.split("_")
          upgrade_emojis += f"{user[key][6]} {upgrade_name[1].capitalize()}: **{user[key][1]}**\n"
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
  
  
  
  
  
  
  @commands.command(aliases = ["upgrades","up","levelup","perks","upgrade","store","$"])
  async def shop(self, ctx):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    balance = user["balance"]
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = f":star2: {ctx.author.name}'s Shop",
    description = f"**Current Balance: ${balance:,}**\nPurchase upgrades by typing: `$buy name`\nNot all upgrades are currently available to purchase, dysfunctional upgrades are marked by `*`")
    
    embed.add_field(name = ":comet: *Apocalypse", value = "**$50M**\nSingle use, bans 50% of the server for 30 minutes.", inline = True)
    embed.add_field(name = ":boom: *Bankrupt", value = "**$10M**\nSingle use, blow up someone's bank account and spread the wealth.", inline = True)
    upgrade_price = user["upgrade_ban"][2]
    upgrade_quantity = await util.superscript(user["upgrade_ban"][1])
    embed.add_field(name = f":hammer: Ban {upgrade_quantity}", value = f"**${upgrade_price:,}**\nSingle use, ban someome temporarily.", inline = True)
  
    upgrade_price = user["upgrade_kick"][2]
    upgrade_quantity = await util.superscript(user["upgrade_kick"][1])
    embed.add_field(name = f":foot: Kick {upgrade_quantity}", value = f"**${upgrade_price:,}**\nSingle use, kicks someone random.", inline = True)
    embed.add_field(name = ":game_die: *Gambling Addict", value = "**$200k^**\nPermanently gain more from all-in bets.", inline = True)
    embed.add_field(name = ":detective: *Steal", value = "**$100k^**\nPermanently unlock the $steal command.", inline = True)
  
    embed.add_field(name = ":smiling_imp: *Sabotage", value = "**$50k**\nSingle use, dramatically decrease someone's win chance for 24 hours.", inline = True)
    upgrade_price = user["upgrade_cooldown"][2]
    upgrade_next_amount = user["upgrade_cooldown"][3] * (user["upgrade_cooldown"][1]+1)
    level = user["upgrade_cooldown"][1]
    upgrade_level = await util.superscript(user["upgrade_cooldown"][1])
    embed.add_field(name = f":hourglass_flowing_sand: Cooldown {upgrade_level}", value = f"**${upgrade_price:,}**\nPermanently reduce all cooldowns by `%{round(100-100*.95**(level+1),2)}`.", inline = True)
    embed.add_field(name = ":shield: *Protection", value = "**$25k^**\n+10% chance to parry $steal, even when offline.", inline = True)
  
  
    embed.add_field(name = ":name_badge: *Rename", value = "**$20k**\nSingle use, set someone's nickname for a day.", inline = True)
    
    upgrade_price = user["upgrade_weekly"][2]
    upgrade_next_amount = user["upgrade_weekly"][3] * (user["upgrade_weekly"][1]+1)
    upgrade_level = await util.superscript(user["upgrade_weekly"][1])
    embed.add_field(name = f":calendar_spiral: Weekly {upgrade_level}", value = f"**${upgrade_price:,}**\nPermanently increase weekly reward by `+${upgrade_next_amount:,}`.", inline = True)
  
    upgrade_price = user["upgrade_passive_income"][2]
    upgrade_next_amount = user["upgrade_passive_income"][3] * (user["upgrade_passive_income"][1]+1)
    upgrade_current_amount = user["upgrade_passive_income"][0]
    upgrade_level = await util.superscript(user["upgrade_passive_income"][1])
    embed.add_field(name = f":chart_with_upwards_trend: Passive Income {upgrade_level}", value = f"**${upgrade_price:,}**\nOnce a minute, have a 50% chance to gain `+${upgrade_next_amount+upgrade_current_amount:,}` from any message.", inline = True)
    
  
    embed.add_field(name = ":gift: *Mystery Box", value = "**$3k**\nMysterious.", inline = True)
  
    upgrade_price = user["upgrade_streak"][2]
    upgrade_current_amount = user["upgrade_streak"][0]
    upgrade_next_amount = user["upgrade_streak"][3] * (user["upgrade_streak"][1]+1)
    upgrade_level = await util.superscript(user["upgrade_streak"][1])
    embed.add_field(name = f":tada: Streak {upgrade_level}", value = f"**${upgrade_price:,}**\nGain `%{upgrade_next_amount+upgrade_current_amount}0` more from your daily streak.", inline = True)
  
    upgrade_price = user["upgrade_daily"][2]
    upgrade_next_amount = user["upgrade_daily"][3] * (user["upgrade_daily"][1]+1)
    upgrade_level = await util.superscript(user["upgrade_daily"][1])
    embed.add_field(name = f":arrow_double_up: Daily {upgrade_level}", value = f"**${upgrade_price:,}**\nPermanently increase daily reward by `+${upgrade_next_amount:,}`.", inline = True)
  
    
    upgrade_price = user["upgrade_mail"][2]
    upgrade_quantity = await util.superscript(user["upgrade_mail"][1])
    embed.add_field(name = f":mailbox: Mail {upgrade_quantity}", value = f"**${upgrade_price:,}**\nAnonymously DM someone a custom message through Rob.", inline = True)
    
    level = user["upgrade_gold_transmutation"][1]
    upgrade_price = user["upgrade_gold_transmutation"][2]
    upgrade_quantity = await util.superscript(user["upgrade_gold_transmutation"][1])
    games_remaining = f"${upgrade_price:,}"
    percent = 1
    games = ""
    if level >= 1:
      total_games = user["stat_league_games_quantity"]
      level_req = [0,15,20,30,40,60,85,120,175,250]
      i=0
      games=0
      while i < level:
        games += level_req[i]
        i+=1
      games_remaining = level_req[level] - (total_games - games)
      games_remaining = f"{games_remaining} Games"
      
      level = user["upgrade_gold_transmutation"][1]
      i=0
      while i < level:
        percent += percent*.43
        i+=1
      percent = round(percent,1)
    embed.add_field(name = f"<:lol_passive:957853326626656307> Gold Transmutation {upgrade_quantity}", value = f"**{games_remaining}**\nTransform `{percent}%` of the gold you earn in League of Legends into Sloans", inline = True)
  
    streak = user["stat_highest_daily_streak"]
    streak_bonus = user["upgrade_streak"][0]
    amount = round((streak*(streak+1)/2)*(10+streak_bonus))
    upgrade_price = round(amount + amount*.5)
    upgrade_quantity = await util.superscript(user["upgrade_restore"][1])
    upgrade_amount = user["stat_highest_daily_streak"]
    embed.add_field(name = f":confetti_ball: Restore Streak {upgrade_quantity}", value = f"**${upgrade_price:,}**\nSingle use, restores your current daily streak to `{upgrade_amount:,}`", inline = True)
  
    upgrade_price = user["upgrade_change_lol"][2]
    upgrade_quantity = await util.superscript(user["upgrade_change_lol"][1])
    embed.add_field(name = f"👤 Change Summoner Name {upgrade_quantity}", value = f"**${upgrade_price:,}**\nUpdate your League of Legends summoner name & region in the database.", inline = True)
    
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