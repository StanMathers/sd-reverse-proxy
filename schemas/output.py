from pydantic import BaseModel
from datetime import datetime


class SportOutSchema(BaseModel):
    sportId: int
    sportName: str


class ListLeaguesOutSchema(BaseModel):
    leagueId: int
    leagueName: str
    leagueShortcut: str
    leagueSeason: str
    sport: SportOutSchema


class LeagueMatchesOutSchema(BaseModel):
    # NOTE: We don't normalize whole match structure bacause it's too big for showcase
    matchID: int
    matchDateTime: datetime
    timeZoneID: str
    leagueId: int
    leagueName: str
    leagueSeason: int
    leagueShortcut: str
    matchDateTimeUTC: datetime


class GetTeamOutSchema(BaseModel):
    # NOTE: As of doing this task, the endpoint is not returning any data, so this is an assumption
    leagueId: int
    teamId: int


class GetMatchOutSchema(BaseModel):
    matchID: int
    matchDateTime: datetime
    timeZoneID: str
    leagueId: int
    leagueName: str
    leagueSeason: int
    leagueShortcut: str
    matchDateTimeUTC: datetime
