import httpx
import asyncio
import random
import time
import logging
from typing import List
from providers.base import SportsProvider
from schemas.output import (
    ListLeaguesOutSchema,
    LeagueMatchesOutSchema,
    GetTeamOutSchema,
    GetMatchOutSchema,
)
from settings import Settings
from utils.rate_limiter import TokenBucket
from utils.logger import logger


class OpenLigaProvider(SportsProvider):
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self.client = httpx.AsyncClient(timeout=cfg.TIMEOUT_SEC)
        self.bucket = TokenBucket(rate_per_min=cfg.RATE_LIMIT_PER_MIN)

    async def _request(self, method: str, url: str) -> httpx.Response:
        await self.bucket.acquire()

        attempts = 0
        last_ecx: Exception | None = None

        while True:
            attempts += 1
            start = time.perf_counter()

            try:
                res = await self.client.request(method, url, follow_redirects=True)
                latency_ms = int((time.perf_counter() - start) * 1000)

                logger.info(
                    "provider_call",
                    extra={
                        "extra_data": {
                            "provider": "OpenLiga",
                            "target": url,
                            "status_code": res.status_code,
                            "latency_ms": latency_ms,
                            "attempt": attempts,
                        }
                    },
                )

                if res.status_code == 429 or res.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        "Transient upstream error",
                        request=res.request,
                        response=res,
                    )

                return res

            # Retry logic
            except (
                httpx.TimeoutException,
                httpx.ConnectError,
                httpx.NetworkError,
                httpx.ReadError,
                httpx.HTTPStatusError,
            ) as exc:
                last_exc = exc

                if attempts > self.cfg.MAX_RETRIES:
                    logger.error(
                        "provider_call_failed",
                        extra={
                            "extra_data": {
                                "provider": "OpenLiga",
                                "target": url,
                                "attempts": attempts,
                                "error": str(exc),
                                "outcome": "give_up",
                            }
                        },
                    )
                    raise

                backoff_ms = self.cfg.BASE_BACKOFF_MS * (2 ** (attempts - 1))
                jitter = 1.0 + (self.cfg.JITTER_FACTOR * (random.random() * 2 - 1))
                sleep_s = (backoff_ms * jitter) / 1000.0

                logger.warning(
                    "provider_retry_scheduled",
                    extra={
                        "extra_data": {
                            "provider": "OpenLiga",
                            "target": url,
                            "attempt": attempts,
                            "sleep_s": round(sleep_s, 3),
                            "reason": type(exc).__name__,
                        }
                    },
                )
                await asyncio.sleep(sleep_s)

    async def list_leagues(self) -> List[ListLeaguesOutSchema]:
        url = f"{self.cfg.BASE_URL}/api/getavailableleagues/"
        res = await self._request("GET", url)
        data = res.json() or []

        out: list[ListLeaguesOutSchema] = []

        for item in data:
            out.append(ListLeaguesOutSchema(**item))
        return out

    async def get_league_matches(self, league_id: int) -> LeagueMatchesOutSchema:
        url = f"{self.cfg.BASE_URL}/api/getmatchdata/{league_id}"
        res = await self._request("GET", url)
        data = res.json() or {}
        return LeagueMatchesOutSchema(**data)

    async def get_team(self, team_id: int) -> GetTeamOutSchema:
        url = f"{self.cfg.BASE_URL}/api/getteam/{team_id}"
        res = await self._request("GET", url)
        data = res.json() or {}
        return GetTeamOutSchema(**data)

    async def get_match(
        self, team_id_1: int, team_id_2: int
    ) -> List[GetMatchOutSchema]:
        url = f"{self.cfg.BASE_URL}/getmatchdata/{team_id_1}/{team_id_2}"
        res = await self._request("GET", url)
        data = res.json() or []

        out: list[GetMatchOutSchema] = []

        for item in data:
            out.append(GetMatchOutSchema(**item))
        return out
