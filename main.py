# Rowan bot by VladZodchey

import asyncio, discord, configparser, sqlite3
from discord.ext import commands
from numexpr import evaluate
from random import choice, randint
from time import sleep

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

token = config['Info']['token']
version = config['Info']['version']

votes = config['Prefs']['votes'].split(',')
en_comms = open('asset/en-help.txt', 'r')
ru_comms = open('asset/ru-help.txt', 'r', encoding='utf-8')
pythonzen = open('asset/zen.txt', 'r')

base = sqlite3.connect('../../Databases/rowan.db')
c = base.cursor()

ru = open('asset/ru.txt', 'r', encoding='utf-8').read().splitlines()
en = open('asset/en.txt', 'r').read().splitlines()

bot = commands.Bot(command_prefix='&', intents=discord.Intents.all())
bot.remove_command('help')

def get_lang(guild_id : int, phrase):
    c.execute('SELECT language FROM Preferences WHERE guild = ?', (guild_id,))
    res = c.fetchone()
    if res[0] == 0:
        if phrase <= len(en): 
            return en[phrase]
        else:
            return 'Phrase id outside of phrase pack' # Фраза не найдена
    elif res[0] == 1:
        if phrase <= len(ru):
            return ru[phrase]
        else:
            return 'Айди фразы вне пака фраз' # Фраза не найдена
    else:
        return 'Queried guild not found. Please register using &register' # Сервер не найден
def incrementate(guild_id : int):
    c.execute('SELECT executed_comms FROM Preferences WHERE guild = ?', (guild_id,))
    res = c.fetchone()
    if res:
        add = res[0] + 1
        c.execute('UPDATE Preferences SET executed_comms = ? WHERE guild = ?', (add, guild_id,))
        base.commit()
@commands.has_permissions(administrator=True)
@bot.command()              
async def register(ctx):
    try:
        c.execute('SELECT * FROM Guilds WHERE guild_id = ?', (ctx.guild.id,))
        if c.fetchone():
            await ctx.send(get_lang(ctx.guild.id, 20)) # Уже зарегестрирован
        else:
            try:
                c.execute('INSERT INTO Guilds (guild_id, prefix)VALUES (?, ?)', (ctx.guild.id, '&',))
                base.commit()
                c.execute('INSERT INTO Preferences (language, guild, executed_comms) VALUES (?, ?, ?)', (0, ctx.guild.id, 0,))
                base.commit()
                await ctx.send(get_lang(ctx.guild.id, 21)) # Успех
            except Exception as e:
                await ctx.send(get_lang(ctx.guild.id, 23).format(e)) # Ошибка
    except:
        await ctx.send(get_lang(ctx.guild.id, 19)) # Недостаточно прав
@commands.has_permissions(administrator=True)
@bot.command()
async def lang(ctx, arg):
    try:
        c.execute('SELECT * FROM Guilds WHERE guild_id = ?', (ctx.guild.id,))
        res = c.fetchone()
        if res:
            if arg == 'english':
                c.execute('UPDATE Preferences SET language = ? WHERE guild = ?', (0, ctx.guild.id,))
                base.commit()
                await ctx.send('Succesfully set language to english') # Язык сменён на английский
            elif arg == 'russian':
                c.execute('UPDATE Preferences SET language = ? WHERE guild = ?', (1, ctx.guild.id,))
                base.commit()
                await ctx.send('Язык успешно сменён на русский') # Язык сменён на русский
            else:
                await ctx.send(get_lang(ctx.guild.id, 22)) # Язык не распознан
        else:
            await ctx.send('Your server is not registered. Please register using &register.') # Гильдия не зарегистрирована
    except:
        await ctx.send(get_lang(ctx.guild.id, 18))
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
@bot.event
async def on_member_join(ctx):
    await ctx.send(get_lang(ctx.guild.id, 0).format(ctx.guild.id)) # Добро пожаловать
@bot.event
async def on_guild_join(ctx):
    c.execute('SELECT * FROM Guilds WHERE guild_id = ?', (ctx.guild.id,))
    if c.fetchone():
        pass
    else:
        try:
            c.execute('INSERT INTO Guilds (guild_id, prefix)VALUES (?, ?)', (ctx.guild.id, '&',))
            base.commit()
            c.execute('INSERT INTO Preferences (language, guild, executed_comms) VALUES (?, ?, ?)', (0, ctx.guild.id, 0,))
            base.commit()
            print(f'Joining guild {ctx.id}:{ctx.name}, register success')
        except Exception as e:
            print(f'Joining guild {ctx.id}:{ctx.name}, experiencing a problem: {e}')
@bot.command()
async def blable(ctx, * , arg):
    await ctx.send(arg)
    incrementate(ctx.guild.id)
