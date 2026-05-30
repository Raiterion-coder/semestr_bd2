
-- Пакет PL/SQL для работы с логами
-- (Просмотр, Отмена, Отчеты)


CREATE PACKAGE audit_management AS
    
    -- Процедура просмотра логов
    PROCEDURE view_audit_log (
        p_start_date DATE DEFAULT NULL,
        p_end_date DATE DEFAULT NULL,
        p_operation_type VARCHAR2 DEFAULT NULL
    );
    
    -- Процедура отмены операции
    PROCEDURE undo_operation (
        p_log_id INTEGER,
        p_status OUT VARCHAR2
    );
    
    -- Процедура получения сводного отчета
    PROCEDURE get_summary_report (
        p_sort_by_entity NUMBER DEFAULT 0,    -- Флаг 1
        p_sort_by_operation NUMBER DEFAULT 0, -- Флаг 2
        p_sort_by_count NUMBER DEFAULT 0      -- Флаг 3
    );
    
    -- Вспомогательная процедура для удаления из таблиц
    PROCEDURE delete_from_table (
        p_table_name VARCHAR2,
        p_entity_id INTEGER,
        p_old_data CLOB
    );
    
    -- Вспомогательная процедура для вставки в таблицы
    PROCEDURE insert_into_table (
        p_table_name VARCHAR2,
        p_old_data CLOB
    );
    -- Вспомогательная функция для преобразования значения из JSON в DATE
    FUNCTION json_to_date(p_json CLOB, p_path VARCHAR2) RETURN DATE;
    
END audit_management;
/

