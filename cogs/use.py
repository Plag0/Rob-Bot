from discord.ext import commands
import discord
import asyncio
import random
from discord_components import DiscordComponents, ComponentsBot, Button, SelectOption, Select
from datetime import datetime, timedelta
from cogs.utility import Utility as util
from cogs.frontend import Frontend as front
from replit import db
import json
import os

class Use(commands.Cog):
  def __init__(self, client):
    self.client = client


  
  active_users = set()
  @commands.command(aliases = ["activate","consume","open"])
  async def use(self, ctx, upgrade=None):
    if upgrade == None:
      await front.inventory(self, ctx)
      return
    if ctx.author in Use.active_users:
      await util.embed_error(ctx,"You can't use multiple upgrades simultaneously!")
      return
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    upgrade = await util.get_upgrade(ctx,user,upgrade)
    upgrade_name = upgrade[2]
    upgrade = upgrade[0]
    if user[upgrade]["level"] <= 0:
      await util.embed_error(ctx,f"You don't have {upgrade_name}!")
      return
      
    abilities = {
      "mail":self.mail,
      "ban":self.ban,
      "kick":self.kick,
      "restore":self.restore,
      "change":self.change,
      "mystery":self.mystery}
    
    if upgrade.split("_")[1] in abilities:
      Use.active_users.add(ctx.author)
      await abilities[upgrade.split("_")[1]](ctx) #,user,rob
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      #await util.save_user_data(user_dict)
    else:
      await util.embed_error(ctx,f"{upgrade_name} is not consumable!")
      return

  
  
  async def mystery(self, ctx):
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    rob = user_dict["906087821373239316"]
    type = random.choices(["special","sloans"], [25,75])[0]
    r = random.randrange
    if type == "sloans":
      t1 = {"prize": r(100,2501,10), "odds": 79.9,"colour":discord.Colour.from_rgb(77,105,205)}
      t2 = {"prize": r(2500,4001,10), "odds": 16.0,"colour":discord.Colour.from_rgb(137,71,255)}
      t3 = {"prize": r(4000,12001,10), "odds": 3.2,"colour":discord.Colour.from_rgb(212,43,230)}
      t4 = {"prize": r(12000,50001,10), "odds": 0.6,"colour":discord.Colour.from_rgb(235,75,75)}
      t5 = {"prize": r(50000,1200001,10), "odds": 0.3,"colour":discord.Colour.from_rgb(249,211,5)}
      prizes = [t1,t2,t3,t4,t5]
      odds = [t1["odds"], t2["odds"], t3["odds"], t4["odds"], t5["odds"]]
    else:
      t1 = {"prize": random.choices(["1 mail","1 change"],[40,60])[0], "odds": 79.9,"colour":discord.Colour.from_rgb(77,105,205)}
      t2 = {"prize": random.choices([f"{r(2,5,1)} mail", "daily_reset"],[70,30])[0], "odds": 16.0,"colour":discord.Colour.from_rgb(137,71,255)}
      t3 = {"prize": random.choices(["weekly_reset" ,"daily_reset"],[30,70])[0], "odds": 3.2,"colour":discord.Colour.from_rgb(212,43,230)}
      t4 = {"prize": random.choices(["restore", "weekly_reset", "daily_reset",f"{r(2,8,1)} mystery"],[7,22,62,9])[0], "odds": 0.6,"colour":discord.Colour.from_rgb(235,75,75)}
      t5 = {"prize": random.choices(["1 ban","1 kick",f"{r(10,50,1)} mystery", "restore"],[24,64,9,3])[0], "odds": 0.3,"colour":discord.Colour.from_rgb(249,211,5)}
      prizes = [t1,t2,t3,t4,t5]
      odds = [t1["odds"], t2["odds"], t3["odds"], t4["odds"], t5["odds"]]
    
    prize = random.choices(prizes, odds)[0]
    prize_message = ""
    description = ""
    if type == "sloans":
      user["balance"] += prize["prize"]
      rob["balance"] -= prize["prize"]
      user["stat_mystery_box_profit"] += prize["prize"]
      if prize['prize'] > user["stat_mystery_box_highest_win"]:
        user["stat_mystery_box_highest_win"] = prize['prize']
      prize_message = f"${prize['prize']:,}"
      description = f"**${prize['prize']:,}** sloans have been added to your account!\nYour new balance is ${user['balance']:,}.\n"
    else:
      user["stat_mystery_box_special_quantity"] += 1
      FMT = "%Y-%m-%d-%H:%M:%S"
      if prize["prize"] == "daily_reset":
        last_daily = datetime.strptime(user["last_daily"], FMT)
        raw_cooldown = timedelta(hours = 24).total_seconds()
        cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
        after_cooldown = last_daily + cooldown
        time_now = datetime.now()
    
        #If on cooldown. This check is done because otherwise users could reset their daily streaks even after letting it expire.
        #Daily Streaks aren't wiped until a daily is done to check the time difference. If someone hasn't done their daily in a week,
        #and then gets this reward, the next time they do their daily they won't lose their streak.
        if time_now < after_cooldown: 
          user["last_daily"] = (datetime.now()-timedelta(hours = 24)).strftime(FMT)
          prize_message = "a Daily Cooldown Reset"
          description = "Your daily cooldown has been reset!\n"
        else:
          prize_message = "nothing!"
          description = "That's right, you got absolutely nothing from that!\n"
      elif prize["prize"] == "weekly_reset":
        #If weekly streaks are added: do the same procedure for the daily reset above.
        user["last_weekly"] = (datetime.now()-timedelta(days = 7)).strftime(FMT)
        prize_message = "a Weekly Cooldown Reset"
        description = "Your weekly cooldown has been reset!\n"
      elif prize["prize"] == "restore":
        user["upgrade_restore"]["level"] += 1
        user["upgrade_restore"]["amount"] = user["stat_highest_daily_streak"]
        prize_message = "Restore Streak"
        description = f"**Restore Streak** has been added to your inventory!\n"
      else:
        fields = prize["prize"].split(" ")
        quantity = int(fields[0])
        upgrade = await util.get_upgrade(ctx,user,fields[1])
        upgrade = upgrade[0]
        user[upgrade]["level"] += quantity
        prize_message = f"{quantity} {fields[1].capitalize()}"
        description = f"**{fields[1].capitalize()}** has been added to your inventory!\n"
    
    user["stat_mystery_box_loss"] -= user["upgrade_mystery_box"]["price"]
    user["stat_mystery_box_quantity"] += 1
    user["upgrade_mystery_box"]["level"] -= 1
        
    
    embed = discord.Embed(
    colour = prize["colour"],
    title = f':gift: You won {prize_message}',
    description = f"{description}\nMystery Boxes Opened: **{user['stat_mystery_box_quantity']:,}**\nAmount Won: **${user['stat_mystery_box_profit']:,}**")
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Opened by {ctx.author.name}")
    await ctx.channel.send(embed=embed)
  
  

  
  async def mail(self, ctx):
    await util.embed_message(ctx,":mailbox:","Send Mail","Paste the user's ID followed by your custom message. You can send up to 10 attachments of any type with or without your message.\nTo get a user's ID, right-click on their username and select **Copy ID**.\n\nExample Message: ```188811740476211200 Hope you're having a great day!```\n\n***TIP**: If you don't see the **Copy ID** option make sure you have **Developer Mode** enabled in **Advanced Settings**!*")
    custom_id = "mail_button_1"
    msg = await ctx.channel.send("", components = [Button(label=f"Cancel", style="4", emoji="⛔", custom_id=custom_id)])
    tasks = [
      asyncio.create_task(self.client.wait_for(
        "message",
        check = lambda m: m.author == ctx.message.author, 
        timeout=120
        ), name="message"),
      asyncio.create_task(self.client.wait_for(
        "button_click", 
        check = lambda i: i.custom_id == custom_id and i.user == ctx.author, 
        timeout=120
        ), name="button")
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
      
    finished: asyncio.Task = list(done)[0]

    for task in pending:
      try:
        task.cancel()
      except asyncio.CancelledError:
        pass

    action = finished.get_name()
    try:
      input = finished.result()
    except asyncio.TimeoutError:
      await msg.delete()
      await util.embed_error(ctx,"Sorry, you're taking too long. This action has been cancelled.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
    
    if action == "button":
      await msg.delete()
      await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled action.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return

    elif action == "message":
      fields = input.content.split(" ", 1)
      username = fields[0]
      if len(fields) >= 2:
        message = fields[1]
      else:
        message = ""
      files = []
      if len(input.attachments) > 0:
          for attachment in input.attachments:
            try:
              #use_cached = True causes some media types to be unsupported.
              files.append(await attachment.to_file(use_cached = False))
            except:
              if ctx.author in Use.active_users:
                Use.active_users.remove(ctx.author)
              await util.embed_error(ctx,f"`{attachment.filename}` is an unsupported media type!")
              return
      
      try:
        target = await self.client.fetch_user(username)
      except:
        if ctx.author in Use.active_users:
          Use.active_users.remove(ctx.author)
        await util.embed_error(ctx,"User not found!")
        return
      
      try:
        dm = await target.create_dm()
        await dm.send(content=message, files=files)
      except Exception as e:
        if ctx.author in Use.active_users:
          Use.active_users.remove(ctx.author)
        await util.embed_error(ctx,f"Your direct message to {target.name} failed to send.\n`{e}`")
        return
  
      user_dict = db["user_dict"]
      user = user_dict[str(ctx.author.id)]
      user["upgrade_mail"]["level"] -= 1
      await util.embed_message(ctx,":white_check_mark:","Success",f"Your direct message to {target.name} was sent successfully!")
  
  
  async def restore(self, ctx):
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    #storing the streak amount in the amount variable
    streak = user["upgrade_restore"]["amount"]
    await util.embed_message(ctx,":confetti_ball:","Restore Streak",f"Type `confirm` to boost your current streak to `{streak}`\n\n***TIP**: To cancel this action, type **$cancel***")
    def validate(m):
      return m.author == ctx.author and "confirm" in m.content.lower() or m.author == ctx.author and "$cancel" in m.content.lower()
    
    try:
      input = await self.client.wait_for("message",check=validate,timeout=120.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,"Sorry, you're taking too long. This action has been cancelled.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
  
    if "$cancel" in input.content.lower():
      await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled action.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    old_streak_bonus = user["daily_streak"]*10 + user["daily_streak"]*10 * user["upgrade_streak"]["amount"] * 0.01
    user["daily_streak"] = streak
    streak_bonus = user["daily_streak"]*10 + user["daily_streak"]*10 * user["upgrade_streak"]["amount"] * 0.01
    user["upgrade_restore"]["level"] -= 1
    await util.embed_message(ctx,":white_check_mark:","Success",f"Your streak has been restored to day {streak}, your next daily streak will yield `+${round(streak_bonus-old_streak_bonus):,}` extra!")
  
  
  
  
  
  
  async def change(self, ctx):
    await util.embed_message(ctx,"👤","Update Summoner Details","Enter **only** your summoner name.\n(Case-sensitive)\n\n***TIP**: To cancel this action, type **$cancel***")
    
    def validate(m):
      return m.author == ctx.message.author and m.channel == ctx.channel
    
    try:
      input = await self.client.wait_for("message",check=validate,timeout=120.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,"Sorry, you're taking too long. This action has been cancelled.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
  
    if "$cancel" in input.content.lower():
      await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled action.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
    summoner_name = input.content
    
    await util.embed_message(ctx,"👤","Update Summoner Details","Enter your account region.\nCurrently supported regions are:\n`oc1` - Oceania\n`na1` - North America\n`la1` - Latin America North\n`la2` - Latin America South\n\n***TIP**: To cancel this action, type **$cancel***")
    regions = ["la1","la2","na1","oc1"]
    def validate(m):
      return m.author == ctx.message.author and m.channel == ctx.channel and m.content.lower() in regions or m.author == ctx.message.author and m.channel == ctx.channel and m.content.lower() == "$cancel"
    
    try:
      input = await self.client.wait_for("message",check=validate,timeout=120.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,"Sorry, you're taking too long. This action has been cancelled.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
  
    if "$cancel" in input.content.lower():
      await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled action.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
  
    region = input.content.strip().lower()
  
  
    await util.embed_message(ctx,"👤","Update Summoner Details",f"Is this correct?\nSummoner Name: `{summoner_name}`\nSummoner Region: `{region}`\n\n***TIP**: To confirm this action, type **$confirm**, or to cancel **$cancel***")
    
    responses = ["$confirm","$cancel"]
    def validate(m):
      return m.author == ctx.message.author and m.channel == ctx.channel and m.content.lower() in responses
    
    try:
      input = await self.client.wait_for("message",check=validate,timeout=120.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,"Sorry, you're taking too long. This action has been cancelled.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
  
    if "$cancel" in input.content.lower():
      await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled action.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
  
    if "$confirm" in input.content.lower():
      user_dict = db["user_dict"]
      user = user_dict[str(ctx.author.id)]
      user["lol"]["summoner_name"] = summoner_name
      user["lol"]["region"] = region
      user["upgrade_change_lol"]["level"] -= 1
      await util.embed_message(ctx,":white_check_mark:","Success",f"Congratulations {summoner_name}, your summoner details have been updated!\n`{summoner_name}` - `{region}`")
  
  
  
  
  
  
  async def ban(self, ctx):
    await util.embed_message(ctx,":hammer:","Ban User","Paste the user's ID followed by an optional reason for the ban. To get a user's ID, right-click on their username and select **Copy ID**.\n\nExample Message: ```188811740476211200 Banned for being gay.```\n\n***TIP**: If you don't see the **Copy ID** option make sure you have **Developer Mode** enabled in **Advanced Settings!***")
    
    def validate(m):
      return m.author == ctx.message.author
    
    try:
      input = await self.client.wait_for("message",check=validate,timeout=120.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,"Sorry, you're taking too long. Try again when you've made up your mind.")
  
    fields = input.content.split(" ", 1)
    username = fields[0]
    message = ""
    if len(fields) >= 1:
      message = f"\n**Reason:** {fields[1]}"
    
    try:
      target = await self.client.fetch_user(username)
      if str(target.id) == "300229174533292032":
        if ctx.author in Use.active_users:
          Use.active_users.remove(ctx.author)
        await util.embed_error(ctx,"You will pay for this.")
        raise ValueError(f"{ctx.author.name} tried to ban Tyaged.")
    except:
      await util.embed_error(ctx,"User not found!")
  
    try:
      dm = await target.create_dm()
      await dm.send(f"**{ctx.author.name} has paid $1,000,000 to temporarily ban you from Mad Gangaz.**{message}")
      await target.ban(reason = message)
    except:
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      await util.embed_error(ctx,f"Failed to ban {target.name}, try someone else!")
      raise ValueError("Failed to ban user.")
    
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    user["upgrade_ban"]["level"] -= 1
  
    await util.embed_message(ctx,":white_check_mark:","Success",f"{target.name} was successfully banned!\nThank god he's gone!")
    await ctx.channel.send("https://goo.gl/P4jEGK")
    
    announcements = await self.client.fetch_channel(350045568371785729)
    await announcements.send(f"{ctx.author.mention} has used their **:hammer: Ban** upgrade to temporarily ban {target.name}!")
    
  
  
  
  
  
  async def kick(self, ctx):
    await util.embed_message(ctx,":foot:","Kick Random User","Are you sure you want to kick a random user?\n\nType yes or no.")
    
    def validate(m):
      return m.author == ctx.message.author
    
    try:
      input = await self.client.wait_for("message",check=validate,timeout=120.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,"Sorry, you're taking too long. Try again when you've made up your mind.")
  
    if input.content.lower() == "no":
      await util.embed_message(ctx,":x:","Cancelled Action","This action has been cancelled. Your item has not been used.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
    elif input.content.lower() == "yes":
      kick_list=[]
      async for user in ctx.guild.fetch_members(limit=None):
        kick_list.append(user)
        #tyaged protection
        if user.id == 300229174533292032:
          kick_list.remove(user)
        target = random.choice(kick_list)
        await util.embed_message(ctx,":no_pedestrians:","Target Locked",f"{target.mention} will be kicked in **3 seconds.**")
        dm = await target.create_dm()
        await dm.send(f"**{ctx.author.name} has paid $350,000 to kick a random member from Mad Gangaz. You were selected, congratulations!")
        await asyncio.sleep(3)
        try:
          await target.kick(reason=None)
        except:
          if ctx.author in Use.active_users:
            Use.active_users.remove(ctx.author)
          await util.embed_error(ctx,f"Failed to kick {target.mention}. Damn.")
          raise ValueError(f"Can't kick user: {target.name}")
        
        user_dict = db["user_dict"]
        user = user_dict[str(ctx.author.id)]
        user["upgrade_kick"]["level"] -= 1
        await util.embed_message(ctx,":white_check_mark:","Success",f"{target.name} was successfully kicked!\nThank god he's gone!")
        await ctx.channel.send("https://goo.gl/P4jEGK")
        announcements = await self.client.fetch_channel(350045568371785729)
        
        await announcements.send(f"{ctx.author.mention} has used their **:foot: Kick** ability to kick {target.name}!")


def setup(client):
  client.add_cog(Use(client))