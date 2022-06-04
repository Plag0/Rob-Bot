from discord.ext import commands
import discord
import asyncio
import random
from discord_components import DiscordComponents, ComponentsBot, Button, SelectOption, Select
from replit import db
from datetime import datetime, timedelta
from cogs.utility import Utility as util

class Rewards(commands.Cog):
  def __init__(self, client):
    self.client = client
    
  async def whack_a_rob(client):
    #sleep_time = random.randrange(3600)
    custom_id = str(len(asyncio.Task.all_tasks()))
    #print(f"Claim event triggered for {sleep_time} seconds. ID: {custom_id}")
    #await asyncio.sleep(sleep_time)
    
    text_channel_list = ["241507995614183424","332130813829447682","334046255384887296","356921343733923841"]
    channel = await client.fetch_channel(random.choice(text_channel_list))
    base_amount = random.randrange(100,1001,50)
    msg = await channel.send("Catch me if you can!", delete_after=30, components = [Button(label=f"Catch (+${base_amount:,})", style="3", emoji="🤑", custom_id=custom_id)])
    try:
      interaction = await client.wait_for("button_click", check = lambda i: i.custom_id == custom_id, timeout=30)
    except asyncio.TimeoutError:
      await channel.send("<a:tumbleweed:890715360163147796>")
      return
    
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(interaction.user.id)]
    rob = user_dict[str(906087821373239316)]
    #claim_bonus = claim_bonus * (use["upgrade_claim"]["amount"]*0.01)
    amount = base_amount #+ claim_bonus
    user["balance"] += amount
    user["stat_claim_profit"] += amount
    rob["balance"] -= amount
    user["stat_claim_quantity"] += 1
    if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance "] = user["balance"]
    #await util.save_user_data(user_dict)

    embed = discord.Embed(
    colour = discord.Colour.green(),
    title = ":partying_face: Claimed!",
    description = f"Claimed **${amount:,}** sloans! You now have ${user['balance']:,}")
    embed.set_footer(icon_url = interaction.user.avatar_url, text = f"{interaction.user.name} has claimed ${user['stat_claim_profit']:,} total")
    #print(f"{interaction.user.name} has claimed Rob Reward - ID: {custom_id}")
    await interaction.respond(embed=embed, ephemeral=False)
    await msg.delete()
      




  @commands.command(aliases = ["day","d"])
  async def daily(self, ctx):
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(906087821373239316)]
    
    FMT = "%Y-%m-%d-%H:%M:%S"
    base_amount = 100
    lost_streak = False
    
    daily_level = user["upgrade_daily"]["level"]
    streak_level = user["upgrade_streak"]["level"]
  
    streak = user["daily_streak"]
    streak_bonus = streak*10
    daily_upgrade_bonus = user["upgrade_daily"]["amount"]
    streak_upgrade_bonus = round(streak_bonus * user["upgrade_streak"]["amount"] * 0.01)
  
    last_daily = datetime.strptime(user["last_daily"], FMT)
    raw_cooldown = timedelta(hours = 24).total_seconds()
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    after_cooldown = last_daily + cooldown
    time_now = datetime.now()

    cooldown_level = user["upgrade_cooldown"]["level"]
    #Too Early
    if time_now < after_cooldown: 
      difference = time_now - last_daily
      time_remaining = cooldown - difference
      message = ""
      reduction = timedelta(hours = 24) - cooldown
      avg_reduction = str(reduction).split(".")[0]

      fields = 0
      embed = discord.Embed(
      colour = (discord.Colour.red()),
      title = f":hourglass: Daily Cooldown",
      description = f"Please wait `{str(time_remaining).split('.')[0]}`{message}\nYour next daily will grant you `+${base_amount+daily_upgrade_bonus+streak_bonus+streak_upgrade_bonus:,}`")
      if daily_level >= 1:
        embed.add_field(name = f":arrow_double_up: Daily Level {daily_level}", value = f"`+${daily_upgrade_bonus:,}`", inline = True)
        fields += 1
      if streak >= 1:
        embed.add_field(name = f":tada: {streak} Day Streak", value = f"`+${streak_bonus:,}`", inline = True)
        fields += 1
      if fields >= 2:
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      if cooldown_level >= 1:
        embed.add_field(name = f":hourglass_flowing_sand: Cooldown Level {cooldown_level}", value = f"`-{avg_reduction}`", inline = True)
        fields += 1
      if streak_level >=1:
        embed.add_field(name = f":confetti_ball: Streak Level {streak_level}", value = f"`+${streak_upgrade_bonus:,}`", inline = True)
        fields += 1
      
      if fields == 3:
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)

      if fields >= 4:
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
        
      embed.set_footer(icon_url = ctx.author.avatar_url, text = f"{ctx.author.name}")
      await ctx.channel.send(embed=embed)
  
    else:
      after_48_hours = last_daily + timedelta(hours = 48) 
      if time_now > after_48_hours and streak > 0:
        old_bonus = streak_upgrade_bonus + streak_bonus
        old_streak = user["daily_streak"]
        user["daily_streak"] = 0
        streak_upgrade_bonus = 0
        streak_bonus = 0
        lost_streak = True
  
      amount = base_amount + daily_upgrade_bonus + streak_bonus + streak_upgrade_bonus
  
      rob["balance"] -= amount
      user["balance"] += amount
      user["stat_daily_profit"] += amount
      user["last_daily"] = datetime.now().strftime(FMT)
      user["daily_streak"] += 1
      user["stat_daily_quantity"] += 1
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance "] = user["balance"]
      if user["daily_streak"] > user["stat_highest_daily_streak"]:
        user["stat_highest_daily_streak"] = user["daily_streak"]
  
      #await util.save_user_data(user_dict)
  
      #checking if the user got their daily early, thanks to the cooldown upgrade.
      time_skipped = False
      if cooldown_level >= 1:
        after_24_hours = last_daily + timedelta(hours = 24)
        if time_now < after_24_hours:
          time_saved = after_24_hours - time_now
          time_skipped = True

      fields = 0
      embed = discord.Embed(
      colour = (discord.Colour.green()),
      title = ":moneybag: Daily",
      description = f"Received **${amount:,}** sloans! You now have ${user['balance']:,}")
      if lost_streak == True:
        embed.add_field(name = f":octagonal_sign: Streak Expired! -${old_bonus:,}", value = f"You lost your daily streak of **{old_streak:,}**!", inline = True)
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      
      if user["upgrade_daily"]["level"] >= 1:
        embed.add_field(name = f":arrow_double_up: Upgrade Bonus! +${daily_upgrade_bonus:,}", value = f"You have a daily level of **{daily_level}**", inline = True)
        fields += 1
      
      if user["daily_streak"] > 1:
        embed.add_field(name = f":tada: Streak! +${streak_bonus:,}", value = f"You're on a **{user['daily_streak']:,}** day streak!", inline = True)
        fields += 1
      
      if fields >= 2:
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      
      if streak_level >=1:
        embed.add_field(name = f":confetti_ball: Streak Bonus! +${streak_upgrade_bonus:,}", value = f"You have a streak level of **{streak_level}**", inline = True)
        fields += 1
  
      if time_skipped == True:
        embed.add_field(name = f":hourglass_flowing_sand: Time Saved! +{str(time_saved).split('.')[0]}", value = f"You have a cooldown level of **{cooldown_level}**", inline = True)
        fields += 1

      if fields == 3:
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)

      if fields >= 4:
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      
      embed.set_footer(icon_url = ctx.author.avatar_url, text = f"{ctx.author.name}")
      await ctx.channel.send(embed=embed)


  @commands.command(aliases = ["week","w"])
  async def weekly(self, ctx):
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(906087821373239316)]
    
    FMT = "%Y-%m-%d-%H:%M:%S"
    base_amount = 1000
  
    last_weekly = datetime.strptime(user["last_weekly"], FMT)
    raw_cooldown = timedelta(days = 7).total_seconds()
    cooldown_level = user["upgrade_cooldown"]["level"]
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    after_7_days = last_weekly + cooldown
    time_now = datetime.now()
  
    #Too Early
    if time_now < after_7_days:
      difference = time_now - last_weekly
      time_remaining = cooldown - difference
      message = ""
      if cooldown_level >= 1:
        reduction = timedelta(days = 7) - cooldown
        avg_reduction = str(reduction).split(".")[0]
        message = f"\n\n:hourglass_flowing_sand: Cooldown Level {cooldown_level}\n`-{avg_reduction}`"
      await util.embed_error_cooldown(ctx, "Please wait", f"{str(time_remaining).split('.')[0]}{message}")
    
    else:
      upgrade_bonus = user["upgrade_weekly"]["amount"]
      amount = base_amount + upgrade_bonus
      rob["balance"] -= amount
      user["balance"] += amount
      user["stat_weekly_profit"] += amount
      user["stat_weekly_quantity"] += 1
      user["last_weekly"] = datetime.now().strftime(FMT)
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance "] = user["balance"]
      #await util.save_user_data(user_dict)
  
      upgrade_level = user["upgrade_weekly"]["level"]
  
      balance = user["balance"]
      embed = discord.Embed(
      colour = (discord.Colour.green()),
      title = ":moneybag: Weekly",
      description = f"Received **${amount:,}** sloans! You now have ${balance:,}")
      if user["upgrade_weekly"]["level"] >= 1:
        embed.add_field(name = f":calendar_spiral: Upgrade Bonus! +${upgrade_bonus}", value = f"You have a weekly level of **{upgrade_level}**")
      await ctx.channel.send(embed=embed)

  
  users_on_cooldown = []
  async def passive_income(message):
    if len(message.content) >= 3 and not message.author.id in Rewards.users_on_cooldown and not message.content.startswith("$") and " " in message.content:
      #user_dict = await util.get_user_data()
      user_dict = db["user_dict"]
      user = user_dict[str(message.author.id)]
      rob = user_dict[str(906087821373239316)]
      if user["upgrade_passive_income"]["level"] >= 1:
        Rewards.users_on_cooldown.append(message.author.id)
        i = random.randint(0,100)
        if i >= 50:
          amount = user["upgrade_passive_income"]["amount"]
          user["balance"] += amount
          rob["balance"] -= amount
          user["stat_passive_income_profit"] += amount
          #await util.save_user_data(user_dict)
          emojis = {1:"<a:level_1:957450255320887367>",2:"<a:level_2:957450258600845322>",3:"<a:level_3:957450258890231838>",4:"<a:level_4:957450258500182066>",5:"<a:level_5:957450258688913428>",6:"<a:level_6:957450258378539028>",7:"<a:level_7:957450259053817978>",8:"<a:level_8:957450258751823882>",9:"<a:level_9:957450258768597032>",10:"<a:level_10:957450258760237176>"}
          emoji = emojis[user["upgrade_passive_income"]["level"]]
          await message.add_reaction(emoji)
        cd_reduction_percent = user["upgrade_cooldown"]["amount"]
        raw_cooldown = 60
        cooldown = raw_cooldown - raw_cooldown*(cd_reduction_percent*0.01)
        await asyncio.sleep(cooldown)
        Rewards.users_on_cooldown.remove(message.author.id)









def setup(client):
  client.add_cog(Rewards(client))