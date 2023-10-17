# Rowan bot by VladZodchey

import discord
from discord.ext import commands
import configparser
from numexpr import evaluate
from random import choice, randint

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

token = config['Info']['token']
version = config['Info']['version']

cursewords = config['Prefs']['cursewords'].split(',')
votes = config['Prefs']['votes'].split(',')

bot = commands.Bot(command_prefix='&', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.command()
async def blable(ctx, *, arg):
    await ctx.send(arg)
@bot.command()
async def info(ctx):
    await ctx.send(f'Rowan ver {version}. Author: https://vladzodchey.carrd.co')
@bot.command()
async def ask(ctx):
    if choice([True,False]):
        await ctx.send('Yes')
    else:
        await ctx.send('No')
@bot.command()
async def dice(ctx, arg):
    try:
        await ctx.send(str(randint(1, int(arg))))
    except:
        await ctx.send('Failed to roll the dice!')
@bot.command()
async def eval(ctx, *, arg):
    try:
        await ctx.send(evaluate(arg))
    except:
        await ctx.send('Failed to solve problem!')
@bot.command()
async def poll(ctx, arg):
    if arg == 'yesno' or arg == 'данет':
        await ctx.message.add_reaction(votes[0])
        await ctx.message.add_reaction(votes[1])
    else:
        try:
            for i in range(int(arg)):
                await ctx.message.add_reaction(votes[i+2])
        except:
            await ctx.send('Failed to create poll!')
@commands.has_permissions(manage_messages=True)
@bot.command()
async def purge(ctx, arg:int):
    try:
        await ctx.channel.purge(limit=arg)
    except:
        await ctx.send('Failed to purge the chat!')
@bot.command()
async def rhelp(ctx):
    await ctx.send(f"Rowan bot's prefix is {bot.command_prefix}. List of commands:\n- rhelp - displays this message.\n- info - shows bot info.\n- blable <m> - copies <m> message.\n- ask <q>- gives you yes/no answer to <q> question.\n- dice <a> - rolls a dice with <a> sides.\n- poll <a> <p> - adds <a> digit reactions to your message (max 9). enter yesno to make it a yes/no poll.\n- eval <p> - will try to solve <p> problem.\n- purge <a> - purges <a> amount of messages in chat. Requires manage messages permission!\n- guess - starts a number guesser game.")
@bot.command()
async def guess(ctx):
    num = randint(1,15)
    await ctx.send(f'I am thinking of a number from 1 to 20. You have 4 tries and 15 seconds.')
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    for i in range(4):
        try:
            msg = await bot.wait_for('message', check=check, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send(f"Time's up! My number was {num}.")
        guess = int(msg.content)
        if guess == num:
            await ctx.send(f'You won! my number was indeed {guess}!')
            return
        elif guess < num:
            await ctx.send('My number is higher!')
        else:
            await ctx.send('My number is lower!')
    await ctx.send(f"You ran out of tries. My number was {num}")

bot.run(token)
