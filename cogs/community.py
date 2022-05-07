from discord.ext import commands
import discord
import asyncio
from cogs.utility import Utility as util

class Community(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(aliases = ["pay", "send"])
  async def give(self, ctx, mention:discord.User, amount):
    if ctx.author.id == mention.id:
      await util.embed_error(ctx, "You can't donate to yourself!")
      return None
    user_dict = await util.get_user_data()
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
    await util.save_user_data(user_dict)
    
    sender_loss = sender["stat_give_loss"]
    receiver_total_profit = receiver["stat_give_profit"]
  
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = ":incoming_envelope: Transaction",
    description = f"{ctx.author.name} sent {mention.name} **${amount:,}** sloans.\n{mention.name} has received a total of ${receiver_total_profit:,} from donations.")
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"{ctx.author.name} has given out ${-sender_loss:,} total")
    await ctx.channel.send(embed=embed)
  
  
  
  @commands.command(aliases = ["purchase"])
  async def buy(self, ctx, upgrade):
    #[0] is core amount
    #[1] is quantity
    #[2] is is price
    #[3] is increment
    #[4] is max upgrade
    #[5] is single use true or false
    #[6] is emoji
  
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(906087821373239316)]
    upgrade = await util.get_upgrade(ctx,upgrade,user)
    upgrade_name = upgrade.split("_")
  
    quantity = user[upgrade][1]
    price = user[upgrade][2]
    increment = user[upgrade][3]
    max_level = user[upgrade][4]
    single_use = user[upgrade][5]
    emoji = user[upgrade][6]
  
    #generates the price for the restore upgrade
    if "restore" in upgrade_name[1]:
      streak = user["stat_highest_daily_streak"]
      streak_bonus = user["upgrade_streak"][0]
      amount = (streak*(streak+1)/2)*(10+streak_bonus)
      price = round(amount + amount*.5)
  
    if price > user["balance"]:
      await util.embed_error(ctx,f"You can't afford {upgrade_name[1]}!")
      return
    elif quantity >= max_level:
      await util.embed_error(ctx,f"{upgrade_name[1]} is max level!")
      return
    else:
      user["balance"] -= price
      rob["balance"] += price
      user["stat_upgrade_loss"] -= price
      #sums 1 to quantity
      user[upgrade][1] +=1
      quantity = user[upgrade][1]
      #core value increases by the value of the increment x quantity
      level = ""
      consumable = ""
      if single_use == 0:
        user[upgrade][0] += increment*quantity
        level = f" Level {quantity}"
      elif single_use == 1:
        consumable = f" \n\n{upgrade_name[1].capitalize()} is a single-use, non-expiring item. To activate this item, type **$use** followed by the item name.\n\nExample Message:```$use {upgrade_name[1].lower()}```\n\n***TIP**: If you want to be incognito, try doing this command in my DMs!*"
      
      #price sums itself
      if single_use == 0:
        user[upgrade][2] += user[upgrade][2]
      elif "restore" in upgrade_name[1]:
        user[upgrade][2] = user["stat_highest_daily_streak"]
      
      await util.save_user_data(user_dict)
      
      balance = user["balance"]
      embed = discord.Embed(
      colour = discord.Colour.green(),
      title = f":shopping_bags: Purchase Successful!",
      description = f"You bought **{emoji} {upgrade_name[1].capitalize()}{level}** for **-${price:,}**!\nYou now have ${balance:,}{consumable}")
      
      #extra info for upgradeable items
      #"or "gold" is added because gold level 1 is not < max_level but I still want it to run.
      if single_use == 0 and quantity < max_level or single_use == 0 and "gold" in upgrade_name[1]:
        next_level = ""
        current_bonus = user[upgrade][0]
        next_bonus = increment*(quantity+1)
  
        if "gold" in upgrade_name[1]:
          level = user["upgrade_gold_transmutation"][1]
          percent = 1
          i=0
          while i < level:
            percent += percent*.43
            i+=1
          percent = round(percent,1)
          next_level = f"\nNext Level: **+ {percent}%** :lock: Play 15 more games to unlock the next level!\n\n***IMPORTANT:** For this upgrade to work, make sure you have `Display current activity as a status message` enabled in User Settings > Activity Status*"
          embed.add_field(name = "Stats", value = f"Current Level: **+ {current_bonus}%**{next_level}")
          #free name change to set up your profile.
          user["upgrade_change_lol"][1] += 1
          await util.use(ctx,"change")
          await util.save_user_data(user_dict)
        elif "streak" in upgrade_name[1]:
          next_level = f"\nNext Level: **+ {next_bonus+current_bonus}0%** :lock: ${price*2:,}"
          embed.add_field(name = "Stats", value = f"Current Level: **+ {current_bonus}0%**{next_level}")
        elif "cooldown" in upgrade_name[1]:
          next_level = f"\nNext Level: **+ {100 - 100*.95**(quantity+1)}%** :lock: ${price*2:,}"
          embed.add_field(name = "Stats", value = f"Current Level: **+ {100 - 100*.95**quantity}%**{next_level}")
        else:
          next_level = f"\nNext Level: **+ ${next_bonus+current_bonus:,}** :lock: ${price*2:,}"
          embed.add_field(name = "Stats", value = f"Current Level: **+ ${current_bonus:,}**{next_level}")
      
      embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Purchased by {ctx.author.name}")
      await ctx.channel.send(embed=embed)


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