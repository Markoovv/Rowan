# Rowan bot by VladZodchey

import discord
import configparser
from numexpr import evaluate as evalu
from random import randint, choice

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
client = discord.Client(intents=discord.Intents.all(), options=8)

token = config['Prefs']['token']
version = config['Prefs']['version']
cursewords = config['Prefs']['cursewords'].split(',')
votes = config['Prefs']['votes'].split(',')
cheers = config['Prefs']['phrases'].split(',')

@client.event
async def on_ready():
    print('Login success {0.user}'.format(client))
@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if any(word in msg.content.lower() for word in cursewords):
        await msg.delete()
    match msg.content:
        case '&help':
            await msg.channel.send("Here's a list of implemented commands:\n&help - Displays this msg\n&ask <q> - gives you yes/no answer for q question\n&dice <n> - rolls a dice with n sides\n&eval <p> - evaluates p problem (Disabled)\n&blable <m> - sends m msg\n&info - displays my portfolio carrd.co\n&poll <a/yesno> <c> - automatically adds reactions to your message. <a> - Adds 1-9 digit emojis; <yesno> - Adds checkmark/cross emojis\n&cheer - Sends you a cheer message!")
        case s if s.startswith('&blable '):
            await msg.channel.send(msg.content[7::])
        case s if s.startswith('&ask '):
            if choice([True, False]):
                await msg.channel.send('Yes')
            else:
                await msg.channel.send('No')
        case s if s.startswith('&dice '):
            try:
                await msg.channel.send(str(randint(1, int(msg.content[5::]))))
            except:
                await msg.channel.send('Failed to roll the dice! Did you put a proper value?')
        case s if s.startswith('&eval'):
            if '9+10' in msg.content or '9 + 10' in msg.content:
                await msg.channel.send('21')
                return
            try:
                await msg.channel.send(evalu(msg.content[6::]))
            except:
                await msg.channel.send('Failed to solve problem')
        case s if s.startswith('&poll'):
            if msg.content[6:11] == 'yesno':
                await msg.add_reaction('\U00002714')
                await msg.add_reaction('\U0000274C')
            else:
                try:
                    for a in range(int(msg.content[6:7])):
                        await msg.add_reaction(votes[a])
                except:
                    await msg.channel.send('Failed to register poll!')
        case '&cheer':
            await msg.channel.send(cheers[randint(0,len(cheers))])
        
        case '&info':
            await msg.channel.send(f'Rowan bot ver {version}. Author carrd: https://vladzodchey.carrd.co/')

client.run(token)
