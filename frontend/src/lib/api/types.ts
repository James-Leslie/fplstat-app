export interface Team {
	id: number;
	name: string;
	short_name: string;
	strength_overall_home: number | null;
	strength_overall_away: number | null;
	strength_attack_home: number | null;
	strength_attack_away: number | null;
	strength_defence_home: number | null;
	strength_defence_away: number | null;
}

export interface Gameweek {
	id: number;
	name: string;
	deadline_time: string;
	finished: boolean;
	is_current: boolean;
	average_entry_score: number | null;
	highest_score: number | null;
}

export type PlayerStatus = 'a' | 'd' | 'i' | 's' | 'u';
export type Position = 1 | 2 | 3 | 4;

export interface Player {
	id: number;
	first_name: string;
	last_name: string;
	web_name: string;
	team_id: number;
	element_type: Position;
	price: number;
	status: PlayerStatus;
	news: string | null;
	total_points: number;
	form: number | null;
	points_per_game: number | null;
	selected_by_percent: number | null;
	minutes: number;
	goals_scored: number;
	assists: number;
	clean_sheets: number;
	bonus: number;
	bps: number;
	influence: number | null;
	creativity: number | null;
	threat: number | null;
	ict_index: number | null;
	transfers_in: number;
	transfers_out: number;
}

export interface Fixture {
	id: number;
	gameweek_id: number | null;
	team_h_id: number;
	team_a_id: number;
	team_h_score: number | null;
	team_a_score: number | null;
	finished: boolean;
	kickoff_time: string | null;
	team_h_difficulty: number | null;
	team_a_difficulty: number | null;
}

export interface PlayerGameweekStats {
	player_id: number;
	fixture_id: number;
	gameweek_id: number;
	opponent_team_id: number;
	was_home: boolean;
	minutes: number;
	total_points: number;
	goals_scored: number;
	assists: number;
	clean_sheets: number;
	bonus: number;
	bps: number;
	influence: number | null;
	creativity: number | null;
	threat: number | null;
	ict_index: number | null;
	expected_goals: number | null;
	expected_assists: number | null;
	expected_goal_involvements: number | null;
	expected_goals_conceded: number | null;
	price: number | null;
	selected: number | null;
	transfers_in: number;
	transfers_out: number;
	fdr: number | null;
	xpts: number | null;
}

export interface LeaderboardEntry {
	player_id: number;
	web_name: string;
	first_name: string;
	last_name: string;
	team_id: number;
	element_type: Position;
	price: number;
	points: number;
	gameweeks_played: number;
}
