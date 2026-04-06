from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class Team(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int
    code: int
    name: str
    short_name: str
    draw: int = 0
    loss: int = 0
    win: int = 0
    played: int = 0
    points: int = 0
    position: Optional[int] = None
    strength: Optional[int] = None
    team_division: Optional[str] = None
    unavailable: bool = False
    strength_overall_home: Optional[int] = None
    strength_overall_away: Optional[int] = None
    strength_attack_home: Optional[int] = None
    strength_attack_away: Optional[int] = None
    strength_defence_home: Optional[int] = None
    strength_defence_away: Optional[int] = None
    pulse_id: Optional[int] = None


class Gameweek(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int
    name: str
    finished: bool = False
    is_current: bool = False
    is_previous: bool = False
    is_next: bool = False
    deadline_time: Optional[str] = None
    average_entry_score: Optional[int] = None
    data_checked: bool = False
    highest_scoring_entry: Optional[int] = None
    deadline_time_epoch: Optional[int] = None
    deadline_time_game_offset: int = 0
    highest_score: Optional[int] = None
    cup_leagues_created: bool = False
    h2h_ko_matches_created: bool = False
    can_enter: bool = False
    can_manage: bool = False
    released: bool = False
    ranked_count: Optional[int] = None
    most_selected: Optional[int] = None
    most_transferred_in: Optional[int] = None
    top_element: Optional[int] = None
    transfers_made: int = 0
    most_captained: Optional[int] = None
    most_vice_captained: Optional[int] = None
    overrides: Optional[Any] = None
    chip_plays: Optional[Any] = None
    top_element_info: Optional[Any] = None


class Player(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int
    code: int
    first_name: str
    second_name: str
    web_name: str
    element_type: int
    team: int
    now_cost: int
    status: str
    can_select: Optional[bool] = None
    removed: bool = False
    minutes: int = 0
    goals_scored: int = 0
    assists: int = 0
    clean_sheets: int = 0
    saves: int = 0
    bonus: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    own_goals: int = 0
    penalties_saved: int = 0
    penalties_missed: int = 0
    total_points: int = 0
    # String-numeric fields — kept as str, cast in SQL views
    influence: Optional[str] = None
    creativity: Optional[str] = None
    threat: Optional[str] = None
    ict_index: Optional[str] = None
    expected_goals: Optional[str] = None
    expected_assists: Optional[str] = None
    expected_goal_involvements: Optional[str] = None
    expected_goals_conceded: Optional[str] = None
    form: Optional[str] = None
    ep_next: Optional[str] = None
    ep_this: Optional[str] = None
    points_per_game: Optional[str] = None
    selected_by_percent: Optional[str] = None
    value_form: Optional[str] = None
    value_season: Optional[str] = None
    price_change_percent: Optional[str] = None


class Fixture(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int
    code: int
    event: Optional[int] = None
    team_h: int
    team_a: int
    team_h_score: Optional[int] = None
    team_a_score: Optional[int] = None
    kickoff_time: Optional[str] = None
    finished: bool = False
    team_h_difficulty: int
    team_a_difficulty: int
    finished_provisional: bool = False
    started: Optional[bool] = None
    minutes: int = 0
    provisional_start_time: bool = False


class PlayerGameweekStat(BaseModel):
    model_config = ConfigDict(extra='allow')

    element: int
    fixture: int
    round: int
    opponent_team: int
    was_home: bool
    total_points: int = 0
    minutes: int = 0
    goals_scored: int = 0
    assists: int = 0
    clean_sheets: int = 0
    goals_conceded: int = 0
    own_goals: int = 0
    penalties_saved: int = 0
    penalties_missed: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    saves: int = 0
    bonus: int = 0
    bps: int = 0
    starts: int = 0
    value: Optional[int] = None
    selected: Optional[int] = None
    # String-numeric fields — kept as str, cast in SQL views
    expected_goals: Optional[str] = None
    expected_assists: Optional[str] = None
    expected_goal_involvements: Optional[str] = None
    expected_goals_conceded: Optional[str] = None
    influence: Optional[str] = None
    creativity: Optional[str] = None
    threat: Optional[str] = None
    ict_index: Optional[str] = None
