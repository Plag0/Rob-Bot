from discord.ext import commands
import discord
import asyncio
#import random
from cogs.utility import Utility as util
from cogs.rewards import Rewards as rewards
from cogs.league import League as league
import time
import math
from datetime import datetime

class Interactions(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    print(after.name)
    print(after.activities)
    await league.league_check(self, after)

  @commands.Cog.listener()
  async def on_member_join(self, member):
    new = await util.create_user(member)
    message = ""
    if new == False:
      message += "Welcome back"
    else:
      message += "Welcome"
  
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = f":tada: {member.name} has joined the server!",
    description = f"{message} {member.mention}!")
    channel = await self.client.fetch_channel("241507995614183424")
    await channel.send(embed=embed)

  #@commands.Cog.listener()
  #async def on_member_remove(member):
    
  """
  bad_users = []
  msg_counter = []
  recent_ids = []

  Lists.msg_counter.append(message)
  
  async def plag_check(message,msg):
    if "plag" in msg:
      await message.channel.send("Mmm my beautiful son plag.")
      return True
  
  async def mcspicy_check(message,msg):
    if "mcspicy" in msg:
      await message.channel.send(random.choice(strings.mcspicy_reactions))
      return True
  
  async def leaguers_check(message,msg):
    if "any leaguer" in msg:
      await message.channel.send(random.choice(strings.leaguers_reactions))
      return True

  async def all_same(items):
    return all(x == items[0] for x in items)
  
  async def consecutive_messages(message):
    Lists.recent_ids.append(message.author.id)
    if "$" in message.content:
      Lists.recent_ids = []
    if len( Lists.recent_ids ) >= 15:
      Lists.recent_ids.pop(0)
      if all_same( Lists.recent_ids ) == True:
        #await asyncio.sleep(1.5)
        await message.channel.send(random.choice(strings.consecutive_messages_reactions))
        Lists.recent_ids = []
        return True
  
  async def random_event(message):
    i = random.randint(200,500)
    if len(Lists.msg_counter) >= i:
      async with message.channel.typing():
        await asyncio.sleep(7)
        await message.channel.send(random.choice(strings.random_responses))
        Lists.msg_counter = []
        return True

  
  async def darkwood_alert(message,msg):
    if "darkwood" in msg:
      plag = await self.client.fetch_user(188811740476211200)
      dm = await plag.create_dm()
      await dm.send(f"DARKWOOD ALERT IN #{message.channel.name.upper()}!!! :scream:\n```{message.author.name}: {message.content}```")
      return True
  
  async def bongos(message):
    channel = message.author.voice.channel
    await channel.connect()

  async def racism_check(message,msg):
    if any(word in msg for word in strings.bad_words):
      await message.channel.send(random.choice(strings.racist_reaction))#,tts=True)
      Lists.bad_users.append(message.author.id)
      return True
    
    elif any(word in msg for word in strings.covid_words):
      await message.channel.send(random.choice(strings.covid_reactions))
      return True
    
    elif message.author.id in Lists.bad_users:
      i = random.randint(0,100)
      if i <=5:
        i = random.randint(0,2)
        reply = ""
        if i == 1:
          reply += message.author.mention + " "
        reply += random.choice(strings.negative_responses_list[i])
        if i == 0:
          reply += " " + message.author.mention
        await message.channel.send(reply)#,tts=True)
        return True

  async def conversation_checks(message,msg):
    #A while loop is used here because I couldn't get "startswith" to work with a for loop.
    i=0
    while i<len(strings.summon):
      if msg.startswith(strings.summon[i]):
        if any(word in msg for word in strings.rob_titles):
          await message.channel.send(random.choice(strings.greetings) + " " + message.author.mention)#,tts=True)
          return True
      i+=1

  """


  
  async def check_message(client, message):
    #msg = message.content.lower()
    """
    activation = await racism_check(message,msg)
    if activation != True:
      if not message.content.startswith(bot_prefix):
        activation = await custom_user_events(message,msg)
        if activation != True:
          activation = await conversation_checks(message,msg)
          if activation != True:
            activation = await consecutive_messages(message)
            if activation != True:
              activation = await random_event(message)
              if activation != True:
                activation = await leaguers_check(message,msg)
                if activation != True:
                  activation = await plag_check(message,msg)
                  if activation != True:
                    activation = await mcspicy_check(message,msg)
                    if activation != True:
                      activation = await darkwood_alert(message,msg)
                      if activation != True:
                        await reward.whack_a_rob()
    """
    if str(message.channel) == "turf-war":
      await Interactions.turf_war(commands.Bot, message.guild, message.author)
    else:
      await rewards.passive_income(message)
      #await util.activity_update(message)




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
    print(f"Channel is: {Interactions.tw_channel}")
    if Interactions.tw_channel == None and user == None:
      print("new turf war")
      Interactions.tw_channel = await guild.create_text_channel(f"turf-war", topic = f"Last person to message wins!")

      # Embed
      desc =f"Last person to message wins **+ ${Interactions.tw_base_amount + Interactions.tw_bonus:,}**!\n"
      desc+=f"There is {time.strftime('%M:%S', time.gmtime(Interactions.tw_time))} remaining.\n"
      desc+=f"Current Players: **{len(Interactions.tw_participants)}**"
      embed = discord.Embed(
      colour = (discord.Colour.green()),
      title = f"⚔ Turf War **+ ${Interactions.tw_base_amount + Interactions.tw_bonus:,}**",
      description = desc)
      Interactions.tw_msg = await Interactions.tw_channel.send(embed=embed)
      await Interactions.tw_msg.pin()

      await Interactions.tw_start_timer(client)
      await Interactions.tw_payout(client)
      await Interactions.tw_channel.set_permissions(guild.default_role, send_messages=False)
      await Interactions.tw_reset(client)
      
    elif Interactions.tw_channel != None and user != None and Interactions.tw_time > 0:
      if Interactions.tw_last_user != user:
        Interactions.tw_time = Interactions.tw_max_time
      Interactions.tw_last_user = user
      Interactions.tw_bonus += int( math.ceil( 1 * Interactions.tw_max_time * 0.01 ) )
      Interactions.tw_messages += 1
      if user not in Interactions.tw_participants:
        Interactions.tw_participants.add(user)

  async def tw_edit_channel(client):
    player_list = ""
    for u in Interactions.tw_participants:
      player_list += f"  • {u.name}\n"
    desc =f"Last person to message wins **+ ${Interactions.tw_base_amount + Interactions.tw_bonus:,}**!\n"
    desc+=f"There is `{time.strftime('%M:%S', time.gmtime(Interactions.tw_time))}` remaining.\n"
    desc+=f"Messages sent: **{Interactions.tw_messages:,}**\n"
    desc+=f"Unique Participants: **{len(Interactions.tw_participants)}**\n{player_list}"
    embed = discord.Embed(
    colour = (discord.Colour.green()),
    title = f"⚔ Turf War **+ ${Interactions.tw_base_amount + Interactions.tw_bonus:,}**",
    description = desc)
    await Interactions.tw_msg.edit(embed=embed)

  async def tw_payout(client):
    print("calling payout")
    time_started = Interactions.tw_channel.created_at
    game_length = datetime.now() - time_started
    if Interactions.tw_last_user == None:
      await Interactions.tw_channel.edit(name=f"turf-war-ended", topic=f"No one participated and missed out on ${Interactions.tw_base_amount:,} Sloans.")
      # Embed
      desc =f"No one participated and missed out on **${Interactions.tw_base_amount:,}** Sloans.\n\n"
      desc+="This channel will self-destruct in **1 minute**."
      embed = discord.Embed(
      colour = (discord.Colour.red()),
      title = "⚔ Turf War Over!",
      description = desc)
    
    else:
      user_dict = await util.get_user_data()
      user = user_dict[str(Interactions.tw_last_user.id)]
      rob = user_dict[str(client.user.id)]
      
      amount = Interactions.tw_base_amount + Interactions.tw_bonus
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
      for u in Interactions.tw_participants:
        user_dict[str(u.id)]["stat_turf_war_quantity"] += 1

      await util.save_user_data(user_dict)

      # Channel Update
      opp_bonus = ""
      if opportunist_bonus > 0:
        opp_bonus = f"🦊 Opportunist Bonus + ${opportunist_bonus:,}"
      await Interactions.tw_channel.edit(name=f"turf-war-ended", topic=f"{Interactions.tw_last_user.name} won ${amount:,}{opp_bonus}! Game length: {str(game_length).split('.')[0]}")
      
      # Embed
      desc =f"{Interactions.tw_last_user.mention} was the last man standing and won **+ ${amount:,}**!\n"
      desc+=f"The fight lasted **{str(game_length).split('.')[0]}**, **{Interactions.tw_messages:,}** messages were sent, and **{len(Interactions.tw_participants)}** players participated!\n\n"
      desc+="This channel will self-destruct in **1 minute**."
      embed = discord.Embed(
      colour = (discord.Colour.green()),
      title = "⚔ Turf War Over!",
      description = desc)
      embed.set_thumbnail(url = Interactions.tw_last_user.display_avatar.url)
      if opportunist_bonus > 0:
        embed.add_field(name = f"{opp_bonus}", value = f"You have an Opportunist level of **{user['upgrade_opportunist']['level']}**")
    await Interactions.tw_channel.send(embed=embed)
    
  async def tw_start_timer(client):
    print("started timer")
    while Interactions.tw_time > 0:
      await asyncio.sleep(5)
      Interactions.tw_time -= 5
      if Interactions.tw_max_time > 30:
        Interactions.tw_max_time -= 1
      await Interactions.tw_edit_channel(client)
    print("finished timer")

  async def tw_reset(client):
    print("reset tw")
    await asyncio.sleep(60)
    await Interactions.tw_channel.delete()
    Interactions.tw_max_time = 600
    Interactions.tw_time = 600
    Interactions.tw_bonus = 0
    Interactions.tw_messages = 0
    Interactions.tw_channel = None
    Interactions.tw_last_user = None
    Interactions.tw_participants = set()
      





async def setup(client):
  await client.add_cog(Interactions(client))