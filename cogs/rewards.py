from discord.ext import commands
import discord
import asyncio
import random
import math
import json
from datetime import datetime, timedelta
import time
from cogs.utility import Utility as util

class Rewards(commands.Cog):
  def __init__(self, client):
    self.client = client

  
  async def gambling_addict_passive(ctx, account, user_dict):
    user = user_dict[str(account.id)]
    rob = user_dict[str(906087821373239316)]
    embed = None
    if user["balance"] <= 0 and user["upgrade_gambling_addict"]["level"] >= 1:
      # Cooldown.
      FMT = "%Y-%m-%d-%H:%M:%S"
      last_rebound = datetime.strptime(user["last_gambling_addict_passive"], FMT)
      raw_cooldown = timedelta(hours = 24).total_seconds()
      cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
      after_cooldown = last_rebound + cooldown
      time_now = datetime.now()
      
      if time_now > after_cooldown:
        amount = int(user["stat_highest_balance"]*0.01)
        user["balance"] += amount
        rob["balance"] -= amount
        user["stat_gambling_addict_profit"] += amount
        user["last_gambling_addict_passive"] = str(datetime.now().strftime(FMT))
        
        embed = discord.Embed(
        colour = discord.Colour.green(),
        title = f"🎲 Gambling Addict")
        embed.add_field(name = f"**🏓 Rebound! +${amount:,}**", value = f"You lost all your Sloans and recieved `1%` of your highest balance as compensation!\nThis ability will become available again in `{str(cooldown).split('.')[0]}`")
        embed.set_footer(text = f"{account.name} has earned +${user['stat_gambling_addict_profit']:,} from rebounds.", icon_url = account.display_avatar.url)
        after_raw_cooldown = last_rebound + timedelta(hours = 24)
        if time_now < after_raw_cooldown:
          time_saved = after_raw_cooldown - time_now
          user["stat_time_saved"] += int(time_saved.total_seconds())
          embed.add_field(name = f":hourglass_flowing_sand: Time Saved! +{str(time_saved).split('.')[0]}", value = f"You have a cooldown level of **{user['upgrade_cooldown']['level']}**", inline = False)
        
    return (user_dict, embed)





    
  async def whack_a_rob(client, drop_party=None):
    # This ID is used in the custom button IDs.
    #unique_id = str(datetime.now())

    text_channel_list = ["241507995614183424","332130813829447682","334046255384887296","356921343733923841"]
    channel = await client.fetch_channel(random.choice(text_channel_list))
    base_amount = random.randrange(100,1001,50)
    emoji = "🤑"
    title = f"Catch (+${base_amount:,})"
    desc = "Catch me if you can!"
    colour = discord.Colour.green()
    claimed = "Whacked!"
    if drop_party == True:
      emoji = "🥳"
      title = f"FREE +${base_amount:,}"
      desc = "DROP PARTY IN SPAWN!"
      claimed = "Claimed!"
      colours = [
      (158,1,66),
      (213,62,79),
      (244,109,67),
      (253,174,97),
      (254,224,139),
      (230,245,152),
      (171,221,164),
      (102,194,165),
      (50,136,189),
      (94,79,162)
      ]
      c = random.choice(colours)
      r=c[0]
      g=c[1]
      b=c[2]
      colour = discord.Colour.from_rgb(r,g,b)

    class Button(discord.ui.View):
      def __init__(self, *, timeout=30):
        super().__init__(timeout=timeout)
  
      @discord.ui.button(label=title, style=discord.ButtonStyle.green, emoji=emoji)
      async def menu(self, interaction:discord.Interaction, button:discord.ui.Button):
        user_dict = await util.get_user_data()
        user = user_dict[str(interaction.user.id)]
        rob = user_dict[str(client.user.id)]
        claim_bonus = round(base_amount * (user["upgrade_opportunist"]["amount"]*0.01))
        amount = base_amount + claim_bonus
        user["balance"] += amount
        user["total_cash_flow"] += amount
        user["daily_cash_flow"] += amount
        user["stat_claim_profit"] += amount
        user["stat_opportunist_profit"] += claim_bonus
        rob["balance"] -= amount
        rob["total_cash_flow"] += amount
        rob["daily_cash_flow"] += amount
        user["stat_claim_quantity"] += 1
        if user["balance"] > user["stat_highest_balance"]:
            user["stat_highest_balance"] = user["balance"]
        
        await util.save_user_data(user_dict)
    
        embed = discord.Embed(
        colour = colour,
        title = f"{emoji} {claimed}",
        description = f"Claimed **${base_amount + claim_bonus:,}** Sloans!\nYour new balance is ${user['balance']:,}.")
        embed.set_footer(icon_url = interaction.user.display_avatar.url, text = f"{interaction.user.name} has claimed ${user['stat_claim_profit']:,} total")
        if claim_bonus > 0:
          embed.add_field(name=f"🦊 Opportunist Bonus! **+${claim_bonus:,}**",value=f"You have an Opportunist level of **{user['upgrade_opportunist']['level']}**")
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
      
      async def on_timeout(self):
        await msg.edit(content="<a:tumbleweed:890715360163147796>", embed=None, view=None)
        
    view = Button()
    msg = await channel.send(desc, view=view)
    


    
    
    
  
  
  
  tw_max_time = 600
  tw_time = 600
  tw_bonus = 0
  tw_messages = 0
  tw_channel = None
  tw_msg = None
  tw_last_user = None
  tw_base_amount = 10000
  tw_participants = set()
  async def turf_war(client, guild, user=None):
    print(f"Channel is: {Rewards.tw_channel}")
    if Rewards.tw_channel == None and user == None:
      print("new turf war")
      Rewards.tw_channel = await guild.create_text_channel(f"turf-war", topic = f"Last person to message wins!")

      # Embed
      desc =f"Last person to message wins **+ ${Rewards.tw_base_amount + Rewards.tw_bonus:,}**!\n"
      desc+=f"There is {time.strftime('%M:%S', time.gmtime(Rewards.tw_time))} remaining.\n"
      desc+=f"Current Players: **{len(Rewards.tw_participants)}**"
      embed = discord.Embed(
      colour = (discord.Colour.green()),
      title = f"⚔ Turf War **+ ${Rewards.tw_base_amount + Rewards.tw_bonus:,}**",
      description = desc)
      Rewards.tw_msg = await Rewards.tw_channel.send(embed=embed)
      await Rewards.tw_msg.pin()

      await Rewards.tw_start_timer(client)
      await Rewards.tw_payout(client)
      await Rewards.tw_channel.set_permissions(guild.default_role, send_messages=False)
      await Rewards.tw_reset(client)
      
    elif Rewards.tw_channel != None and user != None and Rewards.tw_time > 0:
      print("user message accepted")
      if Rewards.tw_last_user != user:
        Rewards.tw_time = Rewards.tw_max_time
      Rewards.tw_last_user = user
      Rewards.tw_bonus += int( math.ceil( 1 * Rewards.tw_max_time * 0.01 ) )
      Rewards.tw_messages += 1
      if user not in Rewards.tw_participants:
        Rewards.tw_participants.add(user)
      print("user message processed")

  async def tw_edit_channel(client):
    player_list = ""
    for u in Rewards.tw_participants:
      player_list += f"  • {u.name}\n"
    desc =f"Last person to message wins **+ ${Rewards.tw_base_amount + Rewards.tw_bonus:,}**!\n"
    desc+=f"There is `{time.strftime('%M:%S', time.gmtime(Rewards.tw_time))}` remaining.\n"
    desc+=f"Messages sent: **{Rewards.tw_messages:,}**\n"
    desc+=f"Unique Participants: **{len(Rewards.tw_participants)}**\n{player_list}"
    embed = discord.Embed(
    colour = (discord.Colour.green()),
    title = f"⚔ Turf War **+ ${Rewards.tw_base_amount + Rewards.tw_bonus:,}**",
    description = desc)
    await Rewards.tw_msg.edit(embed=embed)

  async def tw_payout(client):
    print("calling payout")
    time_started = Rewards.tw_channel.created_at
    game_length = datetime.now() - time_started
    if Rewards.tw_last_user == None:
      await Rewards.tw_channel.edit(name=f"turf-war-ended", topic=f"No one participated and missed out on ${Rewards.tw_base_amount:,} Sloans.")
      # Embed
      desc =f"No one participated and missed out on **${Rewards.tw_base_amount:,}** Sloans.\n\n"
      desc+="This channel will self-destruct in **1 minute**."
      embed = discord.Embed(
      colour = (discord.Colour.red()),
      title = "⚔ Turf War Over!",
      description = desc)
    
    else:
      user_dict = await util.get_user_data()
      user = user_dict[str(Rewards.tw_last_user.id)]
      rob = user_dict[str(client.user.id)]
      
      amount = Rewards.tw_base_amount + Rewards.tw_bonus
      opportunist_bonus = round(amount * (user["upgrade_opportunist"]["amount"]*0.01))
      user["balance"] += amount + opportunist_bonus
      user["total_cash_flow"] += amount + opportunist_bonus
      user["daily_cash_flow"] += amount + opportunist_bonus
      rob["balance"] -= amount + opportunist_bonus
      rob["total_cash_flow"] += amount + opportunist_bonus
      rob["daily_cash_flow"] += amount + opportunist_bonus

      # Stats
      user["stat_opportunist_profit"] += opportunist_bonus
      user["stat_turf_war_profit"] += amount + opportunist_bonus
      user["stat_turf_war_victory"] += 1
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance"] = user["balance"]
      if (amount + opportunist_bonus) > user["stat_turf_war_highest_win"]:
        user["stat_turf_war_highest_win"] = amount + opportunist_bonus
      if int(game_length.total_seconds()) > user["stat_turf_war_longest_game"]:
        user["stat_turf_war_longest_game"] = int(game_length.total_seconds())
      for u in Rewards.tw_participants:
        user_dict[str(u.id)]["stat_turf_war_quantity"] += 1

      await util.save_user_data(user_dict)

      # Channel Update
      opp_bonus = ""
      if opportunist_bonus > 0:
        opp_bonus = f"🦊 Opportunist Bonus + ${opportunist_bonus:,}"
      await Rewards.tw_channel.edit(name=f"turf-war-ended", topic=f"{Rewards.tw_last_user.name} won ${amount:,}{opp_bonus}! Game length: {str(game_length).split('.')[0]}")
      
      # Embed
      desc =f"{Rewards.tw_last_user.mention} was the last man standing and won **+ ${amount:,}**!\n"
      desc+=f"The fight lasted **{str(game_length).split('.')[0]}**, **{Rewards.tw_messages:,}** messages were sent, and **{len(Rewards.tw_participants)}** players participated!\n\n"
      desc+="This channel will self-destruct in **1 minute**."
      embed = discord.Embed(
      colour = (discord.Colour.green()),
      title = "⚔ Turf War Over!",
      description = desc)
      embed.set_thumbnail(url = Rewards.tw_last_user.display_avatar.url)
      if opportunist_bonus > 0:
        embed.add_field(name = f"{opp_bonus}", value = f"You have an Opportunist level of **{user['upgrade_opportunist']['level']}**")
    await Rewards.tw_channel.send(embed=embed)
    
  async def tw_start_timer(client):
    print("started timer")
    while Rewards.tw_time > 0:
      await asyncio.sleep(1.1)
      Rewards.tw_time -= 1
      if Rewards.tw_max_time > 30:
        Rewards.tw_max_time -= 0.2
      await Rewards.tw_edit_channel(client)
    print("finished timer")

  async def tw_reset(client):
    print("reset tw")
    await asyncio.sleep(60)
    await Rewards.tw_channel.delete()
    Rewards.tw_max_time = 600
    Rewards.tw_time = 600
    Rewards.tw_bonus = 0
    Rewards.tw_messages = 0
    Rewards.tw_channel = None
    Rewards.tw_last_user = None
    Rewards.tw_participants = set()
      


  
  @commands.command(aliases = ["day","d"])
  async def daily(self, ctx):
    user_dict = await util.get_user_data()
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
        
      embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"{ctx.author.name}")
      await ctx.channel.send(embed=embed)
  
    else:
      # Too late.
      with open("upgrades.json","r") as f:
        d = json.load(f)
      prot_chance = d["upgrade_protection"]["amounts"][ str(user["upgrade_protection"]["level"]) ]
      base = 48
      hours = base * (100 + prot_chance) * 0.01
      after_48_hours = last_daily + timedelta(hours = hours) 
      if time_now > after_48_hours and streak > 0:
        old_bonus = streak_upgrade_bonus + streak_bonus
        old_streak = user["daily_streak"]
        user["daily_streak"] = 0
        streak_upgrade_bonus = 0
        streak_bonus = 0
        lost_streak = True

      #checking if the user got their daily early, thanks to the cooldown upgrade.
      time_skipped = False
      if cooldown_level >= 1:
        after_24_hours = last_daily + timedelta(hours = 24)
        if time_now < after_24_hours:
          time_saved = after_24_hours - time_now
          time_skipped = True
  
      amount = base_amount + daily_upgrade_bonus + streak_bonus + streak_upgrade_bonus
  
      rob["balance"] -= amount
      rob["total_cash_flow"] += amount
      rob["daily_cash_flow"] += amount
      user["balance"] += amount
      user["total_cash_flow"] += amount
      user["daily_cash_flow"] += amount
      user["stat_daily_profit"] += amount
      user["last_daily"] = datetime.now().strftime(FMT)
      user["daily_streak"] += 1
      user["stat_daily_quantity"] += 1
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance"] = user["balance"]
      if user["daily_streak"] > user["stat_highest_daily_streak"]:
        user["stat_highest_daily_streak"] = user["daily_streak"]

      if time_skipped == True:
        user["stat_time_saved"] += int(time_saved.total_seconds())
  
      await util.save_user_data(user_dict)
  
      
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
      
      embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"{ctx.author.name}")
      await ctx.channel.send(embed=embed)


  @commands.command(aliases = ["week","w"])
  async def weekly(self, ctx):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(906087821373239316)]
    
    FMT = "%Y-%m-%d-%H:%M:%S"
    base_amount = 1000
    upgrade_bonus = user["upgrade_weekly"]["amount"]
    upgrade_level = user["upgrade_weekly"]["level"]
  
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
      reduction = timedelta(days = 7) - cooldown
      avg_reduction = str(reduction).split(".")[0]
      
      embed = discord.Embed(
      colour = (discord.Colour.red()),
      title = f":hourglass: Weekly Cooldown",
      description = f"Please wait `{str(time_remaining).split('.')[0]}`\nYour next weekly will grant you `+${base_amount+upgrade_bonus:,}`")
      if upgrade_level >= 1:
        embed.add_field(name = f"📅 Weekly Level {upgrade_level}", value = f"`+${upgrade_bonus:,}`", inline = True)
      if cooldown_level >= 1:
        embed.add_field(name = f"⏳ Cooldown Level {cooldown_level}", value = f"`-{avg_reduction}`", inline = True)
      await ctx.channel.send(embed=embed)
  
    
    else:

      #checking if the user got their daily early, thanks to the cooldown upgrade.
      time_skipped = False
      if cooldown_level >= 1:
        after_7_days = last_weekly + timedelta(days = 7)
        if time_now < after_7_days:
          time_saved = after_7_days - time_now
          time_skipped = True
      
      amount = base_amount + upgrade_bonus
      rob["balance"] -= amount
      rob["total_cash_flow"] += amount
      rob["daily_cash_flow"] += amount
      user["balance"] += amount
      user["total_cash_flow"] += amount
      user["daily_cash_flow"] += amount
      user["stat_weekly_profit"] += amount
      user["stat_weekly_quantity"] += 1
      user["last_weekly"] = datetime.now().strftime(FMT)
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance"] = user["balance"]

      if time_skipped == True:
        user["stat_time_saved"] += int(time_saved.total_seconds())
      
      await util.save_user_data(user_dict)
  
      balance = user["balance"]
      embed = discord.Embed(
      colour = (discord.Colour.green()),
      title = ":moneybag: Weekly",
      description = f"Received **${amount:,}** sloans! You now have ${balance:,}")
      if upgrade_level >= 1:
        embed.add_field(name = f":calendar_spiral: Upgrade Bonus! +${upgrade_bonus:,}", value = f"You have a weekly level of **{upgrade_level}**")
      if time_skipped == True:
        embed.add_field(name = f":hourglass_flowing_sand: Time Saved! +{str(time_saved).split('.')[0]}", value = f"You have a cooldown level of **{cooldown_level}**", inline = True)
      await ctx.channel.send(embed=embed)

  
  users_on_cooldown = {}
  async def passive_income(message):
    if len(message.content) >= 3 and not str(message.author.id) in Rewards.users_on_cooldown and not message.content.startswith("$") and " " in message.content and not "Direct Message" in str(message.channel):
      user_dict = await util.get_user_data()
      user = user_dict[str(message.author.id)]
      rob = user_dict[str(906087821373239316)]
      if user["upgrade_passive_income"]["level"] >= 1:
        i = random.randint(0,100)
        if i >= 50:
          amount = user["upgrade_passive_income"]["amount"]
          user["balance"] += amount
          user["total_cash_flow"] += amount
          user["daily_cash_flow"] += amount
          rob["balance"] -= amount
          rob["total_cash_flow"] += amount
          rob["daily_cash_flow"] += amount
          user["stat_passive_income_profit"] += amount
          if user["balance"] > user["stat_highest_balance"]:
            user["stat_highest_balance"] = user["balance"]
          await util.save_user_data(user_dict)
          emojis = {1:"<a:level_1:957450255320887367>",2:"<a:level_2:957450258600845322>",3:"<a:level_3:957450258890231838>",4:"<a:level_4:957450258500182066>",5:"<a:level_5:957450258688913428>",6:"<a:level_6:957450258378539028>",7:"<a:level_7:957450259053817978>",8:"<a:level_8:957450258751823882>",9:"<a:level_9:957450258768597032>",10:"<a:level_10:957450258760237176>"}
          emoji = emojis[user["upgrade_passive_income"]["level"]]
          await message.add_reaction(emoji)
        raw_cooldown = 60
        cooldown = raw_cooldown - raw_cooldown*(user["upgrade_cooldown"]["amount"]*0.01)
        Rewards.users_on_cooldown.update(  {str(message.author.id) : time.time() + cooldown} )
        await asyncio.sleep(cooldown)
        del Rewards.users_on_cooldown[str(message.author.id)]

  






async def setup(client):
  await client.add_cog(Rewards(client))