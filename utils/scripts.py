import os

from database.crud import PlayerDinoCRUD
from .rcon_isle import fetch_player_by_id, PlayerData

HOST = os.getenv("RCON_HOST")
PORT = int(os.getenv("RCON_PORT"))
PASSWORD = os.getenv("RCON_PASSWORD")


async def save_dino(discord_id: int):
    player = await PlayerDinoCRUD.get_player_info(discord_id)
    # TODO: Сделать ограничение на кол-во сохранений
    if not player:
        return None, "Нет привязки к Steam"

    steam_id = player.get("player", {}).get("steam_id", "")
    if not steam_id:
        return None, "Нет привязки к Steam"

    isle_player = await fetch_player_by_id(HOST, PORT, PASSWORD, steam_id)
    if not isle_player:
        return None, "Игрок не на сервере"

    result = await PlayerDinoCRUD.add_dino(
        steam_id,
        isle_player.dino_class,
        int(isle_player.growth * 100),
        int(isle_player.hunger * 100),
        int(isle_player.thirst * 100),
        int(isle_player.health * 100)
    )
    if not result:
        return None, "Техническая ошибка. Обратитесь к администратору"

    return result


async def get_all_dinos(discord_id: int) -> list | tuple[None, str]:
    player = await PlayerDinoCRUD.get_player_info(discord_id)
    # TODO: Сделать ограничение на кол-во сохранений
    if not player:
        return None, "Нет привязки к Steam"

    steam_id = player.get("player", {}).get("steam_id", "")
    if not steam_id:
        return None, "Нет привязки к Steam"

    return player.get("dinos", [])


async def del_dino(discord_id: int, dino_id: int):
    player = await PlayerDinoCRUD.get_player_info(discord_id)
    # TODO: Сделать ограничение на кол-во сохранений
    if not player:
        return None, "Нет привязки к Steam"

    steam_id = player.get("player", {}).get("steam_id", "")
    if not steam_id:
        return None, "Нет привязки к Steam"

    result = await PlayerDinoCRUD.delete_dino(steam_id, dino_id)
    if not result:
        return None, "Ошибка во время удаления динозавра"

    return True


async def get_current_dino(discord_id: int) -> PlayerData | tuple[None, str]:
    player = await PlayerDinoCRUD.get_player_info(discord_id)
    # TODO: Сделать ограничение на кол-во сохранений
    if not player:
        return None, "Нет привязки к Steam"

    steam_id = player.get("player", {}).get("steam_id", "")
    if not steam_id:
        return None, "Нет привязки к Steam"

    isle_player = await fetch_player_by_id(HOST, PORT, PASSWORD, steam_id)
    if not isle_player:
        return None, "Игрок не на сервере"

    return isle_player
