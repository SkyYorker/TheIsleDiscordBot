from typing import List

import discord
from discord import Embed
from discord.ui import View, Select, Button


class DinosaurSelectView(View):
    def __init__(self, original_embed: Embed, original_view: View, dinosaurs: List[str]):
        super().__init__(timeout=180)
        self.original_view = original_view
        self.original_embed = original_embed
        self.selected_dino = None
        self.dinosaurs = dinosaurs

        self.embed = self.create_dinosaur_embed()

        self.select_menu = Select(
            placeholder="Выберите динозавра",
            options=[discord.SelectOption(label=dino) for dino in dinosaurs],
            custom_id="select_dino"
        )
        self.add_item(self.select_menu)

        self.activate_button = Button(
            label="Активировать",
            style=discord.ButtonStyle.green,
            custom_id="activate_dino",
            disabled=True,
            row=1
        )
        self.add_item(self.activate_button)

        self.add_item(Button(
            label="Вернуться",
            style=discord.ButtonStyle.red,
            custom_id="go_back",
            row=2
        ))

        self.add_item(Button(
            label="Закрыть",
            style=discord.ButtonStyle.grey,
            custom_id="close",
            row=2
        ))

    def create_dinosaur_embed(self) -> Embed:
        """Создает embed для отображения коллекции динозавров"""
        embed = discord.Embed(
            title="🦖 Моя коллекция динозавров 🦕",
            description="*Выберите динозавра для активации из списка ниже*",
            color=discord.Color.dark_green()
        )

        embed.add_field(
            name="📊 Статистика коллекции",
            value="```\n"
                  f"• Всего динозавров: {len(self.dinosaurs)}\n"
                  f"• Выбран: {self.selected_dino or 'нет'}\n"
                  "```",
            inline=True
        )

        embed.set_footer(
            text="ℹ️ Выберите динозавра из меню и нажмите 'Активировать'",
            icon_url="https://emojicdn.elk.sh/ℹ️"
        )

        embed.set_thumbnail(url="https://emojicdn.elk.sh/🦖")

        return embed

    async def update_view(self, interaction: discord.Interaction):
        """Обновляет состояние кнопок и embed"""
        self.embed = self.create_dinosaur_embed()
        self.activate_button.disabled = self.selected_dino is None
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id = interaction.data["custom_id"]

        if custom_id == "go_back":
            await interaction.response.edit_message(embed=self.original_embed, view=self.original_view)

        elif custom_id == "close":
            await interaction.response.defer()
            await interaction.delete_original_response()

        elif custom_id == "select_dino":
            self.selected_dino = interaction.data["values"][0]
            await self.update_view(interaction)

        elif custom_id == "activate_dino":
            if self.selected_dino:
                # TODO: Активировать динозавра
                await interaction.response.send_message(
                    f"Динозавр {self.selected_dino} успешно активирован!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Сначала выберите динозавра!",
                    ephemeral=True
                )

        return False
