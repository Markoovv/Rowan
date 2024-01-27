# Rowan bot by VladZodchey

import discord, json, os, sqlite3, typing, asyncio, re
from datetime import datetime, timedelta
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
def swearcheck(ctx, dat):
    swears = dat
    if swears:
        swearlist = swears.split(",")
        if any(swear in ctx.content.lower() for swear in swearlist):
            return True
        else:
            return False
    else:
        return False
def capscheck(ctx, dat):
    #print((ctx.author.name, ctx.guild.name, ctx.content))
    if dat:
        if dat != 0:
            z = lambda x : x + 1 if x == 0 else x
            alph = list(filter(str.isalpha, ctx.content))
            if sum(map(str.isupper, alph)) / len(z(alph)) >= dat * 0.01: return True
            return False
        else: return False
    else: return False
def linkcheck(ctx, dat):
    return False
    '''if dat:
        links = re.findall(r"/((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)/", ctx.content)
        if links: return True
        else: return False
    else: return False'''
@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    if is_direct(ctx):
        await bot.process_commands(ctx)
    else:
        c.execute("SELECT swear, caps, url FROM guilds WHERE gid = ?", (ctx.guild.id,))
        response = c.fetchone()
        if response:
            if swearcheck(ctx, response[0]) or capscheck(ctx, response[1]) or linkcheck(ctx, response[2]):
                await ctx.delete()
            else:
                await bot.process_commands(ctx)
        else:
            await bot.process_commands(ctx)
    

@bot.event
async def on_member_join(ctx):
    c.execute("SELECT welcome FROM guilds WHERE gid = ?", (ctx.guild.id,))
    welcome = c.fetchone()
    if welcome:
        await ctx.send(welcome[0].format(ctx.guild.name, ctx.guild.id, ctx.mention))

@bot.command()
async def foo(ctx):
    await ctx.reply(lang(ctx)["phrases"]["hello"])
@commands.has_guild_permissions(manage_guild=True)
@commands.guild_only()
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
@commands.has_guild_permissions(manage_guild=True)
@commands.guild_only()
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
    #if not swearcheck(ctx.message) and not capscheck(ctx.message) and not linkcheck(ctx.message):
    await ctx.send(arg)
@bot.command()
async def zen(ctx):
    await ctx.send(lang(ctx)["zen"])
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
@bot.command()
async def purge(ctx, arg:int = 5):
    await ctx.channel.purge(limit=arg)
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
        else:
            await ctx.send(lang(ctx)["phrases"]["info_fail"])
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
@commands.cooldown(1, 30, commands.BucketType.user)
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
    def check(m): 
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lstrip('-').isdigit()
    for i in range(tris):
        try:
            msg = await bot.wait_for('message', check=check, timeout=time)
            guess = int(msg.content)
            if guess == num:
                await ctx.send(lang(ctx)["phrases"]["guess_win"].format(num))
                return
            else:
                if guess > num:
                    await ctx.send(lang(ctx)["phrases"]["guess_smaller"])
                else:
                    await ctx.send(lang(ctx)["phrases"]["guess_bigger"])
        except asyncio.TimeoutError:
            return await ctx.send(lang(ctx)["phrases"]["guess_fail_time"].format(num))
    await ctx.send(lang(ctx)["phrases"]["guess_fail_tries"].format(num))
@commands.cooldown(1, 10, commands.BucketType.user)
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
    def check(m): 
        try:
            float(m.content)
            return m.author == ctx.author and m.channel == ctx.channel
        except:
            return False
    try:
        msg = await bot.wait_for('message', check=check, timeout=time)
        guess = float(msg.content)
        if guess == num:
            await ctx.send(lang(ctx)["phrases"]["math_win"].format(num))
        else:
            await ctx.send(lang(ctx)["phrases"]["math_fail_wrong"].format(num))
    except asyncio.TimeoutError:
        await ctx.send(lang(ctx)["phrases"]["math_fail_time"].format(num))
    
