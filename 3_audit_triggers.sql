
-- Триггеры для автоматического логирования


-- Функция для преобразования строки в JSON
CREATE OR REPLACE FUNCTION build_json(p_col_name VARCHAR2, p_value VARCHAR2)
RETURN VARCHAR2 IS
BEGIN
    IF p_value IS NULL THEN
        RETURN '"' || p_col_name || '": null';
    ELSE
        RETURN '"' || p_col_name || '": "' || REPLACE(p_value, '"', '\"') || '"';
    END IF;
END;
/

-- ТРИГГЕРЫ ДЛЯ ТАБЛИЦЫ ATHLETE 

CREATE OR REPLACE TRIGGER trg_athlete_cascade_delete_training
BEFORE DELETE ON Athlete
FOR EACH ROW
BEGIN
    DELETE FROM Training
    WHERE athlete_id = :OLD.athlete_id;
END trg_athlete_cascade_delete_training;


CREATE OR REPLACE TRIGGER trg_athlete_insert
AFTER INSERT ON Athlete
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, new_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'ATHLETE',
        :NEW.athlete_id,
        'INSERT',
        SYSTIMESTAMP,
        '{"athlete_id": ' || :NEW.athlete_id || ', "full_name": "' || :NEW.full_name || '", "birth_date": "' || :NEW.birth_date || '", "gender": "' || :NEW.gender || '", "rank": "' || :NEW.rank || '", "club_id": ' || :NEW.club_id || '}',
        USER,
        0
    );
END trg_athlete_insert;
/

CREATE OR REPLACE TRIGGER trg_athlete_update
AFTER UPDATE ON Athlete
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, old_data, new_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'ATHLETE',
        :NEW.athlete_id,
        'UPDATE',
        SYSTIMESTAMP,
        '{"athlete_id": ' || :OLD.athlete_id || ', "full_name": "' || :OLD.full_name || '", "birth_date": "' || :OLD.birth_date || '", "gender": "' || :OLD.gender || '", "rank": "' || :OLD.rank || '", "club_id": ' || :OLD.club_id || '}',
        '{"athlete_id": ' || :NEW.athlete_id || ', "full_name": "' || :NEW.full_name || '", "birth_date": "' || :NEW.birth_date || '", "gender": "' || :NEW.gender || '", "rank": "' || :NEW.rank || '", "club_id": ' || :NEW.club_id || '}',
        USER,
        0
    );
END trg_athlete_update;
/

CREATE OR REPLACE TRIGGER trg_athlete_delete
BEFORE DELETE ON Athlete
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, old_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'ATHLETE',
        :OLD.athlete_id,
        'DELETE',
        SYSTIMESTAMP,
        '{"athlete_id": ' || :OLD.athlete_id || ', "full_name": "' || :OLD.full_name || '", "birth_date": "' || :OLD.birth_date || '", "gender": "' || :OLD.gender || '", "rank": "' || :OLD.rank || '", "club_id": ' || :OLD.club_id || '}',
        USER,
        0
    );
END trg_athlete_delete;
/

-- ТРИГГЕРЫ ДЛЯ ТАБЛИЦЫ COACH

CREATE OR REPLACE TRIGGER trg_coach_cascade_delete_training
BEFORE DELETE ON Coach
FOR EACH ROW
BEGIN
    DELETE FROM Training
    WHERE coach_id = :OLD.coach_id;
END trg_coach_cascade_delete_training;


CREATE OR REPLACE TRIGGER trg_coach_insert
AFTER INSERT ON Coach
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, new_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'COACH',
        :NEW.coach_id,
        'INSERT',
        SYSTIMESTAMP,
        '{"coach_id": ' || :NEW.coach_id || ', "full_name": "' || :NEW.full_name || '", "qualification": "' || :NEW.qualification || '"}',
        USER,
        0
    );
END trg_coach_insert;
/

CREATE OR REPLACE TRIGGER trg_coach_update
AFTER UPDATE ON Coach
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, old_data, new_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'COACH',
        :NEW.coach_id,
        'UPDATE',
        SYSTIMESTAMP,
        '{"coach_id": ' || :OLD.coach_id || ', "full_name": "' || :OLD.full_name || '", "qualification": "' || :OLD.qualification || '"}',
        '{"coach_id": ' || :NEW.coach_id || ', "full_name": "' || :NEW.full_name || '", "qualification": "' || :NEW.qualification || '"}',
        USER,
        0
    );
END trg_coach_update;
/

CREATE OR REPLACE TRIGGER trg_coach_delete
BEFORE DELETE ON Coach
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, old_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'COACH',
        :OLD.coach_id,
        'DELETE',
        SYSTIMESTAMP,
        '{"coach_id": ' || :OLD.coach_id || ', "full_name": "' || :OLD.full_name || '", "qualification": "' || :OLD.qualification || '"}',
        USER,
        0
    );
END trg_coach_delete;
/

--  ТРИГГЕРЫ ДЛЯ ТАБЛИЦЫ TRAINING 

CREATE OR REPLACE TRIGGER trg_training_insert
AFTER INSERT ON Training
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, new_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'TRAINING',
        :NEW.training_id,
        'INSERT',
        SYSTIMESTAMP,
        '{"training_id": ' || :NEW.training_id || ', "athlete_id": ' || :NEW.athlete_id || ', "sport_id": ' || :NEW.sport_id || ', "coach_id": ' || :NEW.coach_id || ', "start_date": "' || :NEW.start_date || '", "end_date": "' || :NEW.end_date || '"}',
        USER,
        0
    );
END trg_training_insert;
/

CREATE OR REPLACE TRIGGER trg_training_update
AFTER UPDATE ON Training
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, old_data, new_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'TRAINING',
        :NEW.training_id,
        'UPDATE',
        SYSTIMESTAMP,
        '{"training_id": ' || :OLD.training_id || ', "athlete_id": ' || :OLD.athlete_id || ', "sport_id": ' || :OLD.sport_id || ', "coach_id": ' || :OLD.coach_id || ', "start_date": "' || :OLD.start_date || '", "end_date": "' || :OLD.end_date || '"}',
        '{"training_id": ' || :NEW.training_id || ', "athlete_id": ' || :NEW.athlete_id || ', "sport_id": ' || :NEW.sport_id || ', "coach_id": ' || :NEW.coach_id || ', "start_date": "' || :NEW.start_date || '", "end_date": "' || :NEW.end_date || '"}',
        USER,
        0
    );
END trg_training_update;
/

CREATE OR REPLACE TRIGGER trg_training_delete
BEFORE DELETE ON Training
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (log_id, entity_name, entity_id, operation_type, operation_date, old_data, user_name, is_reverted)
    VALUES (
        audit_log_seq.NEXTVAL,
        'TRAINING',
        :OLD.training_id,
        'DELETE',
        SYSTIMESTAMP,
        '{"training_id": ' || :OLD.training_id || ', "athlete_id": ' || :OLD.athlete_id || ', "sport_id": ' || :OLD.sport_id || ', "coach_id": ' || :OLD.coach_id || ', "start_date": "' || :OLD.start_date || '", "end_date": "' || :OLD.end_date || '"}',
        USER,
        0
    );
END trg_training_delete;
/
