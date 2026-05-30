
-- Создание основных таблиц

CREATE TABLE Coach (
    coach_id INTEGER PRIMARY KEY,
    full_name VARCHAR2(100) NOT NULL,
    qualification VARCHAR2(100)
);

CREATE TABLE Athlete (
    athlete_id INTEGER PRIMARY KEY,
    full_name VARCHAR2(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR2(10),
    rank VARCHAR2(50),
    club_id INTEGER
);

CREATE TABLE Training (
    training_id INTEGER PRIMARY KEY,
    athlete_id INTEGER NOT NULL,
    sport_id INTEGER,
    coach_id INTEGER,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (athlete_id) REFERENCES Athlete(athlete_id),
    FOREIGN KEY (coach_id) REFERENCES Coach(coach_id)
);


-- Создание таблиц логирования (Audit Trail)


CREATE TABLE Audit_Log (
    log_id INTEGER PRIMARY KEY,
    entity_name VARCHAR2(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    operation_type VARCHAR2(10) NOT NULL, -- INSERT, UPDATE, DELETE
    operation_date TIMESTAMP NOT NULL,
    old_data CLOB, -- JSON с предыдущими значениями
    new_data CLOB, -- JSON с новыми значениями
    user_name VARCHAR2(100),
    is_reverted NUMBER(1) DEFAULT 0 -- 0 = не отменена, 1 = отменена
);

CREATE SEQUENCE audit_log_seq START WITH 1;

CREATE TABLE Undo_History (
    undo_id INTEGER PRIMARY KEY,
    log_id INTEGER NOT NULL,
    undo_date TIMESTAMP NOT NULL,
    undo_status VARCHAR2(50), -- SUCCESS, FAILED
    FOREIGN KEY (log_id) REFERENCES Audit_Log(log_id)
);

CREATE SEQUENCE undo_history_seq START WITH 1;

-- Индексы для быстрого поиска по логам
CREATE INDEX idx_audit_entity ON Audit_Log(entity_name, entity_id);
CREATE INDEX idx_audit_date ON Audit_Log(operation_date);
CREATE INDEX idx_audit_type ON Audit_Log(operation_type);
