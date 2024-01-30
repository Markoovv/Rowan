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

def pref(bot, ctx):
    try:
        c.execute("SELECT prefix FROM guilds WHERE gid = ?", (ctx.guild.id,))
        return c.fetchone()[0]
    except:
        return "$"

bot = commands.Bot(command_prefix=pref, intents=discord.Intents.all())
bot.remove_command('help')

debug = bot.get_channel(1201226108616573039) # Специфичный канал для вывода ошибок

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

def incrementate(ctx):
    c.execute("SELECT count FROM guilds WHERE gid = ?", (ctx.guild.id,))
    response = c.fetchone()
    if response  is not None:
        c.execute("UPDATE guilds SET count = ? WHERE gid = ?", (int(response[0]) + 1, ctx.guild.id,))
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
            z = lambda x: x + 1 if x == 0 else abs(x)
            alph = list(filter(str.isalpha, ctx.content))
            if sum(map(str.isupper, alph)) / z(len(alph)) >= int(dat) * 0.01: return True
            return False
        else: return False
    else: return False
def linkcheck(ctx, dat):
    if dat:
        links = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", ctx.content)
        if links: return True
        else: return False
    else: return False
@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    if is_direct(ctx):
        await bot.process_commands(ctx)
    try:
        ctx.author.roles
    except:
        return
    else:
        c.execute("SELECT swear, caps, url, erid, ecid, chancemoji FROM guilds WHERE gid = ?", (ctx.guild.id,))
        response = c.fetchone()
        if response is not None:
            if response[3]:
                erid = response[3].split(",")
            else:
                erid = []
            if response[4]:
                ecid = response[4].split(",")
            else:
                ecid = []
            if (str(ctx.channel.id) in ecid) or any(str(role.id) in erid for role in ctx.author.roles):
                await bot.process_commands(ctx)
            else:
                #print(response[1])
                if swearcheck(ctx, response[0]) or capscheck(ctx, response[1]) or linkcheck(ctx, response[2]):
                    await ctx.delete()
                else:
                    if randint(1, 100) <= int(response[5]):
                        try:
                            await ctx.add_reaction(choice(tuple(languages["en"]["symbolica"]["emoji"]) + ctx.guild.emojis))
                        except discord.Forbidden:
                            c.execute("UPDATE guilds SET chancemoji = 0 WHERE gid = ?", (ctx.guild.id,))
                            base.commit()
                    await bot.process_commands(ctx)

        else:
            await bot.process_commands(ctx)

@bot.event
async def on_member_join(ctx):
    c.execute("SELECT welcome FROM guilds WHERE gid = ?", (ctx.guild.id,))
    welcome = c.fetchone()
    if welcome is not None:
        if welcome[0]:
            await ctx.send(welcome[0].format(ctx.guild.name, ctx.guild.id, ctx.mention, ctx.name))
@bot.event
async def on_guild_join(ctx):
    try:
        c.execute("INSERT INTO guilds(gid, oid, premium, language, caps, url, count, prefix, chancemoji) VALUES(?, ?, 0, 'en', 0, 0, 0, '&', 0)", (ctx.id, ctx.owner.id,))
        base.commit()
    except Exception as e:
        pass
'''@bot.command()
async def foo(ctx):
    await ctx.reply(lang(ctx)["phrases"]["hello"])'''
@commands.has_guild_permissions(manage_guild=True)
@commands.guild_only()
@bot.command()
async def prefix(ctx, arg):
    try:
        if len(arg) > 32:
            raise TypeError
        c.execute("UPDATE guilds SET prefix = ? WHERE gid = ?", (arg, ctx.guild.id,))
        base.commit()
        await ctx.reply(lang(ctx)["phrases"]["prefix_success"].format(arg))
        incrementate(ctx)
    except TypeError:
        await ctx.reply(lang(ctx)["phrases"]["prefix_fail"])
@bot.command()
async def foo(ctx):
    await ctx.reply(lang(ctx)["phrases"]["hello"])
    incrementate(ctx)
@commands.has_guild_permissions(manage_guild=True)
@commands.guild_only()
@bot.command()
async def language(ctx, arg):
    if arg in languages.keys():
        try:
            c.execute("UPDATE guilds SET language = ? WHERE gid = ?", (arg, ctx.guild.id,))
            base.commit()
            await ctx.send(languages[arg]["phrases"]["lang_success"])
            incrementate(ctx)
        except sqlite3.DatabaseError:
            await ctx.send(lang(ctx)["phrases"]["error_db"])
    else:
        await ctx.send(lang(ctx)["phrases"]["lang_fail"])
