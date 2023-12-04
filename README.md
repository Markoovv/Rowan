
## Rowan
Rowan (Рябина) это небольшой дискорд-бот которого я написал на discord.py.
Рябина может:
- Решать арифметику
- Кидать кубик
- Подбрасывать монетку
- Повторять ваши слова
- Создавать голосования
- Играть в "угадай число" и "реши пример" с вами
- Чистить сообщения
- Цитировать "Дзен Пайтон"
- Говорить на двух языках
- Считать количество исполненных команд на сервере

## Зависимости
Для корректной работы Рябины нужны следующие библиотеки:
- discord
- asyncio
- numexpr
- configparser
- sqlite3

## Руководство к установке
1. Скачайте main.py, defaultconfig.ini и папку asset
2. Переименуйте defaultconfig.ini => config.ini
3. Создайте базу данных .db с таблицами guilds и preferences
4. Создайте в guilds поля guild_id и prefix, в preferences поля guild, language и executed_comms
5. Замените "your token goes here" и "your version goes here" на токен своего приложения и версию вашего форка

Бот должен заработать при запуске. Если в консоль написалось "Logged in as [ваш бот]", то всё исправно.
