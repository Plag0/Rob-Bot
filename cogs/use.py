from discord.ext import commands
import discord
import asyncio
import random
from datetime import datetime, timedelta
from cogs.utility import Utility as util
from cogs.frontend import Frontend as front
import json
from discord.ui import Button

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
    aliases = {"focus":"Gambling Addict", "crate":"Mystery Box", "case":"Mystery Box", "lootbox":"Mystery Box", "send":"Mail"}
    if upgrade.lower() in aliases:
      upgrade = aliases[upgrade]
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    upgrade, quantity, upgrade_name = await util.get_upgrade(ctx,user,upgrade)
    if user[upgrade]["level"] <= 0:
      await util.embed_error(ctx,f"You don't have {upgrade_name}!")
      return
      
    abilities = {
      "mail":self.mail,
      "ban":self.ban,
      "kick":self.kick,
      "restore":self.restore,
      "change":self.change,
      "mystery":self.mystery,
      "gambling":self.focus,
      "sabotage":self.sabotage}
    
    if upgrade.split("_")[1] in abilities:
      Use.active_users.add(ctx.author)
      await abilities[upgrade.split("_")[1]](ctx)
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
    else:
      await util.embed_error(ctx,f"{upgrade_name} is not consumable!")
      return


  
  async def sabotage(self, ctx):
    # This seems so stupid.
    parent_self = self
    desc = f"Sabotaging a user cuts their coin flip odds in half for 24 hours. The target will not be directly alerted.\n"
    desc+= "To select a target, right-click on their username and select **Copy ID**.\n*(Requires Developer Mode to be enabled in Advanced Settings)*"
    embed = discord.Embed(
    colour = discord.Colour.purple(),
    title = f'😈 Sabotage',
    description = desc)
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {ctx.author.name}")

    # Button Setup.
    class Menu(discord.ui.View):
      def __init__(self, timeout=30):
        super().__init__(timeout=timeout)
  
      @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_mail", emoji="⛔")
      async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == ctx.author:
          embed.add_field(name="⛔ Cancelled!",value="Successfully cancelled action.")
          embed.colour = discord.Colour.red()
          await interaction.response.edit_message(embed=embed, view=None)
          self.stop()

      @discord.ui.button(label="Enter ID", style=discord.ButtonStyle.green, custom_id="input", emoji="💬")
      async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == ctx.author:
          await interaction.response.send_modal(Input())
      
      async def on_timeout(self):
        embed.add_field(name="❌ Timed Out!",value="Sorry, you're taking too long.\nThis action has been cancelled.")
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, view=None)

    class Input(discord.ui.Modal, title='Select your target'):
      victim = discord.ui.TextInput(
        label='Victim ID',
        min_length=18,
        max_length=18,
      )
      async def on_submit(self, interaction: discord.Interaction):
        try:
          target = await parent_self.client.fetch_user(self.victim.value)
        except:
          embed.add_field(name="❌ Failed!",value=f"Invalid user ID: `{self.victim.value}`")
          embed.colour = discord.Colour.red()
          await interaction.response.edit_message(embed=embed,view=None)
          self.stop()
          return
          
        user_dict = await util.get_user_data()
        user = user_dict[str(ctx.author.id)]
        victim = user_dict[str(target.id)]
        
        with open("upgrades.json","r") as f:
          d = json.load(f)
        prot_chance = d["upgrade_protection"]["amounts"][ str(victim["upgrade_protection"]["level"]) ]
        base = 0.5
        luck = base * (100 + prot_chance) * 0.01
        
        victim["luck"] = victim["luck"] * luck
        FMT = "%Y-%m-%d-%H:%M:%S"
        expire_date = datetime.utcnow() + timedelta(hours = 24)
        victim["cursed"].append( (expire_date.strftime(FMT), luck) )
    
        user["upgrade_sabotage"]["level"] -= 1
        await util.save_user_data(user_dict)
          
        embed.add_field(name="<:ready:997527681333727253> Success!",value=f"You have successfully cursed {target.name}!\nTheir luck is now **{round(victim['luck']*100, 2)}%**.")
        embed.colour = discord.Colour.green()
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
    
    msg = await ctx.channel.send(embed=embed, view = Menu())


  
  async def focus(self, ctx):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    # Cooldown.
    FMT = "%Y-%m-%d-%H:%M:%S"
    last_focus = datetime.strptime(user["last_gambling_addict_active"], FMT)
    raw_cooldown = timedelta(hours = 24).total_seconds()
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    after_cooldown = last_focus + cooldown
    time_now = datetime.now()

    #Too Early
    if time_now < after_cooldown:
      difference = time_now - last_focus
      time_remaining = cooldown - difference
      reduction = timedelta(hours = 24) - cooldown
      avg_reduction = str(reduction).split(".")[0]
      
      embed = discord.Embed(
      colour = (discord.Colour.red()),
      title = f":hourglass: Focus (Gambling Addict) Cooldown",
      description = f"Please wait `{str(time_remaining).split('.')[0]}`")
      cooldown_level = user["upgrade_cooldown"]["level"]
      if cooldown_level >= 1:
        embed.add_field(name = f":hourglass_flowing_sand: Cooldown Level {cooldown_level}", value = f"`-{avg_reduction}`", inline = True)
      embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {ctx.author.name}")
      await ctx.channel.send(embed=embed)
      return
    
    if user["upgrade_gambling_addict"]["amount"]:
      await util.embed_error(ctx, "You're already focusing.")
      return
      
    user["luck"] = user["luck"] * 1.2
    # Storing the activity status in the amount var.
    user["upgrade_gambling_addict"]["amount"] = True
    user["last_gambling_addict_active"] = str(datetime.now().strftime(FMT))
    
    embed = discord.Embed(
    colour = discord.Colour.green(),
    title = f"🎲 Gambling Addict")
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {ctx.author.name}")
    embed.add_field(name="**🎯 Focus**",value=f"The odds of winning your next coin flip have been increased by **20%**\nThis ability will become available again in `{str(cooldown).split('.')[0]}`",inline=False)
    
    after_raw_cooldown = last_focus + timedelta(hours = 24)
    if time_now < after_raw_cooldown:
      time_saved = after_raw_cooldown - time_now
      user["stat_time_saved"] += int(time_saved.total_seconds())
      embed.add_field(name = f":hourglass_flowing_sand: Time Saved! +{str(time_saved).split('.')[0]}", value = f"You have a cooldown level of **{user['upgrade_cooldown']['level']}**", inline = True)
    await ctx.channel.send(embed=embed)
    await util.save_user_data(user_dict)
  
  async def mystery(self, ctx):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    rob = user_dict["906087821373239316"]
    type = random.choices(["special","sloans"], [25,75])[0]
    r = random.randrange
    if type == "sloans":
      t1 = {"prize": r(500,2501,10), "odds": 79.9,"colour":discord.Colour.from_rgb(77,105,205)}
      t2 = {"prize": r(2500,4001,10), "odds": 16.0,"colour":discord.Colour.from_rgb(137,71,255)}
      t3 = {"prize": r(4000,12001,10), "odds": 3.2,"colour":discord.Colour.from_rgb(212,43,230)}
      t4 = {"prize": r(12000,50001,10), "odds": 0.6,"colour":discord.Colour.from_rgb(235,75,75)}
      t5 = {"prize": r(100000,1200001,10), "odds": 0.3,"colour":discord.Colour.from_rgb(249,211,5)}
      prizes = [t1,t2,t3,t4,t5]
      odds = [t1["odds"], t2["odds"], t3["odds"], t4["odds"], t5["odds"]]
    else:
      t1 = {"prize": random.choices(["1 mail","1 change","1 mystery"],[90,0,10])[0], "odds": 79.9,"colour":discord.Colour.from_rgb(77,105,205)}
      t2 = {"prize": random.choices([f"daily_reset", "2 mystery"],[50,50])[0], "odds": 16.0,"colour":discord.Colour.from_rgb(137,71,255)}
      t3 = {"prize": random.choices(["weekly_reset" ,"daily_reset", "1 sabotage", f"{r(1,8,1)} mystery"],[30,50,10,10])[0], "odds": 3.2,"colour":discord.Colour.from_rgb(212,43,230)}
      t4 = {"prize": random.choices(["restore", "weekly_reset", f"{r(2,25,1)} mystery", f"{r(1,3,1)} sabotage", "1 kick"],[10,40,25,15,10])[0], "odds": 0.6,"colour":discord.Colour.from_rgb(235,75,75)}
      t5 = {"prize": random.choices(["1 ban","2 kick",f"{r(25,101,1)} mystery", "restore", f"{r(3,11,1)} sabotage"],[30,53,10,3,4])[0], "odds": 0.3,"colour":discord.Colour.from_rgb(249,211,5)}
      prizes = [t1,t2,t3,t4,t5]
      odds = [t1["odds"], t2["odds"], t3["odds"], t4["odds"], t5["odds"]]
    
    prize = random.choices(prizes, odds)[0]
    prize_message = ""
    description = ""
    if type == "sloans":
      user["balance"] += prize["prize"]
      user["total_cash_flow"] += prize["prize"]
      user["daily_cash_flow"] += prize["prize"]
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance"] = user["balance"]
      rob["balance"] -= prize["prize"]
      rob["total_cash_flow"] += prize["prize"]
      rob["daily_cash_flow"] += prize["prize"]
      
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
        upgrade, null, null = await util.get_upgrade(ctx,user,fields[1])
        user[upgrade]["level"] += quantity
        prize_message = f"{quantity} {fields[1].capitalize()}"
        description = f"**{fields[1].capitalize()}** has been added to your inventory!\n"
    
    user["stat_mystery_box_quantity"] += 1
    user["upgrade_mystery_box"]["level"] -= 1
    await util.save_user_data(user_dict)
        
    
    embed = discord.Embed(
    colour = prize["colour"],
    title = f':gift: You won {prize_message}',
    description = f"{description}\nMystery Boxes Opened: **{user['stat_mystery_box_quantity']:,}**\nAmount Won: **${user['stat_mystery_box_profit']:,}**")
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Opened by {ctx.author.name}")
    await ctx.channel.send(embed=embed)
  
  

  
  async def mail(self, ctx):
    # Button Setup.
    class Menu(discord.ui.View):
      def __init__(self):
        super().__init__()
        self.value = None
  
      @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_mail", emoji="⛔")
      async def menu(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.user == ctx.author:
          embed.add_field(name="⛔ Cancelled!",value="Successfully cancelled action.")
          embed.colour = discord.Colour.red()
          await button.response.edit_message(embed=embed, view=None)
          self.value = False
          self.stop()
          
    desc = f"**Instructions**\n"
    desc+= "Paste the user's ID followed by your custom message. You can also send up to 10 attachments of any type.\n"
    desc+= "To get someone's ID, right-click on their username and select **Copy ID**.\n*(Requires Developer Mode to be enabled in Advanced Settings)*\n"
    desc+= "```188811740476211200 Hope you're having a great day!```\n"
    embed = discord.Embed(
    colour = discord.Colour.magenta(),
    title = f'📫 Send Mail',
    description = desc)
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {ctx.author.name}")
    
    view = Menu()
    msg = await ctx.channel.send(embed=embed, view = view)

    tasks = [
      asyncio.create_task(self.client.wait_for(
        "message",
        check = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel, 
        timeout=120
        ), name="message"),
      asyncio.create_task(self.client.wait_for(
        "interaction", 
        check = lambda i: i.user == ctx.author and i.data["custom_id"] == "cancel_mail", 
        timeout=120
        ), name="button")
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
      
    finished: asyncio.Task = list(done)[0]

    for task in pending:
      try:
        task.cancel()
      except: #asyncio.CancelledError
        pass

    action = finished.get_name()
    try:
      interaction = finished.result()
    except asyncio.TimeoutError:
      embed.add_field(name="❌ Timed Out!",value="Sorry, you're taking too long.\nThis action has been cancelled.")
      embed.colour = discord.Colour.red()
      await msg.edit(embed=embed, view=None)
      return
    
    if action == "button":
      return
      
    fields = interaction.content.split(" ", 1)
    target_id = fields[0]
    if len(fields) >= 2:
      message = fields[1]
    else:
      message = ""
    files = []
    if len(interaction.attachments) > 0:
        for attachment in interaction.attachments:
          try:
            #use_cached = True causes some media types to be unsupported.
            files.append(await attachment.to_file(use_cached = False))
          except:
            embed.add_field(name="❌ Failed!",value=f"Unsupported media type for: `{attachment.filename}`")
            embed.colour = discord.Colour.red()
            await msg.edit(embed=embed, view=None)
            return
    dm = None
    try:
      target = await self.client.fetch_channel(target_id)
      if target.id == 350045568371785729 or target.id == 965655405927743518:
        embed.add_field(name="❌ Failed!",value=f"You don't have permission to send mail to `{target.name}`")
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, view=None)
        return
      dm = False
    except:
      pass
    #Gets the user object.
    try:
      target = await self.client.fetch_user(target_id)
      dm = True
    except:
      pass
    if dm == None:
      embed.add_field(name="❌ Failed!",value=f"Invalid user/channel ID: `{target_id}`")
      embed.colour = discord.Colour.red()
      await msg.edit(embed=embed, view=None)
      return
      
    #Creates and sends a DM to the specified user.
    if dm == True:
      try:
        dm = await target.create_dm()
        await dm.send(content=message, files=files)
      except Exception as e:
        embed.add_field(name="❌ Failed!",value=f"Your direct message to {target.name} failed to send.\n`{e}`")
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, view=None)
        return
    else:
      try:
        await target.send(content=message, files=files)
      except Exception as e:
        embed.add_field(name="❌ Failed!",value=f"Your channel message to {target.name} failed to send.\n`{e}`")
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, view=None)
        return
        
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    user["upgrade_mail"]["level"] -= 1
    await util.save_user_data(user_dict)
    
    embed.add_field(name="✅ Success!",value=f"Your direct message to {target.name} was sent successfully!")
    embed.colour = discord.Colour.green()
    await msg.edit(embed=embed, view=None)
  
  
  
  
  
  async def restore(self, ctx):
    # Button Setup.
    class Menu(discord.ui.View):
      def __init__(self, *, timeout=30):
        super().__init__(timeout=timeout)
        self.value = None
  
      @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm_restore", emoji="✅")
      async def menu1(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.user == ctx.author:
          user_dict = await util.get_user_data()
          user = user_dict[str(ctx.author.id)]
          old_streak_bonus = user["daily_streak"]*10 + user["daily_streak"]*10 * user["upgrade_streak"]["amount"] * 0.01
          user["daily_streak"] = streak
          streak_bonus = user["daily_streak"]*10 + user["daily_streak"]*10 * user["upgrade_streak"]["amount"] * 0.01
          user["upgrade_restore"]["level"] -= 1
          await util.save_user_data(user_dict)
          
          embed.add_field(name="✅ Success!",value=f"Your streak has been restored to **{streak}**!\nYour next daily streak will yield `+${round(streak_bonus-old_streak_bonus):,}` extra!")
          embed.colour = discord.Colour.green()
          await button.response.edit_message(embed=embed, view=None)
          self.value = False
          self.stop()
          
      @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_restore", emoji="⛔")
      async def menu2(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.user == ctx.author:
          embed.add_field(name="⛔ Cancelled!",value="Successfully cancelled action.")
          embed.colour = discord.Colour.red()
          await button.response.edit_message(embed=embed, view=None)
          self.value = False
          self.stop()

      async def on_timeout(self):
        embed.add_field(name="❌ Timed Out!",value="Sorry, you're taking too long.\nThis action has been cancelled.")
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, view=None)
        
          
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    #storing the streak amount in the amount variable
    streak = user["upgrade_restore"]["amount"]
    embed = discord.Embed(
    colour = discord.Colour.magenta(),
    title = f'🎊 Restore Streak',
    description = f"Are you sure you want to restore your streak to **{streak}**?")
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {ctx.author.name}")
    view = Menu()
    msg = await ctx.channel.send(embed=embed, view=view)
    


  
  async def change(self, ctx):
    await util.embed_error(ctx, "**Change** is currently disabled due to risk of exploitation.")
    return
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    summoner_name = user["lol"]["summoner_name"]
    region = user["lol"]["region"]
    
    class Options(discord.ui.View):
      def __init__(self, *, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None
      
      options = [
          discord.SelectOption(label="Custom", value="custom", description="Manually enter a summoner name & region", emoji="💬")
        ]
      for account in user["lol_accounts"]:
        options.append(discord.SelectOption(label=f"{account[0]} - {account[1].upper()}", value=f"{account[0]}_{account[1]}", emoji="👤"))
      
      @discord.ui.select(placeholder="Change Account", options=options)
      async def select_menu(self, interaction: discord.Interaction, select:discord.ui.Select):
        if select.values[0] == "custom" and interaction.user == ctx.author:
          await interaction.response.send_modal(Input())
        else:
          if interaction.user == ctx.author:
            name = select.values[0].split("_")[0]
            region = select.values[0].split("_")[1]
            user_dict = await util.get_user_data()
            user = user_dict[str(ctx.author.id)]
            user["lol"]["summoner_name"] = name
            user["lol"]["region"] = region
            user["upgrade_change_lol"]["level"] -= 1
            await util.save_user_data(user_dict)
           
            embed.description = f"**{name} - {region}**\n"
            embed.add_field(name="✅ Success!",value="Successfully updated summoner details!")
            embed.colour = discord.Colour.green()
            await interaction.response.edit_message(embed=embed, view=None)
            self.value = False
            self.stop()

      
      @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="⛔")
      async def menu(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.user == ctx.author:
          embed.add_field(name="⛔ Cancelled!",value="Successfully cancelled action.")
          embed.colour = discord.Colour.red()
          await button.response.edit_message(embed=embed, view=None)
          self.value = False
          self.stop()
          
      async def on_timeout(self):
        embed.add_field(name="❌ Timed Out!",value="Sorry, you're taking too long.\nThis action has been cancelled.")
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, view=None)

        
    
    class Input(discord.ui.Modal, title='Custom Details'):
      name = discord.ui.TextInput(
        label='Summoner Name (Case-Sensitive)',
        placeholder='Your name here...',
        min_length=3,
        max_length=16,
      )
      region = discord.ui.TextInput(
        label='Region (e.g. oc1, na1, la1, la2)',
        placeholder='Enter your account region...',
        min_length=3,
        max_length=3,
        default="oc1",
      )
      async def on_submit(self, interaction: discord.Interaction):
        supported_regions = ["oc1","na1","la1","la2"]
        while self.region.value.lower() not in supported_regions:
          # I can't figure out why this causes an error. It somehow works as intended so I've put it in a try except to hide that ugly red text in my console.
          try:
            await interaction.response.send_modal(Input(title="Invalid Region"))
          except:
            pass
        user_dict = await util.get_user_data()
        user = user_dict[str(ctx.author.id)]
        user["lol"]["summoner_name"] = self.name.value
        user["lol"]["region"] = self.region.value.lower()
        user["lol_accounts"].append( (self.name.value, self.region.value.lower()) )
        if len(user["lol_accounts"]) >= 10:
          user["lol_accounts"].pop(0)
        user["upgrade_change_lol"]["level"] -= 1
        await util.save_user_data(user_dict)
        
        embed.description = f"**{self.name.value} - {self.region.value.upper()}**\n"
        embed.add_field(name="✅ Success!",value="Successfully updated summoner details!")
        embed.colour = discord.Colour.green()
        await interaction.response.edit_message(embed=embed, view=None)
        view.stop()

    
    if summoner_name != "":
      summoner_details = f"**{summoner_name} - {region.upper()}**\n"
    else:
      summoner_details = ""
    desc = f"{summoner_details}"
    
    embed = discord.Embed(
    colour = discord.Colour.blue(),
    title = f'<:lol_passive:957853326626656307> Summoner Details',
    description = desc)
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {ctx.author.name}")

    view = Options()
    msg = await ctx.channel.send(embed=embed, view=view)


  
  
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
      return
  
    try:
      dm = await target.create_dm()
      await dm.send(f"**{ctx.author.name} has paid $1,000,000 to temporarily ban you from Mad Gangaz.**{message}")
      print(f"banned {target.name} for {message}")
      await target.ban(reason = message)
    except:
      if ctx.author in Use.active_users:
        Use.active_users.remove(ctx.author)
      await util.embed_error(ctx,f"Failed to ban {target.name}, try someone else!")
      return
    
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    user["upgrade_ban"]["level"] -= 1
    await util.save_user_data(user_dict)
  
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
      try:
        dm = await target.create_dm()
        await dm.send(f"**{ctx.author.name} has paid $350,000 to kick a random member from Mad Gangaz. You were selected, congratulations!")
      except:
        print("Unable to DM target. Moving on.")
        pass
      await asyncio.sleep(3)
      try:
        await target.kick(reason=None)
      except:
        if ctx.author in Use.active_users:
          Use.active_users.remove(ctx.author)
        await util.embed_error(ctx,f"Failed to kick {target.mention}. Damn.")
        raise ValueError(f"Can't kick user: {target.name}")
      
      user_dict = await util.get_user_data()
      user = user_dict[str(ctx.author.id)]
      user["upgrade_kick"]["level"] -= 1
      await util.save_user_data(user_dict)
      
      await util.embed_message(ctx,":white_check_mark:","Success",f"{target.name} was successfully kicked!\nThank god he's gone!")
      await ctx.channel.send("https://goo.gl/P4jEGK")
      announcements = await self.client.fetch_channel(350045568371785729)
      await announcements.send(f"{ctx.author.mention} has used their **:foot: Kick** ability to kick {target.name}!")


async def setup(client):
  await client.add_cog(Use(client))