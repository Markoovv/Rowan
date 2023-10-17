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

@bot.hybrid_command()
async def blable(ctx, *, arg):
    await ctx.send(arg)
@bot.hybrid_command()
async def info(ctx):
    await ctx.send(f'Rowan ver {version}. Author: https://vladzodchey.carrd.co')
@bot.hybrid_command()
async def ask(ctx):
    if choice([True,False]):
        await ctx.send('Yes')
    else:
        await ctx.send('No')
@bot.hybrid_command()
async def dice(ctx, arg):
    try:
        await ctx.send(str(randint(1, int(arg))))
    except:
        await ctx.send('Failed to roll the dice!')
@bot.hybrid_command()
async def eval(ctx, *, arg):
    try:
        await ctx.send(evaluate(arg))
    except:
        await ctx.send('Failed to solve problem!')
@bot.hybrid_command()
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
@bot.hybrid_command(name='rowan_help')
async def help(ctx):
    await ctx.send(f"Rowan bot's prefix is {bot.command_prefix}. List of commands:\n- help - displays this message.\n- info - shows bot info.\n- blable <m> - copies <m> message.\n- ask <q>- gives you yes/no answer to <q> question.\n- dice <a> - rolls a dice with <a> sides.\n- poll <a> <p> - adds <a> digit reactions to your message (max 9). enter yesno to make it a yes/no poll.\n- cheer - cheers you.\n- eval <p> - will try to solve <p> problem.")

bot.run(token)
