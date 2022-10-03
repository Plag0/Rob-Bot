import os
from discord.ext import commands
import discord
import requests
import asyncio
import time
import json
from cogs.utility import Utility as util

class League(commands.Cog):
  def __init__(self, client):
    self.client = client


  @commands.command(aliases = ["lol","gold","transmutate","transmutation"])
  @commands.cooldown(3, 1200, commands.BucketType.user)
  async def league(self, ctx):
    user_dict = await util.get_user_data()
    user = user_dict[str(ctx.author.id)]
    summoner_name = user["lol"]["summoner_name"]
    region = user["lol"]["region"]
    start_time = user["lol"]["last_request_epoch"]
    level = user["upgrade_gold_transmutation"]["level"]
    percent = user["upgrade_gold_transmutation"]["amount"]
    api_key = os.environ['RIOT_KEY']
    summoner_id, summoner_puuid = await League.get_summoner_data(self, api_key, summoner_name, region)
    host = "sea"
    if region != "oc1":
      host = "americas"

    embed = discord.Embed(
      colour = (discord.Colour.blue()),
      title = f"<:lol_passive:957853326626656307> Gold Transmutation | Level **{level}**",
      description = f"<a:loading:998460290280722486> Loading match history for **{summoner_name}**..."
    )
    embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"{ctx.author.name}")
    msg = await ctx.channel.send(embed=embed)

    try:
      # Gets match history.
      ranked = f'https://{host}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?startTime={start_time}&type=ranked&start=0&count=20&api_key={api_key}'
      normal = f'https://{host}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?startTime={start_time}&type=normal&start=0&count=20&api_key={api_key}'
      ranked = requests.get(ranked)
      normal = requests.get(normal)
      match_history = [ranked.json(), normal.json()]

      # Appends 
      player_history = []
      for type in match_history:
        for game in type:
          url = f'https://{host}.api.riotgames.com/lol/match/v5/matches/{game}?api_key={api_key}'
          req = requests.get(url)
          data = req.json()
          for player in data["info"]["participants"]:
            if player["puuid"] == summoner_puuid:
              player_history.append(player)
        if len(player_history) == 0:
          raise
    except Exception as e:
      print(e)
      embed.description = "❌ **No new matches.**"
      await msg.edit(embed=embed)
      return
    
    level_up = False
    level_req = [0,15,20,30,40,60,85,120,175,250]
    total_games = user["stat_league_games_quantity"]
    void_games = 0
    for i in range(level):
      void_games += level_req[i]
    games_remaining = level_req[level] - (total_games - void_games)
    
    amount = 0
    wins = 0
    losses = 0
    gold = []
    kills = []
    deaths = []
    assists = []
    cs = []
    champion = []
    damage = []
    time_dead = []
    match_length = []
    
    # Payout.
    user = user_dict[str(ctx.author.id)]
    rob = user_dict[str(self.client.user.id)]
    for game in player_history:
      games_remaining -= 1
      total_games += 1
      gold.append(game["goldEarned"])
      kills.append(game["kills"])
      deaths.append(game["deaths"])
      assists.append(game["assists"])
      cs.append(game["totalMinionsKilled"] + game["neutralMinionsKilled"])
      champion.append(game["championName"])
      damage.append(game["totalDamageDealtToChampions"])
      time_dead.append(game["totalTimeSpentDead"])
      match_length.append(game["timePlayed"])
      print(game["win"])
      if game["win"]:
        wins += 1
      else:
        losses += 1
      
      amount += round(game["goldEarned"] * (user["upgrade_gold_transmutation"]["amount"] * 0.01))

      # Level Up.
      if games_remaining <= 0:
        with open("upgrades.json","r") as f:
          d = json.load(f)
        user["upgrade_gold_transmutation"]["level"] += 1
        user["upgrade_gold_transmutation"]["amount"] = d["upgrade_gold_transmutation"]["amounts"][str( user["upgrade_gold_transmutation"]["level"] )]
        new_percent = user["upgrade_gold_transmutation"]["amount"]
        level = user["upgrade_gold_transmutation"]["level"]
        void_games = 0
        for i in range(level):
          void_games += level_req[i]
        games_remaining = level_req[level] - (total_games - void_games)
        level_up = True
        
    # Stats.
    user["lol"]["last_request_epoch"] = int(time.time())
    user["stat_league_games_quantity"] = total_games
    user["balance"] += amount
    user["total_cash_flow"] += amount
    user["daily_cash_flow"] += amount
    rob["balance"] -= amount
    rob["total_cash_flow"] += amount
    rob["daily_cash_flow"] += amount
    user["stat_league_games_quantity"] += 1
    user["stat_gold_transmutation_profit"] += amount
    if user["balance"] > user["stat_highest_balance"]:
      user["stat_highest_balance"] = user["balance"]
    if max(gold) > user["stat_highest_gold"]:
        user["stat_highest_gold"] = max(gold)
    
    await util.save_user_data(user_dict)

    # Purely cosmetic from here (for embed).
    games_played = len(player_history)
    most_played = max(set(champion), key = champion.count)
    percent_played = round(champion.count(most_played) / games_played * 100, 2)
    percent_dead = round(sum(time_dead) / sum(match_length) * 100, 2)
    avg_kills = int(sum(kills)/len(kills))
    avg_deaths = int(sum(deaths)/len(deaths))
    avg_assists = int(sum(assists)/len(assists))
    avg_damage = int(sum(damage)/len(damage))
    avg_cs = int(sum(cs)/len(cs))
    ks = " " * (3 - (len(str(avg_kills)) - 1))
    ds = " " * (3 - (len(str(avg_deaths)) - 1))
    ass = " " * (3 - (len(str(avg_assists)) - 1))
    css = " " * (3 - (len(str(avg_cs)) - 1))
    hi_k = max(kills)
    hi_d = max(deaths)
    hi_a = max(assists)
    hi_cs = max(cs)
    hks = " " * (3 - (len(str(hi_k)) - 1))
    hds = " " * (3 - (len(str(hi_d)) - 1))
    hass = " " * (3 - (len(str(hi_a)) - 1))
    hcss = " " * (3 - (len(str(hi_cs)) - 1))
    space = " " * 24
    avg = ""
    avgs = ""
    high = ""
    highs = ""
    a = "a"
    s = ""
    if games_played > 1:
      a = f"**{games_played}**"
      s = "s"
    
    desc = ""
    if len(player_history) == 1:
      if wins >= 1:
        outcome = "won"
      else:
        outcome = "lost"
      desc += f"{summoner_name} {outcome} a game and generated **${amount:,}**\n"
    else:
      desc += f"{summoner_name} played {a} game{s} and generated **${amount:,}**\n"
      
    desc += f"(*${sum(gold):,} gold at a {percent}% conversion rate*)\n"
    desc += f"{ctx.author.name}'s new balance is ${user['balance']:,}.\n\n"
    if len(player_history) > 1:
      desc += f"• Won **{wins}** games and lost {losses} for a {round(wins / (wins+losses) * 100, 2)}% winrate.\n"
    desc += f"• Played for **{time.strftime('%H:%M:%S', time.gmtime(sum(match_length)))}** and spent {percent_dead}% of it dead.\n"
    desc += f"• Dealt an average of **{avg_damage:,}** damage, peaking at {max(damage):,}.\n"
    if len(player_history) > 1:
      desc += f"• Played **{most_played}** {percent_played}% of the time.\n"
      avg = "Average"
      high = "Highest"
      avgs = "       "
      highs = "       "
    else:
      desc += f"Played **{most_played}**\n"
    desc += f"`{avg} K | D | A | CS  `\n"
    desc += f"`{avgs} {avg_kills}{ks}{avg_deaths}{ds}{avg_assists}{ass}{avg_cs}{css}`\n"
    if len(player_history) > 1:
      desc += f"`{space}`\n"
      desc += f"`{high} K | D | A | CS  `\n"
      desc += f"`{highs} {hi_k}{hks}{hi_d}{hds}{hi_a}{hass}{hi_cs}{hcss}`\n"
    games_remaining_message = ""
    if level < 10 and games_remaining > 0:
      desc += f"*Play {games_remaining} more games to reach level {level+1}*\n"
    if level_up:
      embed.add_field(name = f"<:level_up:1014969201011728394> Level Up!", value = f"You played {total_games} games and unlocked **Gold Transmutation Level {level}**\nYour conversion rate has increased from {percent}% » **{new_percent}%**")
      embed.colour = discord.Colour.from_rgb(212,110,185)
    embed.set_thumbnail(url = ctx.author.display_avatar.url)
    embed.description = desc
    await msg.edit(embed = embed)
      


    

  active_users = []
  async def league_check(self, after):
    if after not in League.active_users:
      for item in after.activities:
        if item.name == "League of Legends":
          if item.application_id == 401518684763586560 and item.state == "In Game":
            if item.details == "Summoner's Rift (Normal)":
              print(f"{after.name} confirmed in normal game, calling lol_passive.")
              gamemode = "Normal"
              #await League.lol_passive(self,after,item,gamemode)
            elif item.details == "Summoner's Rift (Ranked)":
              gamemode = "Ranked"
              print(f"{after.name} confirmed in ranked game.")
              #await League.lol_passive(self,after,item,gamemode)
              
  async def lol_passive(self, member, item, gamemode):
    League.active_users.append(member)
    print(f"Called lol_passive for {member.name}")
    api_key = os.environ['RIOT_KEY']
    user_dict = await util.get_user_data()
    user = user_dict[str(member.id)]
    channel = await self.client.fetch_channel(334046255384887296)
    
    if user["upgrade_gold_transmutation"]["level"] >= 1 and user["lol"]["summoner_name"] != "":
      summoner_name = user["lol"]["summoner_name"]
      region = user["lol"]["region"]
      summoner_id, summoner_puuid = await League.get_summoner_data(self, api_key, summoner_name, region)
      
      #get the game id for reference
      game_id = await League.get_game_id(self, api_key, summoner_id, region)
      player = await League.get_player(self, api_key, summoner_puuid, game_id, member, region)
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

      user_dict = await util.get_user_data()
      user = user_dict[str(member.id)]
      rob = user_dict[str(906087821373239316)]
      
      level = user["upgrade_gold_transmutation"]["level"]
      percent = user["upgrade_gold_transmutation"]["amount"]
      amount = round(gold*(percent*0.01))

      user["balance"] += amount
      user["total_cash_flow"] += amount
      user["daily_cash_flow"] += amount
      rob["balance"] -= amount
      rob["total_cash_flow"] += amount
      rob["daily_cash_flow"] += amount
      user["stat_league_games_quantity"] += 1
      user["stat_gold_transmutation_profit"] += amount
      if gold > user["stat_highest_gold"]:
        user["stat_highest_gold"] = gold
      if user["balance"] > user["stat_highest_balance"]:
        user["stat_highest_balance"] = user["balance"]
      
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
        with open("upgrades.json","r") as f:
          d = json.load(f)
        user["upgrade_gold_transmutation"]["level"] += 1
        user["upgrade_gold_transmutation"]["amount"] = d["upgrade_gold_transmutation"]["amounts"][str( user["upgrade_gold_transmutation"]["level"] )]
        level_up = True
        
      await util.save_user_data(user_dict)
      if member in League.active_users:
        League.active_users.remove(member)
  
      balance = user["balance"]
      outcome = ""
      if win == True:
        outcome = "won"
      else:
        outcome = "lost"

      games_remaining_message = ""
      if level < 10 and games_remaining > 0:
        games_remaining_message = f"Play **{games_remaining}** more games to reach level {level+1}.\n"

      icon = member.display_avatar.url
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
        next_percent = d["upgrade_gold_transmutation"]["amounts"][str( level+1 )]
        
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
    print(f"{summoner_name}'s Summoner ID is {summoner_id}")
    print(f"{summoner_name}'s PUUID is {summoner_puuid}")
    return summoner_id, summoner_puuid
  
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
  
  
  async def get_player(self, api_key, summoner_puuid, game_id, member, region):
    await League.wait_for_lobby(self, member)
    await asyncio.sleep(15)
    for i in range(3):
      #gets the most recent match id
      print("RIOT API: Getting list of recent matches...")
      if region == "oc1":
        url = f'https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?start=0&count=1&api_key={api_key}'
      else:
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?start=0&count=1&api_key={api_key}'
      req = requests.get(url)
      match_list = req.json()
      #gets the data for the most recent match
      recent_match = await League.get_match(self, api_key, match_list[0], host)
      if recent_match["info"]["gameId"] == game_id:
        print("Game IDs match, returning gold amount.")
        for player in recent_match["info"]["participants"]:
          if player["puuid"] == summoner_puuid:
            return player
      else:
        print("Most recent Game ID doesn't match, match history probably hasn't updated - waiting 20 seconds...")
      await asyncio.sleep(20)
    print(f"Failed to get match data for gameId: {game_id} after 3 retries")
    League.active_users.remove(member)
  
    
  async def get_match(self, api_key, match_id, host):
    print(f"RIOT API: Getting match data for {match_id}...")
    url = f'https://{host}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    req = requests.get(url)
    data = req.json()
    return data

async def setup(client):
  await client.add_cog(League(client))