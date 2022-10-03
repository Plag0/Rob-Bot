from discord.ext import commands
import discord
import requests
import asyncio
import html
import random
from datetime import datetime
from cogs.utility import Utility as util
from cogs.rewards import Rewards as rewards
from discord import Button

class Vs(commands.Cog):
  def __init__(self, client):
    self.client = client
  
  cooldown = []
  @commands.command(aliases = ["challenge"])
  async def vs(self, ctx, mention:discord.User, game:str, amount, *data):
    # I want the colours of the winning embeds to be picked by users as their custom colour elsewhere.
    user_dict = await util.get_user_data()
    host = user_dict[str(ctx.author.id)]
    if host["rob_banned"] == True:
      await util.embed_rob_banned(ctx, "You don't have permission to perform this action")
      return
  
    opponent = user_dict[str(mention.id)]
    amount = await util.get_value(ctx,amount,host["balance"])

    # This ID is used in the custom button IDs.
    unique_id = str(datetime.now())

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
      rand = False
      name = "Trivia Quiz"
      emoji = "🧠"
      colour = discord.Colour.from_rgb(255,201,74)
      title = f"❓ Category"
      categories = {"Geography": (22,'🌏'), "General": (9,'🧩'), "Games": (15,'🎮'), "Films": (11,'🎞'), "TV":(14,'🎬'), "Science": (17,'🧪'), "Computers": (18,'🖥'), "Sports":(21,'🏀'), "History": (23,'🗿'), "Animals":(27,'🐶'), "Vehicles":(28,'🚗'), "Anime":(31,'🎌'), "Cartoons":(32,'✏')}
      if len(data) <= 0:
        choice = "*Random Category*"
        null, category = random.choice(list(categories.items()))
        data = {"category":category[0], "emoji":category[1], "win_thresh":1}
        
      else:
        if len(data) >= 3:
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
            
        if data[0].lower() == "random":
          choice = "*Random Category*"
          null, c = random.choice(list(categories.items()))
          category = c[0]
          category_emoji = c[1]
          found = True
          rand = True
          
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
        if rand == False:
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

    fields = 0
    embed = discord.Embed(
    colour = colour,
    title = f":crossed_swords: {game.split('_')[0].capitalize()} Challenge",
    description = f"**{ctx.author.name}** has challenged **{mention.name}** to a **{name}**!\n\n{ctx.author.mention} **{host_winrate} VS {opponent_winrate}** {mention.mention}")
    embed.add_field(name = f"{emoji} Gamemode", value = f"{name}", inline = True)
    embed.add_field(name = "**:moneybag: Wager**", value = f"${amount:,} Sloans", inline = True)
    embed.add_field(name = '\u200b', value = '\u200b', inline = True)
    if len(data) >= 1:
      embed.add_field(name = title, value = choice, inline = True) 
      fields += 1
    if len(data) >= 2:
      embed.add_field(name = f"**🎯 Best of {(data['win_thresh']*2)-1}:**", value = f"First to **{data['win_thresh']}**", inline = True)
      fields += 1
    
    if fields == 1:
      embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      embed.add_field(name = '\u200b', value = '\u200b', inline = True)
    elif fields == 2:
      embed.add_field(name = '\u200b', value = '\u200b', inline = True)
      
    
    msg = await ctx.channel.send(embed=embed, components = [[
      Button(label=f"Accept", style="3", emoji="✅", custom_id=f"accept_1v1_{unique_id}"),
      Button(label=f"Decline", style="4", emoji="⛔", custom_id=f"cancel_1v1_{unique_id}")
    ]])
    
    try:
      interaction = await self.client.wait_for(
          "button_click", 
          check = lambda i: i.custom_id == f"accept_1v1_{unique_id}" and i.user == mention   or   i.custom_id == f"cancel_1v1_{unique_id}" and i.user == mention   or   i.custom_id == f"cancel_1v1_{unique_id}" and i.user == ctx.author, 
          timeout=120
          )
    except asyncio.TimeoutError:
      embed.add_field(name="❌ Timed Out!",value=f"{ctx.author.mention}'s challenge has been cancelled. {mention.mention} didn't accept in time.", inline = False)
      embed.colour = discord.Colour.red()
      await msg.edit(embed=embed, components=[])
      return
    
    if interaction.custom_id == f"cancel_1v1_{unique_id}":
      title = "Declined"
      desc = f"{mention.mention} declined this challenge."
      if interaction.user == ctx.author:
        title = "Cancelled"
        desc = f"{ctx.author.mention} cancelled this challenge."
      embed.add_field(name=f"⛔ {title}!", value=f"{desc}", inline = False)
      embed.colour = discord.Colour.red()
      await msg.edit(embed=embed, components=[])
      return
    
    elif interaction.custom_id == f"accept_1v1_{unique_id}":
      if ctx.author in Vs.cooldown or mention in Vs.cooldown:
        embed.add_field(name="❌ Error!", value="You can't participate in multiple challenges at once!", inline = False)
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, components=[])
        return
      # Re-checking balances to verify nothing has changed.
      user_dict = await util.get_user_data()
      host = user_dict[str(ctx.author.id)]
      opponent = user_dict[str(mention.id)]
      if amount > host["balance"] or amount > opponent["balance"]:
        name = "User"
        if amount > host["balance"]:
          name = f"{ctx.author.name}"
        else:
          name = f"{mention.name}"
        embed.add_field(name="❌ Error!", value=f"{name} no longer has the required balance!", inline = False)
        embed.colour = discord.Colour.red()
        await msg.edit(embed=embed, components=[])
        return
      try:
        await interaction.respond()
      except:
        pass
      Vs.cooldown.append(ctx.author)
      await gamemodes[game](self, ctx, mention, amount, data, msg)
      if ctx.author in Vs.cooldown:
        Vs.cooldown.remove(ctx.author)
  
  
  
  async def flip_1v1(self, ctx, mention, amount, data, msg):
    user_dict = await util.get_user_data()
    host = user_dict[str(ctx.author.id)]
    opponent = user_dict[str(mention.id)]
    host_bet = data["side"]
    
    flip = random.choice(["heads","tails"])
    
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
    winner["total_cash_flow"] += amount
    winner["daily_cash_flow"] += amount
    winner["stat_flip_profit"] += amount
    winner["stat_flip_win_streak"] += 1
    if winner["stat_flip_win_streak"] > winner["stat_highest_flip_win_streak"]:
      winner["stat_highest_flip_win_streak"] = winner["stat_flip_win_streak"]
    if winner["balance"] > winner["stat_highest_balance"]:
      winner["stat_highest_balance"] = winner["balance"]
    if amount > winner["stat_highest_flip"]:
      winner["stat_highest_flip"] = amount
    if amount > winner["stat_flip_highest_win"]:
      winner["stat_flip_highest_win"] = amount
    winner["stat_flip_quantity"] += 1
    winner["stat_flip_victory"] += 1
    
    loser["balance"] -= amount
    loser["total_cash_flow"] += amount
    loser["daily_cash_flow"] += amount
    loser["stat_flip_loss"] -= amount
    loser["stat_flip_win_streak"] = 0
    if amount > loser["stat_highest_flip"]:
      loser["stat_highest_flip"] = amount
    loser["stat_flip_quantity"] += 1
    loser["stat_flip_defeat"] += 1

    # Gambling Addict check.
    user_dict, ga_embed = await rewards.gambling_addict_passive(ctx, discord_loser, user_dict)

    await util.save_user_data(user_dict)

    winstreak = winner["stat_flip_win_streak"]
    winner_balance = winner["balance"]
    loser_balance = loser["balance"]
    icon = discord_winner.display_avatar.url
  
    embed = discord.Embed(
    colour = discord.Colour.green(),
    title = f"💸 Flip 1v1 | {flip.capitalize()}")
    embed.add_field(name = f"**{discord_winner.name} wins!**", value = f"**${amount:,}** has been added to {discord_winner.name}'s account!\n{discord_winner.name}'s new balance is **${winner_balance:,}**.\n{discord_loser.name}'s new balance is **${loser_balance:,}**.", inline = True)
    if winstreak >= 3:
      embed.add_field(name = f":tada: Win Streak!",value = f"{discord_winner.name} is on a **{winstreak}** flip win streak!", inline = False)
    embed.set_thumbnail(url = icon)
    embed.set_footer(icon_url = icon, text = f"{ctx.author.name} vs {mention.name}")
    await msg.edit(embed=embed, components=[])
    # Gambling Addict embed.
    if ga_embed != None:
      await ctx.channel.send(embed=ga_embed)
  
  
  
  
  async def trivia_1v1(self, ctx, mention, amount:int, data, msg):
    # Rob takes both players bets until the game is over.
    user_dict = await util.get_user_data()
    host = user_dict[str(ctx.author.id)]
    opponent = user_dict[str(mention.id)]
    rob = user_dict[str(906087821373239316)]
    rob["balance"] += amount*2
    host["balance"] -= amount
    opponent["balance"] -= amount
    # Gambling Addict check.
    user_dict, ga_embed = await rewards.gambling_addict_passive(ctx, discord_loser, user_dict)
    await util.save_user_data(user_dict)
    
    host_wins = 0
    opponent_wins = 0
    time_out = False
    win_thresh = data["win_thresh"]
    while win_thresh > host_wins and win_thresh > opponent_wins:
      url = f"https://opentdb.com/api.php?amount=1&category={data['category']}"
      req = requests.get(url)
      trivia = req.json()["results"][0]
    
      embed = discord.Embed(
      colour = discord.Colour.green(),
      title = f"{data['emoji']} Trivia | {trivia['category']}",
      description = f"{ctx.author.name} - **{host_wins}  VS  {opponent_wins}** - {mention.name}\nDifficulty: **{trivia['difficulty'].capitalize()}**\n\n{html.unescape(trivia['question'])}")
      embed.set_footer(text = f"{ctx.author.name} vs {mention.name}")
      if trivia['type'] == "multiple":
        answer_list = []
        for item in trivia['incorrect_answers']:
          answer_list.append(html.unescape(item))
        answer_list.append(html.unescape(trivia['correct_answer']))
        random.shuffle(answer_list)
        
        answers = {"A":f"{answer_list[0]}","B":f"{answer_list[1]}","C":f"{answer_list[2]}","D":f"{answer_list[3]}"}
        correct_answer = list(answers.keys())[list(answers.values()).index(html.unescape(trivia['correct_answer']))]
        await msg.edit(embed=embed, components=
        [
          [
          Button(label=f"A. {answers['A']}", style="1", custom_id="A"),
          Button(label=f"B. {answers['B']}", style="1", custom_id="B")
          ],
          [
          Button(label=f"C. {answers['C']}", style="1", custom_id="C"),
          Button(label=f"D. {answers['D']}", style="1", custom_id="D")
          ]
        ])
        
      else:
        answers = {"True":"True","False":"False"}
        correct_answer = trivia['correct_answer']
        await msg.edit(embed=embed, components=
        [
          [
          Button(label=f"True", style="1", custom_id="True"),
          Button(label=f"False", style="1", custom_id="False")
          ]
        ])
    
      try:
        interaction = await self.client.wait_for(
          "button_click", 
          check = lambda i: i.user == ctx.author or i.user == mention, 
          timeout=60
          )
      except asyncio.TimeoutError:
        embed.add_field(name="❌ Times Up!",value=f"No one answered the question in time!")
        embed.colour = discord.Colour.red()
        time_out = True
        if host_wins == opponent_wins:
          # Returns the bets.
          user_dict = await util.get_user_data()
          host = user_dict[str(ctx.author.id)]
          opponent = user_dict[str(mention.id)]
          rob = user_dict[str(906087821373239316)]
          rob["balance"] -= amount*2
          host["balance"] += amount
          opponent["balance"] += amount
          await util.save_user_data(user_dict)
          
          embed.description = f"**Draw!**\n{ctx.author.name} - **{host_wins}  VS  {opponent_wins}** - {mention.name}"
          await msg.edit(embed=embed, components=[])
          return
        break
        
      try:
        await interaction.respond()
      except:
        pass
      extra_info = ""
      if interaction.custom_id == correct_answer:
        title = "✅ Correct"
        colour = discord.Colour.green()
        if interaction.user == ctx.author:
          host_wins +=1
          round_winner = ctx.author
        else:
          opponent_wins +=1
          round_winner = mention
      else:
        title = "❌ Incorrect"
        colour = discord.Colour.red()
        loser = interaction.user
        if loser == ctx.author:
          extra_info = f"\n{ctx.author.name} guessed **{answers[interaction.custom_id]}**!"
          opponent_wins +=1
          round_winner = mention
        else:
          extra_info = f"\n{mention.name} guessed **{answers[interaction.custom_id]}**!"
          host_wins +=1
          round_winner = ctx.author

      embed.add_field(name=f"**{title}!**",value=f"{round_winner.name} wins the round!\nThe correct answer was **{answers[correct_answer]}**!{extra_info}")
      embed.colour = colour
      await msg.edit(embed=embed, components=[])
      await asyncio.sleep(2)

    user_dict = await util.get_user_data()
    host = user_dict[str(ctx.author.id)]
    opponent = user_dict[str(mention.id)]
    rob = user_dict[str(906087821373239316)]
    if host_wins > opponent_wins:
      winner = ctx.author
      icon = ctx.author.display_avatar.url
      winner_data = host
      loser = mention
      loser_data = opponent
    else:
      winner = mention
      icon = mention.display_avatar.url
      winner_data = opponent
      loser = ctx.author
      loser_data = host
    rob["balance"] -= amount*2
    winner_data["balance"] += amount*2
    winner_data["total_cash_flow"] += amount
    winner_data["daily_cash_flow"] += amount
    winner_data["stat_trivia_profit"] += amount
    winner_data["stat_trivia_victory"] += 1
    
    loser_data["total_cash_flow"] += amount
    loser_data["daily_cash_flow"] += amount
    loser_data["stat_trivia_loss"] -= amount
    loser_data["stat_trivia_defeat"] += 1
    winner_data["stat_trivia_win_streak"] += 1
    loser_data["stat_trivia_win_streak"] = 0
    if winner_data["stat_trivia_win_streak"] > winner_data["stat_highest_trivia_win_streak"]:
      winner_data["stat_highest_trivia_win_streak"] = winner_data["stat_trivia_win_streak"]
    if winner_data["balance"] > winner_data["stat_highest_balance"]:
      winner_data["stat_highest_balance"] = winner_data["balance"]

    await util.save_user_data(user_dict)

    desc = f"**{winner.name} wins!**\n"
    desc+= f"{ctx.author.name} - **{host_wins}  VS  {opponent_wins}** - {mention.name}\n\n"

    desc+=f"**${amount:,}** has been added to {winner.name}'s account!\n"
    desc+=f"{winner.name}'s new balance is **${winner_data['balance']:,}**.\n"
    desc+=f"{loser.name}'s new balance is **${loser_data['balance']:,}**."
    if time_out == False:
      embed.remove_field(0)
    embed.description = desc
    embed.set_thumbnail(url = icon)
    embed.colour = discord.Colour.green()
    winstreak = winner_data["stat_trivia_win_streak"]
    if winstreak >= 3:
      embed.add_field(name = f"🎉 Win Streak!",value = f"{winner.name} is on a **{winstreak:,}** trivia win streak!", inline = True)
    await msg.edit(embed=embed, components=[])
    if ga_embed != None:
      await ctx.channel.send(embed=ga_embed)
  
  
  
  
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

async def setup(client):
  await client.add_cog(Vs(client))