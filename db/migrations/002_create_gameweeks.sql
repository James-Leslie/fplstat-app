CREATE TABLE gameweeks (
    id                   int4        PRIMARY KEY,
    name                 text        NOT NULL,
    deadline_time        timestamptz NOT NULL,
    finished             bool        NOT NULL DEFAULT false,
    is_current           bool        NOT NULL DEFAULT false,
    average_entry_score  int4,       -- null for future gameweeks
    highest_score        int4        -- null for future gameweeks
);
