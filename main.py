import discord
from discord import app_commands
from discord.ext import commands  # DiscordLang
from random import randint, choice
from numexpr import evaluate
import asyncio
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

token = config['INFO']['token']
version = config['INFO']['version']


bot = commands.Bot(command_prefix='&', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
@bot.event
async def on_member_join(ctx):
    await ctx.send(f'Welcome to {ctx.guild.name}')

@bot.command()
async def blable(ctx, *, arg):
    await ctx.send(arg)
@bot.command()
async def eval(ctx, *, arg):
    try:
        await ctx.send(evaluate(arg))
    except:
        await ctx.send("I don't understand the problem!")
@bot.command()
async def dice(ctx, arg):
    try:
        await ctx.send(randint(1, int(arg)))
    except:
        await ctx.send("Failed to roll the dice!")
@bot.command()
async def coin(ctx):
    if choice([True, False]):
        await ctx.send('Tails')
    else:
        await ctx.send('Heads')
@bot.command()
async def info(ctx):
    await ctx.send(f'ROWAN BOT ver {version}.\n QoL bot for small servers\n Author: https://vladzodchey.carrd.co/')
@commands.has_permissions(manage_messages=True)
@bot.command()
async def purge(ctx, arg):
    await ctx.channel.purge(limit=arg)
@bot.command
async def guess(ctx):
    num = randint(1, 20)
    await ctx.send('I guessed a number from 1 to 20. You have 4 tries and 20 seconds.')

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    for i in range(4):
        try:
            msg = bot.wait_for('message', check=check, timeout=20.0)
        except asyncio.TimeoutError:
            await ctx.send(f'You ran out of time! My number was {num}')
            return
        guess = int(msg)
        if guess == num:
            await ctx.send(f'You won! My number was indeed {num}')
        elif guess > num:
            await ctx.send('My number is lower!')
        else:
            await ctx.send('My number is higher!')
    await ctx.send(f'You ran out of tries! My number was {num}')

bot.run(token)
