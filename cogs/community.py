from discord.ext import commands
import discord
import asyncio
import json
from datetime import datetime, timedelta
from backports.zoneinfo import ZoneInfo
from cogs.utility import Utility as util
from cogs.rewards import Rewards as rewards
from cogs.use import Use as use
from cogs.frontend import Frontend as front
from discord.ui import Button

class Community(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def loan(self, ctx, mention:discord.User, amount, days:int, interest:float = None):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    
    if user["rob_banned"] == True:
      await util.embed_rob_banned(ctx, "You don't have permission to perform this action.")
      return None

    if user["upgrade_banker"]["level"] <= 0:
      await util.embed_error(ctx, "You need at least **Banker Level 1** to grant loans.")
      return
    if mention == ctx.author:
      await util.embed_error(ctx, "You can't give yourself a loan!")
      return
      
    with open("upgrades.json","r") as f:
      d = json.load(f)
    amount = await util.get_value(ctx, amount, max = int( user["balance"] * ( d["upgrade_banker"]["amounts"][ str(user["upgrade_banker"]["level"]) ]*0.01)), value_error = f'You cannot loan out more than `{d["upgrade_banker"]["amounts"][ str(user["upgrade_banker"]["level"]) ]}%` of your balance!')
    infinite = False
    if days == 0:
      days = 3650
      infinite = True
    days = await util.get_value(ctx, days, name = "Days")
    if days > 365 and infinite == False:
      await util.embed_error(ctx, f"Loan repayment period cannot exceed a year.")
      return
    if interest == None:
      interest = 5
    else:
      try:
        interest = round(float(interest),2)
      except:
        await util.embed_error(ctx, f"`{interest}` is not a valid interest rate!")
        return
      if interest < 0:
        await util.embed_error(ctx, f"Interest cannot be negative!")
        return
      if interest > 100:
        await util.embed_error(ctx, f"Interest cannot exceed `100%`")
        return
        
    tz = ZoneInfo("Australia/Sydney")
    FMT = "%Y-%m-%d"
    unique_id = str(datetime.now(tz))
    deadline = (datetime.now(tz) + timedelta(days=days)).strftime(FMT)
    time_now = datetime.now(tz).strftime(FMT)
    days_str = datetime.strptime(deadline, FMT) - datetime.strptime(time_now, FMT)

    text = f"a **{str(days_str).split(' ')[0]} day** repayment period"
    expiry = f"Term Expiry: **{deadline} 12:00am AEST**"
    if days == 3650:
      text = f"an **infinite** repayment period"
      expiry = "Term Expiry: **∞**"
    embed = discord.Embed(
      title = "💵 Sloan Loan",
      description = f"{ctx.author.mention} offered {mention.mention} a **${amount:,}** loan with {text} and **{interest}%** interest.\n\nLoan Amount: **${amount:,}**\n{expiry}\nCompounding Interest: **{interest}%**\n*(Interest compounds daily at 12:00am AEST)*",
      colour = discord.Colour.green()
    )
    embed.set_footer(text=f"{ctx.author.name} has given out {user['stat_loan_quantity_given']:,} loans, totalling ${user['stat_loan_amount_given']:,}", icon_url = ctx.author.display_avatar.url)

    msg = await ctx.channel.send(embed=embed, components = [[
      Button(label=f"Accept", style="3", emoji="✅", custom_id=f"accept_loan_{unique_id}"),
      Button(label=f"Decline", style="4", emoji="⛔", custom_id=f"cancel_loan_{unique_id}")
    ]])
    
    try:
      interaction = await self.client.wait_for(
          "button_click", 
          check = lambda i: i.custom_id == f"accept_loan_{unique_id}" and i.user == mention   or   i.custom_id == f"cancel_loan_{unique_id}" and i.user == mention   or   i.custom_id == f"cancel_loan_{unique_id}" and i.user == ctx.author, 
          timeout=300
          )
    except asyncio.TimeoutError:
      embed.add_field(name="❌ Timed Out!",value=f"{ctx.author.mention}'s offer has been cancelled. {mention.mention} didn't accept in time.", inline = False)
      embed.colour = discord.Colour.red()
      await msg.edit(embed=embed, components=[])
      return
    
    if interaction.custom_id == f"cancel_loan_{unique_id}":
      title = "Declined"
      desc = f"{mention.mention} declined this offer."
      if interaction.user == ctx.author:
        title = "Cancelled"
        desc = f"{ctx.author.mention} cancelled this offer."
      embed.add_field(name=f"⛔ {title}!", value=f"{desc}", inline = False)
      embed.colour = discord.Colour.red()
      await msg.edit(embed=embed, components=[])
      return
    
    elif interaction.custom_id == f"accept_loan_{unique_id}":
      user_dict = await util.get_user_data()
      user = user_dict[str(ctx.author.id)]
      receiver = user_dict[str(mention.id)]

      if amount > int (user["balance"] * ( d["upgrade_banker"]["amounts"][ str(user["upgrade_banker"]["level"]) ] *0.01)):
        embed.add_field(name="❌ Error!",value=f"{ctx.author.mention} no longer has the required balance!", inline = False)
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, components=[])
        return
        
      user["balance"] -= amount
      receiver["balance"] += amount

      user["stat_loan_quantity_given"] += 1
      user["stat_loan_amount_given"] += amount
      receiver["stat_loan_quantity_taken"] += 1
      receiver["stat_loan_amount_taken"] += amount
      
      user["daily_cash_flow"] += amount
      user["total_cash_flow"] += amount
      receiver["daily_cash_flow"] += amount
      receiver["total_cash_flow"] += amount
        
      # Deadline,   Repay amount,   Owed user's ID,   Unique ID/Time of loan,   Base amount,   Interest rate.
      receiver["debt"].append( [deadline, amount, str(ctx.author.id), unique_id, amount, interest] )
      user["owed"].append( [deadline, amount, str(mention.id), unique_id, amount, interest] )

      await util.save_user_data(user_dict)
      
      embed.add_field(name="✅ Success!",value=f"{mention.mention} accepted the terms of {ctx.author.mention}'s loan!\n**${amount:,}** has been added to {mention.name}'s account.\nYou can check on your debt status with the `$debt` command.", inline = False)
      await msg.edit(embed=embed, components=[])



  
  
  @commands.command(aliases = ["pay", "send"])
  async def give(self, ctx, mention:discord.User, amount):
    if ctx.author.id == mention.id:
      await util.embed_error(ctx, "You can't donate to yourself!")
      return None
    user_dict = await util.get_user_data()
    sender = user_dict[str(ctx.author.id)]
    receiver = user_dict[str(mention.id)]

    # Deadline,   Repay amount (int),   Owed user's ID (str),   Unique ID/Time of loan,   Base amount,   Interest rate.
    owed_users = []
    amount_owed = 0
    for debt in sender["debt"]:
      owed_users.append(debt[2])
      if debt[2] == str(mention.id):
        amount_owed += debt[1]
    if sender["rob_banned"] == True and str(mention.id) not in owed_users:
      await util.embed_rob_banned(ctx, "You can only send Sloans to pay off debt.")
      return None
    
    if amount == "debt":
      #Convert the amount to a str temporarily to be processed by get_value
      if amount_owed > sender["balance"]:
        amount = str(sender["balance"])
      else:
        amount = str(amount_owed)
    
    amount = await util.get_value(ctx, amount, max = sender["balance"])
    
    sender["balance"] -= amount
    sender["daily_cash_flow"] += amount
    sender["total_cash_flow"] += amount
    sender["stat_give_loss"] -= amount
    sender["stat_give_quantity_sent"] += 1
    receiver["balance"] += amount
    receiver["daily_cash_flow"] += amount
    receiver["total_cash_flow"] += amount
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
    
    # Debt check.
    user_dict, dp_field, footer = await Community.pay_debt(ctx, user_dict, amount, mention)
    
    # Gambling Addict check.
    user_dict, ga_embed = await rewards.gambling_addict_passive(ctx, ctx.author, user_dict)

    await util.save_user_data(user_dict)
  
    embed = discord.Embed(
    colour = (discord.Colour.green()),
    title = ":incoming_envelope: Transaction",
    description = f"{ctx.author.name} sent {mention.name} **${amount:,}** Sloans!\n{ctx.author.name}'s new balance is ${sender['balance']:,}.\n{mention.name}'s new balance is ${receiver['balance']:,}.")
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"{ctx.author.name} has sent ${-sender['stat_give_loss']:,} total")
    if dp_field != None:
      eval(dp_field)
      eval(footer)
    await ctx.channel.send(embed=embed)
    # Gambling Addict embed.
    if ga_embed != None:
      await ctx.channel.send(embed=ga_embed)




  
  
  async def pay_debt(ctx, user_dict:dict, a:int, mention):
    debts = user_dict[str(ctx.author.id)]["debt"]
    owed = user_dict[str(mention.id)]["owed"]
    finished = []
    contributed = False
    embed = None
    footer = None
    paid_back = 0
    debts.sort()
    
    FMT = "%Y-%m-%d"
    tz = ZoneInfo("Australia/Sydney")
    time_now = datetime.now(tz).strftime(FMT)
    
    for i in range(len(debts)):
      if str(mention.id) == debts[i][2]:
        contributed = True
        # If a debt is entirely paid off.
        if a >= debts[i][1]:
          r = a - debts[i][1]
          a = r
          unique_id = debts[i][3]
          finished.append(unique_id)
          
          # Stat stuff.
          paid_back += debts[i][1]
          user_dict[str(ctx.author.id)]["stat_loan_quantity_paid"] += 1
          user_dict[str(mention.id)]["stat_loan_quantity_returned"] += 1
  
          # If loan was repaid late.
          if datetime.strptime(debts[i][0], FMT) < datetime.strptime(time_now, FMT):
            user_dict[str(ctx.author.id)]["stat_loan_quantity_paid_late"] += 1
          # How many days late/early was the loan paid back.
          days = datetime.strptime(time_now, FMT) - datetime.strptime(debts[i][0], FMT)
          if str(days) == "0:00:00":
            user_dict[str(ctx.author.id)]["average_loan_lateness"].append(0)
          else:
            user_dict[str(ctx.author.id)]["average_loan_lateness"].append(int(str(days).split(' day')[0]))
          # How many days did it take to pay the loan back.
          days = datetime.strptime(time_now, FMT) - datetime.strptime(debts[i][3].split(" ")[0], FMT)
          if str(days) == "0:00:00":
            user_dict[str(ctx.author.id)]["average_loan_repay_time"].append(0)
            if "steal" in debts[i][3]:
              user_dict[str(mention.id)]["stat_steal_victim_profit"] += debts[i][4]
              user_dict[str(ctx.author.id)]["stat_steal_loss"] -= debts[i][4]
            elif "mine" in debts[i][3]:
              user_dict[str(ctx.author.id)]["stat_mine_loss"] -= debts[i][4]
              
          else:
            user_dict[str(ctx.author.id)]["average_loan_repay_time"].append(int(str(days).split(' day')[0]))
            # Calculates the profit from this loan.
            loan_profit = debts[i][4]
            for x in range(int(str(days).split(' day')[0])):
              if loan_profit < debts[i][4]*2:
                loan_profit += int(loan_profit*(debts[i][5]*0.01))
            if "steal" in debts[i][3]:
              user_dict[str(mention.id)]["stat_steal_victim_profit"] += loan_profit
              user_dict[str(ctx.author.id)]["stat_steal_loss"] -= loan_profit
            elif "mine" in debts[i][3]:
              user_dict[str(ctx.author.id)]["stat_mine_loss"] -= loan_profit
            else:
              user_dict[str(mention.id)]["stat_loan_profit"] += loan_profit - debts[i][4]
          # Rob Check
          if str(mention.id) == "906087821373239316":
            user_dict[str(ctx.author.id)]["upgrade_loan"]["level"] = 0
        
        # If a debt is partially paid off.
        else:
          paid_back += a
          debts[i][1]-=a
          # Updating the owed amount for the loaner.
          for o in owed:
            # If IDs match.
            if o[3] == debts[i][3]:
              o[1] -= a
          a=0
    user_dict[str(ctx.author.id)]["stat_loan_amount_paid"] += paid_back
    user_dict[str(mention.id)]["stat_loan_amount_returned"] += paid_back

    # Removing the paid debt(s) for both parties.
    # There has to be a cleaner way to do this.
    debts_paid = 0
    if finished:
      debt_remove = []
      owed_remove = []
      for id in finished:
        for d in debts:
          if id in d:
            debt_remove.append(d)
        for o in owed:
          if id in o:
            owed_remove.append(o)
      for f in debt_remove:
        debts.remove(f)
        debts_paid += 1
      for f in owed_remove:
        owed.remove(f)

    # Unbans the user if there are no overdue debts.
    # This could probably be included in the first loop but this is fine for now.
    overdue = 0
    remaining = 0
    for d in user_dict[str(ctx.author.id)]["debt"]:
      if datetime.strptime(d[0], FMT) < datetime.strptime(time_now, FMT):
        overdue += 1
      if d[2] == str(mention.id):
        remaining += d[1]
    if overdue <= 0:
      user_dict[str(ctx.author.id)]["rob_banned"] = False
    
    if remaining > 0:
      remaining = f"**${remaining:,}** remaining."
    else:
      remaining = ""
    if contributed == True:
      loans_repaid = user_dict[str(ctx.author.id)]["stat_loan_quantity_paid"]
      amount_repaid = user_dict[str(ctx.author.id)]["stat_loan_amount_paid"]
      embed = f"embed.add_field(name ='🏦 Debt',value = '{ctx.author.name} paid **${paid_back:,}** back to {mention.name} and wrote off **{debts_paid:,}** debts! {remaining}')"
      footer = f"embed.set_footer(icon_url = ctx.author.display_avatar.url, text = '{ctx.author.name} has paid back {loans_repaid:,} debts, totalling ${amount_repaid:,} Sloans.')"
    
    return user_dict, embed, footer



  
  @commands.command(aliases = ["purchase"])
  async def buy(self, ctx, *upgrade):
    if len(upgrade) <= 0:
      await front.shop(self, ctx)
      return
      
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    if user["rob_banned"] == True:
      await util.embed_rob_banned(ctx, "You don't have permission to perform this action.")
      return
    
    rob = user_dict[str(906087821373239316)]
    upgrade, quantity, upgrade_name = await util.get_upgrade(ctx,user,*upgrade)

    if upgrade_name == "Loan":
      if quantity == "all":
        quantity = 20000
      amount = quantity
      quantity = 1
      if amount < 100:
        await util.embed_error(ctx, "Loan must be at least **$100**.")
        return
      elif amount > 20000:
        await util.embed_error(ctx, "Loan cannot exceed **$20,000**.")
        return
    
    if quantity == "all":
      quantity = int(user["balance"] / user[upgrade]["price"])
      if quantity == 0:
        quantity = 1


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
        price = upgrade_data["prices"][str( level )]
      
      #Generates the price for the restore upgrade.
      if upgrade_name == "Restore":
        streak = user["stat_highest_daily_streak"]
        percent = user["upgrade_streak"]["amount"]
        amount = streak*(streak+1)/2 * 10  +  streak*(streak+1)/2 * 10 * percent*0.01
        price = await util.round_number(amount+amount*.25, 10)

      elif upgrade_name == "Mystery Box":
        user["stat_mystery_box_loss"] -= user["upgrade_mystery_box"]["price"]
      
      elif upgrade_name == "Banker":
        if len(user["weekly_cash_flow"]) < 7:
          await util.embed_error(ctx,f"Banker will be available for you to purchase in {7 - len(user['weekly_cash_flow'])} days.")
          return

        min_cf = upgrade_data["prices"][str( level )]
        if sum(user["12_week_average_cash_flow"]) < min_cf*len(user["12_week_average_cash_flow"]):
          days_this_week = user['day_counter']%7
          cash_flow_this_week = 0
          for i in range(days_this_week):
            i+=1
            cash_flow_this_week += user["weekly_cash_flow"][len(user["weekly_cash_flow"])-i][1]
          cash_flow_this_week += user["daily_cash_flow"]
          await util.embed_error(ctx,f"You need to transact **${(min_cf + min_cf*len(user['12_week_average_cash_flow']) - sum(user['12_week_average_cash_flow'])) - cash_flow_this_week:,}** more this week ({7 - days_this_week} days) to reach the minimum cash flow to purchase this upgrade!")
          return
          
        price = int( await util.round_number( sum(user["12_week_average_cash_flow"]) / len(user["12_week_average_cash_flow"]) ,1000) * 0.1)
    
      if price > user["balance"]:
        await util.embed_error(ctx,f"You can't afford **{quantity_string}{upgrade_name}**!")
        return
      elif level >= max_level:
        if upgrade_name == "Loan":
          await util.embed_error(ctx,f"You must repay your outstanding debt to Rob before taking out another loan!")
          return
        await util.embed_error(ctx,f"{upgrade_name} is max level!")
        return
      
      user["balance"] -= price
      user["daily_cash_flow"] += price
      user["total_cash_flow"] += price
      rob["balance"] += price
      rob["daily_cash_flow"] += price
      rob["total_cash_flow"] += price
      user["stat_upgrade_loss"] -= price
      #Sums 1 to the level.
      user[upgrade]["level"] +=1
      level = user[upgrade]["level"]
      #Increase amount & price.
      consumable = ""
      level_msg = ""
      if single_use:
        consumable = f" \n\n{upgrade_name} is a single-use, non-expiring item.\nTo activate this item, type `$use {upgrade_name.lower()}`\n\n***TIP**: You can hide your activity by doing this command in my DMs!*"
        if upgrade_name == "Gambling Addict":
          consumable = ""
      else:
        user[upgrade]["amount"] = upgrade_data["amounts"][str( level )]
        user[upgrade]["price"] = upgrade_data["prices"][str( level )]
        level_msg = f" Level {level}"
      
      if upgrade_name == "Restore":
        user[upgrade]["amount"] = user["stat_highest_daily_streak"]
      elif upgrade_name == "Loan":
        tz = ZoneInfo("Australia/Sydney")
        unique_id = str(datetime.now(tz))
        FMT = "%Y-%m-%d"
        deadline = (datetime.now(tz) + timedelta(days=14)).strftime(FMT)
        user["balance"] += amount
        user["daily_cash_flow"] += amount
        user["total_cash_flow"] += amount
        rob["balance"] -= amount
        rob["daily_cash_flow"] += amount
        rob["total_cash_flow"] += amount
        # Deadline,   Repay amount,   Owed user's ID,   Unique ID/Time of loan,   Base amount,   Interest rate.
        user["debt"].append( [deadline, int(amount+amount*0.05), str(906087821373239316), unique_id, amount+amount*0.05, 5.0] )
        rob["owed"].append( [deadline, int(amount+amount*0.05), str(ctx.author.id), unique_id, amount+amount*0.05, 5.0] )
        user["stat_loan_quantity_taken"] += 1
        user["stat_loan_amount_taken"] += amount
        rob["stat_loan_quantity_given"] += 1
        rob["stat_loan_amount_given"] += amount

    # Gambling Addict check.
    user_dict, ga_embed = await rewards.gambling_addict_passive(ctx, ctx.author, user_dict)
    
    await util.save_user_data(user_dict)
    
    desc = f"You bought **{quantity_string}{emoji} {upgrade_name}{level_msg}** for **-${price*quantity:,}**!\nYou have ${user['balance']:,} remaining.{consumable}"
    title = f"🛍 Purchase Successful!"
    if upgrade_name == "Loan":
      title = "🏦 Loan Successful!"
      desc = f"You took out a **${amount:,}** loan! Your new balance is ${user['balance']:,}.\nThis loan must be paid back by **{deadline}**.\nTo pay off a loan, use the `$give` command."
    embed = discord.Embed(
    colour = discord.Colour.green(),
    title = title,
    description = desc)
    
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
        await util.save_user_data(user_dict)
        await use.use(self, ctx, "change")
      elif "streak" in upgrade_name.lower() or "cooldown" in upgrade_name.lower():
        next_level = f"\nNext Level: **+ {next_amount}%** :lock: ${next_price:,}"
        embed.add_field(name = "Stats", value = f"Current Level: **+ {current_amount}%**{next_level}")
      else:
        next_level = f"\nNext Level: **+ ${next_amount:,}** :lock: ${next_price:,}"
        embed.add_field(name = "Stats", value = f"Current Level: **+ ${current_amount:,}**{next_level}")
    
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Purchased by {ctx.author.name}")
    await ctx.channel.send(embed=embed)
    # Gambling Addict embed.
    if ga_embed != None:
      await ctx.channel.send(embed=ga_embed)

  
  #@commands.command(aliases = ["pfp", "pic", "picture"])
  #async def avatar(self, ctx, mention:discord.User = None):
    #account = mention or ctx.author
    #user_dict = await util.get_user_data()
    #user = user_dict[str(account.id)]
    #await ctx.channel.send(user.display_avatar.url)

    
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


async def setup(client):
  await client.add_cog(Community(client))