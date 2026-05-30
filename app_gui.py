"""
GUI приложение для управления спортивными данными с логированием
Использует tkinter для интерфейса
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import threading
from tkcalendar import DateEntry
import oracledb


try:
    oracledb.init_oracle_client(lib_dir=r"C:\Users\gorde\Desktop\client_ora\instantclient_23_0")
except Exception:
    pass

from app_backend import (
    DatabaseConnection, AthleteManager, CoachManager, 
    TrainingManager, AuditManager
)


class MainGUI:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Управление спортивными данными с логированием")
        self.root.geometry("1200x700")
        self.default_date = datetime(2000, 1, 1).date()
        
        # Инициализация компонентов БД
        self.db = DatabaseConnection()
        self.athlete_manager = None
        self.coach_manager = None
        self.training_manager = None
        self.audit_manager = None
        
        self.is_connected = False
        
        self.create_ui()
    
    def create_ui(self):
        """Создание интерфейса"""
        
        # Главная шапка с подключением
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="Хост БД:").pack(side=tk.LEFT, padx=5)
        self.host_entry = ttk.Entry(top_frame, width=20)
        self.host_entry.insert(0, "localhost:1521/XE")
        self.host_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_frame, text="Пользователь:").pack(side=tk.LEFT, padx=5)
        self.user_entry = ttk.Entry(top_frame, width=15)
        self.user_entry.insert(0, "system")
        self.user_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_frame, text="Пароль:").pack(side=tk.LEFT, padx=5)
        self.pass_entry = ttk.Entry(top_frame, width=15, show="*")
        self.pass_entry.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = ttk.Button(top_frame, text="Подключиться", 
                                      command=self.connect_to_db)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(top_frame, text="Отключено", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Создание notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка Athlete
        self.athlete_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.athlete_frame, text="Спортсмены")
        self.create_athlete_tab()
        
        # Вкладка Coach
        self.coach_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.coach_frame, text="Тренеры")
        self.create_coach_tab()
        
        # Вкладка Training
        self.training_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.training_frame, text="Тренировки")
        self.create_training_tab()
        
        # Вкладка Аудит
        self.audit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audit_frame, text="Логирование и Аудит")
        self.create_audit_tab()
    
    def connect_to_db(self):
        """Подключение к базе данных"""
        host = self.host_entry.get()
        user = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not all([host, user, password]):
            messagebox.showerror("Ошибка", "Заполните все поля подключения")
            return
        
        dsn = self._build_dsn(host)
        thread = threading.Thread(target=self._connect_thread, args=(dsn, user, password))
        thread.start()
    
    def _build_dsn(self, host: str) -> str:
        """Преобразует ввод в поле host в полный DSN."""
        normalized = host.strip()
        if not normalized:
            return normalized

        if "/" in normalized or ":" in normalized and normalized.count(":") > 1:
            return normalized
        
        return f"{normalized}:1521/XE"

    def _connect_thread(self, dsn, user, password):
        """Подключение в отдельном потоке"""
        success, message = self.db.connect(user, password, dsn)
        
        if success:
            self.is_connected = True
            self.athlete_manager = AthleteManager(self.db)
            self.coach_manager = CoachManager(self.db)
            self.training_manager = TrainingManager(self.db)
            self.audit_manager = AuditManager(self.db)
            
            self.status_label.config(text="Подключено ✓", foreground="green")
            messagebox.showinfo("Успех", message)
            
            self.connect_btn.config(state=tk.DISABLED)
            self.host_entry.config(state=tk.DISABLED)
            self.user_entry.config(state=tk.DISABLED)
            self.pass_entry.config(state=tk.DISABLED)
            # Установим значения по умолчанию для формы спортсмена (в основном ID и ранга)
            try:
                self.root.after(0, self.set_default_athlete_fields)
                self.root.after(0, self.set_default_coach_fields)
                self.root.after(0, self.set_default_training_fields)
            except Exception:
                pass
        else:
            messagebox.showerror("Ошибка подключения", message)
    
    def create_athlete_tab(self):
        """Создание вкладки Спортсмены"""
        
        # Левая панель - Форма
        left_frame = ttk.LabelFrame(self.athlete_frame, text="Добавить/Изменить спортсмена")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        ttk.Label(left_frame, text="ID:").pack(anchor=tk.W)
        self.athlete_id_entry = ttk.Entry(left_frame, width=30)
        self.athlete_id_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="ФИО:").pack(anchor=tk.W)
        self.athlete_name_entry = ttk.Entry(left_frame, width=30)
        self.athlete_name_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Дата рождения (YYYY-MM-DD):").pack(anchor=tk.W)
        self.athlete_birth_entry = DateEntry(
            left_frame,
            width=27,
            date_pattern='yyyy-mm-dd'
        )
        self.athlete_birth_entry.set_date(self.default_date)
        self.athlete_birth_entry.pack(anchor=tk.W, pady=5)
        
        # Пол — радиокнопки (M/F/Other)
        ttk.Label(left_frame, text="Пол:").pack(anchor=tk.W)
        self.athlete_gender_var = tk.StringVar(value='M')
        gender_frame = ttk.Frame(left_frame)
        gender_frame.pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(gender_frame, text='M', variable=self.athlete_gender_var, value='M').pack(side=tk.LEFT)
        ttk.Radiobutton(gender_frame, text='F', variable=self.athlete_gender_var, value='F').pack(side=tk.LEFT)
        ttk.Radiobutton(gender_frame, text='U', variable=self.athlete_gender_var, value='U').pack(side=tk.LEFT)
        
        ttk.Label(left_frame, text="Ранг:").pack(anchor=tk.W)
        rank_frame = ttk.Frame(left_frame)
        rank_frame.pack(anchor=tk.W, pady=5)
        self.rank_values = ['I', 'CMS', 'MS']
        self.athlete_rank_var = tk.StringVar(value='I')
        self.athlete_rank_entry = ttk.Entry(rank_frame, width=10, textvariable=self.athlete_rank_var)
        self.athlete_rank_entry.pack(side=tk.LEFT)
        ttk.Button(rank_frame, text='▲', width=2, command=lambda: self._change_rank(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(rank_frame, text='▼', width=2, command=lambda: self._change_rank(-1)).pack(side=tk.LEFT)
        
        ttk.Label(left_frame, text="Клуб ID:").pack(anchor=tk.W)
        self.athlete_club_entry = ttk.Entry(left_frame, width=30)
        self.athlete_club_entry.insert(0, '1')
        self.athlete_club_entry.pack(anchor=tk.W, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Добавить", 
              command=self.add_athlete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", 
              command=self.update_athlete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", 
              command=self.delete_athlete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить таблицу", 
              command=self.refresh_athletes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_athlete_fields).pack(side=tk.LEFT, padx=5)
        
        # Правая панель - Таблица
        right_frame = ttk.LabelFrame(self.athlete_frame, text="Список спортсменов")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.athlete_tree = ttk.Treeview(right_frame, columns=('ID', 'ФИО', 'Дата рождения', 'Пол', 'Ранг', 'Клуб'), 
                                         height=20)
        self.athlete_tree.column('#0', width=0, stretch=tk.NO)
        self.athlete_tree.column('ID', anchor=tk.W, width=30)
        self.athlete_tree.column('ФИО', anchor=tk.W, width=150)
        self.athlete_tree.column('Дата рождения', anchor=tk.W, width=100)
        self.athlete_tree.column('Пол', anchor=tk.W, width=50)
        self.athlete_tree.column('Ранг', anchor=tk.W, width=100)
        self.athlete_tree.column('Клуб', anchor=tk.W, width=50)
        
        self.athlete_tree.heading('ID', text='ID', anchor=tk.W)
        self.athlete_tree.heading('ФИО', text='ФИО', anchor=tk.W)
        self.athlete_tree.heading('Дата рождения', text='Дата рождения', anchor=tk.W)
        self.athlete_tree.heading('Пол', text='Пол', anchor=tk.W)
        self.athlete_tree.heading('Ранг', text='Ранг', anchor=tk.W)
        self.athlete_tree.heading('Клуб', text='Клуб', anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.athlete_tree.yview)
        self.athlete_tree.configure(yscroll=scrollbar.set)
        
        self.athlete_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.athlete_tree.bind('<<TreeviewSelect>>', self.on_athlete_select)
    
    def create_coach_tab(self):
        """Создание вкладки Тренеры"""
        
        left_frame = ttk.LabelFrame(self.coach_frame, text="Добавить/Изменить тренера")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        ttk.Label(left_frame, text="ID:").pack(anchor=tk.W)
        self.coach_id_entry = ttk.Entry(left_frame, width=30)
        self.coach_id_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="ФИО:").pack(anchor=tk.W)
        self.coach_name_entry = ttk.Entry(left_frame, width=30)
        self.coach_name_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Квалификация:").pack(anchor=tk.W)
        self.coach_qual_entry = ttk.Entry(left_frame, width=30)
        self.coach_qual_entry.pack(anchor=tk.W, pady=5)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Добавить", 
              command=self.add_coach).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", 
              command=self.update_coach).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", 
              command=self.delete_coach).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить таблицу", 
              command=self.refresh_coaches).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_coach_fields).pack(side=tk.LEFT, padx=5)
        
        right_frame = ttk.LabelFrame(self.coach_frame, text="Список тренеров")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.coach_tree = ttk.Treeview(right_frame, columns=('ID', 'ФИО', 'Квалификация'), 
                                       height=20)
        self.coach_tree.column('#0', width=0, stretch=tk.NO)
        self.coach_tree.column('ID', anchor=tk.W, width=50)
        self.coach_tree.column('ФИО', anchor=tk.W, width=200)
        self.coach_tree.column('Квалификация', anchor=tk.W, width=200)
        
        self.coach_tree.heading('ID', text='ID', anchor=tk.W)
        self.coach_tree.heading('ФИО', text='ФИО', anchor=tk.W)
        self.coach_tree.heading('Квалификация', text='Квалификация', anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.coach_tree.yview)
        self.coach_tree.configure(yscroll=scrollbar.set)
        
        self.coach_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.coach_tree.bind('<<TreeviewSelect>>', self.on_coach_select)
    
    def create_training_tab(self):
        """Создание вкладки Тренировки"""
        
        left_frame = ttk.LabelFrame(self.training_frame, text="Добавить/Изменить тренировку")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        ttk.Label(left_frame, text="ID:").pack(anchor=tk.W)
        self.training_id_entry = ttk.Entry(left_frame, width=30)
        self.training_id_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Спортсмен ID:").pack(anchor=tk.W)
        self.training_athlete_entry = ttk.Entry(left_frame, width=30)
        self.training_athlete_entry.insert(0, '1')
        self.training_athlete_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Спорт ID:").pack(anchor=tk.W)
        self.training_sport_entry = ttk.Entry(left_frame, width=30)
        self.training_sport_entry.insert(0, '1')
        self.training_sport_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Тренер ID:").pack(anchor=tk.W)
        self.training_coach_entry = ttk.Entry(left_frame, width=30)
        self.training_coach_entry.insert(0, '1')
        self.training_coach_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Дата начала (YYYY-MM-DD):").pack(anchor=tk.W)
        self.training_start_entry = DateEntry(
            left_frame,
            width=27,
            date_pattern='yyyy-mm-dd'
        )
        self.training_start_entry.set_date(self.default_date)
        self.training_start_entry.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="Дата окончания (YYYY-MM-DD):").pack(anchor=tk.W)
        self.training_end_entry = DateEntry(
            left_frame,
            width=27,
            date_pattern='yyyy-mm-dd'
        )
        self.training_end_entry.set_date(self.default_date)
        self.training_end_entry.pack(anchor=tk.W, pady=5)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Добавить", 
              command=self.add_training).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", 
              command=self.update_training).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", 
              command=self.delete_training).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить таблицу", 
              command=self.refresh_trainings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_training_fields).pack(side=tk.LEFT, padx=5)
        
        right_frame = ttk.LabelFrame(self.training_frame, text="Список тренировок")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.training_tree = ttk.Treeview(right_frame, 
                                         columns=('ID', 'Спортсмен', 'Спорт', 'Тренер', 'Начало', 'Конец'),
                                         height=20)
        self.training_tree.column('#0', width=0, stretch=tk.NO)
        self.training_tree.column('ID', anchor=tk.W, width=40)
        self.training_tree.column('Спортсмен', anchor=tk.W, width=80)
        self.training_tree.column('Спорт', anchor=tk.W, width=60)
        self.training_tree.column('Тренер', anchor=tk.W, width=60)
        self.training_tree.column('Начало', anchor=tk.W, width=100)
        self.training_tree.column('Конец', anchor=tk.W, width=100)
        
        self.training_tree.heading('ID', text='ID', anchor=tk.W)
        self.training_tree.heading('Спортсмен', text='Спортсмен', anchor=tk.W)
        self.training_tree.heading('Спорт', text='Спорт', anchor=tk.W)
        self.training_tree.heading('Тренер', text='Тренер', anchor=tk.W)
        self.training_tree.heading('Начало', text='Начало', anchor=tk.W)
        self.training_tree.heading('Конец', text='Конец', anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.training_tree.yview)
        self.training_tree.configure(yscroll=scrollbar.set)
        
        self.training_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.training_tree.bind('<<TreeviewSelect>>', self.on_training_select)
    
    def create_audit_tab(self):
        """Создание вкладки Аудит и Логирование"""
        
        # Верхняя панель фильтрации
        filter_frame = ttk.LabelFrame(self.audit_frame, text="Фильтры для просмотра логов")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Начало (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
        self.log_start_var = tk.StringVar(value='')
        self.log_start_entry = DateEntry(
            filter_frame,
            width=17,
            date_pattern='yyyy-mm-dd',
            textvariable=self.log_start_var
        )
        self.log_start_entry.pack(side=tk.LEFT, padx=5)
        self.log_start_var.set('')
        
        ttk.Label(filter_frame, text="Конец (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
        self.log_end_var = tk.StringVar(value='')
        self.log_end_entry = DateEntry(
            filter_frame,
            width=17,
            date_pattern='yyyy-mm-dd',
            textvariable=self.log_end_var
        )
        self.log_end_entry.pack(side=tk.LEFT, padx=5)
        self.log_end_var.set('')
        
        ttk.Label(filter_frame, text="Тип операции:").pack(side=tk.LEFT, padx=5)
        self.log_type_combo = ttk.Combobox(filter_frame, values=['', 'INSERT', 'UPDATE', 'DELETE'], 
                                          width=15, state='readonly')
        self.log_type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Показать логи", 
                  command=self.show_logs).pack(side=tk.LEFT, padx=5)
        
        # Средняя панель отмены
        undo_frame = ttk.LabelFrame(self.audit_frame, text="Отмена операций")
        undo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(undo_frame, text="ID лога для отмены:").pack(side=tk.LEFT, padx=5)
        self.undo_id_entry = ttk.Entry(undo_frame, width=20)
        self.undo_id_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(undo_frame, text="Отменить операцию", 
                  command=self.undo_operation).pack(side=tk.LEFT, padx=5)
        
        # Нижняя панель отчетов
        report_frame = ttk.LabelFrame(self.audit_frame, text="Сводный отчет (отмечьте флаги сортировки)")
        report_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.sort_entity_var = tk.BooleanVar()
        self.sort_operation_var = tk.BooleanVar()
        self.sort_count_var = tk.BooleanVar()
        
        ttk.Checkbutton(report_frame, text="Сортировать по названию сущности (Флаг 1)", 
                       variable=self.sort_entity_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(report_frame, text="Сортировать по типу операции (Флаг 2)", 
                       variable=self.sort_operation_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(report_frame, text="Сортировать по количеству (Флаг 3)", 
                       variable=self.sort_count_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(report_frame, text="Показать отчет", 
                  command=self.show_report).pack(side=tk.LEFT, padx=5)
        
        # Область вывода логов
        self.log_output = scrolledtext.ScrolledText(self.audit_frame, height=20, width=100)
        self.log_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _parse_int_field(self, entry, field_name: str, allow_empty: bool = False):
        value = entry.get().strip()
        if allow_empty and not value:
            return None
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f'Поле "{field_name}" должно быть числом') from exc

    def _parse_date_field(self, entry, field_name: str, allow_empty: bool = False):
        value = entry.get().strip()
        if allow_empty and not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(f'Поле "{field_name}" должно быть в формате YYYY-MM-DD') from exc

    def _format_date_for_entry(self, value):
        if value is None:
            return ''
        if hasattr(value, 'strftime'):
            try:
                return value.strftime('%Y-%m-%d')
            except Exception:
                return str(value)
        text = str(value)
        return text[:10] if len(text) >= 10 else text

    def _set_date_widget(self, widget, value):
        """Безопасно устанавливает дату для виджетов типа DateEntry."""
        if value is None:
            widget.set_date(self.default_date)
            return
        try:
            if hasattr(value, 'date'):
                widget.set_date(value.date())
            else:
                widget.set_date(str(value)[:10])
        except Exception:
            widget.set_date(self.default_date)

    def _get_selected_tree_id(self, tree, field_name: str):
        """Возвращает значение первого столбца из выбранной строки (если есть)."""
        selected_items = tree.selection()
        if selected_items:
            item_id = selected_items[0]
        else:
            item_id = tree.focus()
            if not item_id:
                return None

        item_data = tree.item(item_id)
        item_values = item_data.get("values", ()) if isinstance(item_data, dict) else ()
        if not item_values:
            return None

        try:
            return int(item_values[0])
        except (TypeError, ValueError) as exc:
            raise ValueError(f'В выбранной строке таблицы не найден корректный {field_name}') from exc

    def _get_next_id(self, table: str, id_col: str) -> int:
        """Возвращает следующий доступный ID для указанной таблицы (MAX+1)."""
        if not self.is_connected:
            return 1
        query = f"SELECT NVL(MAX({id_col}),0)+1 FROM {table}"
        success, result = self.db.fetch_data(query)
        if success and result and isinstance(result, list) and len(result) > 0:
            try:
                return int(result[0][0])
            except Exception:
                return 1
        return 1

    def set_default_athlete_fields(self):
        """Устанавливает значения по умолчанию в форме спортсмена: ID = max+1, rank=I, club=1, gender=M."""
        try:
            next_id = self._get_next_id('Athlete', 'athlete_id')
            self.athlete_id_entry.delete(0, tk.END)
            self.athlete_id_entry.insert(0, str(next_id))
            self.athlete_name_entry.delete(0, tk.END)
            self.athlete_birth_entry.set_date(self.default_date)
            # Пол по умолчанию
            try:
                self.athlete_gender_var.set('M')
            except Exception:
                pass
            # Ранг по умолчанию
            try:
                self.athlete_rank_var.set('I')
            except Exception:
                self.athlete_rank_entry.delete(0, tk.END)
            # Клуб по умолчанию
            self.athlete_club_entry.delete(0, tk.END)
            self.athlete_club_entry.insert(0, '1')
        except Exception:
            pass

    def set_default_coach_fields(self):
        """Устанавливает значения по умолчанию в форме тренера: ID = max+1."""
        try:
            next_id = self._get_next_id('Coach', 'coach_id')
            self.coach_id_entry.delete(0, tk.END)
            self.coach_id_entry.insert(0, str(next_id))
            self.coach_name_entry.delete(0, tk.END)
            self.coach_qual_entry.delete(0, tk.END)
        except Exception:
            pass

    def set_default_training_fields(self):
        """Устанавливает значения по умолчанию в форме тренировки."""
        try:
            next_id = self._get_next_id('Training', 'training_id')
            self.training_id_entry.delete(0, tk.END)
            self.training_id_entry.insert(0, str(next_id))

            self.training_athlete_entry.delete(0, tk.END)
            self.training_athlete_entry.insert(0, '1')

            self.training_sport_entry.delete(0, tk.END)
            self.training_sport_entry.insert(0, '1')

            self.training_coach_entry.delete(0, tk.END)
            self.training_coach_entry.insert(0, '1')

            self.training_start_entry.set_date(self.default_date)
            self.training_end_entry.set_date(self.default_date)
        except Exception:
            pass

    def _change_rank(self, delta: int):
        try:
            cur = self.athlete_rank_var.get()
        except Exception:
            cur = 'I'

        try:
            idx = self.rank_values.index(cur)
        except ValueError:
            idx = 0

        idx += delta
        if idx < 0:
            idx = 0
        if idx >= len(self.rank_values):
            idx = len(self.rank_values) - 1

        new_rank = self.rank_values[idx]
        try:
            self.athlete_rank_var.set(new_rank)
        except Exception:
            self.athlete_rank_entry.delete(0, tk.END)
            self.athlete_rank_entry.insert(0, new_rank)

    def clear_athlete_fields(self):
        """Очищает все поля формы спортсмена."""
        try:
            self.athlete_id_entry.delete(0, tk.END)
            self.athlete_name_entry.delete(0, tk.END)
            self.athlete_birth_entry.set_date(self.default_date)
            try:
                self.athlete_gender_var.set('')
            except Exception:
                pass
            try:
                self.athlete_rank_var.set('')
            except Exception:
                self.athlete_rank_entry.delete(0, tk.END)
            self.athlete_club_entry.delete(0, tk.END)
        except Exception:
            pass

    def on_athlete_select(self, event=None):
        selected = self.athlete_tree.selection()
        if not selected:
            return
        values = self.athlete_tree.item(selected[0], 'values')
        if not values or len(values) < 6:
            return

        self.athlete_id_entry.delete(0, tk.END)
        self.athlete_id_entry.insert(0, str(values[0]))

        self.athlete_name_entry.delete(0, tk.END)
        self.athlete_name_entry.insert(0, str(values[1] or ''))

        self._set_date_widget(self.athlete_birth_entry, values[2])

        gender = str(values[3] or '').upper()
        if gender in ('M', 'F', 'U'):
            self.athlete_gender_var.set(gender)

        rank = str(values[4] or '').upper()
        self.athlete_rank_var.set(rank if rank in self.rank_values else 'I')

        self.athlete_club_entry.delete(0, tk.END)
        self.athlete_club_entry.insert(0, '' if values[5] is None else str(values[5]))

    def on_coach_select(self, event=None):
        selected = self.coach_tree.selection()
        if not selected:
            return
        values = self.coach_tree.item(selected[0], 'values')
        if not values or len(values) < 3:
            return

        self.coach_id_entry.delete(0, tk.END)
        self.coach_id_entry.insert(0, str(values[0]))

        self.coach_name_entry.delete(0, tk.END)
        self.coach_name_entry.insert(0, str(values[1] or ''))

        self.coach_qual_entry.delete(0, tk.END)
        self.coach_qual_entry.insert(0, str(values[2] or ''))

    def on_training_select(self, event=None):
        selected = self.training_tree.selection()
        if not selected:
            return
        values = self.training_tree.item(selected[0], 'values')
        if not values or len(values) < 6:
            return

        self.training_id_entry.delete(0, tk.END)
        self.training_id_entry.insert(0, str(values[0]))

        self.training_athlete_entry.delete(0, tk.END)
        self.training_athlete_entry.insert(0, '' if values[1] is None else str(values[1]))

        self.training_sport_entry.delete(0, tk.END)
        self.training_sport_entry.insert(0, '' if values[2] is None else str(values[2]))

        self.training_coach_entry.delete(0, tk.END)
        self.training_coach_entry.insert(0, '' if values[3] is None else str(values[3]))

        self._set_date_widget(self.training_start_entry, values[4])
        self._set_date_widget(self.training_end_entry, values[5])

    def clear_coach_fields(self):
        try:
            self.coach_id_entry.delete(0, tk.END)
            self.coach_name_entry.delete(0, tk.END)
            self.coach_qual_entry.delete(0, tk.END)
        except Exception:
            pass

    def clear_training_fields(self):
        try:
            self.training_id_entry.delete(0, tk.END)
            self.training_athlete_entry.delete(0, tk.END)
            self.training_sport_entry.delete(0, tk.END)
            self.training_coach_entry.delete(0, tk.END)
            self.training_start_entry.set_date(self.default_date)
            self.training_end_entry.set_date(self.default_date)
        except Exception:
            pass
    
    # МЕТОДЫ ДЛЯ РАБОТЫ С ATHLETE 
    def add_athlete(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            athlete_id = self._parse_int_field(self.athlete_id_entry, "ID спортсмена")
            full_name = self.athlete_name_entry.get()
            birth_date = self._parse_date_field(self.athlete_birth_entry, "Дата рождения")
            gender = self.athlete_gender_var.get() or None
            rank = self.athlete_rank_var.get() or None
            club_id = self._parse_int_field(self.athlete_club_entry, "Клуб ID", allow_empty=True)
            
            thread = threading.Thread(target=self._add_athlete_thread, 
                                    args=(athlete_id, full_name, birth_date, gender, rank, club_id))
            thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _add_athlete_thread(self, athlete_id, full_name, birth_date, gender, rank, club_id):
        success, message = self.athlete_manager.add_athlete(athlete_id, full_name, birth_date, gender, rank, club_id)
        messagebox.showinfo("Результат", message)
        if success:
            self.athlete_id_entry.delete(0, tk.END)
            self.athlete_name_entry.delete(0, tk.END)
            self.athlete_birth_entry.delete(0, tk.END)
            try:
                self.athlete_gender_var.set('')
            except Exception:
                pass
            try:
                self.athlete_rank_var.set('')
            except Exception:
                pass
            self.athlete_club_entry.delete(0, tk.END)
            self.refresh_athletes()
    
    def update_athlete(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            athlete_id = self._parse_int_field(self.athlete_id_entry, "ID спортсмена")
            full_name = self.athlete_name_entry.get() or None
            birth_date = self._parse_date_field(self.athlete_birth_entry, "Дата рождения", allow_empty=True)
            gender = self.athlete_gender_var.get() or None
            rank = self.athlete_rank_var.get() or None
            club_id = self._parse_int_field(self.athlete_club_entry, "Клуб ID", allow_empty=True)
            
            thread = threading.Thread(target=self._update_athlete_thread,
                                    args=(athlete_id, full_name, birth_date, gender, rank, club_id))
            thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _update_athlete_thread(self, athlete_id, full_name, birth_date, gender, rank, club_id):
        success, message = self.athlete_manager.update_athlete(athlete_id, full_name, birth_date, gender, rank, club_id)
        messagebox.showinfo("Результат", message)
        if success:
            self.refresh_athletes()
    
    def delete_athlete(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            athlete_id = self._get_selected_tree_id(self.athlete_tree, "ID спортсмена")
            if athlete_id is None:
                athlete_id = self._parse_int_field(self.athlete_id_entry, "ID спортсмена")
            if messagebox.askyesno("Подтверждение", f"Удалить спортсмена ID={athlete_id}?"):
                thread = threading.Thread(target=self._delete_athlete_thread, args=(athlete_id,))
                thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _delete_athlete_thread(self, athlete_id):
        success, message = self.athlete_manager.delete_athlete(athlete_id)
        messagebox.showinfo("Результат", message)
        if success:
            self.refresh_athletes()
            self.refresh_trainings()
    
    def refresh_athletes(self):
        if not self.is_connected:
            return
        
        thread = threading.Thread(target=self._refresh_athletes_thread)
        thread.start()
    
    def _refresh_athletes_thread(self):
        # Очищаем таблицу
        for item in self.athlete_tree.get_children():
            self.athlete_tree.delete(item)
        
        success, data = self.athlete_manager.get_all_athletes()
        if success:
            for row in data:
                self.athlete_tree.insert('', tk.END, values=row)
        # После обновления таблицы установим значения по умолчанию в форме
        try:
            self.root.after(0, self.set_default_athlete_fields)
        except Exception:
            pass
    
    #  МЕТОДЫ ДЛЯ РАБОТЫ С COACH 
    
    def add_coach(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            coach_id = self._parse_int_field(self.coach_id_entry, "ID тренера")
            full_name = self.coach_name_entry.get()
            qualification = self.coach_qual_entry.get()
            
            thread = threading.Thread(target=self._add_coach_thread,
                                    args=(coach_id, full_name, qualification))
            thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _add_coach_thread(self, coach_id, full_name, qualification):
        success, message = self.coach_manager.add_coach(coach_id, full_name, qualification)
        messagebox.showinfo("Результат", message)
        if success:
            self.coach_id_entry.delete(0, tk.END)
            self.coach_name_entry.delete(0, tk.END)
            self.coach_qual_entry.delete(0, tk.END)
            self.refresh_coaches()
    
    def update_coach(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            coach_id = self._parse_int_field(self.coach_id_entry, "ID тренера")
            full_name = self.coach_name_entry.get() or None
            qualification = self.coach_qual_entry.get() or None
            
            thread = threading.Thread(target=self._update_coach_thread,
                                    args=(coach_id, full_name, qualification))
            thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _update_coach_thread(self, coach_id, full_name, qualification):
        success, message = self.coach_manager.update_coach(coach_id, full_name, qualification)
        messagebox.showinfo("Результат", message)
        if success:
            self.refresh_coaches()
    
    def delete_coach(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            coach_id = self._get_selected_tree_id(self.coach_tree, "ID тренера")
            if coach_id is None:
                coach_id = self._parse_int_field(self.coach_id_entry, "ID тренера")
            if messagebox.askyesno("Подтверждение", f"Удалить тренера ID={coach_id}?"):
                thread = threading.Thread(target=self._delete_coach_thread, args=(coach_id,))
                thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _delete_coach_thread(self, coach_id):
        success, message = self.coach_manager.delete_coach(coach_id)
        messagebox.showinfo("Результат", message)
        if success:
            self.refresh_coaches()
            self.refresh_trainings()
    
    def refresh_coaches(self):
        if not self.is_connected:
            return
        
        thread = threading.Thread(target=self._refresh_coaches_thread)
        thread.start()
    
    def _refresh_coaches_thread(self):
        for item in self.coach_tree.get_children():
            self.coach_tree.delete(item)
        
        success, data = self.coach_manager.get_all_coaches()
        if success:
            for row in data:
                self.coach_tree.insert('', tk.END, values=row)
        try:
            self.root.after(0, self.set_default_coach_fields)
        except Exception:
            pass
    
    #  МЕТОДЫ ДЛЯ РАБОТЫ С TRAINING 
    
    def add_training(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            training_id = self._parse_int_field(self.training_id_entry, "ID тренировки")
            athlete_id = self._parse_int_field(self.training_athlete_entry, "ID спортсмена")
            sport_id = self._parse_int_field(self.training_sport_entry, "Спорт ID", allow_empty=True)
            coach_id = self._parse_int_field(self.training_coach_entry, "ID тренера", allow_empty=True)
            start_date = self._parse_date_field(self.training_start_entry, "Дата начала")
            end_date = self._parse_date_field(self.training_end_entry, "Дата окончания")
            
            thread = threading.Thread(target=self._add_training_thread,
                                    args=(training_id, athlete_id, sport_id, coach_id, start_date, end_date))
            thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _add_training_thread(self, training_id, athlete_id, sport_id, coach_id, start_date, end_date):
        success, message = self.training_manager.add_training(training_id, athlete_id, sport_id, coach_id, start_date, end_date)
        messagebox.showinfo("Результат", message)
        if success:
            self.training_id_entry.delete(0, tk.END)
            self.training_athlete_entry.delete(0, tk.END)
            self.training_sport_entry.delete(0, tk.END)
            self.training_coach_entry.delete(0, tk.END)
            self.training_start_entry.delete(0, tk.END)
            self.training_end_entry.delete(0, tk.END)
            self.refresh_trainings()
    
    def update_training(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            training_id = self._parse_int_field(self.training_id_entry, "ID тренировки")
            athlete_id = self._parse_int_field(self.training_athlete_entry, "ID спортсмена", allow_empty=True)
            sport_id = self._parse_int_field(self.training_sport_entry, "Спорт ID", allow_empty=True)
            coach_id = self._parse_int_field(self.training_coach_entry, "ID тренера", allow_empty=True)
            start_date = self._parse_date_field(self.training_start_entry, "Дата начала", allow_empty=True)
            end_date = self._parse_date_field(self.training_end_entry, "Дата окончания", allow_empty=True)
            
            thread = threading.Thread(target=self._update_training_thread,
                                    args=(training_id, athlete_id, sport_id, coach_id, start_date, end_date))
            thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _update_training_thread(self, training_id, athlete_id, sport_id, coach_id, start_date, end_date):
        success, message = self.training_manager.update_training(training_id, athlete_id, sport_id, coach_id, start_date, end_date)
        messagebox.showinfo("Результат", message)
        if success:
            self.refresh_trainings()
    
    def delete_training(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            training_id = self._get_selected_tree_id(self.training_tree, "ID тренировки")
            if training_id is None:
                training_id = self._parse_int_field(self.training_id_entry, "ID тренировки")
            if messagebox.askyesno("Подтверждение", f"Удалить тренировку ID={training_id}?"):
                thread = threading.Thread(target=self._delete_training_thread, args=(training_id,))
                thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _delete_training_thread(self, training_id):
        success, message = self.training_manager.delete_training(training_id)
        messagebox.showinfo("Результат", message)
        if success:
            self.refresh_trainings()
    
    def refresh_trainings(self):
        if not self.is_connected:
            return
        
        thread = threading.Thread(target=self._refresh_trainings_thread)
        thread.start()
    
    def _refresh_trainings_thread(self):
        for item in self.training_tree.get_children():
            self.training_tree.delete(item)
        
        success, data = self.training_manager.get_all_trainings()
        if success:
            for row in data:
                self.training_tree.insert('', tk.END, values=row)
        try:
            self.root.after(0, self.set_default_training_fields)
        except Exception:
            pass
    
    # МЕТОДЫ ДЛЯ РАБОТЫ С AUDIT 
    
    def show_logs(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        self.log_output.delete(1.0, tk.END)
        
        start_date = self.log_start_entry.get() or None
        end_date = self.log_end_entry.get() or None
        operation_type = self.log_type_combo.get() or None
        
        thread = threading.Thread(target=self._show_logs_thread, 
                                args=(start_date, end_date, operation_type))
        thread.start()
    
    def _show_logs_thread(self, start_date, end_date, operation_type):
        success, message = self.audit_manager.view_logs(start_date, end_date, operation_type)
        self.log_output.insert(tk.END, f"Результат: {message}\n\n")
        
        success, data = self.audit_manager.get_logs_data(start_date, end_date, operation_type)
        if success:
            self.log_output.insert(tk.END, "=" * 100 + "\n")
            self.log_output.insert(tk.END, f"{'ID':<6} {'Сущность':<12} {'Entity ID':<10} {'Операция':<10} {'Дата':<20} {'Пользователь':<15} {'Отменено':<8}\n")
            self.log_output.insert(tk.END, "=" * 100 + "\n")
            
            for row in data:
                log_id, entity_name, entity_id, op_type, op_date, user_name, is_reverted = row
                self.log_output.insert(tk.END, f"{log_id:<6} {entity_name:<12} {entity_id:<10} {op_type:<10} {str(op_date):<20} {user_name:<15} {is_reverted:<8}\n")
    
    def undo_operation(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        try:
            log_id = self._parse_int_field(self.undo_id_entry, "ID лога")
            if messagebox.askyesno("Подтверждение", f"Отменить операцию ID={log_id}?"):
                thread = threading.Thread(target=self._undo_operation_thread, args=(log_id,))
                thread.start()
        except ValueError as e:
            messagebox.showerror("Ошибка", 'Поле "ID лога" должно быть числом')
    
    def _undo_operation_thread(self, log_id):
        success, message = self.audit_manager.undo_operation(log_id)
        messagebox.showinfo("Результат", message)
        self.undo_id_entry.delete(0, tk.END)
    
    def show_report(self):
        if not self.is_connected:
            messagebox.showerror("Ошибка", "Не подключены к БД")
            return
        
        self.log_output.delete(1.0, tk.END)
        
        sort_entity = int(self.sort_entity_var.get())
        sort_operation = int(self.sort_operation_var.get())
        sort_count = int(self.sort_count_var.get())
        
        thread = threading.Thread(target=self._show_report_thread,
                                args=(sort_entity, sort_operation, sort_count))
        thread.start()
    
    def _show_report_thread(self, sort_entity, sort_operation, sort_count):
        success, data = self.audit_manager.get_summary_report_data(sort_entity, sort_operation, sort_count)
        if not success:
            self.log_output.insert(tk.END, f"Ошибка при создании отчета: {data}\n")
            return

        self.log_output.insert(tk.END, "========== СВОДНЫЙ ОТЧЕТ ==========" + "\n")
        self.log_output.insert(tk.END, f"Флаг 1 (по сущности): {sort_entity}\n")
        self.log_output.insert(tk.END, f"Флаг 2 (по операции): {sort_operation}\n")
        self.log_output.insert(tk.END, f"Флаг 3 (по количеству): {sort_count}\n")
        self.log_output.insert(tk.END, "-" * 70 + "\n")
        self.log_output.insert(tk.END, f"{'Сущность':<14} {'Операция':<12} {'Количество':<10}\n")
        self.log_output.insert(tk.END, "-" * 70 + "\n")

        for row in data:
            entity_name, operation_type, op_count = row
            self.log_output.insert(tk.END, f"{entity_name:<14} {operation_type:<12} {op_count:<10}\n")

        self.log_output.insert(tk.END, "-" * 70 + "\n")
        self.log_output.insert(tk.END, "Отчет показан в GUI\n")


def main():
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
