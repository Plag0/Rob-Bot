import os
from discord.ext import commands
import discord
import requests
from datetime import datetime, timedelta

from replit import db
import json



class Utility(commands.Cog):
  def __init__(self, client):
    self.client = client

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

  
  async def save_user_data(users):
    db["user_data"] = json.dumps(users)
  
  
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
      await Utility.save_user_data(users)
  
  
  
  @commands.command(aliases = ["update"])
  @commands.is_owner()
  async def update_users(self, ctx):
    user_dict = await Utility.get_user_data()
    for key in user_dict:
      user = user_dict[str(key)]

      #FMT = "%Y-%m-%d-%H:%M:%S"
      #if user["daily_streak"] >= 1:
        #user["daily_streak"] += 2
        #new_time = datetime.now() - timedelta(hours = 10)
        #user["last_daily"] = (new_time.strftime(FMT))
      
      
      """amount = user["upgrade_gold_transmutation"][0]
      quantity = user["upgrade_gold_transmutation"][1]
      price = user["upgrade_gold_transmutation"][2]
      increment = user["upgrade_gold_transmutation"][3]
      max_level = user["upgrade_gold_transmutation"][4]
      single_use = user["upgrade_gold_transmutation"][5]
      emoji = user["upgrade_gold_transmutation"][6]
      if user["upgrade_gold_transmutation"][1] >= 1:
        quantity = 1
        amount = 1
      user["upgrade_gold_transmutation"] = [amount,quantity,1000,1,1,single_use,emoji]"""
      
      
      
      #For renaming a key
      #user["stat_jackpot_lowest_odds_victory"] = user["stat_lowest_odds_victory"]
      #del user["stat_lowest_odds_victory"]
  
      #For updating a value
      #user["key"] = value]
      #user["upgrade_change_lol"] = [0,0,500,1,1,1,"👤"]
      #user["stat_jackpot_lowest_odds_victory"] = 100

      #[0] is core amount
      #[1] is quantity
      #[2] is is price
      #[3] is increment
      #[4] is max upgrade
      #[5] is single use true or false
      #[6] is emoji
      """
      for key in user:
        if str(key).startswith("upgrade_") and type(key) == list:
          user[key] = {
            "level": key[1],
            "amount": key[0],
            "starting_price": 0,
            "price": key[2],
            "amount_formula": "custom",
            "price_formula": "custom",
            "max_level": key[4],
            "single_use": None,
            "emoji": "custom"
          }

      #upgrade example
      user["upgrade_daily"]["starting_price"] = 1000
      user["upgrade_daily"]["amount_formula"] = "i*100"
      user["upgrade_daily"]["price_formula"] = "base_value*(3-i*0.3**(i*0.11))"
      user["upgrade_daily"]["single_use"] = False
      user["upgrade_daily"]["emoji"] = "⏫"
      user["upgrade_daily"]["amount"] = await Utility.formula_calc(0, user["upgrade_daily"]["level"]+1, user["upgrade_daily"]["amount_formula"])
      user["upgrade_daily"]["price"] = await Utility.formula_calc(user["upgrade_daily"]["starting_price"], user["upgrade_daily"]["level"], user["upgrade_daily"]["price_formula"])

      user["upgrade_gold_transmutation"]["starting_price"] = 1000
      user["upgrade_gold_transmutation"]["amount_formula"] = "base_value*0.43"
      user["upgrade_gold_transmutation"]["price_formula"] = "base_value*0.43"
      user["upgrade_gold_transmutation"]["single_use"] = False
      user["upgrade_gold_transmutation"]["amount"] = round(await Utility.formula_calc(1, user["upgrade_gold_transmutation"]["level"]-1, user["upgrade_gold_transmutation"]["amount_formula"],0.1),1)
      user["upgrade_gold_transmutation"]["price"] = await Utility.formula_calc(10, user["upgrade_gold_transmutation"]["level"]-1, user["upgrade_gold_transmutation"]["price_formula"],5)


      user["upgrade_passive_income"]["starting_price"] = 3000
      user["upgrade_passive_income"]["amount_formula"] = "i*2"
      user["upgrade_passive_income"]["price_formula"] = "base_value*(.5+i*0.1)+(i*1048)"
      user["upgrade_passive_income"]["single_use"] = False
      user["upgrade_passive_income"]["amount"] = await Utility.formula_calc(0, user["upgrade_passive_income"]["level"]+1, user["upgrade_passive_income"]["amount_formula"])
      user["upgrade_passive_income"]["price"] = await Utility.formula_calc(user["upgrade_passive_income"]["starting_price"], user["upgrade_passive_income"]["level"]-1, user["upgrade_passive_income"]["price_formula"], 1000)


      user["upgrade_cooldown"]["starting_price"] = 20000
      user["upgrade_cooldown"]["amount_formula"] = "5"
      user["upgrade_cooldown"]["price_formula"] = "base_value*(2.5-i*0.18**(i*0.10355))"
      user["upgrade_cooldown"]["single_use"] = False
      user["upgrade_cooldown"]["amount"] = await Utility.formula_calc(0, user["upgrade_cooldown"]["level"], user["upgrade_cooldown"]["amount_formula"])
      user["upgrade_cooldown"]["price"] = await Utility.formula_calc(user["upgrade_cooldown"]["starting_price"], user["upgrade_cooldown"]["level"]-1, user["upgrade_cooldown"]["price_formula"], 1000)


      user["upgrade_streak"]["starting_price"] = 2500
      user["upgrade_streak"]["amount_formula"] = "(i+1)*5.5"
      user["upgrade_streak"]["price_formula"] = ""
      user["upgrade_streak"]["single_use"] = False
      user["upgrade_streak"]["amount"] = await Utility.formula_calc(0, user["upgrade_streak"]["level"], user["upgrade_streak"]["amount_formula"], 10)
      #user["upgrade_streak"]["price"] = await Utility.formula_calc()

      
      user["upgrade_weekly"]["starting_price"] = 10000
      user["upgrade_weekly"]["amount_formula"] = ""
      user["upgrade_weekly"]["price_formula"] = ""
      user["upgrade_weekly"]["single_use"] = False
      #user["upgrade_weekly"]["amount"] = await Utility.formula_calc()
      #user["upgrade_weekly"]["price"] = await Utility.formula_calc()
      
      
      
      #single-use example
      user["upgrade_mail"]["starting_price"] = 1000
      user["upgrade_mail"]["amount_formula"] = "1"
      user["upgrade_mail"]["price_formula"] = "0"
      user["upgrade_mail"]["single_use"] = True 
      user["upgrade_mail"]["emoji"] = "📫"

      user["upgrade_ban"]["starting_price"] = 1000000
      user["upgrade_ban"]["amount_formula"] = "1"
      user["upgrade_ban"]["price_formula"] = "0"
      user["upgrade_ban"]["single_use"] = True 
      user["upgrade_ban"]["emoji"] = "🔨"

      user["upgrade_kick"]["starting_price"] = 350000
      user["upgrade_kick"]["amount_formula"] = "1"
      user["upgrade_kick"]["price_formula"] = "0"
      user["upgrade_kick"]["single_use"] = True 
      user["upgrade_kick"]["emoji"] = "🦶"

      user["upgrade_restore"]["starting_price"] = 0
      user["upgrade_restore"]["amount_formula"] = "1"
      user["upgrade_restore"]["price_formula"] = "0"
      user["upgrade_restore"]["single_use"] = True 
      user["upgrade_restore"]["emoji"] = "🎊"

      user["upgrade_change_lol"]["starting_price"] = 500
      user["upgrade_change_lol"]["amount_formula"] = "1"
      user["upgrade_change_lol"]["price_formula"] = "0"
      user["upgrade_change_lol"]["single_use"] = True 
      user["upgrade_change_lol"]["emoji"] = "👤"
      """

      
      
        
        
      
      #For adding one pair.
      #user.update( {"key":"value"} )
      #user.update( {"lol":{"summoner_name":"","region":""}} )
      
      #For adding multiple pairs.
      #user.update([ ("key","value"),("key","value") ])
      #user.update([ ("stat_jackpot_highest_win", 0),("stat_jackpot_quantity", 0),("stat_jackpot_victory", 0),("stat_jackpot_defeat", 0),("stat_lowest_odds_victory", 0),("stat_jackpot_profit",0),("stat_jackpot_loss",0) ])
  
      #For removing a pair.
      #del user["key"]
  
      print(f"Successfully updated {key}")
    await Utility.save_user_data(user_dict)
    await ctx.channel.send("Successfully updated all users.")


  async def round_number(amount,num):
    if num != None:
        return num * round(amount/num)
    else:
        return amount

  #Returns the value for the next level.
  #If used for upgrade amounts rather than price make sure put a +1 after the level param.
  async def formula_calc(base_value:int, level:int, formula:str, round_by:int=None):
    round = round_by or None
    for i in range(level):
        base_value += eval(formula)
    return await Utility.round_number(base_value,round)

  @commands.command(aliases = ["backup"])
  @commands.is_owner()
  async def backup_user_data(self, ctx):
    users = await Utility.get_user_data()
    date = datetime.now()
    path = f"backups//user_data_backup_{date}.json"
    with open(path,"w+") as file_object:
      json.dump(users,file_object)
    print(f"Saved user data as 'user_data_backup_{date}.json'")
    await ctx.channel.send("Successfully backed up user data!")

  async def get_value(ctx, value, balance = None):
    if balance != None:
      if value.lower() == "all" or value.lower() == "paul":
        print("value is paul")
        value = balance
    
    try:
      value = int(value)
    except:
      await Utility.embed_error(ctx,f"{value} is not an integer!")
      raise TypeError("Value is invalid!")
    if value <= 0:
      await Utility.embed_error(ctx,"Value can't be zero!")
      raise ValueError("Value is 0")
    if balance != None:
      if value > balance or balance == 0:
        await Utility.embed_error(ctx,"Value can't be greater than balance!")
        raise ValueError("Value greater than balance")
    return value


  async def get_upgrade(ctx, upgrade, user):
    found = False
    for key in user:
      if key.startswith("upgrade_"):
        if upgrade.lower() in key:
          return key
          found = True
    if found != True:
      await Utility.embed_error(ctx,f'Unknown upgrade: "{upgrade}"')

    
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
    user_dict = await Utility.get_user_data()
    giver = user_dict[str(giver_user.id)]
    receiver = user_dict[str(receiver_user.id)]
    amount = await Utility.get_value(ctx, amount, giver["balance"])
    giver["balance"] -= amount
    receiver["balance"] += amount
    await Utility.save_user_data(user_dict)
  
    print(f"Successfully transferred ${amount:,} from {giver_user.name} to {receiver_user.name}")
    await ctx.channel.send(f"Successfully transferred ${amount:,} from {giver_user.name} to {receiver_user.name}")

  async def activity_update(message):
    user_dict = user_dict = await Utility.get_user_data()
    user = user_dict[str(message.author.id)]
    FMT = "%Y-%m-%d-%H:%M:%S"
    user["stat_last_active"] = str(datetime.now().strftime(FMT))
    await Utility.save_user_data(user_dict)

  #@commands.command(aliases = ["database"])
  #@commands.is_owner()
  #async def database_transfer(self, ctx):
    #my_json = await Utility.get_user_data()
    #db["user_data"] = json.dumps(my_json)
    #print(json.loads(db["user_data"])["906087821373239316"]["balance"])
    

  

def setup(client):
  client.add_cog(Utility(client))