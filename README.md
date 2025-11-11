# Simple reverse proxy for OpenLiga


## Install


```bash
pip3 install -r requirements.txt
```


## Run


```bash
uvicorn main:app --reload
```

## Payload schemas expected


**ListLeagues**


Nothing


**GetLeagueMatches**


```json
leagueId: integer
```


**GetTeam**


```json
teamId: integer
```


**GetMatch**


```json
teamId1: integer
teamId2: integer
```


## Decision mapper


The ``DecisionMapper`` is a simple operation router that decides which method of the provider to call based on the operationType received in the request.


1. It receives:


- op: the operation name (ListLeagues, GetTeam, GetMatch)

- payload: the data needed for that operation (leagueId, teamId, etc)


2. It validates the payload using the corresponding Pydantic schema


3. It calls the correct method on the provider (OpenLigaProvider) depending on the operation


## Adapter interface

`SportsProvider` defines the async adapter contract your app calls. Any provider must implement these methods and return the typed schemas:

```python
def list_leagues() -> List[ListLeaguesOutSchema]: ...


def get_league_matches(league_id: int) -> LeagueMatchesOutSchema: ...


def get_team(team_id: int) -> GetTeamOutSchema: ...


def get_match(team_id_1: int, team_id_2: int) -> List[GetMatchOutSchema]: ...
```


This keeps the rest of the code independent from any specific API.


### OpenLiga implementation


`OpenLigaProvider` implements `SportsProvider` against the OpenLiga API.


Key points:

- Uses httpx.AsyncClient with a timeout from Settings.


- Applies a token-bucket rate limiter (TokenBucket) before each request.


- Central _request(method, url) adds structured logging and robust retry logic with exponential backoff + jitter for timeouts, network errors, 5xx, and 429.


- Each public method builds the endpoint URL, calls _request("GET", url), parses res.json(), and maps results into the corresponding Pydantic output schemas.


### Endpoints used:


- list_leagues: GET {BASE_URL}/api/getavailableleagues/


- get_league_matches: GET {BASE_URL}/api/getmatchdata/{league_id}


- get_team: GET {BASE_URL}/api/getteam/{team_id}


- get_match: GET {BASE_URL}/getmatchdata/{team_id_1}/{team_id_2}


## Configuration


To configure the rate limiting and others, create a `.env` file or edit default values in `settings.py`.


Example `.env`:
```env
BASE_URL="https://www.openligadb.de"
RATE_LIMIT_PER_MIN=60
MAX_RETRIES=3
BASE_BACKOFF_MS=200
TIMEOUT_SEC=10
JITTER_FACTOR=0.3
```

NOTE: Per provider configuration is not implemented, so it would affect other providers if added in the future. So in future, per provider configuration can be done using namespaced env vars like `OPENLIGA_RATE_LIMIT_PER_MIN`, service yaml's, etc.


## What logs look like:

```plaintext
[request_response_logger] time=1762880383 level=INFO msg="Incoming request POST /proxy/execute" event='inbound_request' 

requestId='745bc02d-1902-4023-b77a-1f0ec2010460' method='POST' path='/proxy/execute' body_size=104
INFO:httpx:HTTP Request: GET https://www.openligadb.de/api/getmatchdata/8 "HTTP/1.1 301 Moved Permanently"
INFO:httpx:HTTP Request: GET https://api.openligadb.de/getmatchdata/8 "HTTP/1.1 200 OK"
[_request] time=1762880384 level=INFO msg="provider_call" provider='OpenLiga' target='https://www.openligadb.de/api/getmatchdata/8' status_code=200 latency_ms=1188 attempt=1
INFO:root:Executed operation: GetLeagueMatches with payload: {'leagueId': 8}
INFO:root:matchID=8 matchDateTime=datetime.datetime(2006, 8, 11, 20, 45) timeZoneID='W. Europe Standard Time' leagueId=6 leagueName='1. Fussball-Bundesliga 2006/2007' leagueSeason=2006 leagueShortcut='bl1' matchDateTimeUTC=datetime.datetime(2006, 8, 11, 18, 45, tzinfo=TzInfo(0))


[request_response_logger] time=1762880384 level=INFO msg="Completed request POST /proxy/execute" event='outbound_response' requestId='745bc02d-1902-4023-b77a-1f0ec2010460' status_code=200 latency_ms=1227
```