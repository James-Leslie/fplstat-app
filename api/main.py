from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

import psycopg2.extensions
import psycopg2.extras
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from api.db import close_pool, get_conn, init_pool  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    yield
    close_pool()


app = FastAPI(title="fplstat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

Conn = Annotated[psycopg2.extensions.connection, Depends(get_conn)]


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class Team(BaseModel):
    id: int
    name: str
    short_name: str
    strength_overall_home: int | None
    strength_overall_away: int | None
    strength_attack_home: int | None
    strength_attack_away: int | None
    strength_defence_home: int | None
    strength_defence_away: int | None


class Gameweek(BaseModel):
    id: int
    name: str
    deadline_time: datetime
    finished: bool
    is_current: bool
    average_entry_score: int | None
    highest_score: int | None


class Player(BaseModel):
    id: int
    first_name: str
    last_name: str
    web_name: str
    team_id: int
    element_type: int  # 1=GK 2=DEF 3=MID 4=FWD
    price: float  # now_cost / 10
    status: str
    news: str | None
    total_points: int
    form: float | None
    points_per_game: float | None
    selected_by_percent: float | None
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    bonus: int
    bps: int
    influence: float | None
    creativity: float | None
    threat: float | None
    ict_index: float | None
    transfers_in: int
    transfers_out: int


class Fixture(BaseModel):
    id: int
    gameweek_id: int | None
    team_h_id: int
    team_a_id: int
    team_h_score: int | None
    team_a_score: int | None
    finished: bool
    kickoff_time: datetime | None
    team_h_difficulty: int | None
    team_a_difficulty: int | None


class PlayerGameweekStats(BaseModel):
    player_id: int
    fixture_id: int
    gameweek_id: int
    opponent_team_id: int
    was_home: bool
    minutes: int
    total_points: int
    goals_scored: int
    assists: int
    clean_sheets: int
    bonus: int
    bps: int
    influence: float | None
    creativity: float | None
    threat: float | None
    ict_index: float | None
    expected_goals: float | None
    expected_assists: float | None
    expected_goal_involvements: float | None
    expected_goals_conceded: float | None
    price: float | None  # value / 10
    selected: int | None
    transfers_in: int
    transfers_out: int
    fdr: int | None
    xpts: float | None


class LeaderboardEntry(BaseModel):
    player_id: int
    web_name: str
    first_name: str
    last_name: str
    team_id: int
    element_type: int
    price: float
    points: int
    gameweeks_played: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/teams", response_model=list[Team])
def list_teams(conn: Conn):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM public.teams ORDER BY id")
        return [Team.model_validate(dict(row)) for row in cur.fetchall()]


@app.get("/gameweeks", response_model=list[Gameweek])
def list_gameweeks(conn: Conn):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM public.gameweeks ORDER BY id")
        return [Gameweek.model_validate(dict(row)) for row in cur.fetchall()]


@app.get("/fixtures", response_model=list[Fixture])
def list_fixtures(
    conn: Conn,
    gameweek_id: int | None = Query(default=None),
):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        if gameweek_id is not None:
            cur.execute(
                "SELECT * FROM public.fixtures WHERE gameweek_id = %s ORDER BY kickoff_time",
                (gameweek_id,),
            )
        else:
            cur.execute("SELECT * FROM public.fixtures ORDER BY kickoff_time")
        return [Fixture.model_validate(dict(row)) for row in cur.fetchall()]


@app.get("/players", response_model=list[Player])
def list_players(
    conn: Conn,
    team_id: int | None = Query(default=None),
    position: int | None = Query(default=None, ge=1, le=4, description="1=GK 2=DEF 3=MID 4=FWD"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    conditions = []
    params: list = []

    if team_id is not None:
        conditions.append("team_id = %s")
        params.append(team_id)
    if position is not None:
        conditions.append("element_type = %s")
        params.append(position)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [limit, offset]

    sql = f"""
        SELECT id, first_name, last_name, web_name, team_id, element_type,
               now_cost / 10.0 AS price, status, news, total_points,
               form, points_per_game, selected_by_percent, minutes,
               goals_scored, assists, clean_sheets, bonus, bps,
               influence, creativity, threat, ict_index,
               transfers_in, transfers_out
        FROM public.players
        {where}
        ORDER BY total_points DESC
        LIMIT %s OFFSET %s
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [Player.model_validate(dict(row)) for row in cur.fetchall()]


@app.get("/players/{player_id}", response_model=Player)
def get_player(player_id: int, conn: Conn):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, first_name, last_name, web_name, team_id, element_type,
                   now_cost / 10.0 AS price, status, news, total_points,
                   form, points_per_game, selected_by_percent, minutes,
                   goals_scored, assists, clean_sheets, bonus, bps,
                   influence, creativity, threat, ict_index,
                   transfers_in, transfers_out
            FROM public.players
            WHERE id = %s
            """,
            (player_id,),
        )
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return Player.model_validate(dict(row))


@app.get("/players/{player_id}/stats", response_model=list[PlayerGameweekStats])
def get_player_stats(player_id: int, conn: Conn):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT player_id, fixture_id, gameweek_id, opponent_team_id, was_home,
                   minutes, total_points, goals_scored, assists, clean_sheets,
                   bonus, bps, influence, creativity, threat, ict_index,
                   expected_goals, expected_assists, expected_goal_involvements,
                   expected_goals_conceded,
                   value / 10.0 AS price, selected,
                   transfers_in, transfers_out, fdr, xpts
            FROM public.player_gameweek_stats
            WHERE player_id = %s
            ORDER BY gameweek_id
            """,
            (player_id,),
        )
        rows = cur.fetchall()
    if not rows:
        # Verify player exists
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM public.players WHERE id = %s", (player_id,))
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Player not found")
    return [PlayerGameweekStats.model_validate(dict(row)) for row in rows]


@app.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(
    conn: Conn,
    last_n: int = Query(default=5, ge=1, le=38, description="Number of most recent finished gameweeks to aggregate"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            WITH recent_gws AS (
                SELECT id FROM public.gameweeks
                WHERE finished = true
                ORDER BY id DESC
                LIMIT %s
            )
            SELECT
                p.id           AS player_id,
                p.web_name,
                p.first_name,
                p.last_name,
                p.team_id,
                p.element_type,
                p.now_cost / 10.0             AS price,
                COALESCE(SUM(s.total_points), 0)::int AS points,
                COUNT(DISTINCT s.gameweek_id)::int    AS gameweeks_played
            FROM public.players p
            JOIN public.player_gameweek_stats s ON s.player_id = p.id
            WHERE s.gameweek_id IN (SELECT id FROM recent_gws)
            GROUP BY p.id, p.web_name, p.first_name, p.last_name,
                     p.team_id, p.element_type, p.now_cost
            ORDER BY points DESC
            LIMIT %s OFFSET %s
            """,
            (last_n, limit, offset),
        )
        return [LeaderboardEntry.model_validate(dict(row)) for row in cur.fetchall()]
