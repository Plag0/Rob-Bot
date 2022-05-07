from discord.ext import commands
import discord
import asyncio
import random
from cogs.utility import Utility as util

class Use(commands.Cog):
  def __init__(self, client):
    self.client = client
  
  active_users = set()
  @commands.command(aliases = ["activate","consume","inv","inventory"])
  async def use(self, ctx, upgrade=None):
    if ctx.author in Use.active_users:
      await util.embed_error(ctx,"You can't use multiple upgrades simultaneously!")
      return
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    
    if upgrade == None:
      upgrades = ""
      for key in user:
        if key.startswith("upgrade_"):
          #update after upgrade values patch
          if user[key][1] >= 1 and user[key][5] == 1:
            upgrade_name = key.split("_")
            upgrades += f"{user[key][6]} {upgrade_name[1].capitalize()}: **{user[key][1]}**\n"
      if upgrades == "":
        upgrades += "Empty!"
      embed = discord.Embed(
      colour = (discord.Colour.magenta()),
      title = f"{ctx.author.name}'s Inventory",
      description = f"{upgrades}\nTo use an item in your inventory, type **$use** followed by the item name.")
      await ctx.channel.send(embed=embed)
      return
      
    upgrade = await util.get_upgrade(ctx,upgrade,user)
    upgrade_name = upgrade.split("_")
    if user[upgrade][1] <= 0:
      await util.embed_error(ctx,f"You don't have {upgrade_name[1]}!")
      return
      
    abilities = {
      "mail":self.mail,
      "ban":self.ban,
      "kick":self.kick,
      "restore":self.restore,
      "change":self.change}
    
    if upgrade_name[1] in abilities:
      Use.active_users.add(ctx.author)
      await abilities[upgrade_name[1]](ctx,user)
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      await util.save_user_data(user_dict)
    else:
      await util.embed_error(ctx,f"{upgrade_name[1].capitalize()} is not consumable!")
      return
  
  
  async def mail(self, ctx, user):
    await util.embed_message(ctx,":mailbox:","Send Mail","Paste the user's ID followed by your custom message. To get a user's ID, right-click on their username and select **Copy ID**.\n\nExample Message: ```188811740476211200 Hope you're having a great day!```\n\n***TIP**: If you don't see the **Copy ID** option make sure you have **Developer Mode** enabled in **Advanced Settings**!\nTo cancel this action type **$cancel***")
    
    def validate(m):
      return m.author == ctx.message.author and " " in m.content or m.author == ctx.message.author and "$cancel" in m.content
    
    try:
      input = await self.client.wait_for("message",check=validate,timeout=120.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,"Sorry, you're taking too long. Try this command again when you have a message ready to go!")

    if "$cancel" in input.content.lower():
      await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled action.")
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      return
  
    fields = input.content.split(" ", 1)
    username = fields[0]
    message = fields[1]
    
    try:
      target = await self.client.fetch_user(username)
    except:
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      await util.embed_error(ctx,"User not found!")
      raise ValueError("Invalid user ID!")
    
    dm = await target.create_dm()
    await dm.send(message)
    user["upgrade_mail"][1] -= 1
    await util.embed_message(ctx,":white_check_mark:","Success",f"Your direct message to {target.name} was sent successfully!")
  
  
  async def restore(self, ctx, user):
    streak = user["upgrade_restore"][2]
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
    old_streak_bonus = user["daily_streak"]*(10+user["upgrade_streak"][0])
    user["daily_streak"] = streak
    user["upgrade_restore"][1] -= 1
    streak_bonus = user["daily_streak"]*(10+user["upgrade_streak"][0])
    await util.embed_message(ctx,":white_check_mark:","Success",f"Your streak has been restored to day {streak}, your next daily streak will yield `+${streak_bonus-old_streak_bonus}` extra!")
  
  
  
  
  
  
  async def change(self, ctx, user):
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
    #fields = input.content.split(" ")
    #summoner_name = ""
    #i=0
    #while i<len(fields):
      #summoner_name += fields[i]
      #i+=1
    
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
      user["lol"]["summoner_name"] = summoner_name
      user["lol"]["region"] = region
      user["upgrade_change_lol"][1] -= 1
      await util.embed_message(ctx,":white_check_mark:","Success",f"Congratulations {summoner_name}, your summoner details have been updated!\n`{summoner_name}` - `{region}`")
  
  
  
  
  
  
  async def ban(self, ctx, user):
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
    user["upgrade_ban"][1] -= 1
  
    await util.embed_message(ctx,":white_check_mark:","Success",f"{target.name} was successfully banned!\nThank god he's gone!")
    await ctx.channel.send("https://goo.gl/P4jEGK")
    
    announcements = await self.client.fetch_channel(350045568371785729)
    await announcements.send(f"{ctx.author.mention} has used their **:hammer: Ban** upgrade to temporarily ban {target.name}!")
    
  
  
  
  
  
  async def kick(self, ctx, user):
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
        user["upgrade_kick"][1] -= 1
        await util.embed_message(ctx,":white_check_mark:","Success",f"{target.name} was successfully kicked!\nThank god he's gone!")
        await ctx.channel.send("https://goo.gl/P4jEGK")
        announcements = await self.client.fetch_channel(350045568371785729)
        
        await announcements.send(f"{ctx.author.mention} has used their **:foot: Kick** ability to kick {target.name}!")


def setup(client):
  client.add_cog(Use(client))