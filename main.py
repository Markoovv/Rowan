import discord
from random import choice, randint

client = discord.Client(intents=discord.Intents.all(), options=8)

@client.event
async def on_ready():
    print('Успешный логин {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content == ('&help'):
        await message.channel.send("Вот список доступных комманд:\n&help - Показывает эту подсказку\n&eval - Решает введённый пример (ВЫКЛЮЧЕНО)\n&blable - Повторяет фразу, введённую после команды\n&ask даёт ответ да/нет\n&dice Кидает кубик с указанным количеством граней")
    if message.content.startswith('&eval '):
        print('Попытка вызвать команду eval')
        return
        try:
            await message.channel.send(eval(message.content[5::]))
        except:
            await message.channel.send('Не удалось решить задачу')
    if message.content.startswith('&blable '):
        await message.channel.send(message.content[7::])
    if message.content.startswith('&dice '):
        try:
            await message.channel.send(str(randint(1, int(message.content[5::]))))
        except:
            await message.channel.send('Не удалось кинуть кубик!')
    if message.content.startswith('&ask '):
        if choice([True, False]) == True:
            await message.channel.send('Да')
        else:
            await message.channel.send('Нет')

client.run('Removed for obvious reasons :)')
