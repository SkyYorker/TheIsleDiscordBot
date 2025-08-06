import asyncio
import logging
import os

import aiohttp

from database.crud import PlayerDinoCRUD

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


class SteamAPI:
    BASE_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._player_info_cache = {}
        self._avatar_url_cache = {}
        logger.info("SteamAPI initialized with API key")

    async def get_player_info(self, steam_id: str) -> dict:
        if steam_id in self._player_info_cache:
            logger.debug(f"Player info for SteamID {steam_id} found in cache")
            return self._player_info_cache[steam_id]

        params = {
            "key": self.api_key,
            "steamids": steam_id,
            "country": "XX",
            "language": "XX"
        }
        logger.debug(f"Requesting player info for SteamID: {steam_id}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params, timeout=10) as resp:
                    if resp.status == 429:
                        logger.error(f"Steam API rate limit exceeded (HTTP 429) for SteamID {steam_id}")
                        return {"error": "rate_limited", "status": 429}
                    if resp.status != 200:
                        logger.error(f"Steam API returned status {resp.status} for SteamID {steam_id}")
                        return {"error": f"bad_status_{resp.status}", "status": resp.status}
                    data = await resp.json()
                    logger.debug(f"Received response for SteamID {steam_id}: {data}")

                    players = data.get("response", {}).get("players", [])
                    if players:
                        logger.info(f"Successfully retrieved info for SteamID: {steam_id}")
                        self._player_info_cache[steam_id] = players[0]
                        return players[0]
                    logger.warning(f"No player data found for SteamID: {steam_id}")
                    self._player_info_cache[steam_id] = {}
                    return {}
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Error fetching player info for SteamID {steam_id}: {str(e)}")
            return {"error": "network_error", "details": str(e)}

    async def get_avatar_url(self, steam_id: str, size: str = "full") -> str:
        cache_key = (steam_id, size)
        if cache_key in self._avatar_url_cache:
            logger.debug(f"Avatar URL for SteamID {steam_id}, size {size} found in cache")
            return self._avatar_url_cache[cache_key]

        logger.debug(f"Requesting avatar for SteamID: {steam_id}, size: {size}")
        player = await self.get_player_info(steam_id)

        if not player or "error" in player:
            logger.warning(f"No player found for SteamID: {steam_id}, cannot get avatar")
            self._avatar_url_cache[cache_key] = ""
            return ""

        if size == "small":
            avatar_url = player.get("avatar", "")
        elif size == "medium":
            avatar_url = player.get("avatarmedium", "")
        else:
            avatar_url = player.get("avatarfull", "")

        logger.debug(f"Avatar URL for SteamID {steam_id}: {avatar_url}")
        self._avatar_url_cache[cache_key] = avatar_url
        return avatar_url

    async def get_steam_data(self, discord_id: int) -> dict:
        player = await PlayerDinoCRUD.get_player_info(discord_id)
        if not player:
            return {}
        player = player["player"]
        steam_id = player["steam_id"]
        if not steam_id:
            return {}
        steam_info = await self.get_player_info(steam_id)
        if not steam_info or not steam_info.get("personaname") or steam_info.get("error"):
            return {}
        return {
            "username": steam_info.get("personaname", "Unknown"),
            "avatar": steam_info.get("avatarfull", ""),
            "steamid": steam_id,
            "tk": player["tk"]
        }


steam_api = SteamAPI(api_key=os.getenv("STEAM_API_KEY"))
