import os
import logging
import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from inventory.google_inventory_manager import GoogleInventoryManager
from utils.language_selector import select_language
import openpyxl
from openpyxl import Workbook

# Загрузка токена из .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPORT_CHAT_ID = os.getenv("REPORT_CHAT_ID")  # Добавьте этот ID в .env

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Токен Telegram бота не найден. Добавьте его в файл .env")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ALLOWED_USERS = [
    1015632271,  # user_id администратора
    "Polevoy228",  # username без @
    # Добавьте сюда нужные user_id или username
]

category_names = {
    "en": {
        "lift": "Lift",
        "escalator": "Escalator",
        "tools": "Tools"
    },
    "ru": {
        "lift": "Лифт",
        "escalator": "Эскалатор",
        "tools": "Инструменты"
    },
    "ka": {
        "lift": "ლიფტი",
        "escalator": "ესკალატორი",
        "tools": "ინსტრუმენტები"
    },
    "az": {
        "lift": "Lift",
        "escalator": "Eskalatör",
        "tools": "Alətlər"
    }
}

class WarehouseBot:
    def __init__(self):
        self.language = None  # Язык будет выбран пользователем
        self.inventory_manager = GoogleInventoryManager("c:/Projects/warehouse-bot/src/creds.json", "warehousedatabase")
        self.manual_translations = {
            "трос 1м": {
                "az": "Kabel 1m",
                "ka": "კაბელი 1მ",
                "ru": "Кабель 1м",
                "en": "Cable 1m",
            },
            "трос 2м": {
                "az": "Kabel 2m",
                "ka": "კაბელი 2მ",
                "ru": "Трос 2м",
                "en": "Cable 2m",
            },
            "ключ 15": {
                "az": "Açar 15",
                "ka": "გასაღები 15",
                "ru": "Ключ 15",
                "en": "Wrench 15",
            },
            "ключ 10": {
                "az": "Açar 10",
                "ka": "გასაღები 10",
                "ru": "Ключ 10",
                "en": "Wrench 10",
            },
            "масленка": {
                "az": "Yağ qabı",
                "ka": "ზეთის სასწორი",
                "ru": "Масленка",
                "en": "Oil pan",
            },
            "башмак 3300": {
                "az": "Bashmaq 3300",
                "ka": "ფეხსაკარი 3300",
                "ru": "Башмак 3300",
                "en": "Shoe 3300",
            },
            "трос": {
                "az": "Kabel",
                "ka": "თოკი",
                "ru": "Трос",
                "en": "Cable",
            },
        }

    def normalize_item_name(self, item_name):
        """Нормализует название предмета для сопоставления"""
        return item_name.strip().lower()  # Убираем пробелы и приводим к нижнему регистру

    def translate_item_name(self, item_name, target_language):
        """Переводит название предмета на выбранный язык"""
        normalized_name = self.normalize_item_name(item_name)
        logger.info("Нормализованное название: '%s'", normalized_name)
        if normalized_name in self.manual_translations and target_language in self.manual_translations[normalized_name]:
            return self.manual_translations[normalized_name][target_language]
        # Если перевод не найден, возвращаем оригинальное название
        logger.warning("Перевод для '%s' на язык '%s' не найден. Используется оригинальное название.", item_name, target_language)
        return item_name

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает команду /start и предлагает выбрать язык"""
        logger.info("Команда /start получена от пользователя %s", update.effective_user.username)

        # Создание кнопок для выбора языка
        keyboard = [
            [
                InlineKeyboardButton("English", callback_data="lang_en"),
                InlineKeyboardButton("Русский", callback_data="lang_ru"),
            ],
            [
                InlineKeyboardButton("ქართული", callback_data="lang_ka"),
                InlineKeyboardButton("Azərbaycan", callback_data="lang_az"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправка сообщения с кнопками
        await update.message.reply_text(
            "Выберите язык / Select a language:",
            reply_markup=reply_markup
        )

    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор языка"""
        query = update.callback_query
        await query.answer()  # Подтверждение нажатия кнопки

        # Получение выбранного языка из callback_data
        callback_data = query.data
        logger.info("Выбран язык: %s", callback_data)

        if callback_data == "lang_en":
            self.language = select_language("en")
            await query.edit_message_text("Language set to English!")
        elif callback_data == "lang_ru":
            self.language = select_language("ru")
            await query.edit_message_text("Язык установлен на Русский!")
        elif callback_data == "lang_ka":
            self.language = select_language("ka")
            await query.edit_message_text("ენა დაყენებულია ქართულად!")
        elif callback_data == "lang_az":
            self.language = select_language("az")
            await query.edit_message_text("Dil Azərbaycan dilinə təyin edildi!")
        else:
            await query.edit_message_text("Неизвестный выбор языка.")

        # После выбора языка показать категории
        await self.show_categories(query)

    async def show_categories(self, query):
        """Показывает категории после выбора языка"""
        logger.info("Отправка кнопок с категориями")
        lang = self.language["code"] if self.language and "code" in self.language else "ru"
        names = category_names.get(lang, category_names["ru"])
        keyboard = [
            [InlineKeyboardButton(names["lift"], callback_data="category_lift")],
            [InlineKeyboardButton(names["escalator"], callback_data="category_escalator")],
            [InlineKeyboardButton(names["tools"], callback_data="category_tools")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            self.language["select_category"] if self.language and "select_category" in self.language else "Выберите категорию:",
            reply_markup=reply_markup
        )

    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор категории и показывает предметы этой категории"""
        query = update.callback_query
        await query.answer()
        callback_data = query.data
        category = callback_data.replace("category_", "")
        logger.info("Выбрана категория: %s", category)
        await self.show_items(query, category)

    async def show_items(self, query, category=None):
        """Отправляет кнопки с предметами из Excel по категории"""
        logger.info("Отправка кнопок с предметами")
        inventory = self.inventory_manager.get_inventory()
        logger.info(f"Категория для фильтрации: {category}")
        logger.info(f"Пример item: {inventory[0] if inventory else 'нет данных'}")
        keyboard = []

        for item in inventory:
            logger.info(f"Проверяем item: {item}")
            item_name = item["Название"]
            if category is None or (item.get("Категория") and item["Категория"].lower() == category):
                translated_name = self.translate_item_name(item_name, self.language["code"])
                keyboard.append([InlineKeyboardButton(translated_name, callback_data=f"item_{item_name}")])

        if not keyboard:
            await query.message.reply_text("Нет предметов в выбранной категории.")
            return

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            self.language["select_item"] if self.language and "select_item" in self.language else "Выберите предмет:",
            reply_markup=reply_markup
        )

    async def handle_item_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор предмета"""
        query = update.callback_query
        await query.answer()

        # Получение выбранного предмета
        callback_data = query.data
        item_name = callback_data.replace("item_", "")
        logger.info("Выбран предмет: %s", item_name)

        # Показать действия для выбранного предмета
        keyboard = [
            [
                InlineKeyboardButton(self.language["take"], callback_data=f"action_take_{item_name}"),
                InlineKeyboardButton(self.language["return"], callback_data=f"action_return_{item_name}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            self.language["choose_action"].format(item=item_name),
            reply_markup=reply_markup
        )

    async def handle_action_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор действия (взять или вернуть)"""
        query = update.callback_query
        await query.answer()

        # Получение действия и предмета из callback_data
        callback_data = query.data
        parts = callback_data.split("_")
        action = parts[1]
        item_name = "_".join(parts[2:])

        logger.info("Выбрано действие: %s для предмета: %s", action, item_name)

        # Генерация кнопок для выбора количества
        keyboard = []
        if action == "take":
            max_quantity = self.inventory_manager.get_quantity(item_name)
            if max_quantity == 0:
                await query.message.reply_text(f"❗ {item_name}: на складе нет в наличии!")
                return
            for quantity in range(1, max_quantity + 1):
                keyboard.append([InlineKeyboardButton(str(quantity), callback_data=f"quantity_take_{quantity}_{item_name}")])
        elif action == "return":
            for quantity in range(1, 11):  # Ограничиваем количество от 1 до 10
                keyboard.append([InlineKeyboardButton(str(quantity), callback_data=f"quantity_return_{quantity}_{item_name}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"{self.language['choose_quantity']} {item_name}:",
            reply_markup=reply_markup
        )

    async def handle_quantity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор количества"""
        query = update.callback_query
        await query.answer()

        # Получение действия, количества и предмета из callback_data
        callback_data = query.data
        parts = callback_data.split("_")
        action = parts[1]
        quantity = int(parts[2])
        item_name = "_".join(parts[3:])

        logger.info("Действие: %s, Количество: %d, Предмет: %s", action, quantity, item_name)

        user = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else str(update.effective_user.id)
        )

        if action == "take":
            self.inventory_manager.update_quantity(item_name, -quantity)
            self.inventory_manager.log_change(user, "Взял", item_name, quantity)
            await query.edit_message_text(self.language["item_taken"].format(item=item_name, quantity=quantity))
        elif action == "return":
            self.inventory_manager.update_quantity(item_name, quantity)
            self.inventory_manager.log_change(user, "Вернул", item_name, quantity)
            await query.edit_message_text(self.language["item_returned"].format(item=item_name, quantity=quantity))

    def generate_changes_report(self):
        return self.inventory_manager.get_changes_report()

    async def send_changes_report(self, chat_id):
        """Отправляет отчёт об изменениях в чат"""
        report = self.generate_changes_report()
        await self.application.bot.send_message(chat_id=chat_id, text=f"Отчёт об изменениях:\n{report}")

    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает команду /report для отправки отчёта вручную"""
        user_id = str(update.effective_user.id)
        username = update.effective_user.username
        allowed = user_id in map(str, ALLOWED_USERS) or (username and username in ALLOWED_USERS)
        if not allowed:
            await update.message.reply_text("У вас нет прав для просмотра отчёта.")
            return
        chat_id = update.effective_chat.id
        await self.send_changes_report(chat_id)

    async def take_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /take <ID> <количество> — взять предмет по ID"""
        try:
            item_id = int(context.args[0])
            quantity = int(context.args[1])
        except (IndexError, ValueError):
            await update.message.reply_text("Используйте: /take <ID> <количество>")
            return

        inventory = self.inventory_manager.get_inventory()
        item = next((i for i in inventory if str(i["ID"]) == str(item_id)), None)
        if not item:
            await update.message.reply_text("Предмет с таким ID не найден.")
            return

        max_quantity = item["Количество"]
        if max_quantity == 0:
            await update.message.reply_text(f"❗ {item['Название']}: на складе нет в наличии!")
            return
        if quantity > max_quantity:
            await update.message.reply_text(f"На складе только {max_quantity} шт.")
            return

        user = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else str(update.effective_user.id)
        )
        self.inventory_manager.update_quantity(item["Название"], -quantity)
        self.inventory_manager.log_change(user, "Взял", item["Название"], quantity)
        await update.message.reply_text(f"Вы взяли {quantity} шт. {item['Название']} (ID: {item_id})")

    async def return_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /return <ID> <количество> — вернуть предмет по ID"""
        try:
            item_id = int(context.args[0])
            quantity = int(context.args[1])
        except (IndexError, ValueError):
            await update.message.reply_text("Используйте: /return <ID> <количество>")
            return

        inventory = self.inventory_manager.get_inventory()
        item = next((i for i in inventory if str(i["ID"]) == str(item_id)), None)
        if not item:
            await update.message.reply_text("Предмет с таким ID не найден.")
            return

        user = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else str(update.effective_user.id)
        )
        self.inventory_manager.update_quantity(item["Название"], quantity)
        self.inventory_manager.log_change(user, "Вернул", item["Название"], quantity)
        await update.message.reply_text(f"Вы вернули {quantity} шт. {item['Название']} (ID: {item_id})")

    def run(self):
        """Запускает Telegram-бота"""
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.application = application  # Для доступа в send_changes_report

        # Обработчики команд и сообщений
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("report", self.report_command))  # команда для ручного текстового отчёта
        application.add_handler(CommandHandler("take", self.take_command))
        application.add_handler(CommandHandler("return", self.return_command))
        application.add_handler(CallbackQueryHandler(self.handle_language_selection, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_category_selection, pattern="^category_"))
        application.add_handler(CallbackQueryHandler(self.handle_item_selection, pattern="^item_"))
        application.add_handler(CallbackQueryHandler(self.handle_action_selection, pattern="^action_"))
        application.add_handler(CallbackQueryHandler(self.handle_quantity_selection, pattern="^quantity_"))

        # Запуск бота
        logger.info("Бот запущен и ожидает сообщений...")
        application.run_polling()

if __name__ == "__main__":
    bot = WarehouseBot()
    bot.run()