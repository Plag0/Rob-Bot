from discord.ext import commands
import discord
import asyncio
from mutagen.mp3 import MP3
from gtts import gTTS
from cogs.utility import Utility as util
from cogs.timer import Timer as timer

class Voice(commands.Cog):
  def __init__(self, client):
    self.client = client

  #@commands.Cog.listener()
  #async def on_voice_state_update(self, member, before, after):
    #await timer.drop_party_timer(self, member)
    #try:
      #print(f"{member.name} Joined {member.voice.channel}")
    #except:
      #pass
    

  @commands.command(aliases=["jon","john"])
  async def join(self, ctx):
    channel = await ctx.author.voice.channel.connect()
    channel.play(discord.FFmpegPCMAudio('audio//bongos.mp3'))
  
  @commands.command(pass_context=True)
  async def leave(self, ctx):
    await ctx.voice_client.disconnect()
 
  @commands.command(aliases=["speak"])
  async def say(self, ctx):
    msg_fields = ctx.message.content.lower().split(" ")
    msg_fields.pop(0)
    msg = ""
    for i in range(len(msg_fields)):
      msg += msg_fields[i]
    tts = gTTS(msg,"com.au","en")
    tts.save("audio//message.mp3")
    channel = await ctx.author.voice.channel.connect()
    channel.play(discord.FFmpegPCMAudio("audio//message.mp3"))
    audio = MP3("audio//message.mp3")
    await asyncio.sleep(audio.info.length)
    await self.leave(ctx)

def setup(client):
  client.add_cog(Voice(client))