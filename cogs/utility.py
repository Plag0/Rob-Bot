import os
from discord.ext import commands
import discord
import requests
from datetime import datetime, timedelta

from replit import db
import replit
import json

from typing import Tuple, List, Union
from collections import defaultdict
from random import randrange
from itertools import chain

from PIL.Image import Image

import random



class Utility(commands.Cog):
  def __init__(self, client):
    self.client = client

  # This code adapted from https://github.com/python-pillow/Pillow/issues/4644 to resolve an issue
  # described in https://github.com/python-pillow/Pillow/issues/4640
  #
  # There is a known issue with the Pillow library that messes up GIF transparency by replacing the
  # transparent pixels with black pixels (among other issues) when the GIF is saved using PIL.Image.save().
  # This code works around the issue and allows us to properly generate transparent GIFs.
  class TransparentAnimatedGifConverter(object):
      _PALETTE_SLOTSET = set(range(256))
  
      def __init__(self, img_rgba: Image, alpha_threshold: int = 0):
          self._img_rgba = img_rgba
          self._alpha_threshold = alpha_threshold
  
      def _process_pixels(self):
          """Set the transparent pixels to the color 0."""
          self._transparent_pixels = set(
              idx for idx, alpha in enumerate(
                  self._img_rgba.getchannel(channel='A').getdata())
              if alpha <= self._alpha_threshold)
  
      def _set_parsed_palette(self):
          """Parse the RGB palette color `tuple`s from the palette."""
          palette = self._img_p.getpalette()
          self._img_p_used_palette_idxs = set(
              idx for pal_idx, idx in enumerate(self._img_p_data)
              if pal_idx not in self._transparent_pixels)
          self._img_p_parsedpalette = dict(
              (idx, tuple(palette[idx * 3:idx * 3 + 3]))
              for idx in self._img_p_used_palette_idxs)
  
      def _get_similar_color_idx(self):
          """Return a palette index with the closest similar color."""
          old_color = self._img_p_parsedpalette[0]
          dict_distance = defaultdict(list)
          for idx in range(1, 256):
              color_item = self._img_p_parsedpalette[idx]
              if color_item == old_color:
                  return idx
              distance = sum((
                  abs(old_color[0] - color_item[0]),  # Red
                  abs(old_color[1] - color_item[1]),  # Green
                  abs(old_color[2] - color_item[2])))  # Blue
              dict_distance[distance].append(idx)
          return dict_distance[sorted(dict_distance)[0]][0]
  
      def _remap_palette_idx_zero(self):
          """Since the first color is used in the palette, remap it."""
          free_slots = self._PALETTE_SLOTSET - self._img_p_used_palette_idxs
          new_idx = free_slots.pop() if free_slots else \
              self._get_similar_color_idx()
          self._img_p_used_palette_idxs.add(new_idx)
          self._palette_replaces['idx_from'].append(0)
          self._palette_replaces['idx_to'].append(new_idx)
          self._img_p_parsedpalette[new_idx] = self._img_p_parsedpalette[0]
          del(self._img_p_parsedpalette[0])
  
      def _get_unused_color(self) -> tuple:
          """ Return a color for the palette that does not collide with any other already in the palette."""
          used_colors = set(self._img_p_parsedpalette.values())
          while True:
              new_color = (randrange(256), randrange(256), randrange(256))
              if new_color not in used_colors:
                  return new_color
  
      def _process_palette(self):
          """Adjust palette to have the zeroth color set as transparent. Basically, get another palette
          index for the zeroth color."""
          self._set_parsed_palette()
          if 0 in self._img_p_used_palette_idxs:
              self._remap_palette_idx_zero()
          self._img_p_parsedpalette[0] = self._get_unused_color()
  
      def _adjust_pixels(self):
          """Convert the pixels into their new values."""
          if self._palette_replaces['idx_from']:
              trans_table = bytearray.maketrans(
                  bytes(self._palette_replaces['idx_from']),
                  bytes(self._palette_replaces['idx_to']))
              self._img_p_data = self._img_p_data.translate(trans_table)
          for idx_pixel in self._transparent_pixels:
              self._img_p_data[idx_pixel] = 0
          self._img_p.frombytes(data=bytes(self._img_p_data))
  
      def _adjust_palette(self):
          """Modify the palette in the new `Image`."""
          unused_color = self._get_unused_color()
          final_palette = chain.from_iterable(
              self._img_p_parsedpalette.get(x, unused_color) for x in range(256))
          self._img_p.putpalette(data=final_palette)
  
      def process(self) -> Image:
          """Return the processed mode `P` `Image`."""
          self._img_p = self._img_rgba.convert(mode='P')
          self._img_p_data = bytearray(self._img_p.tobytes())
          self._palette_replaces = dict(idx_from=list(), idx_to=list())
          self._process_pixels()
          self._process_palette()
          self._adjust_pixels()
          self._adjust_palette()
          self._img_p.info['transparency'] = 0
          self._img_p.info['background'] = 0
          return self._img_p
  
  
  def _create_animated_gif(images: List[Image], durations: Union[int, List[int]]) -> Tuple[Image, dict]:
      """If the image is a GIF, create an its thumbnail here."""
      save_kwargs = dict()
      new_images: List[Image] = []
  
      for frame in images:
          thumbnail = frame.copy()  # type: Image
          thumbnail_rgba = thumbnail.convert(mode='RGBA')
          thumbnail_rgba.thumbnail(size=frame.size, reducing_gap=3.0)
          converter = Utility.TransparentAnimatedGifConverter(img_rgba=thumbnail_rgba)
          thumbnail_p = converter.process()  # type: Image
          new_images.append(thumbnail_p)
  
      output_image = new_images[0]
      save_kwargs.update(
          format='GIF',
          save_all=True,
          optimize=False,
          append_images=new_images[1:],
          duration=durations,
          disposal=2)
      return output_image, save_kwargs
  
  
  def save_transparent_gif(images: List[Image], durations: Union[int, List[int]], save_file):
      """Creates a transparent GIF, adjusting to avoid transparency issues that are present in the PIL library
  
      Note that this does NOT work for partial alpha. The partial alpha gets discarded and replaced by solid colors.
  
      Parameters:
          images: a list of PIL Image objects that compose the GIF frames
          durations: an int or List[int] that describes the animation durations for the frames of this GIF
          save_file: A filename (string), pathlib.Path object or file object. (This parameter corresponds
                     and is passed to the PIL.Image.save() method.)
      Returns:
          Image - The PIL Image object (after first saving the image to the specified target)
      """
      root_frame, save_args = Utility._create_animated_gif(images, durations)
      root_frame.save(save_file, **save_args)





  #Old Methods
  #async def get_user_data():
    #url = 'https://api.jsonbin.io/v3/b/621c750124f17933e4a086f2/latest'
    #JSON_KEY = os.environ['JSONBin_KEY']
    #headers = {'X-Master-Key': JSON_KEY,'X-Bin-Meta': 'false'}
    #users = requests.get(url, headers=headers)
    #print(f"Requesting data - {users}")
    #return users.json()

  #async def save_user_data(users):
    #url = 'https://api.jsonbin.io/v3/b/621c750124f17933e4a086f2'
    #headers = {'Content-Type': 'application/json',
               #'X-Master-Key': '$2b$10$vuv5EkWiv.GzPpc9hUQgM.NY8/D.5lOZWuTtEucnrOflEMkfXmvxm'}
    #req = requests.put(url, json=users, headers=headers)
    #print(f"Saving data {req}")

  async def get_user_data():
    return json.loads(db["user_data"])
    #return db["user_dict"]

  async def save_user_data(users):
    db["user_data"] = json.dumps(users)
    #pass
  
  #REMEMBER TO RE-ENABLE THIS WITH CHANGES
  async def create_user(user):
    users = await Utility.get_user_data()
    if str(user.id) in users:
      print(f"{user.name} already in database")
      return False
    else:
      FMT = "%Y-%m-%d-%H:%M:%S"
      #core values
      users[str(user.id)] = {}
      users[str(user.id)]["stat_last_active"] = str(datetime.now().strftime(FMT))
      users[str(user.id)]["balance"] = 0
      users[str(user.id)]["daily_streak"] = 0
      users[str(user.id)]["last_daily"] = str(datetime.now().strftime(FMT))
      users[str(user.id)]["last_weekly"] = str(datetime.now().strftime(FMT))
      users[str(user.id)]["rep"] = 0
      users[str(user.id)]["lol"] = {"summoner_name":"","region":""}
      #stats
      #highest refers to the all time high
      users[str(user.id)]["stat_highest_balance"] = 0
      users[str(user.id)]["stat_highest_daily_streak"] = 0
      users[str(user.id)]["stat_highest_flip"] = 0
      users[str(user.id)]["stat_flip_win_streak"] = 0
      users[str(user.id)]["stat_highest_flip_win_streak"] = 0
      users[str(user.id)]["stat_highest_gold"] = 0
      
      users[str(user.id)]["stat_trivia_win_streak"] = 0
      users[str(user.id)]["stat_highest_trivia_win_streak"] = 0
    
      users[str(user.id)]["stat_highest_give_received"] = 0
      users[str(user.id)]["stat_highest_give_received_user"] = ""
      users[str(user.id)]["stat_highest_give_sent"] = 0
      users[str(user.id)]["stat_highest_give_sent_user"] = ""
      
      #profit refers to the total amount gained.
      users[str(user.id)]["stat_daily_profit"] = 0
      users[str(user.id)]["stat_weekly_profit"] = 0
      users[str(user.id)]["stat_flip_profit"] = 0
      users[str(user.id)]["stat_give_profit"] = 0
      users[str(user.id)]["stat_claim_profit"] = 0
      users[str(user.id)]["stat_passive_income_profit"] = 0
      users[str(user.id)]["stat_trivia_profit"] = 0
      users[str(user.id)]["stat_gold_transmutation_profit"] = 0
  
      users[str(user.id)]["stat_trivia_victory"] = 0
      users[str(user.id)]["stat_trivia_defeat"] = 0
      
      users[str(user.id)]["stat_flip_victory"] = 0
      users[str(user.id)]["stat_flip_defeat"] = 0

      users[str(user.id)]["stat_jackpot_profit"] = 0
      users[str(user.id)]["stat_jackpot_loss"] = 0
      users[str(user.id)]["stat_jackpot_highest_win"] = 0
      users[str(user.id)]["stat_jackpot_quantity"] = 0
      users[str(user.id)]["stat_jackpot_victory"] = 0
      users[str(user.id)]["stat_jackpot_defeat"] = 0
      users[str(user.id)]["stat_jackpot_lowest_odds_victory"] = 100

      
      #loss refers to the total amount lost.
      users[str(user.id)]["stat_give_loss"] = 0
      users[str(user.id)]["stat_flip_loss"] = 0
      users[str(user.id)]["stat_upgrade_loss"] = 0
      users[str(user.id)]["stat_trivia_loss"] = 0
  
      #quantity refers to the amount of times a command has been executed.
      users[str(user.id)]["stat_daily_quantity"] = 0
      users[str(user.id)]["stat_weekly_quantity"] = 0
      users[str(user.id)]["stat_flip_quantity"] = 0
      users[str(user.id)]["stat_claim_quantity"] = 0
      users[str(user.id)]["stat_league_games_quantity"] = 0
      
      users[str(user.id)]["stat_give_quantity_sent"] = 0
      users[str(user.id)]["stat_give_quantity_received"] = 0
      users[str(user.id)]["stat_profile_views"] = 0
      #upgrades
      #1st value is main amount, 2nd is quantity of upgrades, 3rd is price, 4th is upgrade increase, 5th is max quantity, 6th is single use true or false.
      users[str(user.id)]["upgrade_daily"] = [0,0,1000,100,10,0,":arrow_double_up:"]
      users[str(user.id)]["upgrade_passive_income"] = [0,0,3000,2,10,0,":chart_with_upwards_trend:"]
      users[str(user.id)]["upgrade_weekly"] = [0,0,10000,1000,10,0,":calendar_spiral:"]
      users[str(user.id)]["upgrade_mail"] = [0,0,1000,1,5,1,":mailbox:"]
      users[str(user.id)]["upgrade_ban"] = [0,0,1000000,1,3,1,":hammer:"]
      users[str(user.id)]["upgrade_kick"] = [0,0,350000,1,1,1,":foot:"]
      users[str(user.id)]["upgrade_cooldown"] = [0,0,25000,0,10,0,":hourglass_flowing_sand:"]
      users[str(user.id)]["upgrade_streak"] = [0,0,2500,1,10,0,":tada:"]
      users[str(user.id)]["upgrade_restore"] = [0,0,0,1,1,1,":confetti_ball:"]
      users[str(user.id)]["upgrade_gold_transmutation"] = [0,0,1000,1,10,0,"<:lol_passive:957853326626656307>"]
      users[str(user.id)]["upgrade_change_lol"] = [0,0,500,1,1,1,"👤"]
      
      
      print(f"Successfully added {user.id} to database!")
      #await Utility.save_user_data(users)
  
  
  #from backports.zoneinfo import ZoneInfo
  #tz = ZoneInfo("Australia/Sydney")
  @commands.command(aliases = ["update"])
  @commands.is_owner()
  async def update_user_data(self, ctx):
    user_dict = await Utility.get_user_data()
    
    # For updating a specific user.
    #user = user_dict[str(188811740476211200)]
    #user["stat_loan_quantity_paid"] -= 1
    #user["stat_loan_amount_paid"] -= 3131
    #user = user_dict[str(182711551353028618)]
    #user["stat_loan_quantity_paid"] -= 1
    #user["stat_mystery_box_loss"]+= int(6000 * 2)
    #user["stat_loan_quantity_taken"] = user["stat_loan_quantity_paid"]
    #user["stat_loan_amount_taken"] = user["stat_loan_amount_paid"]
    #user["stat_loan_quantity_given"] = user["stat_loan_quantity_returned"]
    #user["upgrade_restore"]["level"] -=1
    
    # For updating all users.
    for key in user_dict:
      user = user_dict[str(key)]
      #user["stat_loan_quantity_taken"] = user["stat_loan_quantity_paid"]
      #user["stat_loan_amount_taken"] = user["stat_loan_amount_paid"]
      #user["total_cash_flow"] = int(user["total_cash_flow"])
      #user["lol"].update( {"last_request_epoch":1624023657} )

      # For adding an upgrade.
      #user.update( {
      #"upgrade_miner": {
        #"level": 0, 
        #"amount": 0, 
        #"price": 500000}
      #} )
      
      # For renaming a key.
      #user["stat_loan_quantity_paid_late"] = user["stat_loan_quantity_returned_late"]
      #del user["stat_loan_quantity_returned_late"]
  
      # For updating a value
      #user["stat_steal_lowest_odds_victory"] = 100.0

      # For adding one pair.
      #user.update( {"stat_mine_average_time":[]} )
      
      # For adding multiple pairs.
      user.update([ 
        ("stat_roulette_profit",0),
        ("stat_roulette_loss",0),
        ("stat_roulette_victory",0),
        ("stat_roulette_defeat",0),
        ("stat_roulette_quantity",0),
        ("stat_roulette_current_win_streak",0),
        ("stat_roulette_highest_win_streak",0),

        ("stat_roulette_green_profit",0),
        ("stat_roulette_green_loss",0),
        ("stat_roulette_green_quantity",0),
        ("stat_roulette_green_victory",0),
        ("stat_roulette_green_defeat",0),

        ("stat_roulette_red_profit",0),
        ("stat_roulette_red_loss",0),
        ("stat_roulette_red_quantity",0),
        ("stat_roulette_red_victory",0),
        ("stat_roulette_red_defeat",0),

        ("stat_roulette_black_profit",0),
        ("stat_roulette_black_loss",0),
        ("stat_roulette_black_quantity",0),
        ("stat_roulette_black_victory",0),
        ("stat_roulette_black_defeat",0),

        ("stat_roulette_odd_profit",0),
        ("stat_roulette_odd_loss",0),
        ("stat_roulette_odd_quantity",0),
        ("stat_roulette_odd_victory",0),
        ("stat_roulette_odd_defeat",0),

        ("stat_roulette_even_profit",0),
        ("stat_roulette_even_loss",0),
        ("stat_roulette_even_quantity",0),
        ("stat_roulette_even_victory",0),
        ("stat_roulette_even_defeat",0),

        ("stat_roulette_number_profit",0),
        ("stat_roulette_number_loss",0),
        ("stat_roulette_number_quantity",0),
        ("stat_roulette_number_victory",0),
        ("stat_roulette_number_defeat",0),

        ("stat_roulette_split_profit",0),
        ("stat_roulette_split_loss",0),
        ("stat_roulette_split_quantity",0),
        ("stat_roulette_split_victory",0),
        ("stat_roulette_split_defeat",0),

        ("stat_roulette_street_profit",0),
        ("stat_roulette_street_loss",0),
        ("stat_roulette_street_quantity",0),
        ("stat_roulette_street_victory",0),
        ("stat_roulette_street_defeat",0),

        ("stat_roulette_basket_profit",0),
        ("stat_roulette_basket_loss",0),
        ("stat_roulette_basket_quantity",0),
        ("stat_roulette_basket_victory",0),
        ("stat_roulette_basket_defeat",0),

        ("stat_roulette_dozen_profit",0),
        ("stat_roulette_dozen_loss",0),
        ("stat_roulette_dozen_quantity",0),
        ("stat_roulette_dozen_victory",0),
        ("stat_roulette_dozen_defeat",0),
      ])
  
      # For removing a pair.
      #del user["stat_highest_balance "]
      
      print(f"Updated: {key}")
    await Utility.save_user_data(user_dict)
    print("Successfully updated user data.")
    await ctx.channel.send("Successfully updated user data.")



  async def round_number(amount:int, num:int):
    if num != None:
        return num * round(amount/num)
    else:
        return amount

  # Deprecated
  async def formula_calc(base_value:int, level:int, formula:str, round_by:int=None):
    round_by = round_by or None
    for i in range(level):
        base_value += eval(formula)
    return await Utility.round_number(base_value, round_by)

  
  @commands.command(aliases = ["backup"])
  @commands.is_owner()
  async def backup_user_data(self, ctx=None, *, title=None):
    #user_dict = replit.database.dumps(db["user_dict"])
    #user_dict = replit.database.to_primitive(user_observed_dict)
    user_dict = await Utility.get_user_data()
    date = title or datetime.now()
    path = f"backups//user_data_backup_{date}.json"
    with open(path,"w+") as file_object:
      json.dump(user_dict, file_object)
    print(f"Saved user data as 'user_data_backup_{date}.json'")

  
  async def get_value(ctx, value, *, min = 1, max = None, name:str = None, value_error = None):
    name = name or "Value"
    if max == None:
      value_error = value_error or f"{name} out of range! (min: {min})"
    else:
      if max > 0:
        value_error = value_error or f"{name} out of range! (min: {min}, max: {max})"
      else:
        value_error = f"{name} can't be zero!"
      #if value.lower() == "all" or value.lower() == "paul":
      if value.lower().startswith("a") or value.lower().startswith("p"):
        value = max
      elif value.lower().startswith("h"):
        value = max/2
      elif "%" in value:
        num = ""
        for letter in value:
          if letter.isdigit():
            num+=letter
        value = max*int(num)/100
    try:
      value = int(value)
    except:
      await Utility.embed_error(ctx,f"`{value}` is not an integer!")
      raise TypeError(f"Value is invalid!")
    if value < min:
      await Utility.embed_error(ctx, value_error)
      raise ValueError(f"Value is 0")
    if max != None:
      if value > max or max == 0:
        await Utility.embed_error(ctx, value_error)
        raise ValueError("Value greater than balance")
    return value


  async def get_value_from_interaction(interaction, value, *, min = 1, max = None, name:str = None, value_error = None, ephemeral = True):
    name = name or "Value"
    if max == None:
      value_error = value_error or f"{name} out of range! (min: {min})"
    else:
      if max > 0:
        value_error = value_error or f"{name} out of range! (min: {min}, max: {max})"
      else:
        value_error = f"{name} can't be zero!"
      #if value.lower() == "all" or value.lower() == "paul":
      if value.lower().startswith("a") or value.lower().startswith("p"):
        value = max
      elif value.lower().startswith("h"):
        value = max/2
      elif "%" in value:
        num = ""
        for letter in value:
          if letter.isdigit():
            num+=letter
        value = max*int(num)/100
    try:
      value = int(value)
    except:
      await Utility.embed_interaction_error(interaction, f"`{value}` is not an integer!", ephemeral)
      raise TypeError(f"Value is invalid!")
    if value < min:
      await Utility.embed_interaction_error(interaction, value_error, ephemeral)
      raise ValueError(f"Value is negative!")
    if max != None:
      if value > max or max == 0:
        await Utility.embed_interaction_error(interaction, value_error, ephemeral)
        raise ValueError("Value exceeds max!")
    return value


  async def get_upgrade(ctx, user, *input,):
    num = ""
    upgrade = ""
    for word in input:
      upgrade += f"{word} "
    upgrade = upgrade[:-1]
    
    for letter in upgrade:
        if letter.isdigit():
            num += letter
            upgrade = upgrade.replace(letter, '').strip()
    
    if num != "":
        num = int(num)
    else:
        num = 1

    if "all" in upgrade.lower():
      upgrade = upgrade.replace("all", '').strip()
      num = "all"
    if "paul" in upgrade:
      upgrade = upgrade.replace("paul", '').strip()
      num = "all"
      
    upgrade_word = upgrade.split(" ")[0]
    for key in user:
      if key.startswith("upgrade_"):
        if upgrade_word.lower() in key:
          name = key.replace("_"," ").replace("upgrade ","").title()
          return (key, num, name)
    await Utility.embed_error(ctx,f'Unknown upgrade: `{upgrade}`')

    
  async def embed_error_cooldown(ctx, message, cooldown):
    embed = discord.Embed(
    colour = (discord.Colour.red()),
    title = ":hourglass: Cooldown",
    description = f"{message} **{cooldown}**")
    await ctx.channel.send(embed=embed)

  async def embed_rob_banned(ctx, description):
    embed = discord.Embed(
    colour = (discord.Colour.red()),
    title = "🚫 ROB Banned",
    description = f"{description}")
    await ctx.channel.send(embed=embed)
  
  async def embed_error(ctx, message):
    embed = discord.Embed(
    colour = (discord.Colour.red()),
    title = ":x: Error",
    description = f"{message}")
    await ctx.channel.send(embed=embed)
  
  async def embed_interaction_error(interaction, message, ephemeral = True):
    embed = discord.Embed(
    colour = (discord.Colour.red()),
    title = ":x: Error",
    description = f"{message}")
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
  
  async def embed_message(ctx, emoji, title, message):
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = f"{emoji} {title}",
    description = f"{message}")
    await ctx.channel.send(embed=embed)

  async def superscript(n):
    return "".join(["⁰¹²³⁴⁵⁶⁷⁸⁹"[ord(c)-ord('0')] for c in str(n)]) 
  

  # Dev command.
  @commands.command()
  @commands.is_owner()
  async def inject(self, ctx, mention:discord.User, amount:int):
    user_dict = await Utility.get_user_data()
    user = user_dict[str(mention.id)]
    user["balance"] += amount
    await Utility.save_user_data(user_dict)
    await ctx.channel.send(f"Injected ${amount:,} into {mention.name}'s account.")

  # Dev command.
  @commands.command()
  @commands.is_owner()
  async def display(self, ctx):
    embed = discord.Embed(title="Title", description="Desc", color=0x00ff00)
    file = discord.File('graphics//rob.png', filename="rob.png")
    embed.add_field(name="Test!", value = "testtesttest")
    embed.set_image(url="attachment://rob.png")
    await ctx.send(file=file, embed=embed)


  
    
    


  #@client.command(aliases = ["info"])
  #@commands.is_owner()
  async def activity_info(self, member):
    for item in member.author.activities:
      info = f"{member.author.name} is playing {item.name}\n"
      try:
        info += f"application ID: {item.application_id}\n"
        info += f"assets: {item.assets}\n"
        info += f"details: {item.details}\n"
        info += f"emoji: {item.emoji}\n"
        info += f"end: {item.end}\n"
        info += f"large_image_text: {item.large_image_text}\n"
        info += f"small_image_url: {item.small_image_url}\n"
        info += f"start: {item.start}\n"
        info += f"state: {item.state}\n"
        info += f"timestamps: {item.timestamps}\n"
        info += f"type: {item.type}\n"
        info += f"url: {item.url}\n"
      except:
        info += f"album: {item.album}\n"
        info += f"album_cover_url: {item.album_cover_url}\n"
        info += f"artist: {item.artist}\n"
        info += f"artists: {item.artists}\n"
        info += f"color: {item.color}\n"
        info += f"colour: {item.colour}\n"
        info += f"created_at: {item.created_at}\n"
        info += f"duration: {item.duration}\n"
        info += f"end: {item.end}\n"
        info += f"name: {item.name}\n"
        info += f"party_id: {item.party_id}\n"
        info += f"start: {item.start}\n"
        info += f"title: {item.title}\n"
        info += f"track_id: {item.track_id}\n"
        info += f"type: {item.type}\n"
      print(info)

  # Dev command. Used to give myself upgrades for testing.
  @commands.command(aliases = ["x"])
  @commands.is_owner()
  async def upgrade_test(self, ctx, upgrade):
    #used to give myself upgrades for testing
    user_dict = await Utility.get_user_data()
    user = user_dict[str(188811740476211200)]
    user["upgrade_mystery_box"]["level"] -= 1
    await Utility.save_user_data(user_dict)
  
  
  # Dev command.
  @commands.command(aliases = ["manual_transfer"])
  @commands.is_owner()
  async def transfer(self, ctx, giver_user:discord.User, receiver_user:discord.User, amount):  
    user_dict = await Utility.get_user_data()
    giver = user_dict[str(giver_user.id)]
    receiver = user_dict[str(receiver_user.id)]
    amount = await Utility.get_value(ctx, amount, max = giver["balance"])
    giver["balance"] -= amount
    receiver["balance"] += amount
    await Utility.save_user_data(user_dict)
  
    print(f"Successfully transferred ${amount:,} from {giver_user.name} to {receiver_user.name}")
    await ctx.channel.send(f"Successfully transferred ${amount:,} from {giver_user.name} to {receiver_user.name}")

  async def activity_update(message):
    user_dict = await Utility.get_user_data()
    user = user_dict[str(message.author.id)]
    FMT = "%Y-%m-%d-%H:%M:%S"
    user["stat_last_active"] = str(datetime.now().strftime(FMT))
    await Utility.save_user_data(user_dict)
  
  
  # Dev command.
  @commands.command(aliases = ["database"])
  @commands.is_owner()
  async def database_transfer(self, ctx):
    #my_json = await Utility.get_user_data()
    #db["user_data"] = json.dumps(my_json)
    #print(json.loads(db["user_data"])["906087821373239316"]["balance"])
    user_dict = db.get_raw("user_dict")
    #user_dict = replit.database.dumps(db["user_dict"])
    db["user_data"] = user_dict
    print("success")
    

  

async def setup(client):
  await client.add_cog(Utility(client))