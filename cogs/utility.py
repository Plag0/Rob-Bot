import os
from discord.ext import commands
import discord
import requests
from datetime import datetime, timedelta

from replit import db
import replit
import json



class Utility(commands.Cog):
  def __init__(self, client):
    self.client = client

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
  
  
  
  @commands.command(aliases = ["update"])
  @commands.is_owner()
  async def update_users(self, ctx):
    #user_dict = await Utility.get_user_data()
    user_dict = db["user_dict"]
    for key in user_dict:
      user = user_dict[str(key)]

      #user["upgrade_weekly"]["prices"] = {"0":10000,"1":20000,"2":30000,"3":50000,"4":80000,"5":130000,"6":220000,"7":360000,"8":600000,"9":1000000}


      
      #For renaming a key
      #user["stat_jackpot_lowest_odds_victory"] = user["stat_lowest_odds_victory"]
      #del user["stat_lowest_odds_victory"]
  
      #For updating a value
      #user["key"] = value]
      #user["upgrade_change_lol"] = [0,0,500,1,1,1,"👤"]
      


      #user["upgrade_gold_transmutation"]["amount"] = round(await Utility.formula_calc(1, user["upgrade_gold_transmutation"]["level"]-1, user["upgrade_gold_transmutation"]["amount_formula"],0.1),1)

      
      #For adding one pair.
      #user.update( {"key":"value"} )
      #user.update( {"stat_mystery_box_special_quantity": 0} )
      #user.update( {"upgrade_mystery_box": {"level": 0, "amount": 0, "price": 3000, "max_level": 999, "single_use": True, "emoji": "🎁"}} )
      #"upgrade_mail": {"level": 0, "amount": 0, "price": 1000, "max_level": 5, "single_use": true, "emoji": "\ud83d\udceb"}
      #user.update( {"lol":{"summoner_name":"","region":""}} )
      
      #For adding multiple pairs.
      #user.update([ ("key","value"),("key","value") ])
      #user.update([ ("stat_mystery_box_highest_win", 0),("stat_mystery_box_quantity", 0),("stat_mystery_box_profit",0),("stat_mystery_box_loss",0) ])
  
      #For removing a pair.
      #del user["key"]
      print(f"Updated user: {key}")
    #await Utility.save_user_data(user_dict)
    print("Successfully updated users")
    await ctx.channel.send("Successfully updated all users.")


  async def round_number(amount:int, num:int):
    if num != None:
        return num * round(amount/num)
    else:
        return amount


  async def formula_calc(base_value:int, level:int, formula:str, round_by:int=None):
    round_by = round_by or None
    for i in range(level):
        base_value += eval(formula)
    return await Utility.round_number(base_value, round_by)

  @commands.command(aliases = ["backup"])
  @commands.is_owner()
  async def backup_user_data(self, title:str=None):
    #users = await Utility.get_user_data()
    user_dict = db["user_dict"]
    user_dict = replit.database.dumps(user_dict)
    #user_dict = replit.database.to_primitive(user_observed_dict)
    date = title or datetime.now()
    path = f"backups//user_data_backup_{date}.json"
    with open(path,"w+") as file_object:
      #json.dump(user_dict, file_object)
      file_object.write(user_dict)
    print(f"Saved user data as 'user_data_backup_{date}.json'")

  async def get_value(ctx, value, balance = None):
    if balance != None:
      #if value.lower() == "all" or value.lower() == "paul":
      if value.lower().startswith("a") or value.lower().startswith("p"):
        value = balance
    try:
      value = int(value)
    except:
      await Utility.embed_error(ctx,f"`{value}` is not an integer!")
      raise TypeError("Value is invalid!")
    if value <= 0:
      await Utility.embed_error(ctx,"Value can't be zero!")
      raise ValueError("Value is 0")
    if balance != None:
      if value > balance or balance == 0:
        await Utility.embed_error(ctx,"Value can't be greater than balance!")
        raise ValueError("Value greater than balance")
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
        num = None
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
  
  async def embed_error(ctx, message):
    embed = discord.Embed(
    colour = (discord.Colour.red()),
    title = ":x: Error",
    description = f"{message}")
    await ctx.channel.send(embed=embed)
  
  async def embed_message(ctx, emoji, title, message):
    embed = discord.Embed(
    colour = (discord.Colour.magenta()),
    title = f"{emoji} {title}",
    description = f"{message}")
    await ctx.channel.send(embed=embed)

  async def superscript(n):
    return "".join(["⁰¹²³⁴⁵⁶⁷⁸⁹"[ord(c)-ord('0')] for c in str(n)]) 
  
  @commands.command(aliases = ["total"])
  @commands.is_owner()
  async def inflation(self, ctx):
    total = 0
    users = await Utility.get_user_data()
    async for user in ctx.guild.fetch_members(limit=None):
      total += users[str(user.id)]["balance"]
    await ctx.channel.send(f"There are ${total:,} sloans in circulation")

  @commands.command()
  @commands.is_owner()
  async def inject(self, ctx, mention:discord.User, amount:int):
    #user_dict = await Utility.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(mention.id)]
    user["balance"] += amount
    #await Utility.save_user_data(user_dict)
    await ctx.channel.send(f"Injected ${amount:,} into {mention.name}'s account.")


  @commands.command()
  @commands.is_owner()
  async def display(self, ctx):
    #user_dict = await Utility.get_user_data()
    #print(user_dict)
    #from replit.database import AsyncDatabase
    #db = AsyncDatabase("https://kv.replit.com/v0/eyJhbGciOiJIUzUxMiIsImlzcyI6ImNvbm1hbiIsImtpZCI6InByb2Q6MSIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb25tYW4iLCJleHAiOjE2NTM0NjQ4NDIsImlhdCI6MTY1MzM1MzI0MiwiZGF0YWJhc2VfaWQiOiJkYTM4Yzg5Ny1mODE2LTRiNDUtOTJjOC0yMGM2MzViODgxMDkifQ.mgAAz2U4n9XaKvYh2IvPL-FxfIh_PHwOFwx1eeSuMIjvSkLRxj_2vejusWW4tOKK34qlTFGqOafTNrK_YJXNBg")
    #db["user_dict"] = user_dict
    print("success")
    #user_dict = db["user_dict"]
    #print(type(user_dict))
    #print(user_dict[str(ctx.author.id)]["rep"])
    
    


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



  @commands.command(aliases = ["manual_transfer"])
  @commands.is_owner()
  async def transfer(self, ctx, giver_user:discord.User, receiver_user:discord.User, amount):  
    #user_dict = await Utility.get_user_data()
    user_dict = db["user_dict"]
    giver = user_dict[str(giver_user.id)]
    receiver = user_dict[str(receiver_user.id)]
    amount = await Utility.get_value(ctx, amount, giver["balance"])
    giver["balance"] -= amount
    receiver["balance"] += amount
    #await Utility.save_user_data(user_dict)
  
    print(f"Successfully transferred ${amount:,} from {giver_user.name} to {receiver_user.name}")
    await ctx.channel.send(f"Successfully transferred ${amount:,} from {giver_user.name} to {receiver_user.name}")

  async def activity_update(message):
    #user_dict = await Utility.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(message.author.id)]
    FMT = "%Y-%m-%d-%H:%M:%S"
    user["stat_last_active"] = str(datetime.now().strftime(FMT))
    #await Utility.save_user_data(user_dict)

  #@commands.command(aliases = ["database"])
  #@commands.is_owner()
  #async def database_transfer(self, ctx):
    #my_json = await Utility.get_user_data()
    #db["user_data"] = json.dumps(my_json)
    #print(json.loads(db["user_data"])["906087821373239316"]["balance"])
    

  

def setup(client):
  client.add_cog(Utility(client))