from discord.ext import commands
import discord
import asyncio
import random
from cogs.utility import Utility as util
from cogs.rewards import Rewards as rewards

class Interactions(commands.Cog):
  def __init__(self, client):
    self.client = client

  #more events listed here
  #https://discordpy.readthedocs.io/en/stable/api.html?highlight=wait_for#discord-api-events

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
    await rewards.passive_income(message)
    await rewards.whack_a_rob(client)
    #if not message.content.startswith(client.command_prefix):
      #await util.activity_update(message)




def setup(client):
  client.add_cog(Interactions(client))