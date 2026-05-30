"""
Приложение для управления спортивными данными с логированием
Работает с таблицами: Athlete, Coach, Training
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import oracledb as cx_Oracle
import json
from typing import List, Dict, Tuple
import threading
from datetime import date


try:
    if not hasattr(cx_Oracle, 'STRING') and hasattr(cx_Oracle, 'DB_TYPE_VARCHAR'):
        cx_Oracle.STRING = cx_Oracle.DB_TYPE_VARCHAR
except Exception:
    pass


class DatabaseConnection:
    """Класс для работы с подключением к Oracle БД"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self, username: str, password: str, dsn: str):
        """Подключение к базе данных"""
        try:
            self.connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
            self.cursor = self.connection.cursor()
            return True, "Успешное подключение к БД"
        except Exception as e:
            return False, f"Ошибка подключения: {str(e)}"
    
    def disconnect(self):
        """Отключение от БД"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: Tuple = None):
        """Выполнение запроса"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True, "Запрос выполнен успешно"
        except Exception as e:
            self.connection.rollback()
            return False, f"Ошибка запроса: {str(e)}"

    def fetch_data(self, query: str, params: Tuple = None) -> Tuple[bool, any]:
        """Получение данных из запроса"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            return True, results
        except Exception as e:
            return False, str(e)


def _to_date(value):
    """Преобразует строки YYYY-MM-DD в объекты date для Oracle DATE-параметров."""
    if value is None or isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    return value


def _format_oracle_error(error: Exception) -> str:
    message = str(error)
    if 'ORA-02292' in message:
        return 'Нельзя удалить запись: у нее есть связанные записи в Training. Сначала удалите или измените связанные тренировки.'
    if 'ORA-00001' in message:
        return 'Запись с таким ID уже существует.'
    if 'ORA-01400' in message:
        return 'Не заполнено обязательное поле.'
    return message


class AthleteManager:
    """Управление таблицей Athlete"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def add_athlete(self, athlete_id: int, full_name: str, birth_date: str, 
                   gender: str, rank: str, club_id: int) -> Tuple[bool, str]:
        """Добавление спортсмена"""
        try:
            birth_date = _to_date(birth_date)
            self.db.cursor.callproc('data_management.insert_athlete',
                                   [athlete_id, full_name, birth_date, gender, rank, club_id])
            self.db.connection.commit()
            return True, f"Спортсмен {full_name} добавлен успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при добавлении: {_format_oracle_error(e)}"
    
    def update_athlete(self, athlete_id: int, full_name: str = None, birth_date: str = None,
                      gender: str = None, rank: str = None, club_id: int = None) -> Tuple[bool, str]:
        """Обновление данных спортсмена"""
        try:
            birth_date = _to_date(birth_date)
            self.db.cursor.callproc('data_management.update_athlete',
                                   [athlete_id, full_name, birth_date, gender, rank, club_id])
            self.db.connection.commit()
            return True, f"Спортсмен ID={athlete_id} обновлен успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при обновлении: {_format_oracle_error(e)}"
    
    def delete_athlete(self, athlete_id: int) -> Tuple[bool, str]:
        """Удаление спортсмена"""
        try:
            self.db.cursor.callproc('data_management.delete_athlete', [athlete_id])
            self.db.connection.commit()
            return True, f"Спортсмен ID={athlete_id} удален успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при удалении: {_format_oracle_error(e)}"
    
    def get_all_athletes(self) -> Tuple[bool, List]:
        """Получение всех спортсменов"""
        query = "SELECT * FROM Athlete ORDER BY athlete_id"
        return self.db.fetch_data(query)


