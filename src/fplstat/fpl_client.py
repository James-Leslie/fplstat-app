import asyncio

import httpx

BASE_URL = "https://fantasy.premierleague.com/api"
_CONCURRENCY = 10  # parallel requests for element-summary fetches


def fetch_bootstrap() -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{BASE_URL}/bootstrap-static/")
        resp.raise_for_status()
        return resp.json()


def fetch_fixtures() -> list[dict]:
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{BASE_URL}/fixtures/")
        resp.raise_for_status()
        return resp.json()


async def _fetch_one_history(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    player_id: int,
) -> tuple[int, list[dict]]:
    async with sem:
        resp = await client.get(f"{BASE_URL}/element-summary/{player_id}/")
        resp.raise_for_status()
        return player_id, resp.json().get("history", [])


async def _fetch_all_histories(player_ids: list[int]) -> dict[int, list[dict]]:
    sem = asyncio.Semaphore(_CONCURRENCY)
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [_fetch_one_history(client, sem, pid) for pid in player_ids]
        results = await asyncio.gather(*tasks)
    return dict(results)


def fetch_player_histories(player_ids: list[int]) -> dict[int, list[dict]]:
    return asyncio.run(_fetch_all_histories(player_ids))
