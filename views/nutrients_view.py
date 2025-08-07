import discord
from discord.ui import View, Button

from utils.scripts import give_nutrients, give_food
from utils.steam_api import steam_api


class OtherServicesView(View):
    def __init__(self, shop_view):
        super().__init__(timeout=None)
        self.shop_view = shop_view

        self.add_item(Button(
            label="Пополнение желудка и жажды",
            style=discord.ButtonStyle.blurple,
            custom_id="refill_hunger_thirst",
            row=0
        ))

        self.add_item(Button(
            label="Пополнение нутриентов",
            style=discord.ButtonStyle.blurple,
            custom_id="refill_nutrients",
            row=0
        ))

        self.add_item(Button(
            label="Главное меню",
            style=discord.ButtonStyle.grey,
            custom_id="back_to_main_menu",
            row=1
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id = interaction.data.get("custom_id")

        if custom_id == "refill_hunger_thirst":
            await interaction.response.defer()
            result = await give_food(interaction.user.id)
            if result is True:
                embed = discord.Embed(
                    title="Успех!",
                    description="Еда/Вода Вашего динозавра успешно восполнены по максимуму",
                    color=discord.Color.dark_red()
                )
            else:
                embed = discord.Embed(
                    title="Ошибка",
                    description=result[1] if isinstance(result, tuple) else "Не удалось выдать еду/воду динозавру.",
                    color=discord.Color.orange()
                )
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=None)

        elif custom_id == "refill_nutrients":
            await interaction.response.defer()
            result = await give_nutrients(interaction.user.id)
            if result is True:
                embed = discord.Embed(
                    title="Успех!",
                    description="Нутриииенты Вашего динозавра успешно восполнены по максимуму",
                    color=discord.Color.dark_red()
                )
            else:
                embed = discord.Embed(
                    title="Ошибка",
                    description=result[1] if isinstance(result, tuple) else "Не удалось выдать нутриенты динозавру.",
                    color=discord.Color.orange()
                )
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=None)

        elif custom_id == "back_to_main_menu":
            from views.main_menu import MainMenuView
            steam_data = await steam_api.get_steam_data(interaction.user.id)
            view = MainMenuView(steam_data, interaction.user.id)
            await view.update_player_data(interaction.user.id)
            await interaction.response.edit_message(embed=view.embed, view=view, content=None)

        return False
