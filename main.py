# Rowan bot by VladZodchey

import discord, json, os, sqlite3, typing
from discord.ext import commands
from random import choice, randint
from sympy import solve, sympify
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
    
    try:
        c.execute("SELECT prefix FROM guilds WHERE gid = ?", (ctx.guild.id,))
        return c.fetchone()[0]
    except:
        return "$"

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Started up as {0.user}".format(bot))
    
def is_direct(ctx): #EAFP method
    try:
        ctx.guild.id
        return False
    except:
        return True
def lang(ctx):
    if is_direct(ctx):
        return languages["en"]
    else:
        c.execute("SELECT language FROM guilds WHERE gid = ?", (ctx.guild.id,))
        try:
            return languages[c.fetchone()[0]]
        except:
            return languages["en"]

'''@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    #await ctx.reply(is_direct(ctx))'''
    

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
WHERE gid = ?''', (ctx.id))
    else:
        c.execute('''INSERT INTO guilds
(gid, oid, auid, arid, premium, language, updates, caps, url, swear, enabled, guesstime, guessrange, guesstries, mathtime, mathrange, mathops, ecid, erid, count, welcome, prefix, voteid, votemoji, chancemoji)
VALUES (?, ?, NULL, NULL, 0 ?, NULL, 0, 0, NULL, 1, 20, 20, 4, 20, 100, '+-', NULL, NULL, 0, NULL, '&', NULL, NULL, 0)''', (ctx.id, ctx.owner.id, "en"))
@bot.command()
async def foo(ctx):
    await ctx.reply(lang(ctx)["phrases"]["hello"])

@bot.command()
async def prefix(ctx, arg):
    try:
        if len(arg) > 32:
            raise TypeError("Too long!")
        c.execute("UPDATE guilds SET prefix = ? WHERE gid = ?", (arg, ctx.guild.id,))
        base.commit()
        await ctx.reply(lang(ctx)["phrases"]["prefix_success"].format(arg))
    except:
        await ctx.reply(lang(ctx)["phrases"]["prefix_fail"])
@bot.command()
async def language(ctx, arg):
    if is_direct(ctx):
        await ctx.send(languages[arg]["phrases"]["lang_direct"])
    else:
        if arg in languages.keys():
            c.execute("UPDATE guilds SET language = ? WHERE gid = ?", (arg, ctx.guild.id,))
            base.commit()
            await ctx.send(languages[arg]["phrases"]["lang_success"])
        else:
            await ctx.send(lang(ctx)["phrases"]["lang_fail"])
@bot.command()
async def blable(ctx, * , arg):
    # if not swearcheck(ctx):
    await ctx.send(arg)
@bot.command()
async def zen(ctx):
    await ctx.send(lang(ctx)["zen"])
@commands.has_permissions(manage_messages=True)
@bot.command()
async def purge(ctx, arg:int):
    try:
        await ctx.channel.purge(limit=arg)
    except:
        await ctx.send(lang(ctx)["phrases"]["purge_fail"])
@bot.command()
async def help(ctx, arg:typing.Optional[str] = "all"):
    if arg in lang(ctx)["help"]:
        await ctx.send(lang(ctx)["help"][arg])
    else:
        await ctx.send(lang(ctx)["help"]["not_found"])
@bot.command()
async def coin(ctx):
    if choice([True, False]):
        await ctx.send(lang(ctx)["phrases"]["heads"])
    else:
        await ctx.send(lang(ctx)["phrases"]["tails"])
@bot.command()
async def dice(ctx, arg:typing.Optional[int] = 6):
    try:
        await ctx.send(randint(1, arg))
    except:
        await ctx.send(lang(ctx)["phrases"]["dice_fail"])
@bot.command()
async def info(ctx):
    if is_direct(ctx):
        await ctx.send(lang(ctx)["phrases"]["info_fail"])
    else:
        c.execute("SELECT count FROM guilds WHERE gid = ?", (ctx.guild.id,))
        count = c.fetchone()
        if count:
            await ctx.send(lang(ctx)["phrases"]["info"].format(version, count[0]))
@bot.command()
async def eval(ctx, *, arg):
    arg = arg.replace("^", "**")
    try:
        await ctx.send(str(evaluate(arg)))
    except:
        try:
            expr = sympify("Eq(" + arg.replace("=", ",") + ")")
            solution = ""
            for i in solve(expr):
                solution += f"{i}, "
            if solution:
                solution = solution.replace("**", "^")
                solution = solution.replace("*", "×")
                await ctx.send(solution[:-2])
            else:
                await ctx.send(lang(ctx)["phrases"]["eval_zero"])
        except:
            await ctx.send(lang(ctx)["phrases"]["eval_fail"])
@bot.command()
async def guess(ctx):
    if is_direct(ctx): time = 10; rang = 20; tris = 4
    else:
        c.execute("SELECT guesstime, guessrange, guesstries FROM guilds WHERE gid = ?", (ctx.guild.id,))
        response = c.fetchone()
        if response:
            if response[0]: time = response[0]
            else: time = 10
            if response[1]: rang = response[1]
            else: rang = 20
            if response[2]: tris = response[2]
            else: tris = 4
        else: time = 10; rang = 20; tris = 4
    num = randint(1, rang)
    await ctx.send(lang(ctx)["phrases"]["guess_start"].format(rang, time, tris))
    def check(msg): 
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lstrip('-').isdigit()
    for i in range(tris):
        try:
            msg = await bot.wait_for('message', check=check, timeout=time)
        except:
            return await ctx.send(lang(ctx)["phrases"]["guess_fail_time"].format(num))
        guess = int(msg.content)
        if guess == num:
            await ctx.send(lang(ctx)["phrases"]["guess_win"].format(num))
            return
        else:
            if guess > num:
                await ctx.send(lang(ctx)["phrases"]["guess_smaller"])
            else:
                await ctx.send(lang(ctx)["phrases"]["guess_bigger"])
    await ctx.send(lang(ctx)["phrases"]["guess_fail_tries"].format(num))
@bot.command()
async def math(ctx):
    if is_direct(ctx): 
        time = 10 
        rang = 100 
        oper = "+-"
    else:
        c.execute("SELECT mathtime, mathrange, mathops FROM guilds WHERE gid = ?", (ctx.guild.id,))
        response = c.fetchone()
        if response:
            if response[0]: time = response[0]
            else: time = 10
            if response[1]: rang = response[1]
            else: rang = 100
            if response[2]: oper = response[2]
            else: oper = "+-"
        else:
            time = 10
            rang = 100
            oper = "+-"
    neg = lambda x: "({})".format(x) if x < 0 else str(x)
    expr = str(randint(rang * -1, rang)) + choice(oper) + str(neg(randint(rang * -1, rang))) #str(randint(rang * -1, rang))
    num = round(float(evaluate(expr)), 2)
    await ctx.send(lang(ctx)["phrases"]["math_start"].format(expr, time))
    def check(msg): 
        try:
            float(msg.content)
            return msg.author == ctx.author and msg.channel == ctx.channel
        except:
            return False
    try:
        msg = await bot.wait_for('message', check=check, timeout=time)
    except:
        await ctx.send(lang(ctx)["phrases"]["math_fail_time"].format(num))
    guess = float(msg.content)
    if guess == num:
        await ctx.send(lang(ctx)["phrases"]["math_win"].format(num))
    else:
        await ctx.send(lang(ctx)["phrases"]["math_fail_wrong"].format(num))
bot.run(token)
