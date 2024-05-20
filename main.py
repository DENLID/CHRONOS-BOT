from typing import Optional
import disnake
from disnake.ext import commands
from pymongo import MongoClient
import requests, io
import config

bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all())#, test_guilds=[1227337748650917929])

cluster = MongoClient(config.mongo_api)
users = cluster.db.users



class Registration(disnake.ui.Modal):
    def __init__(self):
        self.channel = bot.get_channel(1220063208564326451)
        components = [
            disnake.ui.TextInput(
                label="USERNAME",
                placeholder="Ваш никнейм в майнкрафте",
                custom_id="username"
            ),
            disnake.ui.TextInput(
                label="TOWN",
                placeholder="Ваш город в майнкрафте (Рим, Пьемонт, Сардиния)",
                custom_id="town"
            )
        ]

        super().__init__(title="Registration", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(title="New member!")
        for key, value in inter.text_values.items():
            embed.add_field(
                name=key.capitalize(),
                value=value[:1024],
                inline=False
            )
        await self.channel.send(embed=embed, view=AcceptView())
        await inter.response.send_message(f"Заявка на гражданство отправлена!", ephemeral=True)


class AcceptView(disnake.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.value = Optional[bool]

    @disnake.ui.button(label='Принять', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.edit_message(embed=disnake.Embed(title="Запрос принят"), view=None)
        self.value = True
        self.stop()

    @disnake.ui.button(label='Отклонить', style=disnake.ButtonStyle.red)
    async def decline(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.edit_message(embed=disnake.Embed(title="Запрос отклонен"), view=None)
        self.value = False
        self.stop()





@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")
    await bot.change_presence(status=disnake.Status.online, activity=disnake.Activity(name="AVE ROME"))


@bot.event
async def on_member_join(member):
    if users.find_one({"_id": member.id}) == None:
        users.insert_one({"_id": member.id, "name": member.name, "balance": 0})

@bot.event
async def on_slash_command_error(ctx, error):
    print(error)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("<:1984:1230918153190768722> У вас недостаточно прав для выполнения этой команды!", ephemeral=True)
    elif isinstance(error, commands.UserInputError):
        await ctx.send(embed=disnake.Embed(
            description=f"Правильное использование команды `{ctx.prefix}{ctx.command.name} ({ctx.command.brief})\nExample: {ctx.prefix}{ctx.command.usage}`"
        ), ephemeral=True)


@bot.slash_command()
async def send_claims(inter):
    await inter.response.send_modal(modal=Registration())


@bot.slash_command(description="Посмотреть баланс пользователя")
async def balance(inter, member: disnake.Member):
    user = users.find_one({"_id": member.id})
    await inter.send(f"Баланс пользователя {member.name}: {user['balance']} BUGCOIN", ephemeral=True)


@bot.slash_command(description="Прибавляет BUGCOIN пользователю")
@commands.has_permissions(administrator=True)
async def add_coin(inter, member: disnake.Member, coins: int):
    if users.find_one({"_id": member.id}) != None:
        users.update_one({"_id": member.id}, {"$inc":{"balance": coins}})
        await inter.send(f"Пользовать {member.name} получил {coins} BUGCOIN", ephemeral=True)
    else:
        await inter.send(f"Пользовать {member.name} не найден в базе!", ephemeral=True)

@bot.slash_command(description="Отнимает BUGCOIN пользователю")
@commands.has_permissions(administrator=True)
async def remove_coin(inter, member: disnake.Member, coins: int):
    if users.find_one({"_id": member.id}) != None:
        users.update_one({"_id": member.id}, {"$inc":{"balance": -coins}})
        await inter.send(f"Пользовать {member.name} потерял {coins} BUGCOIN", ephemeral=True)
    else:
        await inter.send(f"Пользовать {member.name} не найден в базе!", ephemeral=True)


@bot.slash_command()
@commands.has_permissions(administrator=True)
async def addgggggggg(inter):
    guild = bot.get_guild(1227337748650917929)

    for member in guild.members:
        if users.find_one({"_id": member.id}) == None:
            users.insert_one({"_id": member.id, "name": member.name, "balance": 0})


bot.run(config.token)