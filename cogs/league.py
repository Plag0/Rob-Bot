import os
from discord.ext import commands
import discord
import requests
import asyncio
import time
from replit import db
from cogs.utility import Utility as util

class League(commands.Cog):
  def __init__(self, client):
    self.client = client

  active_users = []
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    if after not in self.active_users:
      for item in after.activities:
        if item.name == "League of Legends":
          if item.application_id == 401518684763586560 and item.state == "In Game":
            if item.details == "Summoner's Rift (Normal)":
              print(f"{after.name} confirmed in normal game, calling lol_passive.")
              gamemode = "Normal"
              await self.lol_passive(after,item,gamemode)
            elif item.details == "Summoner's Rift (Ranked)":
              gamemode = "Ranked"
              print(f"{after.name} confirmed in ranked game.")
              await self.lol_passive(after,item,gamemode)
              
  async def lol_passive(self, member, item, gamemode):
    self.active_users.append(member)
    print(f"Called lol_passive for {member.name}")
    api_key = os.environ['RIOT_KEY']
    #user_dict = await util.get_user_data()
    user_dict = db["user_dict"]
    user = user_dict[str(member.id)]
    channel = await self.client.fetch_channel(334046255384887296)
    
    if user["upgrade_gold_transmutation"]["level"] >= 1 and user["lol"]["summoner_name"] != "":
      summoner_name = user["lol"]["summoner_name"]
      region = user["lol"]["region"]
      summoner_data = await self.get_summoner_data(api_key, summoner_name, region)
      summoner_id = summoner_data[0]
      summoner_puuid = summoner_data[1]
      
      #get the game id for reference
      game_id = await self.get_game_id(api_key, summoner_id, region)
      player = await self.get_player(api_key, summoner_puuid, game_id, member)
      gold = player["goldEarned"]
      win = player["win"]
      champion_name = player["championName"]
      lane = player["lane"]
      kills = player["kills"]
      deaths = player["deaths"]
      assists = player["assists"]
      champion_damage = player["totalDamageDealtToChampions"]
      time_spent_dead = player["totalTimeSpentDead"]
      match_length = player["timePlayed"]
      minion_cs = player["totalMinionsKilled"]
      jungle_cs = player["neutralMinionsKilled"]
      cs = minion_cs + jungle_cs

      user_dict = db["user_dict"]
      user = user_dict[str(member.id)]
      rob = user_dict[str(906087821373239316)]
      
      level = user["upgrade_gold_transmutation"]["level"]
      percent = user["upgrade_gold_transmutation"]["amount"]
      amount = round(gold*(percent*0.01))

      user["balance"] += amount
      rob["balance"] -= amount
      user["stat_league_games_quantity"] += 1
      user["stat_gold_transmutation_profit"] += amount
      if gold > user["stat_highest_gold"]:
        user["stat_highest_gold"] = gold
      
      #level up check
      total_games = user["stat_league_games_quantity"]
      level_req = [0,15,20,30,40,60,85,120,175,250]
      games=0
      for i in range(level):
        games += level_req[i]
      games_remaining = level_req[level]-(total_games-games)
      level_up = False
      #if level up
      if level_req[level] <= total_games - games:
        user["upgrade_gold_transmutation"]["level"] += 1
        user["upgrade_gold_transmutation"]["amount"] = user["upgrade_gold_transmutation"]["amounts"][str( user["upgrade_gold_transmutation"]["level"] )]
        level_up = True
        
      #await util.save_user_data(user_dict)
      if member in self.active_users:
        self.active_users.remove(member)
  
      balance = user["balance"]
      outcome = ""
      if win == True:
        outcome = "won"
      else:
        outcome = "lost"

      games_remaining_message = ""
      if level < 10 and games_remaining > 0:
        games_remaining_message = f"Play **{games_remaining}** more games to reach level {level+1}.\n"

      icon = member.avatar_url
      embed = discord.Embed(
      colour = (discord.Colour.blue()),
      title = f"<:lol_passive:957853326626656307> League of Legends Passive",
      description = f"{member.name} **{outcome}** a **{gamemode.lower()}** game playing **{champion_name} {lane.capitalize()}**\n`{summoner_name}: {kills}/{deaths}/{assists} CS: {cs} Gold: ${gold:,} Length: {time.strftime('%M:%S', time.gmtime(match_length))}`\n`Damage to Champions: {champion_damage:,}`\n`Time Spent Dead: {time.strftime('%M:%S', time.gmtime(time_spent_dead))}`")
      embed.add_field(name = f":coin: Transmutation Level {level}! +${amount:,}", value=f"{games_remaining_message}**{percent}%** of your gold has been transformed into Sloans.\nYour new balance is **${balance:,}**.")
      embed.set_footer(icon_url = icon, text = f"{member.name}")
      await channel.send(embed=embed)

      #Level up embed
      if level_up == True:
        level = user["upgrade_gold_transmutation"]["level"]
        percent = user["upgrade_gold_transmutation"]["amount"]
        next_percent = user["upgrade_gold_transmutation"]["amounts"][str( level+1 )]
        
        level_up_embed = discord.Embed(
        colour = (discord.Colour.purple()),
        title = f"<:lol_passive:957853326626656307> Level UP!",
        description = f"{member.name} played **{total_games}** games and leveled up to level **{level}**!")
        level_up_embed.add_field(name = f"Stats", value=f"Current Level: **+ {percent}%**\nNext Level: **+ {next_percent}%** :lock: Play {level_req[level]} more games to unlock the next level!")
        level_up_embed.set_footer(icon_url = icon, text = f"{member.name}")
      if level_up == True:
        await channel.send(embed=level_up_embed)
      print(f"Gave {member.name} +${amount} sloans from {gold} gold, for finishing their league game!")
      
  
  async def get_summoner_data(self, api_key, summoner_name, region):
    print(f"RIOT API: Getting summoner data for {summoner_name}...")
    url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}'
    req = requests.get(url)
    summoner = req.json()
    summoner_id = summoner["id"]
    summoner_puuid = summoner["puuid"]
    summoner_data = [summoner_id,summoner_puuid]
    print(f"{summoner_name}'s Summoner ID is {summoner_id}")
    print(f"{summoner_name}'s PUUID is {summoner_puuid}")
    return summoner_data
  
  async def get_game_id(self, api_key, summoner_id, region):
    print("RIOT API: Getting game id...")
    url = f'https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={api_key}'
    for i in range(3):
      req = requests.get(url)
      current_match = req.json()
      try:
        game_id = current_match["gameId"]
        print(f"Successfully collected game ID: {game_id}")
        return game_id
      except:
        status_code = current_match["status"]["status_code"]
        print(f"Failed to get game ID - Status Code: {status_code} - Waiting 5 seconds")
        await asyncio.sleep(5)
      print("Failed to get game ID after 3 retries.")
      
  
  async def wait_for_lobby(self, member):
    print(f"Waiting for {member.name} to return to lobby")
    def validate(before,after):
      if after == member:
        for item in after.activities:
          if item.name == "League of Legends":
            if item.state == None or item.state == "In Lobby" or item.state == "In Queue":
              return True      
    try:
      await self.client.wait_for("member_update",check=validate,timeout=4800.0)
    except asyncio.TimeoutError:
      print(f"Game timeout expired after 4800 seconds!")
      self.active_users.remove(member)
  
  
  async def get_player(self, api_key, summoner_puuid, game_id, member):
    await self.wait_for_lobby(member)
    await asyncio.sleep(15)
    for i in range(3):
      #gets the most recent match id
      print("RIOT API: Getting list of recent matches...")
      url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?start=0&count=1&api_key={api_key}'
      req = requests.get(url)
      match_list = req.json()
      #gets the data for the most recent match
      recent_match = await self.get_match(api_key, match_list[0])
      if recent_match["info"]["gameId"] == game_id:
        print("Game IDs match, returning gold amount.")
        for player in recent_match["info"]["participants"]:
          if player["puuid"] == summoner_puuid:
            return player
      else:
        print("Most recent Game ID doesn't match, match history probably hasn't updated - waiting 20 seconds...")
      await asyncio.sleep(20)
    print(f"Failed to get match data for gameId: {game_id} after 3 retries")
    self.active_users.remove(member)
  
    
  async def get_match(self, api_key, match_id):
    print(f"RIOT API: Getting match data for {match_id}...")
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    req = requests.get(url)
    data = req.json()
    return data

def setup(client):
  client.add_cog(League(client))