@commands.has_permissions(manage_guild=True)
@commands.guild_only()
@bot.command()
async def configure(ctx, comm=None, value1=None, value2=None):
    #print(comm, value1, value2)
    match comm:
        case "caps":
            try:
                value = int(value1)
                if value <= 100 and value >= 0:
                    c.execute("UPDATE guilds SET caps = ? WHERE gid = ?", (value, ctx.guild.id))
                    base.commit()
                else:
                    raise ValueError
            except sqlite3.DatabaseError:
                await ctx.send(lang(ctx)["phrases"]["error_db"])
            except ValueError:
                await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
        case "url":
            try:
                value = int(value1)
                if value == 0 or value == 1:
                    c.execute("UPDATE guilds SET url = ? WHERE gid = ?", (value, ctx.guild.id,))
                else:
                    raise ValueError
            except sqlite3.DatabaseError:
                await ctx.send(lang(ctx)["phrases"]["error_db"])
            except ValueError:
                await ctx.send(lang(ctx)["phrases"]["configure_fail_other"])
        case "math":
            match value1:
                case "range":
                    try:
                        value = int(value2)
                        if value <= 1000 and value >= 5:
                            c.execute("UPDATE guilds SET mathrange = ? WHERE gid = ?", (value, ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                        else:
                            raise ValueError
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "time":
                    try:
                        value = int(value2)
                        if value <= 120 and value >= 5:
                            c.execute("UPDATE guilds SET mathtime = ? WHERE gid = ?", (value, ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                        else:
                            raise ValueError
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "ops":
                    if any(char not in "+-*/^" for char in value2):
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_other"])
                        print("ended in cycle 1")
                    else:
                        if any(value2.count(char) > 1 for char in value2):
                            await ctx.send(lang(ctx)["phrases"]["configure_fail_other"])
                            print("ended in cycle 2")
                            for char in value2:
                                print(value2.count(char))
                        else:
                            try:
                                c.execute("UPDATE guilds SET mathops = ? WHERE gid = ?", (value2, ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(value1, value2))
                            except sqlite3.DatabaseError:
                                await ctx.send(lang(ctx)["phrases"]["error_db"])
                case _:
                    await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case "guess":
            match value1:
                case "range":
                    try:
                        value = int(value2)
                        if value <= 1000 and value >= 5:
                            c.execute("UPDATE guilds SET mathrange = ? WHERE gid = ?", (value, ctx.guild.id,))
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                        else:
                            raise ValueError
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "time":
                    try:
                        value = int(value2)
                        if value <= 120 and value >= 5:
                            c.execute("UPDATE guilds SET mathtime = ? WHERE gid = ?", (value, ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                        else:
                            raise ValueError
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "tries":
                    try:
                        value = int(value2)
                        if value <= 32 and value >= 1:
                            c.execute("UPDATE guilds SET mathtime = ? WHERE gid = ?", (value, ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                        else:
                            raise ValueError
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case _:
                    await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case "welcome":
            if value1 == "null":
                c.execute("UPDATE guilds SET welcome = NULL WHERE gid = ?", (ctx.guild.id,))
                base.commit()
                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(comm, "none"))
            elif value1:
                formats = re.findall(r"(?<=(?<!\{)\{)[^{}]*(?=\}(?!\}))", value1)
                try:
                    for form in formats:
                        if int(form) > 3:
                            raise TypeError
                        else:
                            continue
                except TypeError:
                    await ctx.send(lang(ctx)["phrases"]["configure_fail_format"])
                    return
                except sqlite3.DatabaseError:
                    await ctx.send(lang(ctx)["phrases"]["error_db"])
                    return
                c.execute("UPDATE guilds SET welcome = ? WHERE gid = ?", (value1, ctx.guild.id))
                base.commit()
                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(comm, f'"{value1}"'))
            else:
                c.execute("SELECT welcome FROM guilds WHERE gid = ?", (ctx.guild.id,))
                response = c.fetchone()
                if response != None:
                    await ctx.send(response[0])
                else:
                    await ctx.send(lang(ctx)["phrases"]["welcome_null"])
        case "filter":
            match value1:
                case "url":
                    try:
                        if int(value2) == 1 or int(value2) == 0:
                            c.execute("UPDATE guilds SET url = ? WHERE gid = ?", (value2, ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(value1, value2))
                        else:
                            raise ValueError
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_bool"])
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                case "swear":
                    c.execute("UPDATE guilds SET swear = ? WHERE gid = ?", (ctx.gui))
                case "caps":
                    try:
                        value = int(value2)
                        if value >= 0 and value <= 100:
                            c.execute("UPDATE guilds SET caps = ? WHERE gid = ?", (value, ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(value1, value2))
                        else:
                            raise ValueError
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                
                    
        case _:
            await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
@commands.has_guild_permissions(kick_members=True)
@commands.guild_only()
@bot.command()
async def kick(ctx, member : discord.Member, reason = None):
    await member.kick(reason=reason)
    if reason:
        reason = f", {reason}"
    else:
        reason = ""
    await ctx.send(lang(ctx)["phrases"]["kick_reason"].format(member, ctx.author.mention, reason))
@commands.has_guild_permissions(ban_members=True)
@commands.guild_only()
@bot.command()
async def ban(ctx, member : discord.Member, reason = None):
    await member.ban(reason=reason)
    if reason:
        reason = f", {reason}"
    else:
        reason = ""
    await ctx.send(lang(ctx)["phrases"]["ban_reason"].format(member, ctx.author.mention, reason))
@commands.has_guild_permissions(moderate_members=True)
@commands.guild_only()
@bot.command()
async def mute(ctx, member : discord.Member, reason = None, days : int = 0, hours : int = 0, minutes : int = 5):
    duration = timedelta(minutes=minutes, hours=hours, days=days)
    await member.timeout(duration, reason=reason)
    if reason:
        reason = f", {reason}"
    else:
        reason = ""
    await ctx.send(lang(ctx)["phrases"]["mute_reason"].format(member, duration, ctx.author.mention, reason))
@commands.has_guild_permissions(moderate_members=True)
@commands.guild_only()
@bot.command()
async def unmute(ctx, member : discord.Member):
    await member.timeout(None)
    await ctx.send(lang(ctx)["phrases"]["unmute_reason"].format(member.mention, ctx.author.mention)) 
@bot.event
async def on_command_error(ctx, error):
    match type(error):
        case commands.errors.MissingRequiredArgument:
            await ctx.send(lang(ctx)["phrases"]["error_specification"])
        case commands.errors.MissingPermissions:
            await ctx.send(lang(ctx)["phrases"]["error_permissions_your"])
        case discord.Forbidden:
            await ctx.send(lang(ctx)["phrases"]["error_permissions_mine"])
        case commands.errors.BadArgument:
            await ctx.send(lang(ctx)["phrases"]["error_argument"])
        case commands.errors.NoPrivateMessage:
            await ctx.send(lang(ctx)["phrases"]["error_private"])
        case commands.errors.CommandNotFound:
            await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case commands.errors.CommandOnCooldown:
            pass
        case _:
            await ctx.send(lang(ctx)["phrases"]["error"])
            print(error)
bot.run(token)
