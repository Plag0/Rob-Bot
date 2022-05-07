from discord.ext import commands
import discord
import asyncio
from cogs.utility import Utility as util

class Voice(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(aliases=["jon","john"])
  async def join(self, ctx):
    channel = await ctx.author.voice.channel.connect()
    channel.play(discord.FFmpegPCMAudio('music//bongos.mp3'))
  
  @commands.command(pass_context=True)
  async def leave(self, ctx):
    await ctx.voice_client.disconnect()

def setup(client):
  client.add_cog(Voice(client))