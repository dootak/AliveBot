import asyncio
import logging
import discord
import random
from discord.ext import commands

intents = discord.Intents().all()

client = commands.Bot(command_prefix='!!', intents=intents)

@client.event
async def on_ready():
    logging.info("Logged in as")
    logging.info("bot name : %s", client.user.name)
    logging.info("bot id : %s", client.user.id)
    
    #봇 상태 출력
    game = discord.Game("개발중... 바보입니다.!!!")
    await client.change_presence(status=discord.Status.online, activity=game)

def find_first_channel(channels):
    position_array = [i.position for i in channels]

    for i in channels:
        if i.position == min(position_array):
            return i

@client.event
async def on_member_join(self, member):
    msg = "<@{}>님이 서버에 들어오셨어요. 환영합니다.".format(str(member.id))
    await find_first_channel(member.guild.text_channels).send(msg)
    return None

@client.event
# 사버에 멤버가 나갔을 때 수행 될 이벤트
async def on_member_remove(self, member):
    msg = "<@{}>님이 서버에서 나가거나 추방되었습니다.".format(str(member.id))
    await find_first_channel(member.guild.text_channels).send(msg)
    return None

# @client.command(aliases=['hi', 'HI', '안녕하세요', 'ㅎㅇ', '안녕'])
# async def hello(ctx):
#     await ctx.send('안녕하세요 개발중입니다.~~!!!')

@client.command(aliases=['팀짜기'])
async def divide_team(ctx, count):

    voice_channel = ctx.author.voice.channel
    members = voice_channel.members
    member_names = []
    for member in members:
        member_names.append(member.mention)
    random.shuffle(member_names)
    
    team = []

    for i in range(0, int(len(member_names)/int(count))):
        temp = []
        for c in range(0, int(count)):
            temp.append(member_names.pop())
        team.append(temp)

    if member_names:
        team.append(member_names)

    for index in range(0, len(team)):
        await ctx.send('{} team : {}'.format(index+1, team[index]))

@client.command(aliases=['빼고팀짜기'])
async def team_except(ctx, count, *args):
    voice_channel = ctx.author.voice.channel

    members = voice_channel.members
    member_names = []

    __MEMBER__ = {}
    
    for member in members:
        __MEMBER__[member.nick] = True

    for except_member in args:
        __MEMBER__[except_member] = False

    for member in members:
        if __MEMBER__[member.nick] != False:
            member_names.append(member.mention)
    random.shuffle(member_names)
    
    team = []

    for i in range(0, int(len(member_names)/int(count))):
        temp = []
        for c in range(0, int(count)):
            temp.append(member_names.pop())
        team.append(temp)

    if member_names:
        team.append(member_names)

    for index in range(0, len(team)):
        await ctx.send('{} team : {}'.format(index+1, team[index]))

client.run('ODIyNDkzNTQ5NjAwOTY0NjA4.YFTEzw.k3fx2S9eUcE7VuGuHirhli6srcc');