@commands.cooldown(1, 1, commands.BucketType.user)
@bot.command()
async def blable(ctx, * , arg):
    #if not swearcheck(ctx.message) and not capscheck(ctx.message) and not linkcheck(ctx.message):
    await ctx.send(arg)
@commands.cooldown(1, 3, commands.BucketType.user)
@bot.command()
async def zen(ctx):
    await ctx.send(lang(ctx)["zen"])
    incrementate(ctx)
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
@bot.command()
async def purge(ctx, arg:int = 5):
    await ctx.channel.purge(limit=arg)
    incrementate(ctx)
@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def help(ctx, arg:typing.Optional[str] = "all"):
    if arg in lang(ctx)["help"]:
        await ctx.send(lang(ctx)["help"][arg])
        incrementate(ctx)
    else:
        await ctx.send(lang(ctx)["help"]["not_found"])
    if not is_direct(ctx): incrementate(ctx)
@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command()
async def coin(ctx):
    if choice([True, False]):
        await ctx.send(lang(ctx)["phrases"]["heads"])
    else:
        await ctx.send(lang(ctx)["phrases"]["tails"])
    if not is_direct(ctx): incrementate(ctx)
@commands.cooldown(1, 3, commands.BucketType.user)
@bot.command()
async def dice(ctx, arg:typing.Optional[int] = 6):
    try:
        await ctx.send(randint(1, arg))
    except:
        await ctx.send(lang(ctx)["phrases"]["dice_fail"])
@commands.cooldown(1, 3, commands.BucketType.user)
@bot.command()
async def info(ctx):
    if is_direct(ctx):
        await ctx.send(lang(ctx)["phrases"]["info_fail"])
    else:
        c.execute("SELECT count FROM guilds WHERE gid = ?", (ctx.guild.id,))
        count = c.fetchone()
        if count is not None:
            await ctx.send(lang(ctx)["phrases"]["info"].format(version, count[0]))
            incrementate(ctx)
        else:
            await ctx.send(lang(ctx)["phrases"]["info_fail"])
