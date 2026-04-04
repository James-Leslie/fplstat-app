CREATE TABLE teams (
    id                    int4  PRIMARY KEY,
    name                  text  NOT NULL,
    short_name            text  NOT NULL,
    strength_overall_home int4,
    strength_overall_away int4,
    strength_attack_home  int4,
    strength_attack_away  int4,
    strength_defence_home int4,
    strength_defence_away int4
);