class CoachManager:
    """Управление таблицей Coach"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def add_coach(self, coach_id: int, full_name: str, qualification: str) -> Tuple[bool, str]:
        """Добавление тренера"""
        try:
            self.db.cursor.callproc('data_management.insert_coach',
                                   [coach_id, full_name, qualification])
            self.db.connection.commit()
            return True, f"Тренер {full_name} добавлен успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при добавлении: {str(e)}"
    
    def update_coach(self, coach_id: int, full_name: str = None, 
                    qualification: str = None) -> Tuple[bool, str]:
        """Обновление данных тренера"""
        try:
            self.db.cursor.callproc('data_management.update_coach',
                                   [coach_id, full_name, qualification])
            self.db.connection.commit()
            return True, f"Тренер ID={coach_id} обновлен успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при обновлении: {str(e)}"
    
    def delete_coach(self, coach_id: int) -> Tuple[bool, str]:
        """Удаление тренера"""
        try:
            self.db.cursor.callproc('data_management.delete_coach', [coach_id])
            self.db.connection.commit()
            return True, f"Тренер ID={coach_id} удален успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при удалении: {str(e)}"
    
    def get_all_coaches(self) -> Tuple[bool, List]:
        """Получение всех тренеров"""
        query = "SELECT * FROM Coach ORDER BY coach_id"
        return self.db.fetch_data(query)


class TrainingManager:
    """Управление таблицей Training"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def add_training(self, training_id: int, athlete_id: int, sport_id: int,
                    coach_id: int, start_date: str, end_date: str) -> Tuple[bool, str]:
        """Добавление тренировки"""
        try:
            start_date = _to_date(start_date)
            end_date = _to_date(end_date)
            self.db.cursor.callproc('data_management.insert_training',
                                   [training_id, athlete_id, sport_id, coach_id, start_date, end_date])
            self.db.connection.commit()
            return True, f"Тренировка ID={training_id} добавлена успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при добавлении: {_format_oracle_error(e)}"
    
    def update_training(self, training_id: int, athlete_id: int = None, sport_id: int = None,
                       coach_id: int = None, start_date: str = None, end_date: str = None) -> Tuple[bool, str]:
        """Обновление данных тренировки"""
        try:
            start_date = _to_date(start_date)
            end_date = _to_date(end_date)
            self.db.cursor.callproc('data_management.update_training',
                                   [training_id, athlete_id, sport_id, coach_id, start_date, end_date])
            self.db.connection.commit()
            return True, f"Тренировка ID={training_id} обновлена успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при обновлении: {_format_oracle_error(e)}"
    
    def delete_training(self, training_id: int) -> Tuple[bool, str]:
        """Удаление тренировки"""
        try:
            self.db.cursor.callproc('data_management.delete_training', [training_id])
            self.db.connection.commit()
            return True, f"Тренировка ID={training_id} удалена успешно"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при удалении: {_format_oracle_error(e)}"
    
    def get_all_trainings(self) -> Tuple[bool, List]:
        """Получение всех тренировок"""
        query = "SELECT * FROM Training ORDER BY training_id"
        return self.db.fetch_data(query)


class AuditManager:
    """Управление логированием и отменой операций"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def view_logs(self, start_date: str = None, end_date: str = None, 
                 operation_type: str = None) -> Tuple[bool, str]:
        """Просмотр логов"""
        try:
            start_date = _to_date(start_date)
            end_date = _to_date(end_date)
            self.db.cursor.callproc('audit_management.view_audit_log',
                                   [start_date, end_date, operation_type])
            return True, "Логи выведены в консоль БД"
        except Exception as e:
            return False, f"Ошибка при просмотре логов: {str(e)}"
    
    def get_logs_data(self, start_date: str = None, end_date: str = None,
                     operation_type: str = None) -> Tuple[bool, List]:
        """Получение данных логов для отображения в GUI"""
        start_date = _to_date(start_date)
        end_date = _to_date(end_date)
        query = """
        SELECT log_id, entity_name, entity_id, operation_type, 
               operation_date, user_name, is_reverted
        FROM Audit_Log
        WHERE (:start_date IS NULL OR operation_date >= :start_date)
        AND (:end_date IS NULL OR operation_date <= :end_date)
        AND (:operation_type IS NULL OR operation_type = :operation_type)
        ORDER BY operation_date DESC
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "operation_type": operation_type,
        }
        return self.db.fetch_data(query, params)
    
    def undo_operation(self, log_id: int) -> Tuple[bool, str]:
        """Отмена операции"""
        try:
            status = self.db.cursor.var(cx_Oracle.STRING)
            self.db.cursor.callproc('audit_management.undo_operation',
                                   [log_id, status])
            self.db.connection.commit()
            return True, f"Операция отменена. Статус: {status.getvalue()}"
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Ошибка при отмене операции: {str(e)}"
    
    def get_summary_report(self, sort_by_entity: int = 0, sort_by_operation: int = 0,
                          sort_by_count: int = 0) -> Tuple[bool, str]:
        """Получение сводного отчета"""
        try:
            self.db.cursor.callproc('audit_management.get_summary_report',
                                   [sort_by_entity, sort_by_operation, sort_by_count])
            return True, "Отчет выведен в консоль БД"
        except Exception as e:
            return False, f"Ошибка при создании отчета: {str(e)}"

    def get_summary_report_data(self, sort_by_entity: int = 0, sort_by_operation: int = 0,
                                sort_by_count: int = 0) -> Tuple[bool, List]:
        """Получение сводного отчета для вывода прямо в GUI."""
        order_parts = []
        if sort_by_entity == 1:
            order_parts.append("entity_name")
        if sort_by_operation == 1:
            order_parts.append("operation_type")
        if sort_by_count == 1:
            order_parts.append("op_count DESC")

        if not order_parts:
            order_parts = ["entity_name", "operation_type"]

        order_clause = ", ".join(order_parts)
        query = f"""
        SELECT entity_name, operation_type, COUNT(*) AS op_count
        FROM Audit_Log
        WHERE is_reverted = 0
        GROUP BY entity_name, operation_type
        ORDER BY {order_clause}
        """
        return self.db.fetch_data(query)

