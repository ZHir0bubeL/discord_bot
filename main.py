import asyncio
import discord
from discord.ext import commands
import random
import logging
import sqlite3
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
con = sqlite3.connect("users.db")       # подключение к БД
cursor = con.cursor()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
dashes_1 = [1, 2, 3, 4, 5, 6]
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']
bot = commands.Bot(command_prefix='!', intents=intents)
TOKEN = "TOKEN"


def founding():     # нахождение ников, существующих в БД на данный момент
    found = cursor.execute("select nickname from data").fetchall()
    found = [found[i][0] for i in range(len(found))]
    return found


class BotClient(discord.Client):
    async def on_ready(self):
        logger.info(f'{self.user} готов к работе')


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll', description='бросок шестигранного кубика')
    async def roll(self, ctx):
        res = random.choice(dashes_1)   # выбирет рандомное значение от 1 до 6
        await ctx.send(str(res) + ' || ' + dashes[res - 1])     # выводит

    @commands.command(name='new_character', description='создaние нового персонажа')
    async def new_character(self, ctx):
        user = ctx.author
        if user.name not in founding():  # Если не существует
            cursor.execute(f"INSERT INTO data (nickname) VALUES ('{user.name}')")  # создает в БД новый столбец
            await ctx.send(f'Персонаж {user.name} успешно создан.')     # сообщает об успехе
            con.commit()    # сохранение изменений в БД
        else:  # если существует
            await ctx.send('У вас уже есть персонаж, удалите его перед созданием нового '   # сообщает об ошибке
                           'с помощью команды !delete_character.')

    @commands.command(name='delete_character', description='удаление персонажа')
    async def delete_character(self, ctx):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"DELETE from data WHERE nickname = '{user.name}'")  # удаляет пользователя из БД
            await ctx.send(f'Персонаж {user.name} успешно удалён.')     # сообщает об успехе
            con.commit()  # сохранение изменений в БД
        else:  # если существует
            await ctx.send('У вас ещё нет персонажа.')   # сообщает об ошибке

    @commands.command(name='character', description='описание персонажа')
    async def character(self, ctx):
        user = ctx.author                                   # нахождение хар-к
        lvl = cursor.execute(f"select level from data WHERE nickname = '{user.name}'").fetchone()[0]
        race = cursor.execute(f"select race from races WHERE id=("
                              f"SELECT race from data WHERE nickname = '{user.name}')").fetchone()[0]
        class_c = cursor.execute(f"select class from classes WHERE id=("
                                 f"SELECT class from data WHERE nickname = '{user.name}')").fetchone()[0]
        gold = cursor.execute(f"select gold from data WHERE nickname = '{user.name}'").fetchone()[0]
        head = cursor.execute(f"select head from data WHERE nickname = '{user.name}'").fetchone()[0]
        armor = cursor.execute(f"select armor from data WHERE nickname = '{user.name}'").fetchone()[0]
        boots = cursor.execute(f"select boots from data WHERE nickname = '{user.name}'").fetchone()[0]
        hands = cursor.execute(f"select hands from data WHERE nickname = '{user.name}'").fetchone()[0]
        if class_c != 'без класса':
            if race != 'человек':
                info = f'{race}-{class_c} {lvl} уровня'
            else:
                info = f'{class_c} {lvl} уровня'
        else:
            info = f'{race} {lvl} уровня'
        info = info[0].upper() + info[1:]
        if user.name in founding():  # Если существует
            await ctx.send(f'**٠•●{info}●•٠** \n'
                           f'Персонаж: {user.name} \n'         # вывод характеристик
                           f'Уровень: {lvl} \n'
                           f'Класс: {class_c} \n'
                           f'Раса: {race} \n'
                           f'Голды: {gold} \n'
                           f'Головняк: {head} \n'
                           f'Броник: {armor} \n'
                           f'Обувка: {boots} \n'
                           f'Руки: {hands} \n')
        else:
            await ctx.send('У вас ещё нет персонажа. Создайте его с помощью команды !new_character.')    # если нет

    @commands.command(name='level_up', description='изменение уровня')
    async def level_up(self, ctx, change=1):
        user = ctx.author
        if user.name in founding():  # Если существует
            answer = cursor.execute(f"select level from data WHERE nickname = '{user.name}'").fetchone()[0] + change
            cursor.execute(f"UPDATE data SET level = {answer} WHERE nickname = '{user.name}'")   # Изменение уровня
            await ctx.send(f'Уровень персонажа {user.name} — {answer}.')    # сообщение об успехе
            con.commit()  # сохранение изменений в БД
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')     # сообщение об ошибке

    @commands.command(name='set_level', description='задание уровня')
    async def set_level(self, ctx, level_num):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"UPDATE data SET level = {level_num} WHERE nickname = '{user.name}'")  # Изменение уровня
            await ctx.send(f'Уровень персонажа {user.name} — {level_num}.')  # сообщение об успехе
            con.commit()  # сохранение изменений в БД
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='gold', description='изменение уровня голдов')
    async def gold(self, ctx, change=0):
        user = ctx.author
        if user.name in founding():  # Если существует
            answer = cursor.execute(f"select gold from data WHERE nickname = '{user.name}'").fetchone()[0] + change
            cursor.execute(f"UPDATE data SET gold = {answer} WHERE nickname = '{user.name}'")  # Изменение богатств
            await ctx.send(f'Голды персонажа {user.name} — {answer}.')  # сообщение об успехе
            con.commit()  # сохранение изменений в БД
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='set_race', description='изменение расы')
    async def set_race(self, ctx, new_race):
        new_race = new_race.lower()
        user = ctx.author
        if user.name in founding():  # Если существует
            races = cursor.execute("SELECT race FROM races").fetchall()
            races = [races[i][0] for i in range(len(races))]
            if new_race in races:   # проверка на корректный ввод
                cursor.execute(f"UPDATE data SET race = ("
                               f"SELECT id FROM races WHERE race = '{new_race}')"
                               f" WHERE nickname = '{user.name}'")  # Изменение расы
                await ctx.send(f'Теперь раса персонажа {user.name} — {new_race}.')  # сообщение об успехе
                con.commit()  # сохранение изменений в БД
            else:
                await ctx.send('Такой расы не существует.')     # сообщение об ошибке
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='set_class', description='изменение класса')
    async def set_class(self, ctx, new_class):
        new_class = new_class.lower()
        user = ctx.author
        if user.name in founding():  # Если существует
            classes = cursor.execute("SELECT class FROM classes").fetchall()
            classes = [classes[i][0] for i in range(len(classes))]
            if new_class in classes:  # проверка на корректный ввод
                cursor.execute(f"UPDATE data SET class = ("
                               f"SELECT id FROM classes WHERE class = '{new_class}')"
                               f" WHERE nickname = '{user.name}'")  # Изменение класса
                await ctx.send(f'Теперь класс персонажа {user.name} — {new_class}.')  # сообщение об успехе
                con.commit()  # сохранение изменений в БД
            else:
                await ctx.send('Такого класса не существует.')  # сообщение об ошибке
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='reset_class', description='сброс класса')
    async def reset_class(self, ctx):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"UPDATE data SET class = 1 WHERE nickname = '{user.name}'")  # Изменение класса
            await ctx.send(f'Теперь класс персонажа {user.name} — без класса.')  # сообщение об успехе
            con.commit()  # сохранение изменений в БД
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='reset_race', description='сброс расы')
    async def reset_race(self, ctx):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"UPDATE data SET race = 4 WHERE nickname = '{user.name}'")  # Изменение расы
            await ctx.send(f'Теперь класс персонажа {user.name} — человек.')  # сообщение об успехе
            con.commit()  # сохранение изменений в БД
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='head', description='изменение головняка')
    async def head(self, ctx, head='-'):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"UPDATE data SET head = '{head}' WHERE nickname = '{user.name}'")  # Изменение головняка
            con.commit()  # сохранение изменений в БД
            if head != '-':
                await ctx.send(f'Персонаж {user.name} надел головняк — это {head}.')  # сообщение об изменении
            else:
                await ctx.send(f'Теперь персонаж {user.name} сидит без головняка.')     # сообщение о снятии
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='armor', description='изменение броника')
    async def armor(self, ctx, armor='-'):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"UPDATE data SET armor = '{armor}' WHERE nickname = '{user.name}'")  # Изменение броника
            con.commit()  # сохранение изменений в БД
            if armor != '-':
                await ctx.send(f'Персонаж {user.name} надел броник — это {armor}.')  # сообщение об изменении
            else:
                await ctx.send(f'Теперь персонаж {user.name} сидит без броника.')  # сообщение о снятии
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='boots', description='изменение обувки')
    async def boots(self, ctx, boots='-'):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"UPDATE data SET boots = '{boots}' WHERE nickname = '{user.name}'")  # Изменение обувки
            con.commit()  # сохранение изменений в БД
            if boots != '-':
                await ctx.send(f'Персонаж {user.name} надел обувку — это {boots}.')  # сообщение об изменении
            else:
                await ctx.send(f'Теперь персонаж {user.name} ходит босиком.')  # сообщение о снятии
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке

    @commands.command(name='hands', description='изменение содержимого рук')
    async def hands(self, ctx, hands='-'):
        user = ctx.author
        if user.name in founding():  # Если существует
            cursor.execute(f"UPDATE data SET boots = '{hands}' WHERE nickname = '{user.name}'")  # Изменение содержимого
            con.commit()  # сохранение изменений в БД
            if hands != '-':
                await ctx.send(f'Персонаж {user.name} взял в руки {hands}.')  # сообщение об изменении
            else:
                await ctx.send(f'Теперь персонаж {user.name} ходит с пустыми руками.')  # сообщение о снятии
        else:
            await ctx.send('Вы не можете выполнять эту команду, '
                           'так как у вас еще нет игрового персонажа.')  # сообщение об ошибке


async def main():
    await bot.add_cog(Commands(bot))
    await bot.start(TOKEN)
asyncio.run(main())