@bot.command()
async def info(ctx):
    await ctx.send(get_lang(ctx.guild.id, 1).format(version)) # Инфо о рябине и создателе
    incrementate(ctx.guild.id)
@bot.command()
async def coin(ctx):
    if choice([True, False]):
        await ctx.send(get_lang(ctx.guild.id, 2)) # Орёл
    else:
        await ctx.send(get_lang(ctx.guild.id, 3)) # Решка
    incrementate(ctx.guild.id)
@bot.command()
async def dice(ctx, arg):
    try:
        await ctx.send(str(randint(1, int(arg))))
    except:
        await ctx.send(get_lang(ctx.guild.id, 4)) # Не удалось кинуть кубик
    incrementate(ctx.guild.id)
@bot.command()
async def eval(ctx, *, arg):
    try:
        await ctx.send(evaluate(arg)) 
    except:
        await ctx.send(get_lang(ctx.guild.id, 5)) # Не удалось решить пример
    incrementate(ctx.guild.id)
@bot.command()
async def poll(ctx, arg):
    if arg == 'yesno' or arg == 'данет':
        await ctx.message.add_reaction(votes[0])
        await ctx.message.add_reaction(votes[1])
        incrementate(ctx.guild.id)
    else:
        try:
            for i in range(int(arg)):
                await ctx.message.add_reaction(votes[i+2])
                sleep(0.02)
                incrementate(ctx.guild.id)
        except:
            await ctx.send(get_lang(ctx.guild.id, 6)) # Не удалось создать опрос
@commands.has_permissions(manage_messages=True)
@bot.command()
async def purge(ctx, arg:int):
    try:
        await ctx.channel.purge(limit=arg)
        incrementate(ctx.guild.id)
    except:
        await ctx.send(get_lang(ctx.guild.id, 7)) # Недостаточно прав
@bot.command()
async def zen(ctx):
    await ctx.send(pythonzen.read()) # Зен пайтон
    incrementate(ctx.guild.id)
@bot.command()
async def help(ctx):
    c.execute('SELECT language FROM Preferences WHERE guild = ?', (int(ctx.guild.id),))
    res = c.fetchone()
    if res[0] == 0:
        await ctx.send(en_comms.read()) # Команды на английском
        incrementate(ctx.guild.id)
    elif res[0] == 1:
        await ctx.send(ru_comms.read()) # Команды на русском
        incrementate(ctx.guild.id)
    else:
        await ctx.send('Your guild is not registered. Please register using &register') # Гильдия не зарегистрирована
@bot.command()
async def guess(ctx): # Игра на "угадай число"
    num = randint(1,20)
    await ctx.send(get_lang(ctx.guild.id, 8)) # Первоначальный ответ
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    incrementate(ctx.guild.id)
    for i in range(4):
        try:
            msg = await bot.wait_for('message', check=check, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send(get_lang(ctx.guild.id, 9).format(num)) # Закончилось время
        guess = int(msg.content)
        if guess == num:
            await ctx.send(get_lang(ctx.guild.id, 10).format(num)) # Верно угадано
            return
        elif guess < num:
            await ctx.send(get_lang(ctx.guild.id, 11)) # Число больше введённого
        else:
            await ctx.send(get_lang(ctx.guild.id, 12)) # Число меньше введённого
    await ctx.send(get_lang(ctx.guild.id, 13).format(num)) # Закончились попытки
@bot.command()
async def math(ctx): # Игра на решение арифметики
    expr = str(randint(-100, 100)) + choice(['+', '-']) + str(randint(-100, 100))
    res = evaluate(expr)
    await ctx.send(get_lang(ctx.guild.id, 14).format(expr)) # Первоначальный запрос
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lstrip('-').isdigit()
    incrementate(ctx.guild.id)
    try:
        msg = await bot.wait_for('message', check=check, timeout=20.0)
    except asyncio.TimeoutError:
        return await ctx.send(get_lang(ctx.guild.id, 15).format(res)) # Закончилось время
    guess = int(msg.content)
    if guess == res:
        await ctx.send(get_lang(ctx.guild.id, 17).format(res)) # Правильное решение
        return
    else:
        await ctx.send(get_lang(ctx.guild.id, 16).format(res)) # Неправильное решение
        return
@bot.command()
async def test(ctx, arg : int):
    await ctx.send(get_lang(ctx.guild.id, arg,))
    incrementate(ctx.guild.id)
@bot.command()
async def count(ctx):
    c.execute('SELECT executed_comms FROM Preferences WHERE guild = ?', (int(ctx.guild.id),))
    res = c.fetchone()
    if res:
        await ctx.send(get_lang(ctx.guild.id, 23).format(res[0]))
    else:
        await ctx.send('Your server is not registered and so, executed commands are not counted. Register using &register')
        
bot.run(token)
