import discord
import configparser
from numexpr import evaluate as evalu
from random import randint, choice

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
client = discord.Client(intents=discord.Intents.all(), options=8)

token = config['Prefs']['token']
version = config['Prefs']['version']
cursewords = config['Prefs']['cursewords']

@client.event
async def on_ready():
    print('Login success {0.user}'.format(client))
@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if any(word in msg.content.lower() for word in cursewords.split(',')):
        await msg.delete()
    match msg.content:
        case '&help':
            await msg.channel.send("Here's a list of implemented commands:\n&help - Displays this msg\n&ask <q> - gives you yes/no answer for q question\n&dice <n> - rolls a dice with n sides\n&eval <p> - evaluates p problem\n&blable <m> - sends m msg\n&info - displays my portfolio carrd.co.")
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
            
        case '&info':
            await msg.channel.send(f'Rowan bot ver {version}. Author carrd: https://vladzodchey.carrd.co/')

client.run(token)