CREATE PACKAGE BODY audit_management AS
    
    -- ПРОЦЕДУРА ПРОСМОТРА ЛОГОВ 
    PROCEDURE view_audit_log (
        p_start_date DATE DEFAULT NULL,
        p_end_date DATE DEFAULT NULL,
        p_operation_type VARCHAR2 DEFAULT NULL
    ) IS
        CURSOR c_logs IS
            SELECT 
                log_id,
                entity_name,
                entity_id,
                operation_type,
                operation_date,
                old_data,
                new_data,
                user_name,
                is_reverted
            FROM Audit_Log
            WHERE (p_start_date IS NULL OR operation_date >= p_start_date)
            AND (p_end_date IS NULL OR operation_date <= p_end_date)
            AND (p_operation_type IS NULL OR operation_type = UPPER(p_operation_type))
            ORDER BY operation_date DESC;
    BEGIN
        DBMS_OUTPUT.PUT_LINE('========== ЛОГ АУДИТА ==========');
        DBMS_OUTPUT.PUT_LINE('Начало: ' || NVL(TO_CHAR(p_start_date, 'DD.MM.YYYY HH24:MI:SS'), 'Не задано'));
        DBMS_OUTPUT.PUT_LINE('Конец: ' || NVL(TO_CHAR(p_end_date, 'DD.MM.YYYY HH24:MI:SS'), 'Не задано'));
        DBMS_OUTPUT.PUT_LINE('Тип операции: ' || NVL(p_operation_type, 'Все'));
        DBMS_OUTPUT.PUT_LINE('================================');
        
        FOR rec IN c_logs LOOP
            DBMS_OUTPUT.PUT_LINE('ID: ' || rec.log_id || 
                                ' | Сущность: ' || rec.entity_name ||
                                ' | Операция: ' || rec.operation_type ||
                                ' | Дата: ' || TO_CHAR(rec.operation_date, 'DD.MM.YYYY HH24:MI:SS') ||
                                ' | Пользователь: ' || rec.user_name ||
                                ' | Отменено: ' || rec.is_reverted);
            
            IF rec.old_data IS NOT NULL THEN
                DBMS_OUTPUT.PUT_LINE('  Старые данные: ' || SUBSTR(rec.old_data, 1, 100) || '...');
            END IF;
            IF rec.new_data IS NOT NULL THEN
                DBMS_OUTPUT.PUT_LINE('  Новые данные: ' || SUBSTR(rec.new_data, 1, 100) || '...');
            END IF;
            DBMS_OUTPUT.PUT_LINE('--------------------------------');
        END LOOP;
        
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при чтении логов: ' || SQLERRM);
    END view_audit_log;
    
    -- ВСПОМОГАТЕЛЬНАЯ ПРОЦЕДУРА УДАЛЕНИЯ 
    PROCEDURE delete_from_table (
        p_table_name VARCHAR2,
        p_entity_id INTEGER,
        p_old_data CLOB
    ) IS
        v_sql VARCHAR2(4000);
    BEGIN
        IF p_table_name = 'ATHLETE' THEN
            DELETE FROM Athlete WHERE athlete_id = p_entity_id;
        ELSIF p_table_name = 'COACH' THEN
            DELETE FROM Coach WHERE coach_id = p_entity_id;
        ELSIF p_table_name = 'TRAINING' THEN
            DELETE FROM Training WHERE training_id = p_entity_id;
        END IF;
    END delete_from_table;

    --  ВСПОМОГАТЕЛЬНАЯ ПРОЦЕДУРА ВОССТАНОВЛЕНИЯ ДАТЫ 
    FUNCTION json_to_date(p_json CLOB, p_path VARCHAR2)
    RETURN DATE IS
        v_value VARCHAR2(100);
    BEGIN
        v_value := JSON_VALUE(p_json, p_path RETURNING VARCHAR2(100));

        IF v_value IS NULL THEN
            RETURN NULL;
        ELSIF REGEXP_LIKE(v_value, '^[0-9]{4}-[0-9]{2}-[0-9]{2}') THEN
            RETURN TO_DATE(SUBSTR(v_value, 1, 10), 'YYYY-MM-DD');
        ELSIF REGEXP_LIKE(v_value, '^[0-9]{2}-[A-Z]{3}-[0-9]{2}', 'i') THEN
            RETURN TO_DATE(v_value, 'DD-MON-RR');
        ELSE
            BEGIN
                RETURN TO_DATE(v_value, 'YYYY-MM-DD HH24:MI:SS');
            EXCEPTION
                WHEN OTHERS THEN
                    BEGIN
                        RETURN TO_DATE(v_value, 'YYYY-MM-DD');
                    EXCEPTION
                        WHEN OTHERS THEN
                            BEGIN
                                RETURN TO_DATE(v_value, 'DD-MON-RR');
                            EXCEPTION
                                WHEN OTHERS THEN
                                    RETURN NULL;
                            END;
                    END;
            END;
        END IF;
    END json_to_date;

    --  ВСПОМОГАТЕЛЬНАЯ ПРОЦЕДУРА ВОССТАНОВЛЕНИЯ ЗАВИСИМЫХ ТРЕНИРОВОК 
    PROCEDURE restore_related_trainings(
        p_parent_table VARCHAR2,
        p_parent_id INTEGER
    ) IS
    BEGIN
        FOR rec IN (
            SELECT log_id, old_data
            FROM Audit_Log
            WHERE entity_name = 'TRAINING'
              AND operation_type = 'DELETE'
              AND is_reverted = 0
              AND (
                    (p_parent_table = 'ATHLETE' AND JSON_VALUE(old_data, '$.athlete_id' RETURNING NUMBER) = p_parent_id)
                 OR (p_parent_table = 'COACH' AND JSON_VALUE(old_data, '$.coach_id' RETURNING NUMBER) = p_parent_id)
              )
        ) LOOP
            BEGIN
                insert_into_table('TRAINING', rec.old_data);

                UPDATE Audit_Log
                SET is_reverted = 1
                WHERE log_id = rec.log_id;

                INSERT INTO Undo_History (undo_id, log_id, undo_date, undo_status)
                VALUES (undo_history_seq.NEXTVAL, rec.log_id, SYSTIMESTAMP, 'SUCCESS');
            EXCEPTION
                WHEN DUP_VAL_ON_INDEX THEN
                    -- Уже существует: считаем восстановленным
                    UPDATE Audit_Log
                    SET is_reverted = 1
                    WHERE log_id = rec.log_id;

                    INSERT INTO Undo_History (undo_id, log_id, undo_date, undo_status)
                    VALUES (undo_history_seq.NEXTVAL, rec.log_id, SYSTIMESTAMP, 'ALREADY_EXISTS');
                WHEN OTHERS THEN
                    -- Не прерываем откат родительской сущности из-за одной зависимой записи
                    DECLARE
                        v_err_text VARCHAR2(120);
                    BEGIN
                        v_err_text := SUBSTR(SQLERRM, 1, 80);
                        INSERT INTO Undo_History (undo_id, log_id, undo_date, undo_status)
                        VALUES (undo_history_seq.NEXTVAL, rec.log_id, SYSTIMESTAMP, 'ERROR: ' || v_err_text);
                    END;
            END;
        END LOOP;
    END restore_related_trainings;
    
    --  ВСПОМОГАТЕЛЬНАЯ ПРОЦЕДУРА ВСТАВКИ 
    PROCEDURE insert_into_table (
        p_table_name VARCHAR2,
        p_old_data CLOB
    ) IS
        v_id NUMBER;
        v_exists NUMBER;
        v_athlete_id NUMBER;
        v_coach_id NUMBER;
    BEGIN
        IF p_table_name = 'ATHLETE' THEN
            v_id := JSON_VALUE(p_old_data, '$.athlete_id' RETURNING NUMBER);
            SELECT COUNT(*) INTO v_exists FROM Athlete WHERE athlete_id = v_id;
            IF v_exists = 0 THEN
                INSERT INTO Athlete (athlete_id, full_name, birth_date, gender, rank, club_id)
                VALUES (
                    v_id,
                    JSON_VALUE(p_old_data, '$.full_name' RETURNING VARCHAR2(100)),
                    json_to_date(p_old_data, '$.birth_date'),
                    JSON_VALUE(p_old_data, '$.gender' RETURNING VARCHAR2(10)),
                    JSON_VALUE(p_old_data, '$.rank' RETURNING VARCHAR2(50)),
                    JSON_VALUE(p_old_data, '$.club_id' RETURNING NUMBER)
                );
            END IF;

        ELSIF p_table_name = 'COACH' THEN
            v_id := JSON_VALUE(p_old_data, '$.coach_id' RETURNING NUMBER);
            SELECT COUNT(*) INTO v_exists FROM Coach WHERE coach_id = v_id;
            IF v_exists = 0 THEN
                INSERT INTO Coach (coach_id, full_name, qualification)
                VALUES (
                    v_id,
                    JSON_VALUE(p_old_data, '$.full_name' RETURNING VARCHAR2(100)),
                    JSON_VALUE(p_old_data, '$.qualification' RETURNING VARCHAR2(100))
                );
            END IF;

        ELSIF p_table_name = 'TRAINING' THEN
            v_id := JSON_VALUE(p_old_data, '$.training_id' RETURNING NUMBER);
            v_athlete_id := JSON_VALUE(p_old_data, '$.athlete_id' RETURNING NUMBER);
            v_coach_id := JSON_VALUE(p_old_data, '$.coach_id' RETURNING NUMBER);

            SELECT COUNT(*) INTO v_exists FROM Training WHERE training_id = v_id;
            IF v_exists = 0 THEN
                -- Проверка, что ссылки существуют, иначе будет FK-ошибка
                SELECT COUNT(*) INTO v_exists FROM Athlete WHERE athlete_id = v_athlete_id;
                IF v_exists = 0 THEN
                    RAISE_APPLICATION_ERROR(-20011, 'Не найден Athlete ID=' || v_athlete_id || ' для восстановления Training ID=' || v_id);
                END IF;

                SELECT COUNT(*) INTO v_exists FROM Coach WHERE coach_id = v_coach_id;
                IF v_exists = 0 THEN
                    RAISE_APPLICATION_ERROR(-20012, 'Не найден Coach ID=' || v_coach_id || ' для восстановления Training ID=' || v_id);
                END IF;

                INSERT INTO Training (training_id, athlete_id, sport_id, coach_id, start_date, end_date)
                VALUES (
                    v_id,
                    v_athlete_id,
                    JSON_VALUE(p_old_data, '$.sport_id' RETURNING NUMBER),
                    v_coach_id,
                    json_to_date(p_old_data, '$.start_date'),
                    json_to_date(p_old_data, '$.end_date')
                );
            END IF;
        END IF;
    END insert_into_table;
    
    -- ПРОЦЕДУРА ОТМЕНЫ ОПЕРАЦИИ 
    PROCEDURE undo_operation (
        p_log_id INTEGER,
        p_status OUT VARCHAR2
    ) IS
        v_entity_name VARCHAR2(50);
        v_entity_id INTEGER;
        v_operation_type VARCHAR2(10);
        v_old_data CLOB;
        v_new_data CLOB;
        v_is_reverted NUMBER(1);
        v_existing_count NUMBER := 0;
    BEGIN
        -- Получение информации об операции
        SELECT entity_name, entity_id, operation_type, old_data, new_data, is_reverted
        INTO v_entity_name, v_entity_id, v_operation_type, v_old_data, v_new_data, v_is_reverted
        FROM Audit_Log
        WHERE log_id = p_log_id;
        
        -- Проверка, не отменена ли уже операция
        IF v_is_reverted = 1 THEN
            IF v_operation_type = 'DELETE' THEN
                IF v_entity_name = 'ATHLETE' THEN
                    SELECT COUNT(*) INTO v_existing_count
                    FROM Athlete
                    WHERE athlete_id = v_entity_id;
                ELSIF v_entity_name = 'COACH' THEN
                    SELECT COUNT(*) INTO v_existing_count
                    FROM Coach
                    WHERE coach_id = v_entity_id;
                ELSIF v_entity_name = 'TRAINING' THEN
                    SELECT COUNT(*) INTO v_existing_count
                    FROM Training
                    WHERE training_id = v_entity_id;
                END IF;

                IF v_existing_count > 0 THEN
                    p_status := 'ALREADY_RESTORED';
                    DBMS_OUTPUT.PUT_LINE('Операция уже была отменена');
                    RETURN;
                END IF;

                -- Разрешенин для повторной попытки восстановления, если запись еще отсутствует
                v_is_reverted := 0;
            ELSE
                p_status := 'ALREADY_REVERTED';
                DBMS_OUTPUT.PUT_LINE('Операция уже была отменена');
                RETURN;
            END IF;
        END IF;
        
        -- Выполнение отмены в зависимости от типа операции
        IF v_operation_type = 'INSERT' THEN
            -- Если была вставка, то удаляем
            delete_from_table(v_entity_name, v_entity_id, NULL);
            
        ELSIF v_operation_type = 'DELETE' THEN
            -- Если было удаление, то восстанавливаем 
            insert_into_table(v_entity_name, v_old_data);
            IF v_entity_name IN ('ATHLETE', 'COACH') THEN
                restore_related_trainings(v_entity_name, v_entity_id);
            END IF;
            
        ELSIF v_operation_type = 'UPDATE' THEN
            -- Если было обновление, то восстанавливаем старые значения
            IF v_entity_name = 'ATHLETE' THEN
                UPDATE Athlete
                SET full_name = 'Восстановлено',
                    birth_date = SYSDATE,
                    gender = 'U',
                    rank = 'Unknown',
                    club_id = NULL
                WHERE athlete_id = v_entity_id;
                
            ELSIF v_entity_name = 'COACH' THEN
                UPDATE Coach
                SET full_name = 'Восстановлено',
                    qualification = 'Unknown'
                WHERE coach_id = v_entity_id;
                
            ELSIF v_entity_name = 'TRAINING' THEN
                UPDATE Training
                SET athlete_id = NULL,
                    sport_id = NULL,
                    coach_id = NULL,
                    start_date = SYSDATE,
                    end_date = SYSDATE
                WHERE training_id = v_entity_id;
            END IF;
        END IF;
        
        -- Обновление флага отмены
        UPDATE Audit_Log
        SET is_reverted = 1
        WHERE log_id = p_log_id;
        
        -- Записывание информации об отмене
        INSERT INTO Undo_History (undo_id, log_id, undo_date, undo_status)
        VALUES (undo_history_seq.NEXTVAL, p_log_id, SYSTIMESTAMP, 'SUCCESS');
        
        COMMIT;
        p_status := 'SUCCESS';
        DBMS_OUTPUT.PUT_LINE('Операция ID=' || p_log_id || ' успешно отменена');
        
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            p_status := 'LOG_NOT_FOUND';
            DBMS_OUTPUT.PUT_LINE('Лог с ID=' || p_log_id || ' не найден');
        WHEN OTHERS THEN
            p_status := 'ERROR: ' || SUBSTR(SQLERRM, 1, 200);
            DBMS_OUTPUT.PUT_LINE('Ошибка при отмене операции: ' || SQLERRM);
            ROLLBACK;
    END undo_operation;
    
    -- ПРОЦЕДУРА СВОДНОГО ОТЧЕТА
    PROCEDURE get_summary_report (
        p_sort_by_entity NUMBER DEFAULT 0,
        p_sort_by_operation NUMBER DEFAULT 0,
        p_sort_by_count NUMBER DEFAULT 0
    ) IS
        TYPE t_report_rec IS RECORD (
            entity_name VARCHAR2(50),
            operation_type VARCHAR2(10),
            op_count INTEGER
        );
        TYPE t_report_table IS TABLE OF t_report_rec;
        v_report t_report_table;
        v_order_clause VARCHAR2(200) := '';
        v_sort_priority_count NUMBER := 0;
    BEGIN
        DBMS_OUTPUT.PUT_LINE('========== СВОДНЫЙ ОТЧЕТ ==========');
        DBMS_OUTPUT.PUT_LINE('Сортировка:');
        DBMS_OUTPUT.PUT_LINE('  По сущности (флаг 1): ' || p_sort_by_entity);
        DBMS_OUTPUT.PUT_LINE('  По типу операции (флаг 2): ' || p_sort_by_operation);
        DBMS_OUTPUT.PUT_LINE('  По количеству (флаг 3): ' || p_sort_by_count);
        DBMS_OUTPUT.PUT_LINE('==================================');
        
        -- создаем ORDER BY в зависимости от флагов
        IF p_sort_by_entity = 1 THEN
            v_order_clause := v_order_clause || CASE WHEN LENGTH(v_order_clause) > 0 THEN ', ' ELSE '' END || 'entity_name';
            v_sort_priority_count := v_sort_priority_count + 1;
        END IF;
        
        IF p_sort_by_operation = 1 THEN
            v_order_clause := v_order_clause || CASE WHEN LENGTH(v_order_clause) > 0 THEN ', ' ELSE '' END || 'operation_type';
            v_sort_priority_count := v_sort_priority_count + 1;
        END IF;
        
        IF p_sort_by_count = 1 THEN
            v_order_clause := v_order_clause || CASE WHEN LENGTH(v_order_clause) > 0 THEN ', ' ELSE '' END || 'op_count DESC';
            v_sort_priority_count := v_sort_priority_count + 1;
        END IF;
        
        IF LENGTH(v_order_clause) = 0 THEN
            v_order_clause := 'entity_name, operation_type';
        END IF;
        
        DBMS_OUTPUT.PUT_LINE('Применяемая сортировка: ' || v_order_clause);
        DBMS_OUTPUT.PUT_LINE('==================================');
        
        -- Выполняение запросов с динамическим ORDER BY
        FOR rec IN (
            SELECT 
                entity_name,
                operation_type,
                COUNT(*) as op_count
            FROM Audit_Log
            WHERE is_reverted = 0
            GROUP BY entity_name, operation_type
            ORDER BY 
                CASE WHEN p_sort_by_entity = 1 THEN entity_name ELSE NULL END,
                CASE WHEN p_sort_by_operation = 1 THEN operation_type ELSE NULL END,
                CASE WHEN p_sort_by_count = 1 THEN COUNT(*) ELSE NULL END DESC
        )
        LOOP
            DBMS_OUTPUT.PUT_LINE('Сущность: ' || rec.entity_name || 
                                ' | Операция: ' || rec.operation_type || 
                                ' | Количество: ' || rec.op_count);
        END LOOP;
        
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при создании отчета: ' || SQLERRM);
    END get_summary_report;
    
END audit_management;
/
