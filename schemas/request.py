from pydantic import BaseModel, Field
from typing import Literal, Optional

OPERATION_TYPE = Literal["ListLeagues", "GetLeagueMatches", "GetTeam", "GetMatch"]


class ListLeaguesPayloadSchema(BaseModel):
    # OpenLiga supports no required payload for listing leagues
    pass


class GetLeagueMatchesPayloadSchema(BaseModel):
    # Payload to get matches for a specific league
    leagueId: int


class GetTeamPayloadSchema(BaseModel):
    # Payload to get team information
    teamId: int


class GetMatchPayloadSchema(BaseModel):
    # Payload to get match information between teams
    teamId1: int
    teamId2: int


class ExecuteRequestSchema(BaseModel):
    operationType: OPERATION_TYPE
    payload: dict = Field(default_factory=dict)
    requestId: Optional[str] = None
