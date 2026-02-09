#GITHUB: zxcresp
from telebot import types

# Состояние настройки приветствия: user_id -> chat_id
welcome_states = {}
rules_states = {}

def start_rules_setup(bot, call):
    chat_id = int(call.data.split("_")[1])
    user_id = call.from_user.id
    rules_states[user_id] = chat_id

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="groups"))
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_rules_{chat_id}"))

    bot.send_message(call.message.chat.id,"📋 Отправь текст правил для этой группы.\n\n"
                                          "Этот текст будет показываться по команде /rules\n\n"
                                          "Нажми ❌ Отмена, чтобы отменить настройку правил.",reply_markup=markup)

def start_welcome_setup(bot, call):
    chat_id = int(call.data.split("_")[1])
    user_id = call.from_user.id
    welcome_states[user_id] = chat_id

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="groups"))
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_welcome_{chat_id}"))

    bot.send_message(call.message.chat.id,"👋 Отправь текст приветствия ИЛИ фото с подписью.\n\n"
                                          "Это сообщение будет показываться новым участникам группы.\n\n"
                                          "Нажми ❌ Отмена, чтобы отменить настройку приветствий.\n\n"
                                          "<b>ДЛЯ ТОГО ЧТОБЫ ОТМЕТИТЬ ПОЛЬЗОВАТЕЛЯ НАПИШИТЕ</b> {user} \n"
                                          "Пример: Добро пожаловать {user} в нашу группу!",parse_mode="HTML",reply_markup=markup)

def is_group_admin(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False

def show_group_menu(bot, call, chat_id, group_title):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("👋 Настройка приветствия", callback_data=f"welcome_{chat_id}"),
        types.InlineKeyboardButton("📋Правила", callback_data=f"rules_{chat_id}"))

   #markup.row(
        #types.InlineKeyboardButton("🔨 Бан/кик", callback_data=f"ban_{chat_id}"),
        #types.InlineKeyboardButton("⚠️ Настройка предупреждений", callback_data=f"warn_{chat_id}"))

    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="groups"))
    bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=f"<b>Настройки группы:</b> {group_title}\nВыберите действие для настройки этой группы:",parse_mode="HTML",reply_markup=markup)

def handle_group_actions(bot, call, group_title_map):

    # ===== ОТМЕНА ПРИВЕТСТВИЯ =====
    if call.data.startswith("cancel_welcome_"):
        chat_id = int(call.data.split("_")[2])
        welcome_states.pop(call.from_user.id, None)
        title = group_title_map.get(chat_id, "Неизвестная группа")

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        show_group_menu(bot, call, chat_id, title)
        return True

    # ===== ОТМЕНА ПРАВИЛ =====
    if call.data.startswith("cancel_rules_"):
        chat_id = int(call.data.split("_")[2])
        rules_states.pop(call.from_user.id, None)
        title = group_title_map.get(chat_id, "Неизвестная группа")

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        show_group_menu(bot, call, chat_id, title)
        return True

    # ===== ВСЕ ОСТАЛЬНЫЕ ДЕЙСТВИЯ =====
    if "_" not in call.data:
        return False

    action, chat_id = call.data.split("_", 1)
    chat_id = int(chat_id)
    user_id = call.from_user.id

    if action in ("welcome", "warn", "ban", "rules"):
        if not is_group_admin(bot, chat_id, user_id):
            bot.answer_callback_query(call.id,"⛔ Только администратор или владелец группы может настраивать бота",show_alert=True)
            return True

    title = group_title_map.get(chat_id, "Неизвестная группа")
    if action == "welcome":
        bot.send_message(call.message.chat.id, f"Вы выбрали настройку приветствия для группы '{title}' (ID: {chat_id}).")
        start_welcome_setup(bot, call)
        return True
    if action == "warn":
        bot.send_message(call.message.chat.id, f"Вы выбрали настройку предупреждений для группы '{title}' (ID: {chat_id}).")
        return True
    if action == "ban":
        bot.send_message(call.message.chat.id, f"Вы выбрали бан/кик участников для группы '{title}' (ID: {chat_id}).")
        return True
    if action == "rules":
        bot.send_message(call.message.chat.id, f"Вы выбрали настройку правил для группы '{title}' (ID: {chat_id}).")
        start_rules_setup(bot, call)
        return True
    return False
