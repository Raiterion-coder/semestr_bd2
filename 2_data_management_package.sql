
-- Пакет PL/SQL для работы с данными
-- (Вставка, Изменение, Удаление)


CREATE PACKAGE data_management AS
    -- Процедуры для таблицы Athlete
    PROCEDURE insert_athlete (
        p_athlete_id INTEGER,
        p_full_name VARCHAR2,
        p_birth_date DATE,
        p_gender VARCHAR2,
        p_rank VARCHAR2,
        p_club_id INTEGER
    );
    
    PROCEDURE update_athlete (
        p_athlete_id INTEGER,
        p_full_name VARCHAR2 DEFAULT NULL,
        p_birth_date DATE DEFAULT NULL,
        p_gender VARCHAR2 DEFAULT NULL,
        p_rank VARCHAR2 DEFAULT NULL,
        p_club_id INTEGER DEFAULT NULL
    );
    
    PROCEDURE delete_athlete (p_athlete_id INTEGER);
    
    -- Процедуры для таблицы Coach
    PROCEDURE insert_coach (
        p_coach_id INTEGER,
        p_full_name VARCHAR2,
        p_qualification VARCHAR2
    );
    
    PROCEDURE update_coach (
        p_coach_id INTEGER,
        p_full_name VARCHAR2 DEFAULT NULL,
        p_qualification VARCHAR2 DEFAULT NULL
    );
    
    PROCEDURE delete_coach (p_coach_id INTEGER);
    
    -- Процедуры для таблицы Training
    PROCEDURE insert_training (
        p_training_id INTEGER,
        p_athlete_id INTEGER,
        p_sport_id INTEGER,
        p_coach_id INTEGER,
        p_start_date DATE,
        p_end_date DATE
    );
    
    PROCEDURE update_training (
        p_training_id INTEGER,
        p_athlete_id INTEGER DEFAULT NULL,
        p_sport_id INTEGER DEFAULT NULL,
        p_coach_id INTEGER DEFAULT NULL,
        p_start_date DATE DEFAULT NULL,
        p_end_date DATE DEFAULT NULL
    );
    
    PROCEDURE delete_training (p_training_id INTEGER);
    
END data_management;
/

CREATE PACKAGE BODY data_management AS
    
    -- ПРОЦЕДУРЫ ДЛЯ ТАБЛИЦЫ ATHLETE

    PROCEDURE insert_athlete (
        p_athlete_id INTEGER,
        p_full_name VARCHAR2,
        p_birth_date DATE,
        p_gender VARCHAR2,
        p_rank VARCHAR2,
        p_club_id INTEGER
    ) IS
    BEGIN
        INSERT INTO Athlete (athlete_id, full_name, birth_date, gender, rank, club_id)
        VALUES (p_athlete_id, p_full_name, p_birth_date, p_gender, p_rank, p_club_id);
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Спортсмен ' || p_full_name || ' успешно добавлен');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при добавлении спортсмена: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END insert_athlete;
    
    PROCEDURE update_athlete (
        p_athlete_id INTEGER,
        p_full_name VARCHAR2 DEFAULT NULL,
        p_birth_date DATE DEFAULT NULL,
        p_gender VARCHAR2 DEFAULT NULL,
        p_rank VARCHAR2 DEFAULT NULL,
        p_club_id INTEGER DEFAULT NULL
    ) IS
    BEGIN
        UPDATE Athlete
        SET full_name = NVL(p_full_name, full_name),
            birth_date = NVL(p_birth_date, birth_date),
            gender = NVL(p_gender, gender),
            rank = NVL(p_rank, rank),
            club_id = NVL(p_club_id, club_id)
        WHERE athlete_id = p_athlete_id;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Спортсмен ID=' || p_athlete_id || ' успешно обновлен');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при обновлении спортсмена: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END update_athlete;
    
    PROCEDURE delete_athlete (p_athlete_id INTEGER) IS
    BEGIN
        DELETE FROM Training WHERE athlete_id = p_athlete_id;
        DELETE FROM Athlete WHERE athlete_id = p_athlete_id;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Спортсмен ID=' || p_athlete_id || ' успешно удален');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при удалении спортсмена: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END delete_athlete;
    
    -- ПРОЦЕДУРЫ ДЛЯ ТАБЛИЦЫ COACH 
    
    PROCEDURE insert_coach (
        p_coach_id INTEGER,
        p_full_name VARCHAR2,
        p_qualification VARCHAR2
    ) IS
    BEGIN
        INSERT INTO Coach (coach_id, full_name, qualification)
        VALUES (p_coach_id, p_full_name, p_qualification);
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Тренер ' || p_full_name || ' успешно добавлен');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при добавлении тренера: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END insert_coach;
    
    PROCEDURE update_coach (
        p_coach_id INTEGER,
        p_full_name VARCHAR2 DEFAULT NULL,
        p_qualification VARCHAR2 DEFAULT NULL
    ) IS
    BEGIN
        UPDATE Coach
        SET full_name = NVL(p_full_name, full_name),
            qualification = NVL(p_qualification, qualification)
        WHERE coach_id = p_coach_id;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Тренер ID=' || p_coach_id || ' успешно обновлен');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при обновлении тренера: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END update_coach;
    
    PROCEDURE delete_coach (p_coach_id INTEGER) IS
    BEGIN
        DELETE FROM Training WHERE coach_id = p_coach_id;
        DELETE FROM Coach WHERE coach_id = p_coach_id;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Тренер ID=' || p_coach_id || ' успешно удален');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при удалении тренера: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END delete_coach;
    
    -- ПРОЦЕДУРЫ ДЛЯ ТАБЛИЦЫ TRAINING 
    
    PROCEDURE insert_training (
        p_training_id INTEGER,
        p_athlete_id INTEGER,
        p_sport_id INTEGER,
        p_coach_id INTEGER,
        p_start_date DATE,
        p_end_date DATE
    ) IS
    BEGIN
        INSERT INTO Training (training_id, athlete_id, sport_id, coach_id, start_date, end_date)
        VALUES (p_training_id, p_athlete_id, p_sport_id, p_coach_id, p_start_date, p_end_date);
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Тренировка ID=' || p_training_id || ' успешно добавлена');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при добавлении тренировки: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END insert_training;
    
    PROCEDURE update_training (
        p_training_id INTEGER,
        p_athlete_id INTEGER DEFAULT NULL,
        p_sport_id INTEGER DEFAULT NULL,
        p_coach_id INTEGER DEFAULT NULL,
        p_start_date DATE DEFAULT NULL,
        p_end_date DATE DEFAULT NULL
    ) IS
    BEGIN
        UPDATE Training
        SET athlete_id = NVL(p_athlete_id, athlete_id),
            sport_id = NVL(p_sport_id, sport_id),
            coach_id = NVL(p_coach_id, coach_id),
            start_date = NVL(p_start_date, start_date),
            end_date = NVL(p_end_date, end_date)
        WHERE training_id = p_training_id;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Тренировка ID=' || p_training_id || ' успешно обновлена');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при обновлении тренировки: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END update_training;
    
    PROCEDURE delete_training (p_training_id INTEGER) IS
    BEGIN
        DELETE FROM Training WHERE training_id = p_training_id;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Тренировка ID=' || p_training_id || ' успешно удалена');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при удалении тренировки: ' || SQLERRM);
            ROLLBACK;
            RAISE;
    END delete_training;
    
END data_management;
/
