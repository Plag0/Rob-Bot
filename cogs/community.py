from discord.ext import commands
import discord
import asyncio
import json
from replit import db
from cogs.utility import Utility as util
from cogs.use import Use as use
from cogs.frontend import Frontend as front
class Community(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(aliases = ["pay", "send"])
  async def give(self, ctx, mention:discord.User, amount):
    if ctx.author.id == mention.id:
      await util.embed_error(ctx, "You can't donate to yourself!")
      return None
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    sender = user_dict[str(ctx.author.id)]
    receiver = user_dict[str(mention.id)]
    if amount.lower() == "all" or amount.lower() == "paul":
      amount = sender["balance"]
    else:
      amount = await util.get_value(ctx,amount,sender["balance"])
    sender["balance"] -= amount
    sender["stat_give_loss"] -= amount
    sender["stat_give_quantity_sent"] += 1
    receiver["balance"] += amount
    receiver["stat_give_profit"] += amount
    receiver["stat_give_quantity_received"] += 1
    if receiver["balance"] > receiver["stat_highest_balance"]:
      receiver["stat_highest_balance"] = receiver["balance"]
    if amount > receiver["stat_highest_give_received"]:
      receiver["stat_highest_give_received"] = amount
      receiver["stat_highest_give_received_user"] = str(ctx.author.id)
    if amount > sender["stat_highest_give_sent"]:
      sender["stat_highest_give_sent"] = amount
      sender["stat_highest_give_sent_user"] = str(mention.id)
    #await util.save_user_data(user_dict)
    
    sender_loss = sender["stat_give_loss"]
    receiver_total_profit = receiver["stat_give_profit"]
  
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = ":incoming_envelope: Transaction",
    description = f"{ctx.author.name} sent {mention.name} **${amount:,}** sloans.\n{mention.name} has received a total of ${receiver_total_profit:,} from donations.")
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"{ctx.author.name} has given out ${-sender_loss:,} total")
    await ctx.channel.send(embed=embed)
  
  
  
  @commands.command(aliases = ["purchase"])
  async def buy(self, ctx, *upgrade):
    if len(upgrade) <= 0:
      await front.shop(self, ctx)
      return
      
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(906087821373239316)]
    upgrade_req = await util.get_upgrade(ctx,user,*upgrade)
    if upgrade_req == None:
      return
    upgrade = upgrade_req[0]
    quantity = upgrade_req[1] or 1
    upgrade_name = upgrade_req[2]

    quantity_string = ""
    if quantity > 1:
        quantity_string = f"{quantity} "

    with open("upgrades.json","r") as f:
      d = json.load(f)
      upgrade_data = d[upgrade]

    for i in range(quantity):
      max_level = upgrade_data["max_level"]
      emoji = upgrade_data["emoji"]
      single_use = upgrade_data["single_use"]
      level = user[upgrade]["level"]
      if single_use:
        price = upgrade_data["price"]
      else:
        price = user[upgrade]["price"]
      
      #Generates the price for the restore upgrade.
      if "restore" in upgrade_name.lower():
        streak = user["stat_highest_daily_streak"]
        percent = user["upgrade_streak"]["amount"]
        amount = streak*(streak+1)/2 * 10 + streak*(streak+1)/2 * 10 * percent*0.01
        price = round(amount + amount*.5)
    
      if price > user["balance"]:
        await util.embed_error(ctx,f"You can't afford **{quantity_string}{upgrade_name}**!")
        return
      elif level >= max_level:
        await util.embed_error(ctx,f"{upgrade_name} is max level!")
        return
      
      user["balance"] -= price
      rob["balance"] += price
      user["stat_upgrade_loss"] -= price
      #Sums 1 to the level.
      user[upgrade]["level"] +=1
      level = user[upgrade]["level"]
      #Increase amount & price.
      consumable = ""
      level_msg = ""
      if single_use:
        consumable = f" \n\n{upgrade_name} is a single-use, non-expiring item.\nTo activate this item, type `$use {upgrade_name.lower()}`\n\n***TIP**: You can hide your activity by doing this command in my DMs!*"
      else:
        user[upgrade]["amount"] = upgrade_data["amounts"][str( level )]
        user[upgrade]["price"] = upgrade_data["prices"][str( level )]
        level_msg = f" Level {level}"
      
      if "restore" in upgrade_name.lower():
        user[upgrade]["amount"] = user["stat_highest_daily_streak"]
    
    #await util.save_user_data(user_dict)
    embed = discord.Embed(
    colour = discord.Colour.green(),
    title = f":shopping_bags: Purchase Successful!",
    description = f"You bought **{quantity_string}{emoji} {upgrade_name}{level_msg}** for **-${price*quantity:,}**!\nYou have ${user['balance']:,} remaining.{consumable}")
    
    #Extra info for upgradeable items.
    #"gold" is included in this statement because gold level 1 is max_level but I still want it to run.
    if single_use == False and level < max_level   or   single_use == False and "gold" in upgrade_name.lower():
      next_level = ""
      current_amount = user[upgrade]["amount"]
      next_amount = upgrade_data["amounts"][str( level+1 )]
      next_price = upgrade_data["prices"][str( level )]

      if "gold" in upgrade_name.lower():
        next_level = f"\nNext Level: **+ {next_amount}%** :lock: Play 15 more games to unlock the next level!\n\n***IMPORTANT:** For this upgrade to work, make sure you have `Display current activity as a status message` enabled in User Settings > Activity Status*"
        embed.add_field(name = "Stats", value = f"Current Level: **+ {current_amount}%**{next_level}")
        #free name change to set up your profile.
        user["upgrade_change_lol"]["level"] += 1
        await use.use(self, ctx, "change")
        #await util.save_user_data(user_dict)
      elif "streak" in upgrade_name.lower() or "cooldown" in upgrade_name.lower():
        next_level = f"\nNext Level: **+ {next_amount}%** :lock: ${next_price:,}"
        embed.add_field(name = "Stats", value = f"Current Level: **+ {current_amount}%**{next_level}")
      else:
        next_level = f"\nNext Level: **+ ${next_amount:,}** :lock: ${next_price:,}"
        embed.add_field(name = "Stats", value = f"Current Level: **+ ${current_amount:,}**{next_level}")
    
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Purchased by {ctx.author.name}")
    await ctx.channel.send(embed=embed)

  
  #@commands.command(aliases = ["pfp", "pic", "picture"])
  #async def avatar(self, ctx, mention:discord.User = None):
    #account = mention or ctx.author
    #user_dict = await util.get_user_data()
    #user = user_dict[str(account.id)]
    #await ctx.channel.send(user.avatar_url)

    
  """
  @commands.command(aliases = ["endorse"])
  async def rep(self, ctx, *mentions:discord.User, amount = None):
    for user in SloanMethods.users:
      if ctx.author.id == user.user_id:
        base_rep = 3
        #might not need this var
        receiver_rep = None
        
        #Assigning rep data.
        sender = user
        fields = sender.rep_data.split(".")
        sender_rep = int(fields[0])
        sender_available_rep = int(fields[1])
        sender_last_rep = fields[2]
  
        FMT = "%Y-%m-%d-%H:%M:%S"
        time_now = datetime.now()
  
        if sender_last_rep == "":
          sender_last_rep = datetime.strptime("1969-01-01-01:01:01", FMT)
        
        elif sender_last_rep != "":
          sender_last_rep = datetime.strptime(sender_last_rep, FMT)
  
        if sender_available_rep == 0:
          embed_colour = discord.Colour.red()
        else:
          embed_colour = discord.Colour.green()
        embed = discord.Embed(
        colour = embed_colour,
        title = ":star: Rob Points",
        description = f"You have {sender_available_rep} Rob Points available")
  
        #Too Early
        after_24_hours = sender_last_rep + timedelta(hours = 24)
        if time_now < after_24_hours:
          difference = time_now - sender_last_rep
          cooldown = timedelta(hours = 24) - difference
          avg_cooldown = str(cooldown).split(".")[0]
          embed.add_field(name = "Reset", value = f"Your Rob Points will reset in {avg_cooldown}")
        
        elif time_now > after_24_hours:
          sender_available_rep = base_rep #+rep_upgrade
  
        #If it's just $rep
        if mentions == None and amount == None:
          print("mentions are empty and amount is none")
          await ctx.channel.send(embed=embed)
  
        elif mentions != None:
          print("mentions are not empty")
          all_mentions = ""
          for item in mentions:
  
            if item.id == ctx.author.id:
              embed = discord.Embed(
              colour = (discord.Colour.red()),
              title = ":x: Error",
              description = f"You can't rep yourself!!")
            await ctx.channel.send(embed=embed)
            return
  
            all_mentions+= f"{item.mention}, "
  
            for user in SloanMethods.users:
              if item.id == user.user_id:
                receiver = user
        
                fields = receiver.rep_data.split(".")
                receiver_rep = int(fields[0])
                receiver_available_rep = int(fields[1])
                receiver_last_rep = fields[2]
  
                amount = amount or 1
                #Exception Handling
                if isinstance(amount, str):
                  if amount.lower() == "all" or amount.lower() == "paul":
                    amount = sender_available_rep
                  else:
                    amount = 1
                if int(amount) > sender_available_rep:
                  embed = discord.Embed(
                    colour = (discord.Colour.red()),
                    title = ":x: Error",
                    description = f"You can't rep more than you have!"
                    )
                  await ctx.channel.send(embed=embed)
                  return
                if int(amount) <= 0 or sender_available_rep == 0:
                  embed = discord.Embed(
                    colour = (discord.Colour.red()),
                    title = ":x: Error",
                    description = f"You can't rep nothing!"
                    )
                  await ctx.channel.send(embed=embed)
                  return
  
                sender_available_rep -= amount
                receiver_rep += amount
                sender_last_rep = datetime.now().strftime(FMT)
  
                sender.rep_data = f"{sender_rep}.{sender_available_rep}.{sender_last_rep}"
                receiver.rep_data = f"{receiver_rep}.{receiver_available_rep}.{receiver_last_rep}"
                SloanMethods.save_balance_sheet()
          
          embed = discord.Embed(
            colour = discord.Colour.magenta(),
            title = ":arrow_up_small: Rob Points",
            description = f"{ctx.author.name} gave {all_mentions} {amount} Rob Points!"
            )
          await ctx.channel.send(embed=embed)
  """


def setup(client):
  client.add_cog(Community(client))