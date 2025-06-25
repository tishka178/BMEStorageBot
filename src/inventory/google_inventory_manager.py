import datetime
import gspread
from google.oauth2.service_account import Credentials

class GoogleInventoryManager:
    def __init__(self, creds_path, sheet_name):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        self.sheet = client.open(sheet_name).sheet1  # используем первый лист

    def get_inventory(self):
        """Возвращает список предметов из Google Sheets"""
        records = self.sheet.get_all_records()
        return records

    def get_quantity(self, item_name):
        """Возвращает количество предмета по названию"""
        records = self.get_inventory()
        for row in records:
            if row["Название"] == item_name:
                return int(row["Количество"])
        return 0

    def update_quantity(self, item_name, change):
        """Обновляет количество предмета"""
        records = self.get_inventory()
        for idx, row in enumerate(records, start=2):  # с учётом заголовка
            if row["Название"] == item_name:
                new_qty = int(row["Количество"]) + change
                self.sheet.update_cell(idx, 3, new_qty)  # 3 — это колонка "Количество"
                return
        raise ValueError(f"Предмет '{item_name}' не найден.")
    
    def log_change(self, user, action, item_name, quantity):
        """Записывает изменение в отдельный лист 'Log' Google Sheets"""
        try:
            log_sheet = self.sheet.spreadsheet.worksheet("Log")
        except gspread.exceptions.WorksheetNotFound:
            log_sheet = self.sheet.spreadsheet.add_worksheet(title="Log", rows="1000", cols="5")
            log_sheet.append_row(["Дата и время", "Пользователь", "Действие", "Предмет", "Количество"])
        log_sheet.append_row([
            datetime.datetime.now().isoformat(),
            user,
            action,
            item_name,
            quantity
        ])

    def get_changes_report(self):
        """Возвращает текстовый отчёт об изменениях за сегодня из листа Log"""
        try:
            log_sheet = self.sheet.spreadsheet.worksheet("Log")
        except gspread.exceptions.WorksheetNotFound:
            return "Изменений за сегодня нет."
        today = datetime.date.today().isoformat()
        rows = log_sheet.get_all_values()[1:]  # пропускаем заголовок
        lines = []
        for row in rows:
            if row and row[0].startswith(today):
                lines.append(" | ".join(row))
        return "\n".join(lines) if lines else "Изменений за сегодня нет."
    
    def generate_changes_report(self):
        return self.inventory_manager.get_changes_report()