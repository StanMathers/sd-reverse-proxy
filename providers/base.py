from typing import List

from schemas.output import (
    ListLeaguesOutSchema,
    LeagueMatchesOutSchema,
    GetTeamOutSchema,
    GetMatchOutSchema,
)


class SportsProvider:
    async def list_leagues(self) -> List[ListLeaguesOutSchema]:
        raise NotImplementedError

    async def get_league_matches(self, league_id: int) -> LeagueMatchesOutSchema:
        raise NotImplementedError

    async def get_team(self, team_id: int) -> GetTeamOutSchema:
        raise NotImplementedError

    async def get_match(
        self, team_id_1: int, team_id_2: int
    ) -> List[GetMatchOutSchema]:
        raise NotImplementedError
