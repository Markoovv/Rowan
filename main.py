# Rowan bot by VladZodchey

import discord, json, os, re, sqlite3, typing
from discord.ext import commands
from random import choice, randint
from sympy import solve, symbols, sympify
from numexpr import evaluate

base = sqlite3.connect("../../Databases/rowan.db")
c = base.cursor()

config = json.load(open("config.json"))

token = config["token"]
version = config["version"]
sign = config["assembly"]

languages = {}

for path in os.listdir("languages"):
    if os.path.splitext(os.path.basename(path))[1]:
        languages[os.path.splitext(os.path.basename(path))[0]] = json.load(open("languages/" + path, mode="r", encoding="utf"))

def prefix(bot, ctx):
    c.execute("SELECT prefix FROM guilds WHERE gid = ?", (ctx.guild.id,))
    try:
        return c.fetchone()[0]
    except:
        return "$"

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Started up as {0.user}".format(bot))
          
def lang(guild):
    c.execute("SELECT language FROM guilds WHERE gid = ?", (guild,))
    try:
        return languages[c.fetchone()[0]]
    except:
        return languages["en"]

'''@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    c.execute("SELECT voteid FROM guilds WHERE gid = ?", (ctx.guild.id,))
    vid = c.fetchone()
    if vid:
        vid = vid[0].split(",")
    if ctx.channel.id in vid:
        c.execute("SELECT votemoji FROM guilds WHERE gid = ?", (ctx.guild.id,))
        vmoji = c.fetchone()
        if vmoji:
            vmoji = vmoji[0].split(",")
            for emoji in vmoji:
                try:
                    await ctx.add_reaction(emoji)
                except:
                    pass'''
    

@bot.event
async def on_member_join(ctx):
    c.execute("SELECT welcome FROM guilds WHERE gid = ?", (ctx.guild.id,))
    welcome = c.fetchone()
    if welcome:
        await ctx.send(welcome[0].format(ctx.guild.name, ctx.guild.id, ctx.mention))
@bot.event
async def on_guild_join(ctx):
    c.execute("SELECT * FROM guilds WHERE gid = ?", (ctx.id,))
    if c.fetchone():
        c.execute('''UPDATE guilds
SET oid = ?,
auid = NULL,
arid = NULL,
premium = 0,
language = 'en',
updates = NULL,
caps = 0,
url = 0,
swear = NULL,
enabled = 1,
guesstime = 20,
guessrange = 20,
guesstries = 4,
mathtime = 20,
mathrange = 100,
mathops = '+-',
ecid = NULL,
erid = NULL,
count = 0,
welcome = NULL,
prefix = &,
voteid = NULL,
votemoji = 0,
chancemoji = 0
WHERE gid = ?''', (ctx.id()))
    else:
        c.execute('''INSERT INTO guilds
(gid, oid, auid, arid, premium, language, updates, caps, url, swear, enabled, guesstime, guessrange, guesstries, mathtime, mathrange, mathops, ecid, erid, count, welcome, prefix, voteid, votemoji, chancemoji)
VALUES (?, ?, NULL, NULL, 0 ?, NULL, 0, 0, NULL, 1, 20, 20, 4, 20, 100, '+-', NULL, NULL, 0, NULL, '&', NULL, NULL, 0)''', (ctx.id, ctx.owner.id, "en"))
@bot.command()
async def foo(ctx):
    await ctx.reply(lang(ctx.guild.id)["phrases"]["hello"])

@bot.command()
async def prefix(ctx, arg):
    try:
        if len(arg) > 32:
            raise TypeError("Too long!")
        c.execute("UPDATE guilds SET prefix = ? WHERE gid = ?", (arg, ctx.guild.id,))
        base.commit()
        await ctx.reply(lang(ctx.guild.id)["phrases"]["prefix_success"].format(arg))
    except:
        await ctx.reply(lang(ctx.guild.id)["phrases"]["prefix_fail"])
@bot.command()
async def language(ctx, arg):
    if arg in languages.keys():
        c.execute("UPDATE guilds SET language = ? WHERE gid = ?", (arg, ctx.guild.id,))
        base.commit()
        await ctx.send(languages[arg]["phrases"]["lang_success"])
    else:
        await ctx.send(lang(ctx.guild.id)["phrases"]["lang_fail"])


@bot.command()
async def blable(ctx, * , arg):
    # if not swearcheck(ctx):
    await ctx.send(arg)
@bot.command()
async def zen(ctx):
    await ctx.send(lang(ctx.guild.id)["zen"])
@commands.has_permissions(manage_messages=True)
@bot.command()
async def purge(ctx, arg:int):
    try:
        await ctx.channel.purge(limit=arg)
    except:
        await ctx.send(lang(ctx.guild.id)["phrases"]["purge_fail"])
@bot.command()
async def help(ctx, arg:typing.Optional[str] = "all"):
    match arg:
            case "all":
                await ctx.send(lang(ctx.guild.id)["help"]["all"])
            case "help":
                await ctx.send(lang(ctx.guild.id)["help"]["help"])
            case _:
                await ctx.send(lang(ctx.guild.id)["help"]["not_found"])
@bot.command()
async def coin(ctx):
    if choice([True, False]):
        await ctx.send(lang(ctx.guild.id)["phrases"]["heads"])
    else:
        await ctx.send(lang(ctx.guild.id)["phrases"]["tails"])
@bot.command()
async def dice(ctx, arg:typing.Optional[int] = 6):
    try:
        await ctx.send(randint(1, arg))
    except:
        await ctx.send(lang(ctx.guild.id)["phrases"]["dice_fail"])
@bot.command()
async def info(ctx):
    c.execute("SELECT count FROM guilds WHERE gid = ?", (ctx.guild.id,))
    count = c.fetchone()
    if count:
        await ctx.send(lang(ctx.guild.id)["phrases"]["info"].format(version, count[0]))
@bot.command()
async def eval(ctx, *, arg):
    try:
        await ctx.send(str(evaluate(arg)))
    except:
        try:
            expr = sympify("Eq(" + arg.replace("=", ",") + ")")
            solution = ""
            for i in solve(expr):
                solution += f"{i}, "
            if solution:
                await ctx.send(solution[:-2])
            else:
                await ctx.send(lang(ctx.guild.id)["phrases"]["eval_zero"])
        except:
            await ctx.send(lang(ctx.guild.id)["phrases"]["eval_fail"])
        
bot.run(token)
