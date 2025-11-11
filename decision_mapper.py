from pydantic import ValidationError
from providers.base import SportsProvider
from schemas.request import (
    ListLeaguesPayloadSchema,
    GetLeagueMatchesPayloadSchema,
    GetTeamPayloadSchema,
    GetMatchPayloadSchema,
)
from utils.errors import get_structured_error


class DecisionMapper:
    def __init__(self, provider: SportsProvider):
        self.provider = provider

    async def execute(self, op: str, payload: dict):
        op = (op or "").strip()
        try:
            if op == "ListLeagues":
                data = ListLeaguesPayloadSchema(**payload)
                return await self.provider.list_leagues()

            elif op == "GetLeagueMatches":
                data = GetLeagueMatchesPayloadSchema(**payload)
                return await self.provider.get_league_matches(league_id=data.leagueId)

            elif op == "GetTeam":
                data = GetTeamPayloadSchema(**payload)
                return await self.provider.get_team(team_id=data.teamId)

            elif op == "GetMatch":
                data = GetMatchPayloadSchema(**payload)
                return await self.provider.get_match(
                    team_id_1=data.teamId1, team_id_2=data.teamId2
                )

            else:
                return {
                    "status": "error",
                    "error": {
                        "code": "UNKNOWN_OPERATION",
                        "operation": op or None,
                        "message": "Unknown operationType.",
                    },
                }
        except ValidationError as ve:
            return get_structured_error(ve, operation=op)
