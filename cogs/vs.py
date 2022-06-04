from discord.ext import commands
import discord
import requests
import asyncio
import html
import random
from replit import db
from cogs.utility import Utility as util
#import json

class Vs(commands.Cog):
  def __init__(self, client):
    self.client = client

  cooldown = []
  @commands.command(aliases = ["challenge"])
  async def vs(self, ctx, mention:discord.User, game:str, amount, *data):
    user_dict = db["user_dict"]
    host = user_dict[str(ctx.author.id)]
    opponent = user_dict[str(mention.id)]
    amount = await util.get_value(ctx,amount,host["balance"])

    gamemodes = {
      "flip":Vs.flip_1v1,
      "trivia":Vs.trivia_1v1}
    
    #Exception Handling
    if opponent["balance"] < amount:
      await util.embed_error(ctx, f"{mention.mention}'s balance is too low!")
      return
    if ctx.author == mention:
      await util.embed_error(ctx, "You can't challenge yourself!")
      return
    if game.lower() not in gamemodes:
      await util.embed_error(ctx, f"Unknown gamemode: `{game}`")
      return
      
    if game.lower() == "flip":
      name = "Coin Flip"
      emoji = "🎲"
      colour = discord.Colour.from_rgb(255,201,74)
      title = "❓ Side"
      if len(data) <= 0:
        choice = "Random Side"
        data = {"side":random.choice(["heads","tails"])}
      else:
        if len(data) > 1:
          await util.embed_error(ctx, f"Invalid data for **Flip**: `{data[1]}`")
          return
        if data[0].lower() == "h" or data[0].lower() == "heads":
          choice = "Heads"
          title = "<:heads:981507458944098345> Side"
        elif data[0].lower() == "t" or data[0].lower() == "tails":
          choice = "Tails"
          title = "<:tails:981507300047065088> Side"
        else:
          await util.embed_error(ctx, f"`{data[0]}` is not a valid side! Try `h` or `t`.")
          return
        data = {"side":choice.lower()}
        
    elif game.lower() == "trivia":
      name = "Trivia Quiz"
      emoji = "🧠"
      colour = discord.Colour.from_rgb(255,201,74)
      title = f"❓ Category"
      categories = {"Geography": (22,'🌏'), "General": (9,'🧩'), "Games": (15,'🎮'), "Films": (11,'🎞'), "TV":(14,'🎬'), "Science": (17,'🧪'), "Computers": (18,'🖥'), "Sports":(21,'🏀'), "History": (23,'🗿'), "Animals":(27,'🐶'), "Vehicles":(28,'🚗'), "Anime":(31,'🎌'), "Cartoons":(32,'✏')}
      if len(data) <= 0:
        choice = "*Random Category*"
        null, category = random.choice(list(categories.items()))
        #correct_answer = list(answers.keys())[list(answers.values()).index(html.unescape(trivia['correct_answer']))].lower()
        data = {"category":category[0], "emoji":category[1], "win_thresh":1}
      else:
        if len(data) > 2:
          await util.embed_error(ctx, f"Invalid data for **Trivia**: `{data[2]}`")
          return
        found = False
        for key in categories:
          if data[0].lower() in key.lower():
            category = categories[key][0]
            category_emoji = categories[key][1]
            choice = key
            found = True
            break
        if found == False:
          await util.embed_error(ctx,f"Unknown category for Trivia: `{data[0]}`")
          return
        if len(data) == 2:
          try:
            win_thresh = int(data[1])
            if win_thresh > 100:
              raise ValueError
          except:
            await util.embed_error(ctx,f"Invalid amount of rounds: `{data[1]}`")
            return
        else:
          win_thresh = 1
        data = {"category":category, "emoji":category_emoji, "win_thresh":win_thresh}
        title = f"{category_emoji} Category"
    
    #Host win rate.
    total_games = host[f"stat_{game.lower()}_victory"] + host[f"stat_{game.lower()}_defeat"]
    if total_games != 0:
      host_winrate = round((host[f"stat_{game.lower()}_victory"] / total_games) * 100, 1)
    else:
      host_winrate = 0
    #Opponent win rate.
    total_games = opponent[f"stat_{game.lower()}_victory"] + opponent[f"stat_{game.lower()}_defeat"]
    if total_games != 0:
      opponent_winrate = round((opponent[f"stat_{game.lower()}_victory"] / total_games) * 100, 1)
    else:
      opponent_winrate = 0

    host_winrate = f" {host_winrate}%"
    opponent_winrate = f" {opponent_winrate}%"
      
    embed = discord.Embed(
    colour = colour,
    title = f":crossed_swords: {game.split('_')[0].capitalize()} Challenge",
    description = f"**{ctx.author.name}** has challenged **{mention.name}** to a **{name}**\n{ctx.author.mention} **{host_winrate} VS {opponent_winrate}** {mention.mention}\n\nTo accept this challenge, mention {ctx.author.name} and type accept.\nExample: `accept @{ctx.author.name}`\n\n***TIP**: To cancel or decline this challenge, type **$cancel** or **$decline***")
    embed.add_field(name = f"{emoji} Gamemode", value = f"{name}", inline = True)
    embed.add_field(name = "**:moneybag: Wager**", value = f"${amount:,} Sloans", inline = True)
    if len(data) >= 1:
      embed.add_field(name = title, value = choice, inline = True) 
    if len(data) >= 2:
      embed.add_field(name = f"**🎯 Best of {(data['win_thresh']*2)-1}:**", value = f"First to **{data['win_thresh']}**", inline = True) 
    await ctx.channel.send(embed=embed)
    
    def validate(m):
      return m.author == mention and ("accept") in m.content.lower() and ctx.author.mentioned_in(m) or m.author == mention and "$decline" in m.content.lower() or m.author == ctx.author and "$cancel" in m.content.lower()
    try:
      input = await self.client.wait_for("message",check=validate,timeout=60.0)
    except asyncio.TimeoutError:
      await util.embed_error(ctx,f"{ctx.author.mention}'s challenge has been cancelled. {mention.mention} didn't accept in time.")
      return
    if input.content.lower() == "$cancel" or input.content.lower() == "$decline":
      await util.embed_message(ctx,":no_entry:","Cancelled",f"{input.author.name} has cancelled the challenge.")
      return
    if ctx.author in Vs.cooldown:
      await util.embed_error(ctx, "You can't participate in multiple challenges at once!")
      return
    Vs.cooldown.append(ctx.author)
    await gamemodes[game](self, ctx, mention, amount, data)
    if ctx.author in Vs.cooldown:
      Vs.cooldown.remove(ctx.author)
  
  async def flip_1v1(self, ctx, mention, amount, data):
    user_dict = db["user_dict"]
    host = user_dict[str(ctx.author.id)]
    opponent = user_dict[str(mention.id)]
    host_bet = data["side"]
    
    flip = random.choice(["heads","tails"])
      
    if flip == "tails":
      coin = "https://cdn.discordapp.com/attachments/894744339794780220/938857632712786010/sloan_tails_v6.png"
    else:
      coin = "https://cdn.discordapp.com/attachments/894744339794780220/938857632389799986/sloan_heads_v3.png"
    
    if flip == host_bet:
      winner = host
      loser = opponent
      discord_winner = ctx.author
      discord_loser = mention
    else:
      winner = opponent
      loser = host
      discord_winner = mention
      discord_loser = ctx.author
    
    winner["balance"] += amount
    winner["stat_flip_profit"] += amount
    winner["stat_flip_win_streak"] += 1
    if winner["stat_flip_win_streak"] > winner["stat_highest_flip_win_streak"]:
      winner["stat_highest_flip_win_streak"] = winner["stat_flip_win_streak"]
    if winner["balance"] > winner["stat_highest_balance"]:
      winner["stat_highest_balance"] = winner["balance"]
    if amount > winner["stat_highest_flip"]:
      winner["stat_highest_flip"] = amount
    winner["stat_flip_quantity"] += 1
    winner["stat_flip_victory"] += 1
    
    loser["balance"] -= amount
    loser["stat_flip_loss"] -= amount
    loser["stat_flip_win_streak"] = 0
    if amount > loser["stat_highest_flip"]:
      loser["stat_highest_flip"] = amount
    loser["stat_flip_quantity"] += 1
    loser["stat_flip_defeat"] += 1

    winstreak = winner["stat_flip_win_streak"]
    winner_balance = winner["balance"]
    loser_balance = loser["balance"]
    icon = discord_winner.avatar_url
  
    embed = discord.Embed(
    colour = discord.Colour.magenta(),
    title = f":money_with_wings: Flip | {flip.capitalize()}")
    embed.add_field(name = f"{discord_winner.name} wins!", value = f"**${amount:,}** has been added to {discord_winner.name}'s account!\n{discord_winner.name}'s new balance is $**{winner_balance:,}**.\n{discord_loser.name}'s new balance is $**{loser_balance:,}**.", inline = True)
    if winstreak >= 3:
      embed.add_field(name = f":tada: Win Streak!",value = f"{discord_winner.name} is on a **{winstreak}** flip win streak!", inline = False)
    embed.set_thumbnail(url = coin)
    embed.set_footer(icon_url = icon, text = f"{ctx.author.name} vs {mention.name}")
    await ctx.channel.send(embed=embed)
  
  
  
  
  async def trivia_1v1(self, ctx, mention, amount, data):
    user_dict = db["user_dict"]
    host = user_dict[str(ctx.author.id)]
    opponent = user_dict[str(mention.id)]
    
    host_wins = 0
    opponent_wins = 0
    win_thresh = data["win_thresh"]
    final_score = ""
    while win_thresh > host_wins and win_thresh > opponent_wins:
      url = f"https://opentdb.com/api.php?amount=1&category={data['category']}"
      req = requests.get(url)
      trivia = req.json()["results"][0]
    
      embed = discord.Embed(
      colour = discord.Colour.green(),
      title = f"{data['emoji']} Trivia | {trivia['category']}",
      description = f"Difficulty: **{trivia['difficulty'].capitalize()}**\n\n{html.unescape(trivia['question'])}")
      if trivia['type'] == "multiple":
        answer_list = []
        for item in trivia['incorrect_answers']:
          answer_list.append(html.unescape(item))
        answer_list.append(html.unescape(trivia['correct_answer']))
        random.shuffle(answer_list)
        
        answers = {"A":f"{answer_list[0]}","B":f"{answer_list[1]}","C":f"{answer_list[2]}","D":f"{answer_list[3]}"}
        correct_answer = list(answers.keys())[list(answers.values()).index(html.unescape(trivia['correct_answer']))].lower()
        embed.add_field(name = f"A.", value = f"{answers['A']}", inline = True)
        embed.add_field(name = f"B.", value = f"{answers['B']}", inline = True)
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
        embed.add_field(name = f"C.", value = f"{answers['C']}", inline = True)
        embed.add_field(name = f"D.", value = f"{answers['D']}", inline = True)
        embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      else:
        embed.add_field(name = f"True or False?", value = '\u200b', inline = True)
        correct_answer = trivia['correct_answer'].lower()
      
      await ctx.channel.send(embed=embed)
    
      def validate(m):
        return m.author.id == mention.id and m.channel == ctx.channel or m.author.id == ctx.author.id and m.channel == ctx.channel
      try:
        input = await self.client.wait_for("message",check=validate,timeout=120.0)
      except asyncio.TimeoutError:
        Vs.cooldown.remove(ctx.author)
        await util.embed_error(ctx,f"Challenge cancelled. No one answered in time.")
        return
      
      print(f"{input.content.lower()},{correct_answer} by {input.author.name}")
      wrong_message = ""
      if input.content.lower() in correct_answer and len(input.attachments) <= 0 and len(input.stickers) <= 0:
        right_answer = True
        print("right answer")
        emoji = "✅"
        await input.add_reaction(emoji)
        winner = input.author
        icon = input.author.avatar_url
        #if the host wins
        if input.author.id == ctx.author.id:
          host_wins +=1
          winner_data = host
          loser = mention
          loser_data = opponent
        #if the mentioned wins
        elif input.author.id == mention.id:
          opponent_wins +=1
          winner_data = opponent
          loser = ctx.author
          loser_data = host
      
      #if the messager got it wrong
      else:
        right_answer = False
        print("wrong answer")
        emoji = "❌"
        await input.add_reaction(emoji)
        wrong_message = f"The correct answer was **{correct_answer.capitalize()}**!\n"
        loser = input.author
        if input.author.id == ctx.author.id:
          opponent_wins +=1
          loser_data = host
          winner = mention
          icon = mention.avatar_url
          winner_data = opponent
        elif input.author.id == mention.id:
          host_wins +=1
          loser_data = opponent
          winner = ctx.author
          icon = ctx.author.avatar_url
          winner_data = host
      
      if len(data) >= 2 and host_wins <= win_thresh and opponent_wins <= win_thresh:
        correct_message = ""
        final_score = f"\n{ctx.author.name} - **{host_wins}  VS  {opponent_wins}** - {mention.name}\n\n"
        if right_answer == False:
          correct_message = f"The correct answer was **{correct_answer.capitalize()}**!"
        if host_wins < win_thresh and opponent_wins < win_thresh:
          await util.embed_message(ctx,"🎭","Score",f"{correct_message}\n\n{ctx.author.name} - **{host_wins}  VS  {opponent_wins}** - {mention.name}")
        await asyncio.sleep(1.3)
  
    winner_data["balance"] += amount
    winner_data["stat_trivia_profit"] += amount
    winner_data["stat_trivia_victory"] += 1
    loser_data["balance"] -= amount
    loser_data["stat_trivia_loss"] -= amount
    loser_data["stat_trivia_defeat"] += 1
    winner_data["stat_trivia_win_streak"] += 1
    loser_data["stat_trivia_win_streak"] = 0
    if winner_data["stat_trivia_win_streak"] > winner_data["stat_highest_trivia_win_streak"]:
      winner_data["stat_highest_trivia_win_streak"] = winner_data["stat_trivia_win_streak"]
    if winner_data["balance"] > winner_data["stat_highest_balance"]:
      winner_data["stat_highest_balance"] = winner_data["balance"]
  
    winner_balance = winner_data["balance"]
    loser_balance = loser_data["balance"]
    winstreak = winner_data["stat_trivia_win_streak"]
  
    embed = discord.Embed(
    colour = discord.Colour.green(),
    title = f":earth_asia: Trivia | {trivia['category']}")
    embed.add_field(name = f"{winner.name} wins!", value = f"{wrong_message}{final_score}**${amount:,}** has been added to {winner.name}'s account!\n{winner.name}'s new balance is $**{winner_balance:,}**.\n{loser.name}'s new balance is $**{loser_balance:,}**.", inline = True)
    if winstreak >= 3:
      embed.add_field(name = f":tada: Win Streak!",value = f"{winner.name} is on a **{winstreak}** trivia win streak!", inline = False)
    embed.set_footer(icon_url = icon, text = f"{ctx.author.name} vs {mention.name}")
    await ctx.channel.send(embed=embed)
    Vs.cooldown.remove(ctx.author)
  
  
  
  
  @commands.command()
  async def trivia(self, ctx):
    command_help = "Trivia is a 1v1 gamemode that can be played using the $vs command.\nIn Trivia, both players are presented with a random question from a category of the host's choosing. The first player to answer the question correctly wins a point. If you answer incorrectly the other player wins that point.\n\nTo challenge someone to a game of Trivia, format the command as follows: ```$vs (@mention) trivia (bet) (category*) (points to win*)```*Arguments followed by an asterisk are optional.*\n\nReal Example:```$vs @Molasso trivia 100 geography 3```\n"
    categories = {"Geography": (22,'🌏'), "General": (9,'🧩'), "Games": (15,'🎮'), "Films": (11,'🎞'), "TV":(14,'🎬'), "Science": (17,'🧪'), "Computers": (18,'🖥'), "Sports":(21,'🏀'), "History": (23,'🗿'), "Animals":(27,'🐶'), "Vehicles":(28,'🚗'), "Anime":(31,'🎌'), "Cartoons":(32,'✏')}
    message = ""
    count = 0
    for key in categories:
      emoji = categories[key][1]
      count += 1
      message += f"**{count}.**  {emoji}  {key}\n"
    await util.embed_message(ctx,"🧠","Trivia Information", f"{command_help}\n**Trivia Categories:**\n{message}\n***TIP**: When choosing a category it's not necessary to type the full name.*")

def setup(client):
  client.add_cog(Vs(client))