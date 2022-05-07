from discord.ext import commands
import discord
import asyncio
import random
import re
from cogs.utility import Utility as util
import strings
import time

class Gambling(commands.Cog):
  def __init__(self, client:commands.Bot):
    self.client = client


  paulers = set()
  consecutive = 1
  last_side = ""
  @commands.command(aliases = ["flips","slots","f"])
  async def flip(self, ctx, amount, side:str = None):
    bot_commands = await self.client.fetch_channel(334046255384887296)
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(906087821373239316)]
    wrong_room = None
    paul = False
    win = False
    paul_bonus = 0

    amount = await util.get_value(ctx,amount,user["balance"])
  
    if amount == user["balance"]:
      paul = True
    else:
      if ctx.author in Gambling.paulers:
        Gambling.paulers.remove(ctx.author)
    
    #Caps the max flip
    max_alert = ""
    max_bet = 100000
    if amount > max_bet:
      amount = max_bet
      max_alert = f"Your bet was capped at {max_bet:,}"

    #Assigns the side
    if side != None:
      if side.lower().startswith("h"):
        bet = "heads"
      elif side.lower().startswith("t"):
        bet = "tails"
      else:
        bet = random.choice(["heads","tails"])
    else:
      bet = random.choice(["heads","tails"])
    
    flip = random.choice(["heads","tails"])
    
    if flip == bet:
      win = True
      winner = user
      loser = rob
      emoji = "money_with_wings"
      outcome = "won"
      luck = ":four_leaf_clover: Lucky!"
      message = "sloans have been added to your account!"
      outcome_colour = discord.Colour.green()
    else:
      if ctx.author in Gambling.paulers:
        Gambling.paulers.remove(ctx.author)
      winner = rob
      loser = user
      emoji = "boom"
      outcome = "lost"
      luck = ":black_cat: Unlucky!"
      message = "sloans have been removed from your account!"
      outcome_colour = discord.Colour.red()
    
    if ctx.author in Gambling.paulers:
      paul_bonus = round(amount*0.25)
    if ctx.channel != bot_commands and win == True:
      penalty = round(amount*0.25)
      amount -= penalty
      wrong_room = True
      paul = False
    if paul == True and win == True:
      Gambling.paulers.add(ctx.author)
      
    winner["balance"] += (amount + paul_bonus)
    loser["balance"] -= (amount + paul_bonus)

    winner["stat_flip_profit"] += amount
    winner["stat_flip_win_streak"] += 1
    if winner["stat_flip_win_streak"] > winner["stat_highest_flip_win_streak"]:
      winner["stat_highest_flip_win_streak"] = winner["stat_flip_win_streak"]

    loser["stat_flip_loss"] -= amount
    loser["stat_flip_win_streak"] = 0
      
    if amount > winner["stat_highest_flip"]:
      winner["stat_highest_flip"] = amount
    if amount > loser["stat_highest_flip"]:
      loser["stat_highest_flip"] = amount
  
    if winner["balance"] > winner["stat_highest_balance"]:
      winner["stat_highest_balance"] = winner["balance"]
    
    winner["stat_flip_quantity"] += 1
    winner["stat_flip_victory"] += 1
    loser["stat_flip_quantity"] += 1
    loser["stat_flip_defeat"] += 1
    
    await util.save_user_data(user_dict)
    
    balance = user["balance"]
    if bet == "heads":
      rob_bet = "tails"
    else:
      rob_bet = "heads"

    if flip == "tails":
      coin = "https://cdn.discordapp.com/attachments/894744339794780220/938857632712786010/sloan_tails_v6.png"
    else:
      coin = "https://cdn.discordapp.com/attachments/894744339794780220/938857632389799986/sloan_heads_v3.png"
    
    if Gambling.last_side == flip:
      Gambling.consecutive += 1
    else:
      Gambling.consecutive = 1
    Gambling.last_side = flip
    
    embed = discord.Embed(
    colour = outcome_colour,
    title = f":{emoji}: Flip | {flip.capitalize()}",
    icon_url = ctx.author.avatar_url,)
    embed.add_field(name = f"You {outcome}!", value = f"**${amount + paul_bonus:,}** {message}\nYour new balance is ${balance:,}.", inline = True)
    if win == True and paul == True:
      paul_text = ":star: Incoming Paul Bonus!"
      if paul_bonus > 0:
        paul_text = f":star2: Paul Bonus! +${paul_bonus:,}"
      embed.add_field(name = f"{paul_text}", value = f"Go all in again for **+${round(balance*.25):,}** extra!", inline = False)
    if wrong_room == True:
      embed.add_field(name = ":rotating_light: Wrong Channel -25%!", value = f"**${penalty:,}** has been subtracted from your win and any Paul bonuses have been cancelled.\nTry using {bot_commands.mention}!", inline = False)
    if Gambling.consecutive >= 3:
      val = 0.5**Gambling.consecutive*100
      odds_string = str(f"{val:.20f}")
      zeros = len(re.search('\d+\.(0*)', odds_string).group(1))
      odds = f"{val:.{zeros+2}f}"
      embed.add_field(name = luck, value = f"It's been {flip} **{Gambling.consecutive}** times in a row, the odds of that are **{odds}%**!", inline = False)
    if side == None:
      embed.add_field(name = f"CyberRob chose {rob_bet}.",value = "Since you didn't pick a side Rob chose first.", inline = False)
    embed.set_thumbnail(url = coin)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"{ctx.author.name} vs CyberRob {max_alert}")
    await ctx.channel.send(embed=embed)
    
    #bonus rob reaction for big wins
    if outcome == "won" and amount >=10000:
      async with ctx.channel.typing():
        await asyncio.sleep(2)
        await ctx.channel.send(random.choice(strings.loss_reactions))






  active = False
  message = None
  pot = 0
  activity_log = ["","","",""]
  participants = {}
  time_remaining = 120
  @commands.command(aliases = ["jack","pot","j","jake","jp"])
  async def jackpot(self, ctx, amount):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    amount = await util.get_value(ctx,amount,user["balance"])
    max_time = 120
    
    #For starting the game.
    if Gambling.active == False:
      Gambling.pot = amount
      Gambling.activity_log.pop(0)
      Gambling.activity_log.append(f"**{ctx.author.name}** started the jackpot at **${amount:,}**")
      Gambling.participants.update( {ctx.author.id:{"account":ctx.author,"amount":amount}} )
      Gambling.message = await self.create_jackpot(ctx, Gambling.activity_log, Gambling.participants)
      user["balance"] -= amount
      await util.save_user_data(user_dict)
      Gambling.active = True
      status = await self.wait_for_players(ctx)
      if status == False:
        user_dict = await util.get_user_data()
        user = user_dict[str(ctx.author.id)]
        user["balance"] += Gambling.pot
        await util.save_user_data(user_dict)
        await self.reset_jackpot()
        return
      await self.start_timer()
      await self.payout()
      await self.reset_jackpot()
    
    #For adding to the game.
    else:
      old_pot = Gambling.pot
      Gambling.pot += amount
      user["balance"] -= amount
      await util.save_user_data(user_dict)

      #If a new user has entered the pot, creates a dictionary entry for them.
      #Otherwise the amount is summed to the already existing entry.
      new_user = False
      if ctx.author.id in Gambling.participants:
        Gambling.participants[ctx.author.id]["amount"] += amount
        action = "re-entered"
      else:
        action = "entered"
        new_user = True
      if new_user == True:
        Gambling.participants.update( {ctx.author.id:{"account":ctx.author,"amount":amount}} )
      
      #handles the activity log.
      Gambling.activity_log.pop(0)
      Gambling.activity_log.append(f"**{ctx.author.name}** {action} the pot with **${amount:,}**")
      
      #Increases the time by 50% of the percentage of the amount of the pot, capped at 100% of the pot
      #e.g. doubling the pot increases the timer by 60 seconds
      percent = amount / old_pot * 0.5
      if percent > 0.5:
        percent = 0.5
      elif percent < 0.05:
        percent = 0
      old_time = Gambling.time_remaining
      Gambling.time_remaining += round(max_time * percent)
      if Gambling.time_remaining > max_time:
        Gambling.time_remaining = max_time
      time = Gambling.time_remaining - old_time
      if time != 0:
        Gambling.activity_log.pop(0)
        Gambling.activity_log.append(f"*Countdown extended by **{Gambling.time_remaining - old_time}** seconds*")
      
      await self.edit_jackpot()

  
  
  async def wait_for_players(self, ctx):
    try:
      input = await self.client.wait_for("message", check = lambda m: len(Gambling.participants) > 1 or m.author == ctx.author and m.content.lower() == "$cancel", timeout=300)
    except asyncio.TimeoutError:
      await util.embed_message(ctx,":no_entry:","Cancelled",f"No one joined your jackpot!")
      return False
    if input.content.lower() == "$cancel":
        await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled jackpot!")
        return False
      
  async def start_timer(self):
    while Gambling.time_remaining >= 1:
      await asyncio.sleep(1)
      Gambling.time_remaining -= 1
      await self.edit_jackpot()

  async def payout(self):
    players = []
    odds = []
    for player in Gambling.participants:
      account = Gambling.participants[player]["account"]
      amount = Gambling.participants[player]["amount"]
      pot = Gambling.pot
      chance = amount / pot * 100
      players.append(account)
      odds.append(chance)
    winner = random.choices(players, odds)[0]

    amount = Gambling.participants[winner.id]["amount"]
    chance = amount / pot * 100

    user_dict = await util.get_user_data()
    #winner stats
    user = user_dict[str(winner.id)]
    user["balance"] += pot
    user["stat_jackpot_profit"] += pot
    user["stat_jackpot_quantity"] += 1
    user["stat_jackpot_victory"] += 1
    if user["stat_jackpot_highest_win"] < pot:
      user["stat_jackpot_highest_win"] = pot
    if user["stat_jackpot_lowest_odds_victory"] > chance:
      user["stat_jackpot_lowest_odds_victory"] = chance

    #loser stats
    for player in Gambling.participants:
      if player != winner.id:
        user_dict[str(player)]["stat_jackpot_loss"] -= Gambling.participants[player]["amount"]
        user_dict[str(player)]["stat_jackpot_defeat"] += 1
        user_dict[str(player)]["stat_jackpot_quantity"] += 1
  
    
    odds_string = str(f"{chance:.20f}")
    zeros = len(re.search('\d+\.(0*)', odds_string).group(1))
    extra_zeros = 2
    if zeros == 20:
      zeros = 0
      extra_zeros = 0
    odds = f"{chance:.{zeros+extra_zeros}f}"
    winner = {"name":winner.name,"odds":odds}
    await self.edit_jackpot(winner)
    await util.save_user_data(user_dict)
  
  async def create_jackpot(self, ctx, activity_log:list, participants:dict):
    embed = discord.Embed(
    colour = discord.Colour.orange(),
    title = f":honey_pot: Jackpot | ${Gambling.pot:,}",
    description = f"**Waiting for players...**\n\nTo enter the pot type `$jackpot` followed by the amount of sloans you wish to bet. You can add more sloans to your bet at any time by repeating the command!"
    )
    embed.add_field(name = "Activity", value = f"{activity_log[0]}\n{activity_log[1]}\n{activity_log[2]}\n{activity_log[3]}\n", inline = True)
    
    players_string = ""
    data = []
    for player in participants:
      name = Gambling.participants[player]["account"].name
      amount = Gambling.participants[player]["amount"]
      odds = round((amount / Gambling.pot) * 100, 2)
      user = (amount,odds,name)
      data.append(user)
    
    data.sort(reverse=True)
    for i in range(len(data)):
      players_string += f"*{data[i][1]}% | {data[i][2]} | ${data[i][0]:,}*\n"
      
    embed.add_field(name = "Players", value = players_string, inline = True)
    message = await ctx.channel.send(embed=embed)
    return message

  
  async def edit_jackpot(self, winner = None):
    embed = discord.Embed()
    if len(Gambling.participants) == 1:
      embed.title = f":honey_pot: Jackpot | ${Gambling.pot:,}"
      embed.description = f"**Waiting for players...**\n\nTo enter the pot type `$jackpot` followed by the amount of sloans you wish to bet. You can add more sloans to your bet at any time by repeating the command!" 
      embed.colour = discord.Colour.orange()
    else:
      embed.title = f":moneybag: Jackpot | ${Gambling.pot:,}"
      embed.description = f"{time.strftime('%M:%S', time.gmtime(Gambling.time_remaining))}"
      embed.colour = discord.Colour.green()
    activity_log = Gambling.activity_log
    embed.add_field(name = "Activity", value = f"{activity_log[0]}\n{activity_log[1]}\n{activity_log[2]}\n{activity_log[3]}\n", inline = True)
    
    players_string = ""
    data = []
    for player in Gambling.participants:
      name = Gambling.participants[player]["account"].name
      amount = Gambling.participants[player]["amount"]
      odds = round((amount / Gambling.pot) * 100, 2)
      user = (amount,odds,name)
      data.append(user)
    
    data.sort(reverse=True)
    for i in range(len(data)):
      players_string += f"*{data[i][1]}% | {data[i][2]} | ${data[i][0]:,}*\n"
      
    embed.add_field(name = "Players", value = players_string, inline = True)

    if winner != None:
      embed.colour = discord.Colour.magenta()
      embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      embed.add_field(name = f":money_with_wings: {winner['name'].upper()} WINS!", value = f"**{winner['name']}** won the pot worth **${Gambling.pot:,}** with a **{winner['odds']}%** chance!", inline = True)
    await Gambling.message.edit(embed=embed)

 
  async def reset_jackpot(self):
    Gambling.active = False
    Gambling.message = None
    Gambling.pot = 0
    Gambling.activity_log = ["","","",""]
    Gambling.participants = {}
    Gambling.time_remaining = 120
      
      
     
    

def setup(client:commands.Bot):
  client.add_cog(Gambling(client))