from discord.ext import commands
import discord
import asyncio
import random
import re
import os
import pyimgur
from datetime import datetime, timedelta
from cogs.utility import Utility as util
from cogs.rewards import Rewards as rewards
from cogs.frontend import Frontend as front
from PIL import Image, ImageDraw, ImageFont
import time
import json
from backports.zoneinfo import ZoneInfo
from typing import Union
import requests
import multiprocessing

imgbb_key = os.environ['imgbb_key']
client_id = os.environ['Imgur_CLIENT_ID']

class Gambling(commands.Cog):
  def __init__(self, client:commands.Bot):
    self.client = client

  class Roulette_Buttons(discord.ui.View):
    def __init__(self):
      super().__init__()
      
    @discord.ui.button(label=f"Green 36x", style=discord.ButtonStyle.green)
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Green())

    @discord.ui.button(label=f"Red 2x", style=discord.ButtonStyle.red)
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Red())

    @discord.ui.button(label=f"Black 2x", style=discord.ButtonStyle.grey)
    async def black(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Black())
    
    @discord.ui.button(label=f"Odd 2x", style=discord.ButtonStyle.blurple)
    async def odd(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Odd())
  
    @discord.ui.button(label=f"Even 2x", style=discord.ButtonStyle.blurple)
    async def even(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Even())

    @discord.ui.button(label=f"Straight Up 36x", style=discord.ButtonStyle.blurple)
    async def straight_up(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Straight_Up())

    @discord.ui.button(label=f"Split 18x", style=discord.ButtonStyle.blurple)
    async def split(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Split())
      
    @discord.ui.button(label=f"Street 12x", style=discord.ButtonStyle.blurple)
    async def street(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Street())
      
    @discord.ui.button(label=f"Basket 9x", style=discord.ButtonStyle.blurple)
    async def basket(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Basket())
    
    @discord.ui.button(label=f"Dozen 3x", style=discord.ButtonStyle.blurple)
    async def dozen(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(Gambling.Roulette_Dozen())
  
  class Roulette_Green(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "green"
    bet = True
    mult = 36
    text_input = discord.ui.TextInput(label="Enter Bet Amount")
    input_type = "amount"
    text_input.max_length = 7
    text_input.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input.value, self.input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, self.bet, amount, self.mult)

  class Roulette_Red(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "red"
    bet = True
    mult = 2
    text_input = discord.ui.TextInput(label="Enter Bet Amount")
    input_type = "amount"
    text_input.max_length = 7
    text_input.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input.value, self.input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, self.bet, amount, self.mult)

  class Roulette_Black(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "black"
    bet = True
    mult = 2
    text_input = discord.ui.TextInput(label="Enter Bet Amount")
    input_type = "amount"
    text_input.max_length = 7
    text_input.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input.value, self.input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, self.bet, amount, self.mult)

  class Roulette_Odd(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "odd"
    bet = True
    mult = 2
    text_input = discord.ui.TextInput(label="Enter Bet Amount")
    input_type = "amount"
    text_input.max_length = 7
    text_input.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input.value, self.input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, self.bet, amount, self.mult)

  class Roulette_Even(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "even"
    bet = True
    mult = 2
    text_input = discord.ui.TextInput(label="Enter Bet Amount")
    input_type = "amount"
    text_input.max_length = 7
    text_input.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input.value, self.input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, self.bet, amount, self.mult)

  class Roulette_Straight_Up(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "number"
    mult = 36
    min = 1
    max = 36
    text_input_number = discord.ui.TextInput(label="Choose Number (1-36)")
    first_input_type = "single_number"
    text_input_number.max_length = 2
    text_input_number.min_length = 1
    text_input_number.placeholder = "e.g. 3"
    text_input_amount = discord.ui.TextInput(label="Enter Bet Amount")
    second_input_type = "amount"
    text_input_amount.max_length = 7
    text_input_amount.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      bet = await Gambling.process_roulette_modal_input(interaction, self.text_input_number.value, self.first_input_type, self.min, self.max)
      if bet == None:
        return
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input_amount.value, self.second_input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, bet, amount, self.mult)

  class Roulette_Split(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "split"
    mult = 18
    min = 1
    max = 36
    text_input_number = discord.ui.TextInput(label="Choose Number (0-36)")
    first_input_type = "single_number"
    text_input_number.max_length = 2
    text_input_number.min_length = 1
    text_input_number.placeholder = "e.g. 12"
    text_input_amount = discord.ui.TextInput(label="Enter Bet Amount")
    second_input_type = "amount"
    text_input_amount.max_length = 7
    text_input_amount.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      bet = await Gambling.process_roulette_modal_input(interaction, self.text_input_number.value, self.first_input_type, self.min, self.max)
      if bet == None:
        return
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input_amount.value, self.second_input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, bet, amount, self.mult)

  class Roulette_Street(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "street"
    mult = 12
    text_input_number = discord.ui.TextInput(label="Enter Three Consecutive Numbers")
    first_input_type = "multi_number"
    text_input_number.max_length = 8
    text_input_number.min_length = 5
    text_input_number.placeholder = "e.g. 4,5,6"
    text_input_amount = discord.ui.TextInput(label="Enter Bet Amount")
    second_input_type = "amount"
    text_input_amount.max_length = 7
    text_input_amount.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      bet = await Gambling.process_roulette_modal_input(interaction, self.text_input_number.value, self.first_input_type)
      if bet == None:
        return
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input_amount.value, self.second_input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, bet, amount, self.mult)

  class Roulette_Basket(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "basket"
    bet = True
    mult = 9
    text_input = discord.ui.TextInput(label="Enter Bet Amount")
    input_type = "amount"
    text_input.max_length = 7
    text_input.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input.value, self.input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, self.bet, amount, self.mult)

  class Roulette_Dozen(discord.ui.Modal, title='Enter Roulette'):
    bet_type = "dozen"
    mult = 3
    min = 1
    max = 3
    text_input_number = discord.ui.TextInput(label="Choose Number (1-3)")
    first_input_type = "single_number"
    text_input_number.max_length = 1
    text_input_number.min_length = 1
    text_input_number.placeholder = "e.g. 1"
    text_input_amount = discord.ui.TextInput(label="Enter Bet Amount")
    second_input_type = "amount"
    text_input_amount.max_length = 7
    text_input_amount.min_length = 1
    async def on_submit(self, interaction:discord.Interaction):
      bet = await Gambling.process_roulette_modal_input(interaction, self.text_input_number.value, self.first_input_type, self.min, self.max)
      if bet == None:
        return
      amount = await Gambling.process_roulette_modal_input(interaction, self.text_input_amount.value, self.second_input_type)
      if amount == None:
        return
      await Gambling.add_roulette_bet(interaction, self.bet_type, bet, amount, self.mult)

  class Roulette():
    max_bet = 1_000_000
    spin_timeout = 5
    numbers = (0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26)
    
    def __init__(self, round_time):
      self.round_time = round_time
      self.spinning = False
      self.need_update = False
      self.spin_history = []
      self.spins = 0
      self.bets = {}
      self.msg = None
      self.embed = None
      self.view = None
      self.next_spin = datetime.now() + timedelta(seconds = round_time)
      self.last_activity = 0
      self.last_update = datetime.now()
      self.number = None
      self.poster_url = "https://cdn.discordapp.com/attachments/984028243202039818/1026276389395107951/roblette_poster.jpg"
      self.spin_animation_url = None

    help = "**Green** *36x*\n - The colour green.\n - "
    help += "**Straight Up** *x36*\n - A single number.\n - "
    help += "**Split** *18x*\n - Two numbers parallel to a number.\n - "
    help += "**Street** *12x*\n - Three consecutive vertical numbers.\n - "
    help += "**Basket** *9x*\n - Four numbers 0, 1, 2, 3.\n - "
    help += "**Dozen** *3x*\n - Groups of 12 numbers.\n - "
    help += "**Odd/Even** *2x*\n - Odd or even numbers.\n - "
    help += "**Red/Black** *2x*\n - The colours red or black.\n - "

    bet_types = ""
    bet_descs = ""
    fields = help.split("-")
    for i in range(len(fields)):
      if i == 0 or i % 2 == 0:
        bet_types += fields[i]
      else:
        bet_descs += fields[i]
    emojis = {
      0:"<:r_0:1024751646242258975>",
      1:"<:r_1:1024751647823507466>", 
      2:"<:r_2:1024751649455099957>",
      3:"<:r_3:1024751651145396364>",
      4:"<:r_4:1024751652554690592>",
      5:"<:r_5:1024751654521798696>",
      6:"<:r_6:1024751656220512367>",
      7:"<:r_7:1024751657822728313>", 
      8:"<:r_8:1024751659554971739>", 
      9:"<:r_9:1024751661291413636>", 
      10:"<:r_10:1024751662511968267>", 
      11:"<:r_11:1024751664516845758>", 
      12:"<:r_12:1024751666093891736>", 
      13:"<:r_13:1024751667654168647>", 
      14:"<:r_14:1024751669659041913>", 
      15:"<:r_15:1024751671781380136>", 
      16:"<:r_16:1024751673383583825>", 
      17:"<:r_17:1024751675052937299>", 
      18:"<:r_18:1024751676885835856>", 
      19:"<:r_19:1024766842784456744>",
      20:"<:r_20:1024766845061972078>",
      21:"<:r_21:1024766847066845235>",
      22:"<:r_22:1024766848769736756>", 
      23:"<:r_23:1024766850627809281>", 
      24:"<:r_24:1024766852532011129>", 
      25:"<:r_25:1024766854566260756>", 
      26:"<:r_26:1024767215377068052>", 
      27:"<:r_27:1024766856604692621>", 
      28:"<:r_28:1024766858416623656>",
      29:"<:r_29:1024751695936356362>", 
      30:"<:r_30:1024751697471492106>", 
      31:"<:r_31:1024751699333750824>", 
      32:"<:r_32:1024751701208608840>", 
      33:"<:r_33:1024751703360274563>", 
      34:"<:r_34:1024751705025421422>", 
      35:"<:r_35:1024751707177091215>", 
      36:"<:r_36:1024751708846444625>",
    }

  class Roulette_Number():
    def __init__(self, num):
      self.green = False
      self.red = False
      self.black = False
      self.odd = False
      self.even = False
      self.number = None
      self.basket = False
      self.dozen = 0
      # These instance variables don't hold any value because their outcome is decided on a per user basis.
      self.split = None
      self.street = None

      # Colours.
      if num == 0:
        self.green = True
      elif num >= 1 and num <= 10 or num >= 19 and num <= 28:
        if num % 2 == 0:
          self.black = True
        else:
          self.red = True
      elif num >= 11 and num <= 18 or num >= 29 and num <= 36:
        if num % 2 == 0:
          self.red = True
        else:
          self.black = True
      # Odd/Even.
      if num != 0:
        if num % 2 == 0:
          self.even = True
        else:
          self.odd = True
      # Number.
      self.number = num
      # Basket.
      if num in [0,1,2,3]:
        self.basket = True
      #Dozen.
      if num >= 1 and num <= 12:
        self.dozen = 1
      elif num >= 13 and num <= 24:
        self.dozen = 2
      elif num >= 25 and num <= 36:
        self.dozen = 3
    
  async def process_roulette_modal_input(interaction, raw_amount, custom_id, min = 1, max = None):
    game = Gambling.roulette_active_servers[interaction.guild]
    if game.spinning:
      await util.embed_interaction_error(interaction, f"Too late! Try again when the wheel stops spinning.")
      return None
    try:
      if custom_id == "amount":
        user_dict = await util.get_user_data()
        user = user_dict[str(interaction.user.id)]
        max = Gambling.Roulette.max_bet
        if user["balance"] < max:
          max = user["balance"]
        amount = await util.get_value_from_interaction(interaction, raw_amount, max = max)
        return amount
      elif custom_id == "single_number":
        number = await util.get_value_from_interaction(interaction, raw_amount, max = max, min = min, value_error = f"Value exceeds roulette limit! (min: {min}, max: {max})")
        return number
      elif custom_id == "multi_number":
        number = await Gambling.get_roulette_street_numbers(interaction, raw_amount)
        return number
    except Exception as e:
      print(e)
      return None

  async def get_roulette_street_numbers(interaction, value):
    numbers = []
    fields = value.split(",")
    for num in fields:
      num = await util.get_value_from_interaction(interaction, num, max = 36, min = 1, value_error = f"Value exceeds street limit! (min: 1, max: 36)")
      numbers.append(num)
    n = numbers
    #If numbers are greater than 1 apart.
    if n[1]-n[0] < -1 or n[1]-n[0] > 1  or  n[2]-n[1] < -1 or n[2]-n[1] > 1:
      await util.embed_interaction_error(interaction, f"Street bets must be consecutive e.g. 7,8,9")
      raise ValueError("Street values not consecutive.")
    if len(numbers) != len(set(numbers)):
      await util.embed_interaction_error(interaction, f"You can't use the same number twice!")
      raise ValueError("Duplicate values in Street.")
    if len(numbers) > 3 or len(numbers) < 3:
      await util.embed_interaction_error(interaction, f"Street bets must have 3 numbers.")
      raise ValueError("Street numbers out of range.")
    return numbers

  
  async def add_roulette_bet(interaction, bet_type, bet, amount, mult):
    existing = False
    game = Gambling.roulette_active_servers[interaction.guild]
    user_obj = interaction.user
    bet_type = f"{bet_type}_{bet}"
    # If user has no bets.
    if not user_obj in game.bets:
      game.bets[user_obj] = { bet_type: [bet, amount, mult, interaction] } 
    else:
      for b in game.bets[user_obj]:
        # If user has an existing identical bet.
        if bet_type == b and bet == game.bets[user_obj][bet_type][0]:
          amount = await Gambling.add_to_bet(interaction, game, bet_type, amount)
          if amount <= 0:
            return
          existing = True
          break
      # If user has an existing different bet.
      if existing == False:
        game.bets[user_obj][bet_type] = [bet, amount, mult, interaction]

    user_dict = await util.get_user_data()
    user = user_dict[str(interaction.user.id)]
    rob = user_dict[str(906087821373239316)]
    user["balance"] -= amount
    rob["balance"] += amount
    await util.save_user_data(user_dict)
    
    embed = discord.Embed(
      title = f"<:roblette:1024790477670715513> You're in!",
      description = f"You bet **${amount:,}** on **{await Gambling.get_roulette_bet_titles(game, bet_type, bet)}**!",
      colour = discord.Colour.from_rgb(34, 184, 76))
    await interaction.response.send_message(embed=embed, ephemeral = True)
    game.last_activity = 0
    game.need_update = True

  async def add_to_bet(interaction, game, bet_type, amount):
    # Maybe revisit this block when I've got some sleep. It just seems like a weird way to do it.
    base = game.bets[interaction.user][bet_type][1]
    if base + amount > game.max_bet:
      amount += max - (base + amount)
      game.bets[interaction.user][bet_type][1] += amount
    else:
      game.bets[interaction.user][bet_type][1] += amount
    if amount <= 0:
      await util.embed_interaction_error(interaction, f"You can't bet any more on **{game.bets[interaction.user][bet_type][0]}**.")
    return amount

    
  async def update_roulette_display(ctx, number = None):
    game = Gambling.roulette_active_servers[ctx.guild]
    countdown = ""
    image = game.poster_url
    if game.last_activity < game.spin_timeout:
      timestamp = discord.utils.format_dt(game.next_spin, style='R')
      countdown = f"Spinning {timestamp}\n"
    history = ""
    for i in range(len(game.spin_history)):
      history += str(game.spin_history[(len(game.spin_history)-1)-i])

    if game.spinning:
      print(game.spin_animation_url)
      image = game.spin_animation_url
      countdown = f"<a:loader:998459694635036723> Spinning...\n"
    elif number != None:
      countdown = f"{game.emojis[number.number]}\n"
      
    game.embed.description = f"{countdown}Spins: {game.spins}\n History ➧ {history}"
    game.embed.set_image(url = image)

    # Rebuilding embed from the ground up each update. This may be inefficient. A dict to embed approach may be ideal.
    game.embed.clear_fields()
    game.embed.add_field(name = "Bet Info", value = game.bet_types)
    game.embed.add_field(name = "\u200b", value = game.bet_descs)
    game.embed.add_field(name = "\u200b", value = "\u200b")
    if not game.bets:
      game.embed.add_field(name = "Bets", value = "*None*", inline = False)

    # The rest of this method is possibly the most messy and confusing code I've ever written and it's all for a nice looking frontend. The sacrifices we make.
    bets = {}
    for player in game.bets:
      for bet_type in game.bets[player]:
        bet_type_name = str(bet_type).split("_")[0]
        if bet_type_name not in bets:
          bets[bet_type_name] = []
        bets[bet_type_name].append( [game.bets[player][bet_type][1], bet_type, player, game.bets[player][bet_type][2], game.bets[player][bet_type][0], await Gambling.get_roulette_bet_titles(game, bet_type, game.bets[player][bet_type][0])] )
    for bet_list in bets:
      try:
        #I have no idea how this can trigger an error sometimes. It must be a certain bet type.
        bets[bet_list].sort(reverse = True)
      except TypeError as e:
        print(e)
        

    special_categories = ["number", "dozen", "split", "street"]
    # Normal version.
    if number == None:
      for category in bets:
        category_name = category.capitalize()
        bet_list = ""
        if category in special_categories:
          for user_bet in bets[category]:
            bet_list += f"**${user_bet[0]:,}** {user_bet[2].name} on **{user_bet[5]}**\n"
          game.embed.add_field(name = category_name, value = bet_list)
        else:
          for user_bet in bets[category]:
            bet_list += f"**${user_bet[0]:,}** {user_bet[2].name}\n"
          game.embed.add_field(name = category_name, value = bet_list)
      game = Gambling.roulette_active_servers[ctx.guild]
      try:
        await game.msg.edit(embed = game.embed, view = game.view)
      except discord.errors.NotFound as e:
        print(e)
    # Display winners version.
    else:
      for category in bets:
        category_name = category.capitalize()
        if str(number.__dict__[category]) == "True":
          category_name = f"{category_name} 👑"
        bet_list = ""
        if category in special_categories:
          for user_bet in bets[category]:
            win_flag = False
            if await Gambling.roulette_win_check(user_bet[2], game, user_bet[1], number):
              win_flag = True
            elif category == "split":
              if await Gambling.roulette_split_check(user_bet[4], number) == True:
                win_flag = True
            elif category == "street":
              if await Gambling.roulette_street_check(user_bet[4], number) == True:
                win_flag = True
            if win_flag == True:
              bet_list += f"🏆 ${user_bet[0]:,} {user_bet[2].name} on **{user_bet[5]}** **+ ${user_bet[0] * user_bet[3]:,}**\n"
            else:
              bet_list += f"**${user_bet[0]:,}** {user_bet[2].name} on **{user_bet[5]}**\n"
          game.embed.add_field(name = category_name, value = bet_list)
        else:
          for user_bet in bets[category]:
            if number.__dict__[category] == True:
              bet_list += f"${user_bet[0]:,} {user_bet[2].name} **+ ${user_bet[0] * user_bet[3]:,}**\n"
            else:
              bet_list += f"**${user_bet[0]:,}** {user_bet[2].name}\n"
          game.embed.add_field(name = category_name, value = bet_list)
          
      await game.msg.edit(embed = game.embed, view = game.view)
    
  
  async def get_roulette_bet_titles(game, bet_type, bet):
    title = str(bet_type).split("_")[0].title()
    bet_type = bet_type.split("_")[0]
    # Number.
    if bet_type == "number":
      title = bet
    # Dozen.
    elif bet_type == "dozen":
      if bet == 1:
        title = "1st Dozen"
      elif bet == 2:
        title = "2nd Dozen"
      else:
        title = "3rd Dozen"
    # Split.
    elif bet_type == "split":
      nums = Gambling.Roulette.numbers
      title = f"{ nums[(nums.index(bet) - 1) % len(nums) ] } or { nums[(nums.index(bet) + 1) % len(nums)] }"
    # Street.
    elif bet_type == "street":
      title = f"{str(bet).replace('[','').replace(']','')}"
    return title
    
  async def display_roulette(ctx, game):
    # Replace the live roulette message.
    if game.msg == None:
      # First & only time embed creation.
      view = Gambling.Roulette_Buttons()
      timestamp = discord.utils.format_dt(game.next_spin, style='R')
      embed = discord.Embed(
        title = "<:roblette:1024790477670715513> Roblette",
        description = f"Spinning {timestamp}\n Spins: {game.spins}\n History ➧ *None*",
        colour = discord.Colour.from_rgb(255, 255, 255))
      embed.set_image(url = game.poster_url)
      embed.add_field(name = "Bet Info", value = game.bet_types)
      embed.add_field(name = "\u200b", value = game.bet_descs)
      embed.add_field(name = "\u200b", value = "\u200b")
      embed.add_field(name = "Bets", value = "*None*", inline = False)
      
      game.embed = embed
      game.view = view
    else:
      await game.msg.delete()
    msg = await ctx.channel.send(embed = game.embed, view = game.view)
    game.msg = msg

  async def roulette_split_check(bet, number):
    nums = Gambling.Roulette.numbers
    num = number.number
    if bet in [ nums[(nums.index(num) - 1) % len(nums) ], nums[(nums.index(num) + 1) % len(nums)] ]:
      return True
      
  async def roulette_street_check(bet, number):
    if number.number in bet:
      return True

  async def roulette_win_check(player, game, bet_type, number):
    bet_attribute = bet_type.split("_")[0]
    for attribute in number.__dict__:
      if attribute == bet_attribute:
        if game.bets[player][bet_type][0] == number.__dict__[attribute]:
          return True
    return False

  async def roulette_payout(ctx, game, number):
    user_dict = await util.get_user_data()
    for player in game.bets:
      for bet_type in game.bets[player]:
        win = False
        if await Gambling.roulette_win_check(player, game, bet_type, number):
          win = True
        # Unique bets that have to checked from the perspective of the user's chosen number.
        elif bet_type.split("_")[0] == "split":
          if await Gambling.roulette_split_check(game.bets[player][bet_type][0], number) == True:
            win = True
        elif bet_type.split("_")[0] == "street":
          if await Gambling.roulette_street_check(game.bets[player][bet_type][0], number) == True:
            win = True
        
        if win == False:
          user_dict = await Gambling.roulette_lose(user_dict, player, bet_type.split("_")[0], game.bets[player][bet_type][1])
        else:
          original_amount = game.bets[player][bet_type][1]
          new_amount = game.bets[player][bet_type][1] * game.bets[player][bet_type][2]
          user_dict = await Gambling.roulette_win(user_dict, player, bet_type.split("_")[0], new_amount)
          embed = discord.Embed(
            title = f"🏆 You won ${new_amount:,}",
            description = f"You bet ${original_amount:,} on **{await Gambling.get_roulette_bet_titles(game, bet_type, game.bets[player][bet_type][0])}** and won **${new_amount:,}**!\nYour new balance is ${user_dict[str(player.id)]['balance']:,}.",
            colour = discord.Colour.from_rgb(34, 184, 76))
          followup = game.bets[player][bet_type][3].followup
          try:
            await followup.send(embed = embed, ephemeral = True)
          except discord.errors.HTTPException as e:
            print(e)
            
    await util.save_user_data(user_dict)

  
  async def roulette_win(user_dict, player, bet_type_name, amount):
    user = user_dict[str(player.id)]
    rob = user_dict[str(906087821373239316)]

    user["balance"] += amount
    if user["balance"] > user["stat_highest_balance"]:
      user["stat_highest_balance"] = user["balance"]
    user["daily_cash_flow"] += amount
    user["total_cash_flow"] += amount
    rob["balance"] -= amount
    rob["daily_cash_flow"] += amount
    rob["total_cash_flow"] += amount

    user["stat_roulette_profit"] += amount
    rob["stat_roulette_loss"] -= amount
    user["stat_roulette_victory"] += 1
    rob["stat_roulette_defeat"] += 1
    user["stat_roulette_quantity"] += 1
    rob["stat_roulette_quantity"] += 1
    user["stat_roulette_current_win_streak"] += 1
    if user["stat_roulette_current_win_streak"] > user["stat_roulette_highest_win_streak"]:
      user["stat_roulette_highest_win_streak"] = user["stat_roulette_current_win_streak"]

    user[f"stat_roulette_{bet_type_name}_profit"] += amount
    rob[f"stat_roulette_{bet_type_name}_loss"] -= amount
    user[f"stat_roulette_{bet_type_name}_quantity"] += 1
    rob[f"stat_roulette_{bet_type_name}_quantity"] += 1
    user[f"stat_roulette_{bet_type_name}_victory"] += 1
    rob[f"stat_roulette_{bet_type_name}_defeat"] += 1
    return user_dict
    
  async def roulette_lose(user_dict, player, bet_type_name, amount):
    user = user_dict[str(player.id)]
    rob = user_dict[str(906087821373239316)]

    rob["daily_cash_flow"] += amount
    rob["total_cash_flow"] += amount
    user["daily_cash_flow"] += amount
    user["total_cash_flow"] += amount

    rob["stat_roulette_profit"] += amount
    user["stat_roulette_loss"] -= amount
    rob["stat_roulette_victory"] += 1
    user["stat_roulette_defeat"] += 1
    rob["stat_roulette_quantity"] += 1
    user["stat_roulette_quantity"] += 1
    rob["stat_roulette_current_win_streak"] += 1
    if rob["stat_roulette_current_win_streak"] > rob["stat_roulette_highest_win_streak"]:
      rob["stat_roulette_highest_win_streak"] = rob["stat_roulette_current_win_streak"]

    rob[f"stat_roulette_{bet_type_name}_profit"] += amount
    user[f"stat_roulette_{bet_type_name}_loss"] -= amount
    rob[f"stat_roulette_{bet_type_name}_quantity"] += 1
    user[f"stat_roulette_{bet_type_name}_quantity"] += 1
    rob[f"stat_roulette_{bet_type_name}_victory"] += 1
    user[f"stat_roulette_{bet_type_name}_defeat"] += 1
    return user_dict

    
  async def roulette_spin_cycle(ctx, game):
    while game.last_activity < game.spin_timeout:
      await asyncio.sleep(1)

      if game.number is None:
        number = Gambling.Roulette_Number( random.choice(Gambling.Roulette.numbers) )
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        process = multiprocessing.Process(target=Gambling.roulette_spin_animation, args=[number, return_dict])
        process.start()
        game.number = number
        
      if game.need_update and datetime.now() >= game.last_update + timedelta(seconds = 5)  and  datetime.now() <= game.next_spin - timedelta(seconds = 5):
        await Gambling.update_roulette_display(ctx)
        game.need_update = False
        game.last_update = datetime.now()
      
      if datetime.now() >= game.next_spin:
        process.join()
        game.spinning = True
        game.spin_animation_url = return_dict["url"]
        await Gambling.update_roulette_display(ctx)
        await asyncio.sleep(8)
        game.spinning = False
        game.spins += 1
        game.number = None
        
        game.spin_history.append(game.emojis[number.number])
        if len(game.spin_history) > 15:
          game.spin_history.pop(0)
        
        if number.green == True:
          game.embed.colour = discord.Colour.from_rgb(34, 184, 76)
        elif number.red == True:
          game.embed.colour = discord.Colour.from_rgb(247, 42, 42)
        else:
          game.embed.colour = discord.Colour.from_rgb(26, 26, 26)
          
        if game.bets:
          await Gambling.roulette_payout(ctx, game, number)
          await Gambling.update_roulette_display(ctx, number)
          game.bets = {}
        else:
          await Gambling.update_roulette_display(ctx, number)
          game.last_activity += 1
        await asyncio.sleep(4)
        
        if game.last_activity < game.spin_timeout:
          game.next_spin = datetime.now() + timedelta(seconds = game.round_time)
          await Gambling.update_roulette_display(ctx)
    game.view = None
    game.embed.title = "<:roblette:1024790477670715513> Roblette (Session Ended)"
    game.embed.colour = discord.Colour.from_rgb(47, 49, 54)
    await Gambling.update_roulette_display(ctx)
    del Gambling.roulette_active_servers[ctx.guild]

  
  def roulette_spin_animation(number, return_dict):
    number_degrees = {
      0:0,
      26:9.729,
      3:19.459,
      35:29.189,
      12:38.918,
      28:48.648,
      7:58.378,
      29:68.108,
      18:77.837,
      22:87.567,
      9:97.297,
      31:107.027,
      14:116.756,
      20:126.486,
      1:136.216,
      33:145.945,
      16:155.675,
      24:165.405,
      5:175.135,
      10:184.864,
      23:194.594,
      8:204.324,
      30:214.054,
      11:223.783,
      36:233.513,
      13:243.243,
      27:252.972,
      6:262.702,
      34:272.432,
      17:282.162,
      25:291.891,
      2:301.621,
      21:311.351,
      4:321.081,
      19:330.810,
      15:340.540,
      32:350.270
    }
    path = "graphics//roblette"
    board = Image.open(f'{path}//roblette_background.jpg')
    wheel = Image.open(f'{path}//roblette_wheel.png')
    arrow = Image.open(f'{path}//roblette_wheel_foreground.png')
    
    iterations = 35
    files = [f'{path}//roblette_frames//img{i}.png' for i in range(iterations + 1)]
    
    A = - number_degrees[number.number] + 720
    r = 0.30
    n = 0
    degree = 0
    
    roated_wheel = wheel.rotate(A)
    roated_wheel.save(f'{path}//roblette_temp_wheel.png')
    
    random_offet = random.randrange(-4,5)
    
    for f in files:
        P = A/(1 + r)**n
        degree = P + random_offet
        n += 1
        #print(f"Frame {n}: {degree}")
        
        wheel = Image.open(f'{path}//roblette_temp_wheel.png')
        roated_wheel = wheel.rotate(degree)
        board.paste(roated_wheel, (0,0), roated_wheel)
        board.paste(arrow, (0,0), arrow)
        board.save(f)
    
    frames = []
    for f in files:
        frame = Image.open(f)
        frames.append(frame)
    
    util.save_transparent_gif(frames, 120, f"{path}//roblette_spin.gif")
    
    url = f"https://api.imgbb.com/1/upload?expiration=60&key={imgbb_key}"
    files = {'image': open(f"{path}//roblette_spin.gif", "rb")}
    req = requests.post(url, files=files)
    image = req.json()

    return_dict["url"] = image["data"]["url"]
    
    # This block updates the embed poster with the last frame of the gif.
    # In theory, this makes it so when the wheel lands on a number it visually stays there until the next roll.
    # In practice this doesn't work due to the I/O limitations of having to download the image, making the process janky.
    # 
    # And besides, the way this block is currently written it creates a massive exploit.
    # Since the number the wheel lands on is submitted as the poster before the wheel starts spinning,
    # any updates before the wheel spins will reveal the winning number.
    # Not hard to fix but considering the jank of this feature overall. Easier to drop it.
    #
    #game = Gambling.roulette_active_servers[ctx.guild]
    #frames[len(frames)-1].save(f"{path}//roblette_temp_poster.png")
    #files = {'image': open(f"{path}//roblette_temp_poster.png", "rb")}
    #req = requests.post(url, files=files)
    #last_frame = req.json()
    #game.poster_url = last_frame["data"]["url"]
    
    
  
  roulette_active_servers = {}
  @commands.command(aliases = ["r","roulette"])
  @commands.cooldown(1, 5, commands.BucketType.guild)
  async def roblette(self, ctx, round_time = 30):
    try:
      round_time = await util.get_value(ctx, str(round_time), min = 15, max = 120, name = "Round timer")
    except Exception as e:
      print(e)
      return
    if not ctx.guild in Gambling.roulette_active_servers:
      Gambling.roulette_active_servers[ctx.guild] = Gambling.Roulette(round_time)
      await Gambling.display_roulette(ctx, Gambling.roulette_active_servers[ctx.guild])
      await Gambling.roulette_spin_cycle(ctx, Gambling.roulette_active_servers[ctx.guild])
    else:
      await Gambling.display_roulette(ctx, Gambling.roulette_active_servers[ctx.guild])
      pass
    
  mine_active_servers = set()
  @commands.command(aliases = ["drill","miner"])
  async def mine(self, ctx):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    mining_level = user["upgrade_miner"]["level"]
    if mining_level <= 0:
      await util.embed_error(ctx, "You have to purchase **Miner** to use this command.")
      return
    if user["rob_banned"] == True:
      await util.embed_rob_banned(ctx, "You don't have permission to perform this action.")
      return
    if ctx.guild == None:
      await util.embed_error(ctx, "You can only mine in a server.")
      return
    if ctx.guild in Gambling.mine_active_servers:
      await util.embed_error(ctx, "There's already a mine running in this server.")
      return

    with open("upgrades.json","r") as f:
      d = json.load(f)
    rate = d["upgrade_miner"]["amounts"][ str(mining_level) ]
    name = ctx.author.name.replace(ctx.author.name[0],ctx.author.name[0].upper())

    # Cooldown.
    FMT = "%Y-%m-%d-%H:%M:%S"
    last_use = datetime.strptime(user["last_mine"], FMT)
    raw_cooldown = timedelta(hours = 48).total_seconds()
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    after_cooldown = last_use + cooldown
    time_now = datetime.now()
    
    #Too Early
    if time_now < after_cooldown:
      difference = time_now - last_use
      time_remaining = cooldown - difference
      reduction = timedelta(hours = 48) - cooldown
      avg_reduction = str(reduction).split(".")[0]
      
      embed = discord.Embed(
      colour = (discord.Colour.red()),
      title = f":hourglass: Miner Cooldown",
      description = f"Please wait `{str(time_remaining).split('.')[0]}`")
      cooldown_level = user["upgrade_cooldown"]["level"]
      if cooldown_level >= 1:
        embed.add_field(name = f":hourglass_flowing_sand: Cooldown Level {cooldown_level}", value = f"`-{avg_reduction}`", inline = True)
      embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {name}")
      await ctx.channel.send(embed=embed)
      return

    start_timestamp = discord.utils.format_dt(time_now,style='R')
    amount = 0
    hp = 200
    fine_brackets = {
      100000:50000,
      50000:25000,
      10000:5000,
      5000:2500,
      0:500,
    }
    
    tiers = list(fine_brackets.keys())
    mining_thumb = "https://c.tenor.com/ZeliFQLpC_8AAAAC/mining-mlm.gif"
    alert_thumb = "https://c.tenor.com/ige8u-u4o1MAAAAC/caution.gif"
    success_thumb = "https://c.tenor.com/U57XQlDbcisAAAAS/shannon-sharpe-guy-in-tuxedo.gif"
    interrupt_thumb = "https://c.tenor.com/yMXHFf82NBsAAAAd/oh-the-misery-eggcat.gif"
    embed_name = ""
      
    embed = discord.Embed(
      title = "👨‍🏭 Illegal Mining Operation",
      description = f"Drill started {discord.utils.format_dt(time_now,style='R')}\nThis mine is level **{mining_level}** and makes **${rate}/m**\nDurability **{hp}/200**\nUnrealised Profit **${int(amount):,}**",
      colour = discord.Colour.gold()
    )
    embed.set_thumbnail(url=mining_thumb)
    embed.set_footer(text = f"{name} has mined for {str(timedelta(seconds=user['stat_mine_time']))} total.", icon_url = ctx.author.display_avatar.url)
      
    # I feel like this entire command is horrendously arranged, but anyway. Here's a class just for variables that I can modify from nested functions.
    class Variables:
      response = None
      
    # Default Button Setup.
    class Buttons(discord.ui.View):
      def __init__(self):
        super().__init__()
        self.outcome = ""
        self.inter = None
        
      @discord.ui.button(label=f"STOP", style=discord.ButtonStyle.red, emoji="🛑")
      async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != ctx.author:
          self.outcome = "interrupt"
        else:
          self.outcome = "win"
        self.inter = interaction
        task.cancel()
        self.stop()

      @discord.ui.button(label=f"Reprogram Drill", style=discord.ButtonStyle.green, emoji="🔧", disabled = True)
      async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == ctx.author:
          await interaction.response.send_modal(Question())
    
    class Question(discord.ui.Modal, title='Reprogram Drill'):
      text_input = discord.ui.TextInput(label="Question")
      async def on_submit(self, interaction: discord.Interaction):
        if self.text_input.value.lower() == str(answer):
          print("correct")
          Variables.response = True
          embed.set_field_at(index = 0, name="✅ Correct", value="Crisis averted.")
        else:
          print(f"incorrect, answer was {answer}")
          Variables.response = False
          embed.set_field_at(index = 0, name="❌ Incorrect", value="Sustained heavy damage.")
        await interaction.response.defer()
      async def on_error(self, interaction: discord.Interaction, error:Exception):
        print("too late to submit")
        await interaction.response.defer()

    view = Buttons()
    Gambling.mine_active_servers.add(ctx.guild)
    msg = await ctx.channel.send(embed=embed, view=view)

    interval = 1
    profit = rate/60*interval
    last_update = datetime.now()
    future_update = None
    obstacle = None
    pocket = datetime.now() + timedelta( seconds = random.randrange(240,361,5) )
    # The timestamp variable is made to save on unnecessary format_dt function calls.
    pocket_timestamp = discord.utils.format_dt(pocket, style='R')
    pocket_display_time = datetime.now() + timedelta( seconds = random.randrange(15,30,5) )
    pocket_amount = profit * 20 * (random.randrange(100, 126) / 100)
    timeout = None
    
    task = asyncio.create_task( Gambling.mine_sleep_interval(interval) )
    await task
    while view.inter == None:
      amount += profit
      # Pays out and creates new pockets.
      if datetime.now() >= pocket:
          amount += pocket_amount
          pocket = datetime.now() + timedelta( seconds = random.randrange(240,361,5) )
          pocket_timestamp = discord.utils.format_dt(pocket, style='R')
          # GLOSSARY
          # PROFIT  |  Provides level scaling & balances out parameter 2.
          # AMOUNT/PROFIT  |  acts as a rough representation of how many seconds would be required to attain the current AMOUNT with the current upgrade level.
          # I am using this number as a baseline for creating the value of Sloan pockets. Tying this number to the AMOUNT allows it to dynamically scale with the game.
          # RANDRANGE() / 100  |  randrange() is used over uniform() for the cleaner decimal output, though this probably doesn't matter.
          # * 0.2  |  This serves as a general multiplier for the Sloan pocket value.
          pocket_amount = profit * amount/profit * random.randrange(50, 126) / 100 * 0.2
          if pocket_amount > rate*10:
            pocket_amount = rate*10
          pocket_display_time = datetime.now() + timedelta( seconds = random.randrange(15,30,5) )
     
      # Creating and handling future obstacles.
      if obstacle == None:
        print(f"{datetime.now()} - Creating obstacle time")
        obstacle = datetime.now() + timedelta( seconds = random.randrange(120,600,5) )
        future_update = obstacle
      elif datetime.now() >= obstacle and timeout == None:
        timeout = datetime.now() + timedelta(seconds = 30)
        future_update = timeout
        question, answer = await Gambling.generate_question()
        Question.text_input.label = question
        view.children[1].disabled = False
        last_update = datetime.now()
        # Embed.
        embed.set_thumbnail(url=alert_thumb)
        embed.add_field(inline = False, name="⚠ Collision Alert!", value = f"{discord.utils.format_dt(timeout, style='R')} your drill will collide with an obstacle. Reprogram the drill to avoid crashing!")
        embed.colour = discord.Colour.orange()
        await msg.edit(embed=embed, view=view)
        print(f"{datetime.now()} - Edit Message (Create Obstacle)")

      if timeout != None:
        if datetime.now() >= timeout:
          print(f"{datetime.now()} - Out of time")
          timeout = True
      if timeout == True or Variables.response == False:
        print("Damaging HP")
        hp -= random.randrange(20,51,1)
        if hp <= 0:
          hp = 0
        
      # Updates AMOUNT and HP values for embed. The order of this code block relative to the others is necessary.
      next_vein_str = ""
      if datetime.now() >= pocket_display_time:
        next_vein_str = f"Incoming Bonus **${int(pocket_amount):,}** {pocket_timestamp}"
      embed.description = f"Drill started {start_timestamp}\nThis mine is level **{mining_level}** and makes **${rate}/m**\nDurability **{hp}/200**\nUnrealised Profit **${int(amount):,}**\n{next_vein_str}"

      #When the obstacle has passed.
      if timeout == True or Variables.response != None:
        print("Obstacle passed")
        if hp <= 0:
          view.outcome = "win"
          embed_name = f"💥 Drill Broke -${int(amount*.25):,}"
          amount = amount*.75
          break
        Variables.response = None
        view.children[1].disabled = True
        
        embed.set_thumbnail(url=mining_thumb)
        embed.colour = discord.Colour.gold()
        if timeout == True:
          embed.set_field_at(index = 0, name="💥 BANG", value = "Sustained heavy damage.")
        await msg.edit(embed=embed, view=view)
        last_update = datetime.now()
        print(f"{datetime.now()} - Edit Message (Clearing Obstacle)")
        embed.remove_field(0)
        obstacle = None
        timeout = None
      
      # Routine Update
      if datetime.now() >= last_update + timedelta(seconds = 5) and datetime.now() <= future_update + timedelta(seconds = -3):
        await msg.edit(embed=embed, view=view)
        last_update = datetime.now()
        print(f"{datetime.now()} - Edit Message (Routine)")

      # Sleep.
      task = asyncio.create_task( Gambling.mine_sleep_interval(interval) )
      await task

    # If game over.
    if ctx.guild in Gambling.mine_active_servers:
      Gambling.mine_active_servers.remove(ctx.guild)
    inter = view.inter
    outcome = view.outcome
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(906087821373239316)]

    #temp fix maybe its just better idk
    if embed_name == "":
      embed_name = f"<:ready:997527681333727253> Mining Stopped +${int(amount):,}"
    
    #General Stats.
    finish_time = datetime.now()
    start_time = time_now
    playtime = round( (finish_time - start_time).total_seconds(), 2)
    user["stat_mine_time"] += playtime
    user["stat_mine_quantity"] += 1
    user["stat_mine_average_time"].append(playtime)

    raw_cooldown = timedelta(hours = 48).total_seconds()
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    cooldown_str = f"\nDrill will cool down in `{str(cooldown).split('.')[0]}`."

    # Win.
    if outcome == "win":
      user_dict = await util.get_user_data()
      user = user_dict[str(ctx.author.id)]
      rob = user_dict[str(906087821373239316)]

      end_amount = int(amount)
      user["balance"] += end_amount
      rob["balance"] -= end_amount
      user["total_cash_flow"] += amount
      user["daily_cash_flow"] += amount
      rob["total_cash_flow"] += amount
      rob["daily_cash_flow"] += amount
      user["stat_mine_profit"] += end_amount
      user["stat_mine_victory"] += 1
      if end_amount > user["stat_mine_highest_victory"]:
        user["stat_mine_highest_victory"] = end_amount
      if playtime > user["stat_mine_longest_victory"]:
        user["stat_mine_longest_victory"] = playtime
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance"] = user["balance"]
      # Embed.
      embed.colour = discord.Colour.green()
      embed.set_thumbnail(url=success_thumb)
      embed.set_footer(text = f"{name} has made ${user['stat_mine_profit']:,} from illegal mining operations.", icon_url = ctx.author.display_avatar.url)
      embed.add_field(name = f"{embed_name}", value = f"{name} mined for `{str(timedelta(seconds=playtime)).split('.')[0]}` and excavated **${end_amount:,}**!\n{name}'s new balance is ${user['balance']:,}.{cooldown_str}")
    
    # Interrupt.
    elif outcome == "interrupt":
      # The name "ant" is short for "antagonist". Yeah, I should've spent another 20 seconds thinking about a better name.
      ant = user_dict[str(inter.user.id)]
      user["stat_mine_defeat"] += 1
      if playtime > user["stat_mine_longest_defeat"]:
        user["stat_mine_longest_defeat"] = playtime

      reward = 0
      reward_str = ""
      if amount >= 2:
        reward = int(amount/2)
        reward_str = f" and was rewarded with **${reward:,}**"
        ant["balance"] += reward
        ant["total_cash_flow"] += reward
        ant["daily_cash_flow"] += reward
        ant["stat_mine_interrupt_profit"] += reward
        rob["balance"] -= reward
        rob["total_cash_flow"] += reward
        rob["daily_cash_flow"] += reward
        if ant["balance"] > ant["stat_highest_balance"]:
          ant["stat_highest_balance"] = ant["balance"]
      ant["stat_mine_interrupt_quantity"] += 1
      ant["stat_mine_interrupt_time"] += playtime
      
      tz = ZoneInfo("Australia/Sydney")
      tFMT = "%Y-%m-%d"
      unique_id = str(datetime.now(tz)) + "_mine"
      deadline = (datetime.now(tz) + timedelta(days=14)).strftime(tFMT)
      for key in tiers:
        if amount >= key:
          fine_amount = fine_brackets[key]
          break
      # Deadline,   Repay amount,   Owed user's ID,   Unique ID/Time of loan,   Base amount,   Interest rate.
      user["debt"].append( [deadline, fine_amount, str(906087821373239316), unique_id, fine_amount, 5.0] )
      rob["owed"].append( [deadline, fine_amount, str(ctx.author.id), unique_id, fine_amount, 5.0] )

      embed.colour = discord.Colour.red()
      embed.set_thumbnail(url=interrupt_thumb)
      embed.add_field(inline = False, name = "🚨 Caught Mining!", value = f"{inter.user.name} caught you mining after `{str(timedelta(seconds=playtime)).split('.')[0]}`{reward_str}.\nYou've been fined for **${fine_amount:,}**{cooldown_str}")

    user["last_mine"] = str(datetime.now().strftime(FMT))
    await util.save_user_data(user_dict)
    if len(embed.fields) >= 2:
      embed.remove_field(0)
    await msg.edit(embed=embed, view=None)
    print(f"{datetime.now()} - Edit Message (Final)")

  
  async def mine_sleep_interval(interval):
    try:
      await asyncio.sleep(interval)
    except asyncio.CancelledError:
      pass
      
  async def generate_question():
    r = random.randrange
    c = random.choice
    operator = c(["+","-","*"])
    operator2 = c( [c(["+","-","*"]), ""] )
    number1 = f"{r(1,10,1)}{c( [r(1,10,1), ''] )}"
    number2 = f"{r(1,10,1)}{c( [r(1,10,1), ''] )}"
    number3 = ""
    if operator2 != "":
      number3 = f"{r(1,10,1)}{c( [r(1,10,1), ''] )}"
    question = (f"{number1} {operator} {number2} {operator2} {number3}")
    
    answer = str(eval(question))
    question = question.replace("*","×").replace("/","÷")
    return question, answer
      



      
      
  # This method could do with some organisation for readability purposes.
  steal_active_users = set()
  @commands.command(aliases = ["rob","take"])
  async def steal(self, ctx, mention : Union[discord.User, int] = None, amount=None):
    if mention == None:
      await front.help_steal(self,ctx)
      return 
      
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    if user["upgrade_steal"]["level"] <= 0:
      await util.embed_error(ctx, "You need to purchase **Steal** to use this command.")
      return
    
    with open("upgrades.json","r") as f:
      d = json.load(f)
    safe_max = d["upgrade_steal"]["amounts"][ str(user["upgrade_steal"]["level"]) ]
    
    # Odds simulation.
    # Future cleaning note: These try, except and some if else statements can be avoided just by checking the type of value e.g. if type(amount) == discord.User
    try:
      amount = int(mention)
      if amount <= 0:
        amount = 1
      if len(str(amount)) <= 9:
        # If user is not on cooldown display personalised odds based on how much they've already taken.
        stolen_str = ""
        already_stolen = user["steal_temp_profit"]
        # This still isn't a proper 100% fix.
        if already_stolen < safe_max:
          odds = safe_max / (amount + already_stolen) * 100 / ((amount + already_stolen) / safe_max)
          stolen_str = f" with **${already_stolen:,}** already stolen"
        else:
          odds = safe_max / amount * 100 / (amount / safe_max)
        if odds > 100.0:
          odds = 100.0
        # Dynamically add zeros based on how many are present and avoid scientific notation.
        odds_string = str(f"{odds:.20f}")
        zeros = len(re.search('\d+\.(0*)', odds_string).group(1))
        extra_zeros = 2
        if zeros >= 20:
          zeros = 0
          extra_zeros = 0
        odds_string = f"{odds:.{zeros+extra_zeros}f}"
        
        embed = discord.Embed(
        title = "🕵️‍♂️ Criminal Planning",
        description = f"The odds of successfully stealing **${amount:,}** at **Level {user['upgrade_steal']['level']}**{stolen_str} is **{odds_string}%**.",
        )
        await ctx.channel.send(embed=embed)
        return
      else:
        pass
    except:
      pass
    # If the number is over 9 digits long, attempt to access it as a user object. (Note: Actual IDs are 18 digits but I just don't see the point of simulating the odds of anything over 9 digits.)
    try:
      # Just keep in mind this important variable is assigned here.
      target = user_dict[str(mention.id)]
    except:
      await util.embed_error(ctx, f"Calculating odds for amounts over ${100000000:,} is not supported.")
      return
      
    if ctx.author in Gambling.steal_active_users:
      await util.embed_error(ctx, "You can't commit multiple crimes at once!")
      return
    if user["rob_banned"] == True:
      await util.embed_rob_banned(ctx, "You don't have permission to perform this action.")
      return
    if ctx.author == mention:
      await util.embed_error(ctx, "You can't steal from yourself!")
      return
    
    # Check to make sure you're not stealing from the same person too much without paying them.
    fines = 0
    for debt in user["debt"]:
      for owed in target["owed"]:
        if debt[3] == owed[3] and "steal" in debt[3]:
          fines += 1
    if fines >= 3:   
      await util.embed_error(ctx, f"{mention.name} has caught you too many times! Pay off your fines before stealing from them again.")
      return


    if ctx.guild == None:
      await util.embed_error(ctx, "You can only steal in a server.")
      return
      
    # Checking if the target user is a deserter or just not in the same server as the user.
    # This could look cleaner by appending each user to a list and then checking to see if mention is not in that list, but this seems faster.
    deserter = True
    for guild in self.client.guilds:
      async for disc_user in guild.fetch_members(limit=None):
        if disc_user == mention:
          deserter = False
          break
    in_server = False
    async for disc_user in ctx.guild.fetch_members(limit=None):
      if disc_user == mention:
        in_server = True
        break
    if in_server == False and deserter == False:
      await util.embed_error(ctx, "You can only steal from someone in the same server or someone in no servers.")
      return

    # Cooldown.
    FMT = "%Y-%m-%d-%H:%M:%S"
    last_focus = datetime.strptime(user["last_steal"], FMT)
    last_first_attempt = datetime.strptime(user["steal_temp_time"], FMT)
    raw_cooldown = timedelta(hours = 24).total_seconds()
    cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
    after_cooldown = last_focus + cooldown
    after_attempt_cooldown = last_first_attempt + cooldown
    time_now = datetime.now()
    
    #Too Early
    if time_now < after_cooldown:
      difference = time_now - last_focus
      time_remaining = cooldown - difference
      reduction = timedelta(hours = 24) - cooldown
      avg_reduction = str(reduction).split(".")[0]
      
      embed = discord.Embed(
      colour = (discord.Colour.red()),
      title = f":hourglass: Steal Cooldown",
      description = f"Please wait `{str(time_remaining).split('.')[0]}`")
      cooldown_level = user["upgrade_cooldown"]["level"]
      if cooldown_level >= 1:
        embed.add_field(name = f":hourglass_flowing_sand: Cooldown Level {cooldown_level}", value = f"`-{avg_reduction}`", inline = True)
      embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Used by {ctx.author.name}")
      await ctx.channel.send(embed=embed)
      return

    # Resetting attempts if enough time has passed since first attempt.
    if time_now > after_attempt_cooldown:
      user["steal_temp_time"] = str(datetime.now().strftime(FMT))
      user["steal_temp_attempts"] = 0
      user["steal_temp_profit"] = 0
      await util.save_user_data(user_dict)

    already_stolen = user["steal_temp_profit"]
    amount = amount or str(safe_max - already_stolen)
    try:
      amount = await util.get_value(ctx, amount, max = target["balance"], value_error = "You can't take more than the victim has.")
    except Exception as e:
      print(e)
      return
    fine_amount = int(safe_max/2)
    tz = ZoneInfo("Australia/Sydney")
    tFMT = "%Y-%m-%d"
    unique_id = str(datetime.now(tz)) + "_steal"
    deadline = (datetime.now(tz) + timedelta(days=14)).strftime(tFMT)
    fine_str = ""
    if deserter == False:
      fine_str = f" and have been fined for **${fine_amount:,}**"
    odds = safe_max / (amount + already_stolen) * 100 / ((amount + already_stolen) / safe_max)
    if odds >= 100.0:
      odds = 100.0
    fail_odds = 100.0 - odds

    prot_chance = d["upgrade_protection"]["amounts"][ str(target["upgrade_protection"]["level"]) ]
    # Custom defense for Rob
    if mention == self.client.user:
      prot_chance = 50
    hack_chance = 100.0 - prot_chance

    odds_string = str(f"{odds * hack_chance / 100:.20f}")
    zeros = len(re.search('\d+\.(0*)', odds_string).group(1))
    extra_zeros = 2
    if zeros >= 20:
      zeros = 0
      extra_zeros = 0
    odds_string = f"{odds * hack_chance / 100:.{zeros+extra_zeros}f}"

    s2_odds_str = str(f"{odds:.20f}")
    zeros = len(re.search('\d+\.(0*)', s2_odds_str).group(1))
    extra_zeros = 2
    if zeros >= 20:
      zeros = 0
      extra_zeros = 0
    s2_odds_str = f"{odds:.{zeros+extra_zeros}f}"
      

    # Note: If I wanted to get the targets status I would need to fetch them from the guild using ctx.guild.fetch_member(mention.id), this returns a Member object rather than a User object. Which contains the raw_status attribute.
    
    remaining_str = f"\nYou have **{(3-user['steal_temp_attempts'])-1}** more attempts today to steal **${safe_max - user['steal_temp_profit']:,}** Sloans."
    if (3-user['steal_temp_attempts'])-1 <= 0:
      # Cooldown.
      FMT = "%Y-%m-%d-%H:%M:%S"
      raw_cooldown = timedelta(hours = 24).total_seconds()
      cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
      time_remaining = cooldown
      remaining_str = f"\nYou can steal again in `{str(time_remaining).split('.')[0]}`."

    # Button Setup.
    class Menu(discord.ui.View):
      def __init__(self):
        super().__init__()
        self.value = None
  
      @discord.ui.button(label="INTERRUPT!", style=discord.ButtonStyle.red, emoji="👮‍♂️")
      async def menu(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.user == mention:
          embed.colour = discord.Colour.red()
          if stage == 0:
            embed.set_field_at(index = 0, name = f"❌ Bypassing Security ({hack_chance}%)", value = f"`Action interrupted.`")
            embed.set_field_at(index = 1, name = f"❌ Gathering Funds ({s2_odds_str}%)", value = "`Cancelled.`")
            embed.set_field_at(index = 2, name = "❌ Getting Out", value = "`Cancelled.`")
          elif stage == 1:
            embed.set_field_at(index = 1, name = f"❌ Gathering Funds ({s2_odds_str}%)", value = "`Action interrupted.`")
            embed.set_field_at(index = 2, name = "❌ Getting Out", value = "`Cancelled.`")
          else:
            embed.set_field_at(index = 2, name = "❌ Getting Out", value = "`Action interrupted.`")
          
          embed.add_field(name = "🚨 Caught Stealing!", value = f"{mention.name} caught you stealing from them and fined you for **${fine_amount:,}**.{remaining_str}")
          embed.title = "🕵️‍♂️ Crime Interrupted"
          await Gambling.steal_interrupt(self, ctx, mention, deserter, deadline, fine_amount, unique_id)
          await button.response.edit_message(embed=embed, view=None)
          self.value = False
          self.stop()
    
    embed = discord.Embed(
      title = "🕵️‍♂️ Crime in Progress...",
      description = f"{ctx.author.name} is stealing **${amount:,}** from {mention.name} with a **{odds_string}%** chance of success.",
    )
    embed.add_field(name = f"<a:loading:998460290280722486> Bypassing Security ({hack_chance}%)", value = f"`Breaching {mention.name}'s security...`")
    embed.add_field(name = f"<a:loading:998460290280722486> Gathering Funds ({s2_odds_str}%)", value = "`Waiting...`")
    embed.add_field(name = "<a:loading:998460290280722486> Getting Out", value = "`Waiting...`")
    embed.set_footer(text = f"{ctx.author.name} has stolen ${user['stat_steal_profit']:,} total.", icon_url = ctx.author.display_avatar.url)
    Gambling.steal_active_users.add(ctx.author)
          
    view = Menu()
    msg = await ctx.channel.send(f"{mention.mention} You are being stolen from. You have 20 seconds to interrupt the crime.", embed=embed, view = view)

    stage = 0
    time_interval = 7
    # Stage 1 -- Waiting...
    await asyncio.sleep(time_interval)
    if view.value == False:
      return

    # Rolling the dice...
    result = random.choices(["Success","Fail"],[hack_chance,prot_chance])[0]
    if result == "Success":
      embed.set_field_at(index = 0, name = f"<:ready:997527681333727253> Bypassed Security ({hack_chance}%)", value = "`I'm in.`")
      embed.set_field_at(index = 1, name = f"<a:loading:998460290280722486> Gathering Funds ({s2_odds_str}%)", value = "`Collecting Sloans...`")
      embed.colour = discord.Colour.from_rgb(194,255,219)
      await msg.edit(embed=embed)
      stage += 1
    else:
      embed.colour = discord.Colour.red()
      embed.set_field_at(index = 0, name = f"❌ Bypassing Security ({hack_chance}%)", value = "`Action Failed.`")
      embed.set_field_at(index = 1, name = f"❌ Gathering Funds ({s2_odds_str}%)", value = "`Cancelled.`")
      embed.set_field_at(index = 2, name = "❌ Getting Out", value = "`Cancelled.`")
      if mention != self.client.user:
        embed.add_field(name = "🚨 Steal Failed!", value = f"You failed to breach {mention.name}'s security{fine_str}. {mention.name} has a Protection level of {target['upgrade_protection']['level']}.{remaining_str}")
        embed.title = "🕵️‍♂️ Crime Failed"
        await msg.edit(embed=embed, view = None)
        await Gambling.steal_interrupt(self, ctx, mention, deserter, deadline, fine_amount, unique_id)
        return
      else:
        embed.colour = discord.Colour.red()
        embed.add_field(name = "🚨 Caught Stealing!", value = f"{mention.name} caught you stealing from them and fined you for **${int(fine_amount*2):,}**.{remaining_str}")
        embed.title = "🕵️‍♂️ Crime Interrupted"
        await msg.edit(embed=embed, view = None)
        # Stealing from Rob will fine you for double the normal amount.
        await Gambling.steal_interrupt(self, ctx, mention, deserter, deadline, int(fine_amount*2), unique_id)
        async with ctx.channel.typing():
          await asyncio.sleep(1.5)
          await ctx.channel.send(random.choice(["lol","nice try pal","psht.","seriously?","gotem","hah psht","you look like a fool","coward, I would've let you win if you took more.","dude. I'm right here.", "bro im literally online", "this guy thinks I have notifications off", "Rob never sleeps.", "gotcha", "sewer rat", "Running a little light in the pockets, lad?", "this amount of money is nothing to me, I stopped you just for fun", "what a joke", "you really think I wouldn't see that?", "that was close, heard the notification and came running lol"]))
        return
    
   
    # Stage 2 -- Waiting 5 seconds...
    await asyncio.sleep(time_interval)
    if view.value == False:
      return

    # Rolling the dice...
    result = random.choices(["Success","Fail"],[odds,fail_odds])[0]
    if result == "Success":
      embed.set_field_at(index = 1, name = f"<:ready:997527681333727253> Gathered Funds ({s2_odds_str}%)", value = "`Sloans acquired.`")
      embed.set_field_at(index = 2, name = "<a:loading:998460290280722486> Getting Out", value = f"`Logging out before {mention.name} sees...`")
      embed.colour = discord.Colour.from_rgb(119,226,164) 
      await msg.edit(embed=embed)
      stage += 1
    else:
      embed.colour = discord.Colour.red()
      embed.set_field_at(index = 1, name = f"❌ Gathering Funds ({s2_odds_str}%)", value = "`Action Failed.`")
      embed.set_field_at(index = 2, name = "❌ Getting Out", value = "`Cancelled.`")
      embed.add_field(name = "🚨 Steal Failed!", value = f"You failed to steal the Sloans{fine_str}.{remaining_str}")
      embed.title = "🕵️‍♂️ Crime Failed"
      await msg.edit(embed=embed, view = None)
      await Gambling.steal_interrupt(self, ctx, mention, deserter, deadline, fine_amount, unique_id)
      return
    
    
    # Stage 3 -- Waiting 5 seconds...
    await asyncio.sleep(time_interval)
    if view.value == False:
      return

    # IF SUCCESSFUL:
    #Re-assigning values after awaiting to prevent overwriting data.
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    target = user_dict[str(mention.id)]
      
    # Stats.
    user["balance"] += amount
    target["balance"] -= amount
    user["total_cash_flow"] += amount
    user["daily_cash_flow"] += amount
    target["total_cash_flow"] += amount
    target["daily_cash_flow"] += amount

    user["stat_steal_profit"] += amount
    target["stat_steal_victim_loss"] -= amount
    user["stat_steal_quantity"] += 1
    target["stat_steal_victim_quantity"] += 1
    user["stat_steal_victory"] += 1
    target["stat_steal_victim_defeat"] += 1

    if amount > user["stat_steal_highest_victory"]:
      user["stat_steal_highest_victory"] = amount
    if odds * hack_chance / 100 < user["stat_steal_lowest_odds_victory"]:
      user["stat_steal_lowest_odds_victory"] = odds * hack_chance / 100
    if user["balance"] > user["stat_highest_balance"]:
      user["stat_highest_balance"] = user["balance"]
    
    user["steal_temp_profit"] += amount
    user["steal_temp_attempts"] += 1

    remaining_str = f"\nYou have **{3-user['steal_temp_attempts']}** more attempts today to steal **${safe_max - user['steal_temp_profit']:,}** Sloans."
    # Enables Cooldown.
    if user["steal_temp_attempts"] >= 3 or user["steal_temp_profit"] >= safe_max:
      user["last_steal"] = str(datetime.now().strftime(FMT))
      # Displays Cooldown.
      FMT = "%Y-%m-%d-%H:%M:%S"
      last_steal = datetime.strptime(user["last_steal"], FMT)
      raw_cooldown = timedelta(hours = 24).total_seconds()
      cooldown = timedelta(seconds = raw_cooldown - raw_cooldown * user["upgrade_cooldown"]["amount"] * 0.01)
      time_now = datetime.now()
      difference = time_now - last_steal
      time_remaining = cooldown - difference
      remaining_str = f"\nYou can steal again in `{str(time_remaining).split('.')[0]}`."

    await util.save_user_data(user_dict)
    
    embed.set_field_at(index = 2, name = "<:ready:997527681333727253> Got Out", value = f"`Sucessfully escaped!`")
    embed.colour = discord.Colour.green()
    embed.add_field(name = "💸 Robbery Successful!", value = f"You stole **${amount:,}** from {mention.name} with a **{odds_string}%** chance!\nYour new balance is ${user['balance']:,}.{remaining_str}")
    embed.title = "🕵️‍♂️ Crime Successful"
    await msg.edit(embed=embed, view = None)
    if ctx.author in Gambling.steal_active_users:
      Gambling.steal_active_users.remove(ctx.author)
      return


  async def steal_interrupt(self, ctx, mention, deserter, deadline, fine_amount, unique_id, prot = None):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    target = user_dict[str(mention.id)]
    FMT = "%Y-%m-%d-%H:%M:%S"
    
    if deserter == False:
      # Deadline,   Repay amount,   Owed user's ID,   Unique ID/Time of loan,   Base amount,   Interest rate.
      user["debt"].append( [deadline, fine_amount, str(mention.id), unique_id, fine_amount, 5.0] )
      target["owed"].append( [deadline, fine_amount, str(ctx.author.id), unique_id, fine_amount, 5.0] )
    user["stat_steal_quantity"] += 1
    user["stat_steal_defeat"] += 1
    target["stat_steal_victim_quantity"] += 1
    target["stat_steal_victim_victory"] += 1
    if prot != None:
      target["stat_protection_quantity"] += 1
    user["steal_temp_attempts"] += 1
    # Enables Cooldown if enough attempts have been made.
    if user["steal_temp_attempts"] >= 3:
      user["last_steal"] = str(datetime.now().strftime(FMT))
    await util.save_user_data(user_dict)
    if ctx.author in Gambling.steal_active_users:
      Gambling.steal_active_users.remove(ctx.author)
    



  
  paulers = set()
  last_bal = {}
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
    paul_cancel = ""
    win = False
    paul_bonus = 0

    try:
      amount = await util.get_value(ctx, amount, max = user["balance"])
    except Exception as e:
      print(e)
      return
    
    # Caps the max flip.
    max_alert = ""
    max_bet = 100000
    if amount > max_bet:
      amount = max_bet
      max_alert = f"Your bet was capped at {max_bet:,}"

    # Paul bonus.
    try:
      last = Gambling.last_bal[str(ctx.author.id)]
    except:
      Gambling.last_bal[str(ctx.author.id)] = user["balance"]
      last = Gambling.last_bal[str(ctx.author.id)]
    if amount == user["balance"]   and   last > user["balance"] * 0.9   and   last < user["balance"] * 1.1:
      paul = True
    else:
      if ctx.author in Gambling.paulers:
        Gambling.paulers.remove(ctx.author)
      if last < user["balance"] * 0.9 and user["balance"] == amount  or   last > user["balance"] * 1.1 and user["balance"] == amount:
        paul_cancel = "Your balance shifted more than 10% since your last flip.\nYour Paul Bonus has been reset!"

    # Curse check.
    FMT = "%Y-%m-%d-%H:%M:%S"
    if user["cursed"]:
      expired = []
      for curse in user["cursed"]:
          if datetime.utcnow() > datetime.strptime(curse[0], FMT):
            user["luck"] = user["luck"]/curse[1]
            expired.append(curse)
      for curse in expired:
          user["cursed"].remove(curse)
  
    #Assigns the side.
    if side != None:
      if side.lower().startswith("h"):
        bet = "heads"
      elif side.lower().startswith("t"):
        bet = "tails"
      else:
        await util.embed_error(ctx,f"`{side}` is not a valid side! Try `h` or `t`.")
        return
    else:
      bet = random.choice(["heads","tails"])
   
    if bet == "heads":
      rob_bet = "tails"
    else:
      rob_bet = "heads"
      
    user_odds = 50 * user["luck"]
    rob_odds = 100 - user_odds
    flip = random.choices([bet,rob_bet], [user_odds,rob_odds])[0]
    
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
    
    if ctx.author in Gambling.paulers and max_alert == "":
      paul_bonus = round(amount*0.25)
    if ctx.channel != bot_commands and win == True:
      penalty = round(amount*0.25)
      amount -= penalty
      wrong_room = True
      paul = False
    if paul == True and win == True:
      Gambling.paulers.add(ctx.author)

    winner["balance"] += (amount + paul_bonus)
    if win == True:
      Gambling.last_bal[str(ctx.author.id)] = winner["balance"]
    else:
      del Gambling.last_bal[str(ctx.author.id)]
    winner["daily_cash_flow"] += (amount + paul_bonus)
    winner["total_cash_flow"] += (amount + paul_bonus)
    winner["average_flip_balance"].append(winner["balance"])
    if len(winner["average_flip_balance"]) > 5000:
      winner["average_flip_balance"].pop(0)
    loser["balance"] -= (amount + paul_bonus)
    loser["daily_cash_flow"] += (amount + paul_bonus)
    loser["total_cash_flow"] += (amount + paul_bonus)
    loser["average_flip_balance"].append(loser["balance"])
    if len(loser["average_flip_balance"]) > 5000:
      loser["average_flip_balance"].pop(0)

    winner["stat_flip_profit"] += amount
    winner["stat_flip_win_streak"] += 1
    if winner["stat_flip_win_streak"] > winner["stat_highest_flip_win_streak"]:
      winner["stat_highest_flip_win_streak"] = winner["stat_flip_win_streak"]

    loser["stat_flip_loss"] -= amount
    loser["stat_flip_win_streak"] = 0
      
    if amount > winner["stat_highest_flip"]:
      winner["stat_highest_flip"] = amount
    if amount > winner["stat_flip_highest_win"]:
      winner["stat_flip_highest_win"] = amount
    if amount > loser["stat_highest_flip"]:
      loser["stat_highest_flip"] = amount
  
    if winner["balance"] > winner["stat_highest_balance"]:
      winner["stat_highest_balance"] = winner["balance"]
    
    winner["stat_flip_quantity"] += 1
    winner["stat_flip_victory"] += 1
    loser["stat_flip_quantity"] += 1
    loser["stat_flip_defeat"] += 1

    # Gambling Addict active check.
    if user["upgrade_gambling_addict"]["amount"] == True:
      user["luck"] = user["luck"]/1.2
      user["upgrade_gambling_addict"]["amount"] = False

    # Gambling Addict passive check.
    if win == False:
      user_dict, ga_embed = await rewards.gambling_addict_passive(ctx, ctx.author, user_dict)
    
    await util.save_user_data(user_dict)
    
    balance = user["balance"]

    if flip == "tails":
      coin = "https://cdn.discordapp.com/attachments/894744339794780220/938857632712786010/sloan_tails_v6.png"
    else:
      coin = "https://cdn.discordapp.com/attachments/894744339794780220/938857632389799986/sloan_heads_v3.png"
    
    animation = False
    if amount >= 1000:
      animation = True
      if win == True and bet == "heads":
        gif = "https://cdn.discordapp.com/attachments/984028243202039818/985080468435259412/flip_heads_win_small.gif"
      elif win == True and bet == "tails":
        gif = "https://cdn.discordapp.com/attachments/984028243202039818/985080467856424990/flip_tails_win_small.gif"
      elif win == False and bet == "heads":
        gif = "https://cdn.discordapp.com/attachments/984028243202039818/985080468766613544/flip_tails_lose_small.gif"
      elif win == False and bet == "tails":
        gif = "https://cdn.discordapp.com/attachments/984028243202039818/985080468166832148/flip_heads_lose_small.gif"
        
      embed = discord.Embed(
        title = f"{ctx.author.name} | ${amount:,}"
      )
      embed.set_image(url = gif)
      msg = await ctx.channel.send(embed=embed)
      await asyncio.sleep(4)
    
    if Gambling.last_side == flip:
      Gambling.consecutive += 1
    else:
      Gambling.consecutive = 1
    Gambling.last_side = flip
    
    embed = discord.Embed(
      colour = outcome_colour,
      title = f":{emoji}: Flip | {flip.capitalize()}")
    embed.set_thumbnail(url = ctx.author.display_avatar.url)
    embed.add_field(name = f"You {outcome}!", value = f"**${amount + paul_bonus:,}** {message}\nYour new balance is ${balance:,}.", inline = True)
    if win == True and paul == True and max_alert == "" :
      paul_text = ":star: Incoming Paul Bonus!"
      if paul_bonus > 0:
        paul_text = f":star2: Paul Bonus! +${paul_bonus:,}"
      embed.add_field(name = f"{paul_text}", value = f"Go all in again for **+${round(balance*.25):,}** extra!", inline = False)
    elif paul_cancel != "" and win == True:
      embed.add_field(name = f"🚫 Paul Bonus Failed!", value = paul_cancel, inline = False)
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
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"{ctx.author.name} vs CyberRob {max_alert}")
    if animation == False:
      await ctx.channel.send(embed=embed)
    else:
      await msg.edit(embed=embed)
    
    # Gambling Addict embed.
    if win == False and ga_embed != None:
      await ctx.channel.send(embed=ga_embed)




  active = False
  message = None
  image = None
  pot = 0
  activity_log = ["","","",""]
  participants = {}
  time_remaining = 120
  @commands.command(aliases = ["jack","pot","j","jake","jp"])
  async def jackpot(self, ctx, amount):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    if user["rob_banned"] == True:
      await util.embed_rob_banned(ctx, "You don't have permission to perform this action")
      return
  
    rob = user_dict[str(906087821373239316)]
    try:
      amount = await util.get_value(ctx, amount, max = user["balance"])
    except Exception as e:
      print(e)
      return
    max_time = 120
    
    #For starting the game.
    if Gambling.active == False:
      Gambling.pot = amount
      Gambling.activity_log.pop(0)
      Gambling.activity_log.append(f"**{ctx.author.name}** started the jackpot at **${amount:,}**")
      Gambling.participants.update( {ctx.author.id:{"account":ctx.author,"amount":amount}} )
      Gambling.message = await self.create_jackpot(ctx, Gambling.activity_log, Gambling.participants)
      user["balance"] -= amount
      #rob holds the bet temporarily so the sloans don't vanish into the void.
      rob["balance"] += amount
      # Gambling Addict check.
      user_dict, ga_embed = await rewards.gambling_addict_passive(ctx, ctx.author, user_dict)
      await util.save_user_data(user_dict)
      if ga_embed != None:
        await ctx.channel.send(embed = ga_embed)
      Gambling.active = True
      status = await self.wait_for_players(ctx)
      if status == False:
        user_dict = await util.get_user_data()
        user = user_dict[str(ctx.author.id)]
        rob = user_dict[str(906087821373239316)]
        user["balance"] += Gambling.pot
        rob["balance"] -= Gambling.pot
        await util.save_user_data(user_dict)
        await self.reset_jackpot()
        return
      await self.start_timer(rob)
      await self.payout()
      await self.reset_jackpot()
    
    #For adding to the game.
    else:

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

      old_pot = Gambling.pot
      Gambling.pot += amount
      user["balance"] -= amount
      rob["balance"] += amount
      # Gambling Addict check.
      user_dict, ga_embed = await rewards.gambling_addict_passive(ctx, ctx.author, user_dict)
      await util.save_user_data(user_dict)

      # Gambling Addict embed.
      if ga_embed != None:
        await ctx.channel.send(embed = ga_embed)
      
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
    timeout = 300
    while len(Gambling.participants) < 2 and timeout > 0:
      await asyncio.sleep(1)
      timeout -= 1
    if timeout <= 0:
      embed = Gambling.message.embeds[0]
      embed.add_field(name="❌ Timed Out!",value="No one joined your jackpot!", inline = False)
      embed.description = "**GAME OVER**"
      embed.colour = discord.Colour.red()
      await Gambling.message.edit(embed=embed)
      return False
      
    #try:
      #input = await self.client.wait_for("message", check = lambda m: len(Gambling.participants) > 1 or m.author == ctx.author and m.content.lower() == "$cancel", timeout=300)
    #except asyncio.TimeoutError:
      #await util.embed_message(ctx,":no_entry:","Cancelled",f"No one joined your jackpot!")
      #return False
    #if input.content.lower() == "$cancel":
        #await util.embed_message(ctx,":no_entry:","Cancelled",f"Successfully cancelled jackpot!")
        #return False

      
  async def start_timer(self, rob):
    while Gambling.time_remaining >= 1:
      await asyncio.sleep(1)
      Gambling.time_remaining -= 1
      await self.edit_jackpot(time_update = True)

      if Gambling.time_remaining <= 10  and  len(Gambling.participants) >= 3  and  Gambling.pot > 10000  and  rob["balance"] >= Gambling.pot*50  and  random.randrange(1,901) <= 1:
        ctx = Gambling.message.channel.send(f"$jackpot {Gambling.pot*9}")
        self.jackpot(ctx, Gambling.pot*9)
        

  
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
    rob = user_dict[str(906087821373239316)]
    user["balance"] += pot
    user["daily_cash_flow"] += pot
    user["total_cash_flow"] += pot
    rob["balance"] -= pot

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
        user_dict[str(player)]["total_cash_flow"] += Gambling.participants[player]["amount"]
        user_dict[str(player)]["daily_cash_flow"] += Gambling.participants[player]["amount"]
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
    await self.edit_jackpot(winner = winner)
    await util.save_user_data(user_dict)

  
  async def create_jackpot(self, ctx, activity_log:list, participants:dict):
    embed = discord.Embed(
    colour = discord.Colour.orange(),
    title = f"🍯 Jackpot | ${Gambling.pot:,}",
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

  
  async def edit_jackpot(self, winner = None, time_update = None):
    embed = Gambling.message.embeds[0]
    embed.title = f"🍯 Jackpot | ${Gambling.pot:,}"
    started = False
    if len(Gambling.participants) > 1:
      started = True
      embed.description = f"{time.strftime('%M:%S', time.gmtime(Gambling.time_remaining))}"
      embed.colour = discord.Colour.green()

    #If the embed is not being updated due to the timer.
    if time_update == None:
      activity_log = Gambling.activity_log
      embed.set_field_at(index = 0, name = "Activity", value = f"{activity_log[0]}\n{activity_log[1]}\n{activity_log[2]}\n{activity_log[3]}\n", inline = True)

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
      i=0
      data = []
      players = Gambling.participants
      for player in players:
        name = players[player]["account"].name
        amount = players[player]["amount"]
        if i < 9:
          colour = colours[i]
        else:
          colour = (180,180,180)
        i+=1
        odds = round((amount / Gambling.pot) * 100, 2)
        user = (amount,odds,name,colour)
        data.append(user)
        
      data.sort(reverse=True)
  
  
      w, h = 600, 400
      shape = [(10, 10), (w-210, h-10)]
      # Creating new Image object.
      img = Image.new("RGBA", (w, h))
      img1 = ImageDraw.Draw(img)
      
      tdeg = 0
      h = 10
      font = ImageFont.truetype("font//Poppins-Light.ttf", 22)
      players_string = ""
      for i in range(len(data)):
        players_string += f"*{data[i][1]}% | {data[i][2]} | ${data[i][0]:,}*\n"
        
        colour = random.choice(colours)
        if colours:
          colours.remove(colour)
        deg = 360*data[i][1]*0.01
        tdeg += deg
        img1.pieslice(shape, start = tdeg-deg, end = tdeg, fill = data[i][3], outline = None)
        img1.text((400, h), f"• {data[i][2]}", font= font, fill = data[i][3])
        h+=25
      
      path = 'graphics//pie.png'
      img.save(path)
      im = pyimgur.Imgur(client_id)
      image = im.upload_image(path, title="pie")
      link = image.link
      if started == True:
        embed.set_image(url = link)
      embed.set_field_at(index = 1, name = "Players", value = players_string, inline = True)
      if Gambling.image != None:
        Gambling.image.delete()
      Gambling.image = image

    if winner != None:
      embed.description = "**GAME OVER**"
      embed.colour = discord.Colour.magenta()
      embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      embed.add_field(name = f"💸 **{winner['name'].upper()} WINS!**", value = f"**{winner['name']}** won the pot worth **${Gambling.pot:,}** with a **{winner['odds']}%** chance!", inline = True)
    await Gambling.message.edit(embed=embed)

 
  async def reset_jackpot(self):
    Gambling.active = False
    Gambling.message = None
    Gambling.image = None
    Gambling.pot = 0
    Gambling.activity_log = ["","","",""]
    Gambling.participants = {}
    Gambling.time_remaining = 120
      

async def setup(client:commands.Bot):
  await client.add_cog(Gambling(client))