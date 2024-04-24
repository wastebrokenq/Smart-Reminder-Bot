import telebot
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.background import BackgroundScheduler
from config import TELEGRAM_API_TOKEN

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
scheduler = BackgroundScheduler()  # экземпляр планировщика для запуска задач по расписанию
scheduler.start()

reminders = {}  # словарь для хранения напоминаний


def remind(chat_id, message):
    bot.send_message(chat_id, f"⏰ Напоминание: {message}")
    reminders[chat_id] = [reminder for reminder in reminders[chat_id] if reminder['message'] != message]


def parse_date_time(date_time_str):
    return datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')


def generate_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Установить напоминание", callback_data="set_remind"),
        InlineKeyboardButton("Просмотреть напоминания", callback_data="view_remind")
    )
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет! Чтобы установить напоминание, используйте /remind <ГГГГ-ММ-ДД ЧЧ:ММ> <сообщение>. Чтобы "
                 "просмотреть все напоминания, используйте /view.")
    bot.send_message(message.chat.id, "Выберите команду:", reply_markup=generate_menu())


@bot.message_handler(commands=['remind'])
def set_reminder(message):
    try:
        parts = message.text.split(maxsplit=3)
        if len(parts) < 4:
            bot.reply_to(message,
                         "🛑 Ошибка: Недостаточно аргументов. Формат должен быть /remind <ГГГГ-ММ-ДД ЧЧ:ММ> <сообщение>")
            return

        date_part = parts[1]
        time_part = parts[2]
        reminder_text = parts[3]
        date_time_str = f"{date_part} {time_part}"

        try:
            run_date = parse_date_time(date_time_str)
        except ValueError:
            bot.reply_to(message, "🛑 Ошибка: Неправильный формат даты и времени.")
            return

        if run_date <= datetime.datetime.now():
            bot.reply_to(message, "🛑 Ошибка: Нельзя установить напоминание на прошедшее время.")
            return

        existing_reminders = reminders.get(message.chat.id, [])
        if any(reminder['time'] == run_date and reminder['message'] == reminder_text for reminder in
               existing_reminders):
            bot.reply_to(message, "🛑 Ошибка: Напоминание с таким временем и содержанием уже существует.")
            return

        scheduler.add_job(remind, 'date', run_date=run_date, args=[message.chat.id, reminder_text])
        reminders[message.chat.id] = existing_reminders + [{'time': run_date, 'message': reminder_text}]
        bot.reply_to(message, f"✔️ Напоминание установлено на {run_date}!")

    except Exception as e:
        bot.reply_to(message, f"🛑 Непредвиденная ошибка: {str(e)}")


@bot.message_handler(commands=['view'])
def view_reminders(message):
    chat_id = message.chat.id
    if chat_id in reminders and reminders[chat_id]:
        response = "⏰ Ваши напоминания:\n"
        for reminder in reminders[chat_id]:
            response += f"- {reminder['time'].strftime('%Y-%m-%d %H:%M')}: {reminder['message']}\n"
        bot.send_message(chat_id, response)
    else:
        bot.send_message(chat_id, "У вас пока нет активных напоминаний.")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "set_remind":
        msg = bot.send_message(call.message.chat.id,
                               "Введите напоминание в формате: /remind <ГГГГ-ММ-ДД ЧЧ:ММ> <сообщение>")
        bot.register_next_step_handler(msg, set_reminder)
    elif call.data == "view_remind":
        view_reminders(call.message)


if __name__ == '__main__':
    bot.polling(none_stop=True)