@commands.cooldown(1, 3, commands.BucketType.user)
@bot.command()
async def eval(ctx, *, arg = "9+10"):
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
            return
    if not is_direct(ctx): incrementate(ctx)
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
        incrementate(ctx)
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
        else: time = 10; rang = 100; oper = "+-"
        incrementate(ctx)
    neg = lambda x: "({})".format(x) if x < 0 else str(x) # Лямбда-функция, или статическая функция
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
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.guild_only()
@bot.command()
async def configure(ctx, comm=None, value1=None, value2 : typing.Union[discord.Role, discord.TextChannel, str] = None):
    #print(comm, value1, value2)
    match comm:
        case "math":
            match value1:
                case "range":
                    try:
                        if value2 is not None:
                            value = int(value2)
                            if value <= 1000 and value >= 5:
                                c.execute("UPDATE guilds SET mathrange = ? WHERE gid = ?", (value, ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                            else:
                                raise ValueError
                        else:
                            c.execute("SELECT mathrange FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(f"{response[0] * -1}-{response[0]}")
                    except sqlite3.DatabaseError and AttributeError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "time":
                    try:
                        if value2 is not None:
                            value = int(value2)
                            if value <= 120 and value >= 5:
                                c.execute("UPDATE guilds SET mathtime = ? WHERE gid = ?", (value, ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                            else:
                                raise ValueError
                        else:
                            c.execute("SELECT mathtime FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(f"{response[0]}s")
                    except sqlite3.DatabaseError and AttributeError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "ops":
                    try:
                        if value2 is not None:
                            if any(char not in "+-*/^" for char in value2):
                                raise ValueError
                            else:
                                if any(value2.count(char) > 1 for char in value2):
                                    raise ValueError
                                else:
                                    c.execute("UPDATE guilds SET mathops = ? WHERE gid = ?", (value2, ctx.guild.id,))
                                    base.commit()
                                    await ctx.send(lang(ctx)["phrases"]["configure_success"].format(value1, value2))
                        else:
                            c.execute("SELECT mathops FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(response[0])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_other"])
                    except sqlite3.DatabaseError and AttributeError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                case _:
                    await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case "guess":
            match value1:
                case "range":
                    try:
                        if value2 is not None:
                            value = int(value2)
                            if value <= 1000 and value >= 5:
                                c.execute("UPDATE guilds SET guessrange = ? WHERE gid = ?", (value, ctx.guild.id,))
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                            else:
                                raise ValueError
                        else:
                            c.execute("SELECT guessrange FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(f"{response[0] * -1}-{response[0]}")
                    except sqlite3.DatabaseError and AttributeError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "time":
                    try:
                        if value2 is not None:
                            value = int(value2)
                            if value <= 120 and value >= 5:
                                c.execute("UPDATE guilds SET guesstime = ? WHERE gid = ?", (value, ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                            else:
                                raise ValueError
                        else:
                            c.execute("SELECT guesstime FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(f"{response[0]}s")
                    except sqlite3.DatabaseError and AttributeError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                case "tries":
                    try:
                        if value2 is not None:
                            value = int(value2)
                            if value <= 32 and value >= 1:
                                c.execute("UPDATE guilds SET guesstries = ? WHERE gid = ?", (value, ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm} {value1}", value2))
                            else:
                                raise ValueError
                        else:
                            c.execute("SELECT guesstries FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(str(response[0]))
                    except sqlite3.DatabaseError and AttributeError:
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
                except sqlite3.DatabaseError and AttributeError:
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
                        if value2 is not None:
                            if int(value2) == 1 or int(value2) == 0:
                                c.execute("UPDATE guilds SET url = ? WHERE gid = ?", (value2, ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(value1, value2))
                            else:
                                raise ValueError
                        else:
                            c.execute("SELECT url FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(str(response[0]))
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_bool"])
                    except sqlite3.DatabaseError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                case "swear":
                    try:
                        if value2 != "null" and value2 is not None:
                            c.execute("UPDATE guilds SET swear = ? WHERE gid = ?", (str(value2).lower(), ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm}-{value1}", f'"{value2}"'))
                        elif value2 == "null":
                            c.execute("UPDATE guilds SET swear = ? WHERE gid = ?", (None, ctx.guild.id,))
                            base.commit()
                            await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm}-{value1}", "None"))
                        else:
                            c.execute("SELECT swear FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response[0]:
                                await ctx.send(response[0])
                            else:
                                await ctx.send("None")
                    except sqlite3.DatabaseError and AttributeError:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                case "caps":
                    if value2:
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
                        except sqlite3.DatabaseError and AttributeError:
                            await ctx.send(lang(ctx)["phrases"]["error_db"])
                    else:
                        c.execute("SELECT caps FROM guilds WHERE gid = ?", (ctx.guild.id,))
                        response = c.fetchone()
                        if response:
                            await ctx.send(lang(ctx)["phrases"]["caps"].format(response[0]))
                        else:
                            await ctx.send(lang(ctx)["phrases"]["error_db"])
                case _:
                    await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case "exclude":
            match value1:
                case "add":
                    if type(value2) == discord.TextChannel:
                        c.execute("SELECT ecid FROM guilds WHERE gid = ?", (ctx.guild.id,))
                        response = c.fetchone()
                        if response is not None:
                            if response[0]:
                                if str(value2.id) in response[0].split(","):
                                    await ctx.send(lang(ctx)["phrases"]["configure_fail_already"].format(f"<#{value2.id}>", f"{comm}-{value1}"))
                                    return
                        new_filter = str(response[0] or '') + f"{value2.id},"
                        c.execute("UPDATE guilds SET ecid = ? WHERE gid = ?", (new_filter, ctx.guild.id,))
                        base.commit()
                        await ctx.send(lang(ctx)["phrases"]["configure_add"].format(f"{comm}-{value1}", f"<#{value2.id}>"))
                    elif type(value2) == discord.Role:
                        c.execute("SELECT erid FROM guilds WHERE gid = ?", (ctx.guild.id,))
                        response = c.fetchone()
                        if response is not None:
                            if response[0]:
                                if str(value2.id) in response[0].split(","):
                                    await ctx.send(lang(ctx)["phrases"]["configure_fail_already"].format(f"<@&{value2.id}>", f"{comm}-{value1}"))
                                    return
                        new_filter = str(response[0] or '') + f"{value2.id},"
                        c.execute("UPDATE guilds SET erid = ? WHERE gid = ?", (new_filter, ctx.guild.id,))
                        base.commit()
                        await ctx.send(lang(ctx)["phrases"]["configure_add"].format(f"{comm}-{value1}", f"<@&{value2.id}>"))
                    else:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_other"])
                case "remove":
                    if type(value2) == discord.TextChannel:
                        c.execute("SELECT ecid FROM guilds WHERE gid = ?", (ctx.guild.id,))
                        response = c.fetchone()
                        if response is not None:
                            if str(value2.id) in response[0].split(","):
                                new_filter = response[0].replace(f"{value2.id},", "")
                            else:
                                await ctx.send(lang(ctx)["phrases"]["configure_fail_notincluded"].format(f"<#{value2.id}>", str(comm)))
                                return
                        else:
                            await ctx.send(lang(ctx)["phrases"]["configure_fail_notincluded"].format(f"<#{value2.id}>", str(comm)))
                            return
                        if new_filter == "":
                            new_filter = None
                        c.execute("UPDATE guilds SET ecid = ? WHERE gid = ?", (new_filter, ctx.guild.id,))
                        base.commit()
                        await ctx.send(lang(ctx)["phrases"]["configure_remove"].format(f"{comm}-{value1}", f"<#{value2.id}>"))
                    elif type(value2) == discord.Role:
                        c.execute("SELECT erid FROM guilds WHERE gid = ?", (ctx.guild.id,))
                        response = c.fetchone()
                        if response is not None:
                            if str(value2.id) in response[0].split(","):
                                new_filter = response[0].replace(f"{value2.id},", "")
                            else:
                                await ctx.send(lang(ctx)["phrases"]["configure_fail_notincluded"].format(f"<#{value2.id}>", str(comm)))
                                return
                        else:
                            await ctx.send(lang(ctx)["phrases"]["configure_fail_notincluded"].format(f"<@&{value2.id}>", str(comm)))
                            return
                        if new_filter == "":
                            new_filter = None
                        c.execute("UPDATE guilds SET erid = ? WHERE gid = ?", (new_filter, ctx.guild.id,))
                        base.commit()
                        await ctx.send(lang(ctx)["phrases"]["configure_remove"].format(f"{comm}-{value1}", f"<@&{value2.id}>"))
                    else:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_other"])
                case "reset":
                    match value2:
                        case "channels":
                            try:
                                c.execute("UPDATE guilds SET ecid = NULL WHERE gid = ?", (ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm}-{value2}", "None"))
                            except sqlite3.DatabaseError:
                                await ctx.send(lang(ctx)["phrases"]["error_db"])
                        case "roles":
                            try:
                                c.execute("UPDATE guilds SET erid = NULL WHERE gid = ?", (ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(f"{comm}-{value2}", "None"))
                            except sqlite3.DatabaseError and AttributeError:
                                await ctx.send(lang(ctx)["phrases"]["error_db"])
                        case _:
                            await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
                case None:
                    c.execute("SELECT erid, ecid FROM guilds WHERE gid = ?", (ctx.guild.id,))
                    response = c.fetchone()
                    if response  is not None:
                        rols = ""
                        chans = ""
                        if response[0] != None:
                            for rol in response[0].split(",")[:-1]:
                                rols += f"<@&{rol}>,"
                        else:
                            rols = "None"
                        if response[1] != None:
                            for chan in response[1].split(",")[:-1]:
                                chans += f"<#{chan}>,"
                        else:
                            chans = "None"
                        await ctx.send(lang(ctx)["phrases"]["configure_excluded"].format(rols, chans))
                    else:
                        await ctx.send(lang(ctx)["phrases"]["error_db"])
                case _:
                    await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case "fun":
            match value1:
                case "emoji":
                    try:
                        if value2 is not None:
                            chance = int(value2)
                            if chance >= 0 or chance <= 100:
                                c.execute("UPDATE guilds SET chancemoji = ? WHERE gid = ?", (chance, ctx.guild.id,))
                                base.commit()
                                await ctx.send(lang(ctx)["phrases"]["configure_success"].format(value1, f"{chance}%"))
                            else:
                                raise ValueError
                        else:
                            c.execute("SELECT chancemoji FROM guilds WHERE gid = ?", (ctx.guild.id,))
                            response = c.fetchone()
                            if response:
                                await ctx.send(f"{response[0]}%")
                    except ValueError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_int"])
                    except sqlite3.DatabaseError and AttributeError:
                        await ctx.send(lang(ctx)["phrases"]["configure_fail_db"])
                case _:
                    await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case _:
            await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
    incrementate(ctx)
@commands.has_guild_permissions(kick_members=True)
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.guild_only()
@bot.command()
async def kick(ctx, member : discord.Member, reason = None):
    await member.kick(reason=reason)
    if reason:
        reason = f", {reason}"
    else:
        reason = ""
    await ctx.send(lang(ctx)["phrases"]["kick_reason"].format(member, ctx.author.mention, reason))
    incrementate(ctx)
@commands.has_guild_permissions(ban_members=True)
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.guild_only()
@bot.command()
async def ban(ctx, member : discord.Member, reason = None):
    await member.ban(reason=reason)
    if reason:
        reason = f", {reason}"
    else:
        reason = ""
    await ctx.send(lang(ctx)["phrases"]["ban_reason"].format(member, ctx.author.mention, reason))
    incrementate(ctx)
@commands.has_guild_permissions(moderate_members=True)
@commands.cooldown(1, 3, commands.BucketType.user)
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
    incrementate(ctx)
@commands.has_guild_permissions(moderate_members=True)
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.guild_only()
@bot.command()
async def unmute(ctx, member : discord.Member):
    await member.timeout(None)
    await ctx.send(lang(ctx)["phrases"]["unmute_reason"].format(member.mention, ctx.author.mention)) 
    incrementate(ctx)
@commands.has_guild_permissions(manage_guild=True)
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.guild_only()
@bot.command()
async def register(ctx):
    c.execute("SELECT * FROM guilds WHERE gid = ?", (ctx.guild.id,))
    if c.fetchone():
        await ctx.send(lang(ctx)["phrases"]["register_already"])
    else:
        c.execute("INSERT INTO guilds(gid, oid, premium, language, caps, url, count, prefix, chancemoji) VALUES(?, ?, 0, 'en', 0, 0, 0, '&', 0)", (ctx.guild.id, ctx.guild.owner.id,))
        base.commit()
        await ctx.send(lang(ctx)["phrases"]["register_success"])
        incrementate(ctx)
@commands.cooldown(1, 3, commands.BucketType.user)
@bot.command()
async def poll(ctx, arg : int = 0):
    if arg == 0:
        await ctx.message.add_reaction("✔️")
        await ctx.message.add_reaction("❌")
    elif 2 <= arg <= 10:
        for i in range(arg):
            await ctx.message.add_reaction(languages["en"]["symbolica"]["poll"][i])
    else:
        await ctx.send(lang(ctx)["phrases"]["poll_fail"])
    if not is_direct(ctx): incrementate(ctx)
@bot.command()
async def shutdown(ctx):
    if ctx.author.id == 619200346379780098 or ctx.author.id == 1125066987421302876:
        base.commit()
        base.close()
        exit
    else:
        await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
@bot.event
async def on_command_error(ctx, error):
    match type(error):
        case commands.errors.MissingRequiredArgument:
            await ctx.send(lang(ctx)["phrases"]["error_specification"])
        case commands.errors.MissingPermissions:
            await ctx.send(lang(ctx)["phrases"]["error_permissions_your"])
        case discord.Forbidden:
            try:
                await ctx.send(lang(ctx)["phrases"]["error_permissions_mine"])
            except:
                pass
        case commands.errors.BadArgument:
            await ctx.send(lang(ctx)["phrases"]["error_argument"])
        case commands.errors.NoPrivateMessage:
            await ctx.send(lang(ctx)["phrases"]["error_private"])
        case commands.errors.CommandNotFound:
            await ctx.send(lang(ctx)["phrases"]["configure_unknown"])
        case commands.errors.CommandOnCooldown:
            pass
        case _:
            try:
                await ctx.send(lang(ctx)["phrases"]["error"])
                await debug.send(f"ROWAN ИСПЫТЫВАЕТ ПРОБЛЕМУ: {error}")
            except Exception as e:
                print(e)
            print(error)
bot.run(token)
