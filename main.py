# Rowan bot by VladZodchey

import discord
import configparser
from random import choice, randint

config = configparser.ConfigParser()
config.read('config.ini')
client = discord.Client(intents=discord.Intents.all(), options=8)

@client.event
async def on_ready():
    print('Login success {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content == ('&help'):
        await message.channel.send("Here's a list of supported commands:\n&help - Displays this menu\n&info - Shows current Rowan version\n&blable - Copies you\n&ask - Gives you a yes/no answer\n&dice n - Throws a dice with n amount of sides")
    if message.content.startswith('&eval '):
        print('There was a try to call eval')
        return
        try:
            await message.channel.send(eval(message.content[5::]))
        except:
            await message.channel.send('Failed to solve!')
    if message.content.startswith('&blable '):
        await message.channel.send(message.content[7::])
    if message.content.startswith('&dice '):
        try:
            await message.channel.send(str(randint(1, int(message.content[5::]))))
        except:
            await message.channel.send('Failed to roll the dice!')
    if message.content.startswith('&ask '):
        if choice([True, False]) == True:
            await message.channel.send('Yes')
        else:
            await message.channel.send('No')
    if message.content == ('&info'):
        await message.channel.send(f"Rowan bot ver. {config['Prefs']['version']}")
client.run(config['Prefs']['token'])
