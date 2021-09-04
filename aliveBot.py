import asyncio
import logging
import discord
import random
import os
from discord.ext import commands
import urllib
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
import re # Regex for youtube link
import warnings
import requests
import unicodedata
import json
import time
import datetime
import lxml.html
from extractors import (
    extract_level, extract_endorsement, extract_icon_url,
    extract_competitive_rank, extract_time_played_ratios, extract_stats
)
from ids import OVERALL_CATEGORY_ID, HERO_CATEGORY_IDS
from utils import has_played

# for lolplayersearch
tierScore = {
    'default' : 0,
    'iron' : 1,
    'bronze' : 2,
    'silver' : 3,
    'gold' : 4,
    'platinum' : 5,
    'diamond' : 6,
    'master' : 7,
    'grandmaster' : 8,
    'challenger' : 9
}

def tierCompare(solorank,flexrank):
    if tierScore[solorank] > tierScore[flexrank]:
        return 0
    elif tierScore[solorank] < tierScore[flexrank]:
        return 1
    else:
        return 2

def convert_seconds_to_time(in_seconds):
    """초를 입력받아 n days, nn:nn:nn으로 변환"""
    return str(datetime.timedelta(seconds=in_seconds))

def deleteTags(htmls):
    for a in range(len(htmls)):
        htmls[a] = re.sub('<.+?>','',str(htmls[a]),0).strip()
    return htmls

def find_first_channel(channels):
    position_array = [i.position for i in channels]

    for i in channels:
        if i.position == min(position_array):
            return i

warnings.filterwarnings(action='ignore')
intents = discord.Intents().all()
client = commands.Bot(command_prefix='!!', intents=intents)

async def status_task():
    while True:
        game = discord.Game("봇이 새롭게 탄생했어요!")
        await client.change_presence(status=discord.Status.online, activity=game)
        await asyncio.sleep(5)
        game = discord.Game("!!도움말 : 도움말")
        await client.change_presence(status=discord.Status.online, activity=game)
        await asyncio.sleep(5)
        game = discord.Game("{}개의 서버 / {}명의 유저가 이용중!".format(len(client.guilds), len(set(client.get_all_members()))))
        await client.change_presence(status=discord.Status.online, activity=game)
        await asyncio.sleep(5)

@client.event
async def on_ready():
    logging.info("Logged in as")
    logging.info("bot name : %s", client.user.name)
    logging.info("bot id : %s", client.user.id)
    client.loop.create_task(status_task())
    #봇 상태 출력
    #game = discord.Game("!!도움말 : 도움말")
    #await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("!!팀짜기"):

        if len(message.content.split(" ")) == 1:
            embed = discord.Embed(title="팀 인원이 정해지지 않았습니다.", description="", color=0x5CD1E5)
            embed.add_field(name="team count not entered",value="To use command !!팀짜기 (count)", inline=False)
            await message.channel.send("Error : Incorrect command usage ", embed=embed)
        else:
            count = (message.content).split(" ")[1:]
            if message.author.voice != None:
                voice_channel = message.author.voice.channel
                members = voice_channel.members
                member_names = []
                for member in members:
                    member_names.append(member.mention)
                random.shuffle(member_names)
                
                team = []
                
                if len(count) == 1:
                    count = int(count[0])
                else:
                    embed = discord.Embed(title="팀 인원이 정해지지 않았습니다.", description="", color=0x5CD1E5)
                    embed.add_field(name="team count not entered",value="To use command !!팀짜기 (count)", inline=False)
                    await message.channel.send("Error : Incorrect command usage ", embed=embed)

                for i in range(0, int(len(member_names)/int(count))):
                    temp = []
                    for c in range(0, int(count)):
                        temp.append(member_names.pop())
                    team.append(temp)

                if member_names:
                    team.append(member_names)

                for index in range(0, len(team)):
                    await message.channel.send('{} 팀 : {}'.format(index+1, team[index]))
            else:
                embed = discord.Embed(title="채널에 입장하지 않았습니다.", description="", color=0x5CD1E5)
                embed.add_field(name="user voice channel connect",value="팀짜기는 채널에 입장해서 사용하셔야 합니다.", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

    if message.content.startswith("!!빼고팀짜기"):
        if len(message.content.split(" ")) == 1:
            embed = discord.Embed(title="팀 인원이 정해지지 않았습니다.", description="", color=0x5CD1E5)
            embed.add_field(name="team count not entered",value="To use command !!빼고팀짜기 (count) (빼는닉네임)", inline=False)
            await message.channel.send("Error : Incorrect command usage ", embed=embed)
        else:
            count = (message.content).split(" ")[1]
            if message.author.voice != None:
                voice_channel = message.author.voice.channel
                members = voice_channel.members
                member_names = []
                args = []
                __MEMBER__ = {}
                temp = message.content.split(" ")

                for i in range(len(temp)):
                    if i <= 1: 
                        continue
                    args.append(temp[i])
                
                for member in members:
                    __MEMBER__[member.nick] = True

                for except_member in args:
                    __MEMBER__[except_member] = False

                for member in members:
                    if __MEMBER__[member.nick] != False:
                        member_names.append(member.mention)
                random.shuffle(member_names)
                
                team = []

                if len(count) == 1:
                    count = int(count[0])
                else:
                    embed = discord.Embed(title="팀 인원이 정해지지 않았습니다.", description="", color=0x5CD1E5)
                    embed.add_field(name="team count not entered",value="To use command !!빼고팀짜기 (count) (빼는닉네임)", inline=False)
                    await message.channel.send("Error : Incorrect command usage ", embed=embed)

                for i in range(0, int(len(member_names)/int(count))):
                    temp = []
                    for c in range(0, int(count)):
                        temp.append(member_names.pop())
                    team.append(temp)

                if member_names:
                    team.append(member_names)

                for index in range(0, len(team)):
                    await message.channel.send('{} 팀 : {}'.format(index+1, team[index]))
            else:
                embed = discord.Embed(title="채널에 입장하지 않았습니다.", description="", color=0x5CD1E5)
                embed.add_field(name="user voice channel connect",value="팀짜기는 채널에 입장해서 사용하셔야 합니다.", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
    
    # if message.content.startswith("!!배그경쟁전1인칭"):
    #     baseURL = "https://dak.gg/profile/"
    #     playerNickname = ''.join((message.content).split(' ')[1:])
    #     URL = baseURL + quote(playerNickname)
        
    #     try:
    #         html = urlopen(URL)
    #         bs = BeautifulSoup(html, 'html.parser')
    #         if len(message.content.split(" ")) == 1:
    #             embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
    #             embed.add_field(name="Player nickname not entered", value="To use command !!배그경쟁전1인칭 (Nickname)", inline=False)
    #             await message.channel.send("Error : Incorrect command usage ", embed=embed)
    #         else:
    #             accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

    #             # Season Information : ['PUBG',(season info),(Server),'overview']
    #             seasonInfo = []
    #             for si in bs.findAll('li', {'class': "active"}):
    #                 seasonInfo.append(si.text.strip())
    #             serverAccessorAndStatus = []
    #             # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
    #             for a in accessors:
    #                 serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

    #             rankElements = bs.findAll('div',{'class' : re.compile('squad ranked [A-Za-z0-9]')})
                
    #             if rankElements[1].find('div',{'class' : 'no_record'}) != None: # 인덱스 0 : 경쟁전 fpp -> 정보가 있는지 없는지 유무를 판별한다a.
    #                 embed = discord.Embed(title="Record not found", description="Solo que record not found.",color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP Ranking information",embed=embed) 
    #             else:
    #                 #Short of fpp Rank
    #                 fR = rankElements[1]
    #                 # Get tier medal image
    #                 tierMedalImage = fR.find('div',{'class' : 'grade-info'}).img['src']
    #                 # Get tier Information
    #                 tierInfo = fR.find('div',{'class' : 'grade-info'}).img['alt']
    #                 RPScore = fR.find('div',{'class' : 'rating'}).find('span',{'class' : 'caption'}).text
    #                 #등수
    #                 topRatioRank  = topRatio = fR.find('p',{'class' : 'desc'}).find('span',{'class' : 'rank'}).text     
    #                 #상위 %                          
    #                 topRatio = fR.find('p',{'class' : 'desc'}).find('span',{'class' : 'top'}).text
    #                 mainStatsLayout = fR.find('div',{'class' : 'stats'})
    #                 statsList = mainStatsLayout.findAll('p',{'class' : 'value'})# [KDA,승률,Top10,평균딜량, 게임수, 평균등수]
    #                 statsRatingList = mainStatsLayout.findAll('span',{'class' : 'top'})#[KDA, 승률,Top10 평균딜량, 게임수]
            
    #                 for r in range(0,len(statsList)):
    #                 # \n으로 큰 여백이 있어 split 처리
    #                     statsList[r] = statsList[r].text.strip().split('\n')[0]
    #                     statsRatingList[r] = statsRatingList[r].text
    #                 # 평균등수는 stats Rating을 표시하지 않는다.
    #                 statsRatingList = statsRatingList[0:5]
                    
    #                 embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)  
    #                 embed.add_field(name="Player located server", value=seasonInfo[2] + " Server", inline=False)
    #                 embed.add_field(name = "Tier / Top Rate / Average Rank",value = tierInfo + " (" + RPScore + ") / "+topRatio + " / " + topRatioRank,inline=False)
    #                 embed.add_field(name="K/D", value=statsList[0] + "/" + statsRatingList[0], inline=True)
    #                 embed.add_field(name="승률", value=statsList[1] + "/" + statsRatingList[1], inline=True)
    #                 embed.add_field(name="Top 10 비율", value=statsList[2] + "/" + statsRatingList[2], inline=True)
    #                 embed.add_field(name="평균딜량", value=statsList[3] + "/" + statsRatingList[3], inline=True)
    #                 embed.add_field(name="게임수", value=statsList[4] + "판/" + statsRatingList[4], inline=True)
    #                 embed.add_field(name="평균등수", value=statsList[5],inline=True)
    #                 embed.set_thumbnail(url=f'https:{tierMedalImage}')
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP Ranking information", embed=embed)
            
    #     except HTTPError as e:
    #         embed = discord.Embed(title="Not existing plyer", description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)
    #     except AttributeError as e:
    #         embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)
    
    if message.content.startswith("!!배그경쟁"):
        baseURL = "https://dak.gg/pubg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",value="To use command !!배그경쟁 (Nickname)", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                rankElements = bs.findAll('div',{'class' : re.compile('squad ranked [A-Za-z0-9]')})
                
                if rankElements[0].find('div',{'class' : 'no_record'}) != None: # 인덱스 0 : 경쟁전 fpp -> 정보가 있는지 없는지 유무를 판별한다.
                    embed = discord.Embed(title="Record not found", description="Rank TPP record not found.",color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP Ranking information",embed=embed)
                else:
                    fR = rankElements[0]
                    tierMedalImage = fR.find('div',{'class' : 'grade-info'}).img['src']
                    tierInfo = fR.find('div',{'class' : 'grade-info'}).img['alt']
                    RPScore = fR.find('div',{'class' : 'rating'}).find('span',{'class' : 'caption'}).text
                    #등수
                    #topRatioRank  = topRatio = fR.find('p',{'class' : 'desc'}).find('span',{'class' : 'rank'}).text     
                    #상위 %                          
                    #topRatio = fR.find('p',{'class' : 'desc'}).find('span',{'class' : 'top'}).text
                    mainStatsLayout = fR.find('div',{'class' : 'stats'})
                    statsList = mainStatsLayout.findAll('p',{'class' : 'value'})# [KDA,승률,Top10,평균딜량, 게임수, 평균등수]
                    statsRatingList = mainStatsLayout.findAll('span',{'class' : 'top'})#[KDA, 승률,Top10 평균딜량, 게임수]
            
                    for r in range(0,len(statsList)):
                    # \n으로 큰 여백이 있어 split 처리
                        statsList[r] = statsList[r].text.strip().split('\n')[0]
                        statsRatingList[r] = statsRatingList[r].text
                    # 평균등수는 stats Rating을 표시하지 않는다.
                    statsRatingList = statsRatingList[0:5]
                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)  
                    embed.add_field(name="Player located server", value=seasonInfo[2] + " Server", inline=False)
                    #embed.add_field(name = "Tier / Top Rate / Average Rank",value = tierInfo + " (" + RPScore + ") / "+topRatio + " / " + topRatioRank,inline=False)
                    embed.add_field(name="K/D", value=statsList[0] + "/" + statsRatingList[0], inline=True)
                    embed.add_field(name="승률", value=statsList[1] + "/" + statsRatingList[1], inline=True)
                    embed.add_field(name="Top 10 비율", value=statsList[2] + "/" + statsRatingList[2], inline=True)
                    embed.add_field(name="평균딜량", value=statsList[3] + "/" + statsRatingList[3], inline=True)
                    embed.add_field(name="게임수", value=statsList[4] + "판/" + statsRatingList[4], inline=True)
                    embed.add_field(name="평균등수", value=statsList[5],inline=True)
                    embed.set_thumbnail(url=f'https:{tierMedalImage}')
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP Ranking information", embed=embed)
                    
            
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer", description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!!배그솔로"):
        baseURL = "https://dak.gg/pubg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",value="To use command !!배그솔로 (Nickname)", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                soloQueInfo = bs.find('section', {'class': "solo modeItem"}).find('div', {'class': "mode-section tpp"})
                if soloQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Solo que record not found.",color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP solo que information", embed=embed)
                else:
                    # print(soloQueInfo)
                    # Get total playtime
                    soloQueTotalPlayTime = soloQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    soloQueGameWL = soloQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = soloQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = soloQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/pubg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    print(tierImage)
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in soloQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(''.join(ci.text.split()))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server", value=seasonInfo[2] + " Server / Total playtime : " +soloQueTotalPlayTime, inline=False)
                    embed.add_field(name="Tier",
                                    value=tier + " ("+rankPoint+"p)" , inline=False)
                    embed.add_field(name="K/D", value=comInfo[0], inline=True)
                    embed.add_field(name="승률", value=comInfo[1], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판", inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬", inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8], inline=True)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP solo que information", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer", description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        
    if message.content.startswith("!!배그듀오"):
        baseURL = "https://dak.gg/pubg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",value="To use command !!배그듀오 (Nickname)", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})
                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))
                
                duoQueInfo = bs.find('section',{'class' : "duo modeItem"}).find('div',{'class' : "mode-section tpp"})
                if duoQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Duo que record not found.",color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP duo que information", embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    duoQueTotalPlayTime = duoQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    duoQueGameWL = duoQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = duoQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = duoQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/pubg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in duoQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(''.join(ci.text.split()))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="", color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server and total playtime", value=seasonInfo[2] + " Server / Total playtime : " +duoQueTotalPlayTime, inline=False)
                    embed.add_field(name="Tier(Rank Point)", value=tier + " ("+rankPoint+"p)", inline=False)
                    embed.add_field(name="K/D", value=comInfo[0], inline=True)
                    embed.add_field(name="승률", value=comInfo[1], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판", inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬", inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8], inline=True)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP duo que information", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
    
    if message.content.startswith("!!배그스쿼드"):
        baseURL = "https://dak.gg/pubg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",value="To use command !!배그스쿼드 (Nickname)", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                squadQueInfo = bs.find('section',{'class' : "squad modeItem"}).find('div',{'class' : "mode-section tpp"})
                if squadQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Squad que record not found.",color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP squad que information", embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    squadQueTotalPlayTime = squadQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    squadQueGameWL = squadQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = squadQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = squadQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/pubg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in squadQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(''.join(ci.text.split()))
                    
                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server", value=seasonInfo[2] + " Server / Total playtime : " +squadQueTotalPlayTime, inline=False)
                    embed.add_field(name="Tier(Rank Point)",value=tier + " (" + rankPoint + "p)", inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] , inline=True)
                    embed.add_field(name="승률", value=comInfo[1] , inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] , inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] , inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판", inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬", inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8], inline=True)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP squad que information", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    # if message.content.startswith("!!배그솔로1인칭"):
    #     baseURL = "https://dak.gg/profile/"
    #     playerNickname = ''.join((message.content).split(' ')[1:])
    #     URL = baseURL + quote(playerNickname)
    #     try:
    #         html = urlopen(URL)
    #         bs = BeautifulSoup(html, 'html.parser')
    #         if len(message.content.split(" ")) == 1:
    #             embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
    #             embed.add_field(name="Player nickname not entered",value="To use command !!배그솔로1인칭 (Nickname)", inline=False)
    #             await message.channel.send("Error : Incorrect command usage ", embed=embed)

    #         else:
    #             accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})
    #             # Season Information : ['PUBG',(season info),(Server),'overview']
    #             seasonInfo = []
    #             for si in bs.findAll('li', {'class': "active"}):
    #                 seasonInfo.append(si.text.strip())
    #             serverAccessorAndStatus = []
    #             # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
    #             for a in accessors:
    #                 serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

    #             # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]
    #             soloQueInfo = bs.find('section', {'class': "solo modeItem"}).find('div', {'class': "mode-section fpp"})
    #             if soloQueInfo == None:
    #                 embed = discord.Embed(title="Record not found", description="Solo que record not found.",color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP solo que information",embed=embed)
    #             else:
    #                 # print(soloQueInfo)
    #                 # Get total playtime
    #                 soloQueTotalPlayTime = soloQueInfo.find('span', {'class': "time_played"}).text.strip()
    #                 # Get Win/Top10/Lose : [win,top10,lose]
    #                 soloQueGameWL = soloQueInfo.find('em').text.strip().split(' ')
    #                 # RankPoint
    #                 rankPoint = soloQueInfo.find('span', {'class': 'value'}).text
    #                 # Tier image url, tier
    #                 tierInfos = soloQueInfo.find('img', {
    #                     'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
    #                 tierImage = "https:" + tierInfos['src']
    #                 print(tierImage)
    #                 tier = tierInfos['alt']

    #                 # Comprehensive info
    #                 comInfo = []
    #                 # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
    #                 for ci in soloQueInfo.findAll('p', {'class': 'value'}):
    #                     comInfo.append(''.join(ci.text.split()))
    #                 embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)
    #                 embed.add_field(name="Player located server",value=seasonInfo[2] + " Server / Total playtime : " + soloQueTotalPlayTime,inline=False)
    #                 embed.add_field(name="Tier(Rank Point)",value=tier + " (" + rankPoint + "p)", inline=False)
    #                 embed.add_field(name="K/D", value=comInfo[0], inline=True)
    #                 embed.add_field(name="승률", value=comInfo[1], inline=True)
    #                 embed.add_field(name="Top 10 비율", value=comInfo[2], inline=True)
    #                 embed.add_field(name="평균딜량", value=comInfo[3], inline=True)
    #                 embed.add_field(name="게임수", value=comInfo[4] + "판" , inline=True)
    #                 embed.add_field(name="최다킬수", value=comInfo[5] + "킬" , inline=True)
    #                 embed.add_field(name="헤드샷 비율", value=comInfo[6] , inline=True)
    #                 embed.add_field(name="저격거리", value=comInfo[7], inline=True)
    #                 embed.add_field(name="평균생존시간", value=comInfo[8] , inline=True)
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP solo que information",embed=embed)
    #     except HTTPError as e:
    #         embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)
    #     except AttributeError as e:
    #         embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)

    # if message.content.startswith("!!배그듀오1인칭"):
    #     baseURL = "https://dak.gg/profile/"
    #     playerNickname = ''.join((message.content).split(' ')[1:])
    #     URL = baseURL + quote(playerNickname)
    #     try:
    #         html = urlopen(URL)
    #         bs = BeautifulSoup(html, 'html.parser')
    #         if len(message.content.split(" ")) == 1:
    #             embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
    #             embed.add_field(name="Player nickname not entered",value="To use command !!배그듀오1인칭 (Nickname)", inline=False)
    #             await message.channel.send("Error : Incorrect command usage ", embed=embed)
    #         else:
    #             accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})
    #             # Season Information : ['PUBG',(season info),(Server),'overview']
    #             seasonInfo = []
    #             for si in bs.findAll('li', {'class': "active"}):
    #                 seasonInfo.append(si.text.strip())
    #             serverAccessorAndStatus = []
    #             # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
    #             for a in accessors:
    #                 serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

    #             # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

    #             duoQueInfo = bs.find('section', {'class': "duo modeItem"}).find('div', {'class': "mode-section fpp"})
    #             if duoQueInfo == None:
    #                 embed = discord.Embed(title="Record not found", description="Duo que record not found.",color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP duo que information",embed=embed)
    #             else:
    #                 # print(duoQueInfo)
    #                 # Get total playtime
    #                 duoQueTotalPlayTime = duoQueInfo.find('span', {'class': "time_played"}).text.strip()
    #                 # Get Win/Top10/Lose : [win,top10,lose]
    #                 duoQueGameWL = duoQueInfo.find('em').text.strip().split(' ')
    #                 # RankPoint
    #                 rankPoint = duoQueInfo.find('span', {'class': 'value'}).text
    #                 # Tier image url, tier
    #                 tierInfos = duoQueInfo.find('img', {
    #                     'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
    #                 tierImage = "https:" + tierInfos['src']
    #                 tier = tierInfos['alt']

    #                 # Comprehensive info
    #                 comInfo = []
    #                 # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
    #                 for ci in duoQueInfo.findAll('p', {'class': 'value'}):
    #                     comInfo.append(''.join(ci.text.split()))
    #                 embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)
    #                 embed.add_field(name="Player located server and total playtime",value=seasonInfo[2] + " Server / Total playtime : " + duoQueTotalPlayTime,inline=False)
    #                 embed.add_field(name="Tier(Rank Point)",value=tier + " (" + rankPoint + "p)", inline=False)
    #                 embed.add_field(name="K/D", value=comInfo[0] , inline=True)
    #                 embed.add_field(name="승률", value=comInfo[1], inline=True)
    #                 embed.add_field(name="Top 10 비율", value=comInfo[2], inline=True)
    #                 embed.add_field(name="평균딜량", value=comInfo[3], inline=True)
    #                 embed.add_field(name="게임수", value=comInfo[4] + "판", inline=True)
    #                 embed.add_field(name="최다킬수", value=comInfo[5] + "킬", inline=True)
    #                 embed.add_field(name="헤드샷 비율", value=comInfo[6] , inline=True)
    #                 embed.add_field(name="저격거리", value=comInfo[7] , inline=True)
    #                 embed.add_field(name="평균생존시간", value=comInfo[8] , inline=True)
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP duo que information",embed=embed)
    #     except HTTPError as e:
    #         embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)
    #     except AttributeError as e:
    #         embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)

    # if message.content.startswith("!!배그스쿼드1인칭"):
    #     baseURL = "https://dak.gg/profile/"
    #     playerNickname = ''.join((message.content).split(' ')[1:])
    #     URL = baseURL + quote(playerNickname)
    #     try:
    #         html = urlopen(URL)
    #         bs = BeautifulSoup(html, 'html.parser')
    #         if len(message.content.split(" ")) == 1:
    #             embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
    #             embed.add_field(name="Player nickname not entered",value="To use command !!배그스쿼드1인칭 (Nickname)", inline=False)
    #             await message.channel.send("Error : Incorrect command usage ", embed=embed)
    #         else:
    #             accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})
    #             # Season Information : ['PUBG',(season info),(Server),'overview']
    #             seasonInfo = []
    #             for si in bs.findAll('li', {'class': "active"}):
    #                 seasonInfo.append(si.text.strip())
    #             serverAccessorAndStatus = []
    #             # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
    #             for a in accessors:
    #                 serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))
    #             # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

    #             squadQueInfo = bs.find('section', {'class': "squad modeItem"}).find('div',{'class': "mode-section fpp"})
    #             if squadQueInfo == None:
    #                 embed = discord.Embed(title="Record not found", description="Squad que record not found.",color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP squad que information",embed=embed)
    #             else:
    #                 # print(duoQueInfo)
    #                 # Get total playtime
    #                 squadQueTotalPlayTime = squadQueInfo.find('span', {'class': "time_played"}).text.strip()
    #                 # Get Win/Top10/Lose : [win,top10,lose]
    #                 squadQueGameWL = squadQueInfo.find('em').text.strip().split(' ')
    #                 # RankPoint
    #                 rankPoint = squadQueInfo.find('span', {'class': 'value'}).text
    #                 # Tier image url, tier
    #                 tierInfos = squadQueInfo.find('img', {
    #                     'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
    #                 tierImage = "https:" + tierInfos['src']
    #                 tier = tierInfos['alt']

    #                 # Comprehensive info
    #                 comInfo = []
    #                 # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
    #                 for ci in squadQueInfo.findAll('p', {'class': 'value'}):
    #                     comInfo.append(''.join(ci.text.split()))
    #                 embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
    #                                         color=0x5CD1E5)
    #                 embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
    #                 embed.add_field(name="Real Time Accessors and Server Status",value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +serverAccessorAndStatus[1].split(':')[-1], inline=False)
    #                 embed.add_field(name="Player located server",value=seasonInfo[2] + " Server / Total playtime : " + squadQueTotalPlayTime,inline=False)
    #                 embed.add_field(name="Tier(Rank Point)",value=tier + " (" + rankPoint + "p)", inline=False)
    #                 embed.add_field(name="K/D", value=comInfo[0], inline=True)
    #                 embed.add_field(name="승률", value=comInfo[1], inline=True)
    #                 embed.add_field(name="Top 10 비율", value=comInfo[2], inline=True)
    #                 embed.add_field(name="평균딜량", value=comInfo[3], inline=True)
    #                 embed.add_field(name="게임수", value=comInfo[4] + "판", inline=True)
    #                 embed.add_field(name="최다킬수", value=comInfo[5] + "킬", inline=True)
    #                 embed.add_field(name="헤드샷 비율", value=comInfo[6] , inline=True)
    #                 embed.add_field(name="저격거리", value=comInfo[7], inline=True)
    #                 embed.add_field(name="평균생존시간", value=comInfo[8], inline=True)
    #                 await message.channel.send("PUBG player " + playerNickname + "'s FPP squad que information",embed=embed)
    #     except HTTPError as e:
    #         embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)
    #     except AttributeError as e:
    #         embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
    #         await message.channel.send("Error : Not existing player", embed=embed)
    
    # if message.content.startswith("!!롤전적"):
    #     opggsummonersearch = 'https://www.op.gg/summoner/userName='

    #     try:
    #         if len(message.content.split(" ")) == 1:
    #             embed = discord.Embed(title="소환사 이름이 입력되지 않았습니다!", description="", color=0x5CD1E5)
    #             embed.add_field(name="Summoner name not entered",value="To use command !!롤전적 (Summoner Nickname)", inline=False)
    #             await message.channel.send("Error : Incorrect command usage ", embed=embed)
    #         else:
    #             playerNickname = ''.join((message.content).split(' ')[1:])
    #             # Open URL
    #             checkURLBool = urlopen(opggsummonersearch + quote(playerNickname))
    #             bs = BeautifulSoup(checkURLBool, 'html.parser')

    #             Medal = bs.find('div', {'class': 'SideContent'})
    #             RankMedal = Medal.findAll('img', {'src': re.compile('\/\/[a-z]*\-[A-Za-z]*\.[A-Za-z]*\.[A-Za-z]*\/[A-Za-z]*\/[A-Za-z]*\/[a-z0-9_]*\.png')})
    #             # Variable RankMedal's index 0 : Solo Rank
    #             # Variable RankMedal's index 1 : Flexible 5v5 rank

    #             # for mostUsedChampion
    #             mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
    #             mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
    #             # 솔랭, 자랭 둘다 배치가 안되어있는경우 -> 사용된 챔피언 자체가 없다. 즉 모스트 챔피언 메뉴를 넣을 필요가 없다.
    #             # Scrape Summoner's Rank information
    #             # [Solorank,Solorank Tier]
    #             solorank_Types_and_Tier_Info = deleteTags(bs.findAll('div', {'class': {'RankType', 'TierRank'}}))
    #             # [Solorank LeaguePoint, Solorank W, Solorank L, Solorank Winratio]
    #             solorank_Point_and_winratio = deleteTags(
    #                 bs.findAll('span', {'class': {'LeaguePoints', 'wins', 'losses', 'winratio'}}))
    #             # [Flex 5:5 Rank,Flexrank Tier,Flextier leaguepoint + W/L,Flextier win ratio]
    #             flexrank_Types_and_Tier_Info = deleteTags(bs.findAll('div', {'class': {'sub-tier__rank-type', 'sub-tier__rank-tier', 'sub-tier__league-point','sub-tier__gray-text'}}))
    #             # ['Flextier W/L]
    #             flexrank_Point_and_winratio = deleteTags(bs.findAll('span', {'class': {'sub-tier__gray-text'}}))

    #             if len(solorank_Point_and_winratio) == 0 and len(flexrank_Point_and_winratio) == 0:
    #                 embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
    #                 embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,inline=False)
    #                 embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
    #                 embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
    #                 embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
    #                 await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)

    #             # 솔로랭크 기록이 없는경우
    #             elif len(solorank_Point_and_winratio) == 0:

    #                 # most Used Champion Information : Champion Name, KDA, Win Rate
    #                 mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
    #                 mostUsedChampion = mostUsedChampion.a.text.strip()
    #                 mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
    #                 mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
    #                 mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
    #                 mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

    #                 FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
    #                 FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]
    #                 embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
    #                 embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,inline=False)
    #                 embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
    #                 embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
    #                 embed.add_field(name="Most Used Champion : " + mostUsedChampion,value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,inline=False)
    #                 embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
    #                 await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)

    #             # 자유랭크 기록이 없는경우
    #             elif len(flexrank_Point_and_winratio) == 0:
    #                 # most Used Champion Information : Champion Name, KDA, Win Rate
    #                 mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
    #                 mostUsedChampion = mostUsedChampion.a.text.strip()
    #                 mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
    #                 mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
    #                 mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
    #                 mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

    #                 SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
    #                 SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
    #                 embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
    #                 embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname, inline=False)
    #                 embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
    #                 embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
    #                 embed.add_field(name="Most Used Champion : " + mostUsedChampion, value="KDA : " + mostUsedChampionKDA + " / " + "WinRate : " + mostUsedChampionWinRate, inline=False)
    #                 embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
    #                 await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)
    #             # 두가지 유형의 랭크 모두 완료된사람
    #             else:
    #                 # 더 높은 티어를 thumbnail에 안착
    #                 solorankmedal = RankMedal[0]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')
    #                 flexrankmedal = RankMedal[1]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')

    #                 # Make State
    #                 SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
    #                 SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
    #                 FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
    #                 FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]

    #                 # most Used Champion Information : Champion Name, KDA, Win Rate
    #                 mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
    #                 mostUsedChampion = mostUsedChampion.a.text.strip()
    #                 mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
    #                 mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
    #                 mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
    #                 mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

    #                 cmpTier = tierCompare(solorankmedal[0], flexrankmedal[0])
    #                 embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
    #                 embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
    #                                 inline=False)
    #                 embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
    #                 embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
    #                 embed.add_field(name="Most Used Champion : " + mostUsedChampion,
    #                                 value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,
    #                                 inline=False)
    #                 if cmpTier == 0:
    #                     embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
    #                 elif cmpTier == 1:
    #                     embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
    #                 else:
    #                     if solorankmedal[1] > flexrankmedal[1]:
    #                         embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
    #                     elif solorankmedal[1] < flexrankmedal[1]:
    #                         embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
    #                     else:
    #                         embed.set_thumbnail(url='https:' + RankMedal[0]['src'])

    #                 await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)
    #     except HTTPError as e:
    #         embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
    #         embed.add_field(name="", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
    #         await message.channel.send("Wrong Summoner Nickname")

    #     except UnicodeEncodeError as e:
    #         embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
    #         embed.add_field(name="???", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
    #         await message.channel.send("Wrong Summoner Nickname", embed=embed)

    #     except AttributeError as e:
    #         embed = discord.Embed(title="존재하지 않는 소환사", description="", color=0x5CD1E5)
    #         embed.add_field(name="해당 닉네임의 소환사가 존재하지 않습니다.", value="소환사 이름을 확인해주세요", inline=False)
    #         await message.channel.send("Error : Non existing Summoner ", embed=embed)
    
    if message.content.startswith("!!옵치일반"):
        STATS_URL = 'https://playoverwatch.com/en-us/career/{platform}/{battle_tag}'
        AVAILABLE_PLAY_MODES = ('quick', 'competitive')
        playerNickname = ''.join((message.content).split(' ')[1:])
        try:
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",value="To use command !!옵치일반 (Nickname)", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
            else:
                
                tagName = message.content.split(" ")[1:]
                name = tagName[0].replace("#", "-")                
                url = STATS_URL.format(platform='pc', battle_tag=name)

                response = requests.get(url)

                if response == None:
                    embed = discord.Embed(title="Record not found", description="OverWatch Profile not found.",color=0x5CD1E5)
                    embed.add_field(name="Profile search from overWatch API", value=URL, inline=False)
                    await message.channel.send("OverWatch player " + playerNickname + "'s Profile not information",embed=embed)
                else:
                    if response.status_code == 200:
                        tree = lxml.html.fromstring(response.text)
                        output = {}
                        output['level'] = extract_level(tree)
                        output['endorsement'] = extract_endorsement(tree)
                        output['icon_url'] = extract_icon_url(tree)
                        competitive_rank = extract_competitive_rank(tree)
                        if competitive_rank:
                            output['competitive_rank'] = competitive_rank

                        for mode in AVAILABLE_PLAY_MODES:
                            if not has_played(tree, mode):
                                continue

                            output[mode] = {
                                'overall': {},
                                'heroes': {},
                            }

                            # overall
                            output[mode]['overall'] = extract_stats(tree, mode, OVERALL_CATEGORY_ID)

                            # heroes
                            time_played_ratios = extract_time_played_ratios(tree, mode)
                            for hero, category_id in HERO_CATEGORY_IDS.items():
                                if not has_played(tree, mode, category_id):
                                    continue

                                output[mode]['heroes'][hero] = extract_stats(tree, mode, category_id)
                                output[mode]['heroes'][hero]['time_played_ratio'] = time_played_ratios[hero]

                        e = discord.Embed(color=0xFC9A23, title="{} Overwatch Profile".format(playerNickname))
                        e.add_field(name="Level", value="```" + str(output['level']) + "```")
                        
                        endorsement = output['endorsement']
                        e.add_field(name="endorsement Level", value="```" + str(endorsement['level']) + "```", inline=True)
                        e.add_field(name="shotcaller", value="```" + str(endorsement['shotcaller']) + "```", inline=True)
                        e.add_field(name="teammate", value="```" + str(endorsement['teammate']) + "```", inline=True)
                        e.add_field(name="sportsmanship", value="```" + str(endorsement['sportsmanship']) + "```", inline=True)
                        e.set_thumbnail(url=output['icon_url'])
                        await message.channel.send("OVERWATCH player " + playerNickname + "'s Profile information",embed=e)

                        quickData = output['quick']

                        if quickData != None:
                            overallData = quickData['overall']
                            #heroesData = quickData['heroes']

                            if overallData != None:
                                e1 = discord.Embed(color=0xFC9A23, title="{} Overwatch Best".format(playerNickname))
                                e1.add_field(name="모든 피해 완료", value="```" + str(overallData['all_damage_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="배리어 데미지 완료", value="```" + str(overallData['barrier_damage_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="수비 지원", value="```" + str(overallData['defensive_assist_most_in_game']) + "```", inline=True)
                                e1.add_field(name="처치", value="```" + str(overallData['elimination_most_in_game']) + "```", inline=True)
                                e1.add_field(name="환경 처치", value="```" + str(overallData['environmental_kill_most_in_game']) + "```", inline=True)
                                e1.add_field(name="결정타", value="```" + str(overallData['final_blow_most_in_game']) + "```", inline=True)
                                e1.add_field(name="치유 완료", value="```" + str(overallData['healing_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="영웅 피해 완료", value="```" + str(overallData['hero_damage_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="연속 처치-최고", value="```" + str(overallData['kill_streak_best']) + "```", inline=True)
                                e1.add_field(name="근접 결정타", value="```" + str(overallData['melee_final_blow_most_in_game']) + "```", inline=True)
                                e1.add_field(name="멀티 킬-최고", value="```" + str(overallData['multikill_best']) + "```", inline=True)
                                e1.add_field(name="목표 처치", value="```" + str(overallData['objective_kill_most_in_game']) + "```", inline=True)
                                e1.add_field(name="목표 시간", value="```" + convert_seconds_to_time(overallData['objective_time_most_in_game']) + "```", inline=True)
                                e1.add_field(name="공격 지원", value="```" + str(overallData['offensive_assist_most_in_game']) + "```", inline=True)
                                e1.add_field(name="정찰 지원", value="```" + str(overallData['recon_assist_most_in_game']) + "```", inline=True)
                                e1.add_field(name="솔로 처치", value="```" + str(overallData['solo_kill_most_in_game']) + "```", inline=True)
                                e1.add_field(name="파괴 된 순간 이동기 패드", value="```" + str(overallData['teleporter_pad_destroyed_most_in_game']) + "```", inline=True)
                                e1.add_field(name="폭주 시간", value="```" + convert_seconds_to_time(overallData['time_spent_on_fire_most_in_game']) + "```", inline=True)
                                e1.add_field(name="파괴 된 포탑", value="```" + str(overallData['turret_destroyed_most_in_game']) + "```", inline=True)
                                await message.channel.send(embed=e1)

                                e2 = discord.Embed(color=0xFC9A23, title="{} Overwatch Assists".format(playerNickname))
                                e2.add_field(name="방어 지원", value="```" + str(overallData['defensive_assist']) + "```", inline=True)
                                e2.add_field(name="치유 완료", value="```" + str(overallData['healing_done']) + "```", inline=True)
                                e2.add_field(name="공격 지원", value="```" + str(overallData['offensive_assist']) + "```", inline=True)
                                e2.add_field(name="정찰 지원", value="```" + str(overallData['recon_assist']) + "```", inline=True)
                                await message.channel.send(embed=e2)

                                e3 = discord.Embed(color=0xFC9A23, title="{} Overwatch Game".format(playerNickname))
                                e3.add_field(name="패배 한 경기", value="```" + str(overallData['game_lost']) + "```", inline=True)
                                e3.add_field(name="플레이 한 경기", value="```" + str(overallData['game_played']) + "```", inline=True)
                                e3.add_field(name="승리 한 경기", value="```" + str(overallData['game_won']) + "```", inline=True)
                                e3.add_field(name="플레이 시간", value="```" + convert_seconds_to_time(overallData['time_played']) + "```", inline=True)
                                await message.channel.send(embed=e3)

                                e4 = discord.Embed(color=0xFC9A23, title="{} Overwatch Average 평균 10분".format(playerNickname))
                                e4.add_field(name="모든 피해 완료", value="```" + str(overallData['all_damage_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="배리어 데미지 완료", value="```" + str(overallData['barrier_damage_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="사망", value="```" + str(overallData['death_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="제거 횟수", value="```" + str(overallData['elimination_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="최종 타격", value="```" + str(overallData['final_blow_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="치유 완료", value="```" + str(overallData['healing_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="영웅 피해 완료", value="```" + str(overallData['hero_damage_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="목표 처치", value="```" + str(overallData['objective_kill_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="목표 시간", value="```" + convert_seconds_to_time(overallData['objective_time_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="솔로 킬", value="```" + str(overallData['solo_kill_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="화재 소요 시간", value="```" + convert_seconds_to_time(overallData['time_spent_on_fire_avg_per_10_min']) + "```", inline=True)
                                await message.channel.send(embed=e4)

                                e5 = discord.Embed(color=0xFC9A23, title="{} Overwatch Combat".format(playerNickname))
                                e5.add_field(name="모든 손상 완료", value="```" + str(overallData['all_damage_done']) + "```", inline=True)
                                e5.add_field(name="베리어 손상 완료", value="```" + str(overallData['barrier_damage_done']) + "```", inline=True)
                                e5.add_field(name="손상 완료", value="```" + str(overallData['damage_done']) + "```", inline=True)
                                e5.add_field(name="사망자", value="```" + str(overallData['death']) + "```", inline=True)
                                e5.add_field(name="제거", value="```" + str(overallData['elimination']) + "```", inline=True)
                                e5.add_field(name="환경 살인", value="```" + str(overallData['environmental_kill']) + "```", inline=True)
                                e5.add_field(name="최종 타격", value="```" + str(overallData['final_blow']) + "```", inline=True)
                                e5.add_field(name="영웅 피해 완료", value="```" + str(overallData['hero_damage_done']) + "```", inline=True)
                                e5.add_field(name="근접 최종 타격", value="```" + str(overallData['melee_final_blow']) + "```", inline=True)
                                e5.add_field(name="멀티 킬", value="```" + str(overallData['multikill']) + "```", inline=True)
                                e5.add_field(name="목표 처치", value="```" + str(overallData['objective_kill']) + "```", inline=True)
                                e5.add_field(name="목표 시간", value="```" + convert_seconds_to_time(overallData['objective_time']) + "```", inline=True)
                                e5.add_field(name="솔로 킬", value="```" + str(overallData['solo_kill']) + "```", inline=True)
                                e5.add_field(name="불에 보낸 시간", value="```" + convert_seconds_to_time(overallData['time_spent_on_fire']) + "```", inline=True)
                                await message.channel.send(embed=e5)

                                e6 = discord.Embed(color=0xFC9A23, title="{} Overwatch Match Awards".format(playerNickname))
                                e6.add_field(name="메달-골드", value="```" + str(overallData['medal_gold']) + "```", inline=True)
                                e6.add_field(name="카드", value="```" + str(overallData['card']) + "```", inline=True)
                                e6.add_field(name="메달", value="```" + str(overallData['medal']) + "```", inline=True)
                                e6.add_field(name="메달-브론즈", value="```" + str(overallData['medal_bronze']) + "```", inline=True)
                                e6.add_field(name="메달-실버", value="```" + str(overallData['medal_silver']) + "```", inline=True)
                                await message.channel.send(embed=e6)
                        
                    elif response.status_code == 404:
                        await message.channel.send("The user `{}` wasn't found.".format(playerNickname))
                    else:
                        await message.channel.send("Request returned status code " + str(response.status_code))
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!!옵치경쟁"):
        STATS_URL = 'https://playoverwatch.com/en-us/career/{platform}/{battle_tag}'
        AVAILABLE_PLAY_MODES = ('quick', 'competitive')
        playerNickname = ''.join((message.content).split(' ')[1:])
        try:
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",value="To use command !!옵치경쟁 (Nickname)", inline=False)
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
            else:
                
                tagName = message.content.split(" ")[1:]
                name = tagName[0].replace("#", "-")                
                url = STATS_URL.format(platform='pc', battle_tag=name)

                response = requests.get(url)

                if response == None:
                    embed = discord.Embed(title="Record not found", description="OverWatch Profile not found.",color=0x5CD1E5)
                    embed.add_field(name="Profile search from overWatch API", value=URL, inline=False)
                    await message.channel.send("OverWatch player " + playerNickname + "'s Profile not information",embed=embed)
                else:
                    if response.status_code == 200:
                        tree = lxml.html.fromstring(response.text)
                        output = {}
                        output['level'] = extract_level(tree)
                        output['endorsement'] = extract_endorsement(tree)
                        output['icon_url'] = extract_icon_url(tree)
                        competitive_rank = extract_competitive_rank(tree)
                        if competitive_rank:
                            output['competitive_rank'] = competitive_rank

                        for mode in AVAILABLE_PLAY_MODES:
                            if not has_played(tree, mode):
                                continue

                            output[mode] = {
                                'overall': {},
                                'heroes': {},
                            }

                            # overall
                            output[mode]['overall'] = extract_stats(tree, mode, OVERALL_CATEGORY_ID)

                            # heroes
                            time_played_ratios = extract_time_played_ratios(tree, mode)
                            for hero, category_id in HERO_CATEGORY_IDS.items():
                                if not has_played(tree, mode, category_id):
                                    continue

                                output[mode]['heroes'][hero] = extract_stats(tree, mode, category_id)
                                output[mode]['heroes'][hero]['time_played_ratio'] = time_played_ratios[hero]

                        e = discord.Embed(color=0xFC9A23, title="{} Overwatch Profile".format(playerNickname))
                        e.add_field(name="Level", value="```" + str(output['level']) + "```")
                        
                        endorsement = output['endorsement']
                        e.add_field(name="endorsement Level", value="```" + str(endorsement['level']) + "```", inline=True)
                        e.add_field(name="shotcaller", value="```" + str(endorsement['shotcaller']) + "```", inline=True)
                        e.add_field(name="teammate", value="```" + str(endorsement['teammate']) + "```", inline=True)
                        e.add_field(name="sportsmanship", value="```" + str(endorsement['sportsmanship']) + "```", inline=True)
                        e.set_thumbnail(url=output['icon_url'])
                        await message.channel.send("OVERWATCH player " + playerNickname + "'s Profile information",embed=e)

                        quickData = output['competitive']

                        if quickData != None:
                            overallData = quickData['overall']
                            #heroesData = quickData['heroes']

                            if overallData != None:
                                e1 = discord.Embed(color=0xFC9A23, title="{} Overwatch Best".format(playerNickname))
                                e1.add_field(name="모든 피해 완료", value="```" + str(overallData['all_damage_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="배리어 데미지 완료", value="```" + str(overallData['barrier_damage_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="수비 지원", value="```" + str(overallData['defensive_assist_most_in_game']) + "```", inline=True)
                                e1.add_field(name="처치", value="```" + str(overallData['elimination_most_in_game']) + "```", inline=True)
                                e1.add_field(name="환경 처치", value="```" + str(overallData['environmental_kill_most_in_game']) + "```", inline=True)
                                e1.add_field(name="결정타", value="```" + str(overallData['final_blow_most_in_game']) + "```", inline=True)
                                e1.add_field(name="치유 완료", value="```" + str(overallData['healing_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="영웅 피해 완료", value="```" + str(overallData['hero_damage_done_most_in_game']) + "```", inline=True)
                                e1.add_field(name="연속 처치-최고", value="```" + str(overallData['kill_streak_best']) + "```", inline=True)
                                e1.add_field(name="근접 결정타", value="```" + str(overallData['melee_final_blow_most_in_game']) + "```", inline=True)
                                e1.add_field(name="멀티 킬-최고", value="```" + str(overallData['multikill_best']) + "```", inline=True)
                                e1.add_field(name="목표 처치", value="```" + str(overallData['objective_kill_most_in_game']) + "```", inline=True)
                                e1.add_field(name="목표 시간", value="```" + convert_seconds_to_time(overallData['objective_time_most_in_game']) + "```", inline=True)
                                e1.add_field(name="공격 지원", value="```" + str(overallData['offensive_assist_most_in_game']) + "```", inline=True)
                                e1.add_field(name="정찰 지원", value="```" + str(overallData['recon_assist_most_in_game']) + "```", inline=True)
                                e1.add_field(name="솔로 처치", value="```" + str(overallData['solo_kill_most_in_game']) + "```", inline=True)
                                e1.add_field(name="폭주 시간", value="```" + convert_seconds_to_time(overallData['time_spent_on_fire_most_in_game']) + "```", inline=True)
                                e1.add_field(name="파괴 된 포탑", value="```" + str(overallData['turret_destroyed_most_in_game']) + "```", inline=True)
                                await message.channel.send(embed=e1)

                                e2 = discord.Embed(color=0xFC9A23, title="{} Overwatch Assists".format(playerNickname))
                                e2.add_field(name="방어 지원", value="```" + str(overallData['defensive_assist']) + "```", inline=True)
                                e2.add_field(name="치유 완료", value="```" + str(overallData['healing_done']) + "```", inline=True)
                                e2.add_field(name="공격 지원", value="```" + str(overallData['offensive_assist']) + "```", inline=True)
                                e2.add_field(name="정찰 지원", value="```" + str(overallData['recon_assist']) + "```", inline=True)
                                await message.channel.send(embed=e2)

                                e3 = discord.Embed(color=0xFC9A23, title="{} Overwatch Game".format(playerNickname))
                                e3.add_field(name="패배 한 경기", value="```" + str(overallData['game_lost']) + "```", inline=True)
                                e3.add_field(name="플레이 한 경기", value="```" + str(overallData['game_played']) + "```", inline=True)
                                e3.add_field(name="승리 한 경기", value="```" + str(overallData['game_won']) + "```", inline=True)
                                e3.add_field(name="플레이 시간", value="```" + convert_seconds_to_time(overallData['time_played']) + "```", inline=True)
                                await message.channel.send(embed=e3)

                                e4 = discord.Embed(color=0xFC9A23, title="{} Overwatch Average 평균 10분".format(playerNickname))
                                e4.add_field(name="모든 피해 완료", value="```" + str(overallData['all_damage_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="배리어 데미지 완료", value="```" + str(overallData['barrier_damage_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="사망", value="```" + str(overallData['death_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="제거 횟수", value="```" + str(overallData['elimination_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="최종 타격", value="```" + str(overallData['final_blow_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="치유 완료", value="```" + str(overallData['healing_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="영웅 피해 완료", value="```" + str(overallData['hero_damage_done_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="목표 처치", value="```" + str(overallData['objective_kill_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="목표 시간", value="```" + convert_seconds_to_time(overallData['objective_time_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="솔로 킬", value="```" + str(overallData['solo_kill_avg_per_10_min']) + "```", inline=True)
                                e4.add_field(name="화재 소요 시간", value="```" + convert_seconds_to_time(overallData['time_spent_on_fire_avg_per_10_min']) + "```", inline=True)
                                await message.channel.send(embed=e4)

                                e5 = discord.Embed(color=0xFC9A23, title="{} Overwatch Combat".format(playerNickname))
                                e5.add_field(name="모든 손상 완료", value="```" + str(overallData['all_damage_done']) + "```", inline=True)
                                e5.add_field(name="베리어 손상 완료", value="```" + str(overallData['barrier_damage_done']) + "```", inline=True)
                                e5.add_field(name="손상 완료", value="```" + str(overallData['damage_done']) + "```", inline=True)
                                e5.add_field(name="사망자", value="```" + str(overallData['death']) + "```", inline=True)
                                e5.add_field(name="제거", value="```" + str(overallData['elimination']) + "```", inline=True)
                                e5.add_field(name="환경 살인", value="```" + str(overallData['environmental_kill']) + "```", inline=True)
                                e5.add_field(name="최종 타격", value="```" + str(overallData['final_blow']) + "```", inline=True)
                                e5.add_field(name="영웅 피해 완료", value="```" + str(overallData['hero_damage_done']) + "```", inline=True)
                                e5.add_field(name="근접 최종 타격", value="```" + str(overallData['melee_final_blow']) + "```", inline=True)
                                e5.add_field(name="멀티 킬", value="```" + str(overallData['multikill']) + "```", inline=True)
                                e5.add_field(name="목표 처치", value="```" + str(overallData['objective_kill']) + "```", inline=True)
                                e5.add_field(name="목표 시간", value="```" + convert_seconds_to_time(overallData['objective_time']) + "```", inline=True)
                                e5.add_field(name="솔로 킬", value="```" + str(overallData['solo_kill']) + "```", inline=True)
                                e5.add_field(name="불에 보낸 시간", value="```" + convert_seconds_to_time(overallData['time_spent_on_fire']) + "```", inline=True)
                                await message.channel.send(embed=e5)

                                e6 = discord.Embed(color=0xFC9A23, title="{} Overwatch Match Awards".format(playerNickname))
                                e6.add_field(name="메달-골드", value="```" + str(overallData['medal_gold']) + "```", inline=True)
                                e6.add_field(name="카드", value="```" + str(overallData['card']) + "```", inline=True)
                                e6.add_field(name="메달", value="```" + str(overallData['medal']) + "```", inline=True)
                                e6.add_field(name="메달-브론즈", value="```" + str(overallData['medal_bronze']) + "```", inline=True)
                                e6.add_field(name="메달-실버", value="```" + str(overallData['medal_silver']) + "```", inline=True)
                                await message.channel.send(embed=e6)
                        
                    elif response.status_code == 404:
                        await message.channel.send("The user `{}` wasn't found.".format(playerNickname))
                    else:
                        await message.channel.send("Request returned status code " + str(response.status_code))
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
    
    if message.content.startswith("!!도움말"):
        try:
            embed = discord.Embed(title="AliveBot", description="```Help Information```",color=0x5CD1E5)
            embed.add_field(name="팀짜기", value="```!!팀짜기 [count]```", inline=False)
            embed.add_field(name="빼고팀짜기", value="```!!빼고팀짜기 [count] [팀짜기 제외 닉네임]```", inline=False)
            embed.add_field(name="배그경쟁", value="```!!배그경쟁 [게임아이디]```", inline=False)
            embed.add_field(name="배그솔로", value="```!!배그솔로 [게임아이디]```", inline=False)
            embed.add_field(name="배그듀오", value="```!!배그듀오 [게임아이디]```", inline=False)
            embed.add_field(name="배그스쿼드", value="```!!배그스쿼드 [게임아이디]```", inline=False)
            # embed.add_field(name="롤전적", value="```!!롤전적 [게임아이디]```", inline=False)
            embed.add_field(name="옵치일반", value="```!!옵치일반 [배틀Tag]```", inline=False)
            embed.add_field(name="옵치경쟁", value="```!!옵치경쟁 [배틀Tag]```", inline=False)
            await message.channel.send("", embed=embed)
        except:
            embed = discord.Embed(title="도움말 오류",description="날 점검해줘~~~~~~",color=0x5CD1E5)
            await message.channel.send("Error : help", embed=embed)
 
client.run(os.environ['token']);