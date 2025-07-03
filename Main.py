import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

user_data = {}

questions = [
    {
        "text": "Ты больше любишь работать с людьми или с техникой?",
        "options": ["люди", "+/-", "техника"]
    },
    {
        "text": "Тебе нравится решать логические задачи?",
        "options": ["да", "+/-", "нет"]
    },
    {
        "text": "Ты любишь творческие задания?",
        "options": ["да", "+/-", "нет"]
    },
    {
        "text": "Ты предпочитаешь стабильную работу или готов к риску?",
        "options": ["стабильность", "+/-", "риск"]
    },
    {
        "text": "Тебе нравится учить других людей?",
        "options": ["да", "+/-", "нет"]
    },
    {
        "text": "Ты считаешь себя трудолюбивым?",
        "options": ["да", "+/-", "нет"]
    },
    {
        "text": "Какие у тебя обычно оценки?",
        "options": ["отличные", "хорошие", "средние(+/-)", "плохие"]
    }
]

options = {
    "1": ["люди", "да", "нет", "стабильность", "да", "да", "хорошие"],
    "2": ["техника", "да", "нет", "риск", "нет", "да", "отличные"],
    "3": ["люди", "нет", "да", "риск", "да", "нет", "средние(+/-)"],
    "4": ["техника", "нет", "да", "стабильность", "нет", "нет", "плохие"],
    "5": ["люди", "нет", "нет", "стабильность", "нет", "нет", "плохие"]
}

results = {
    "1": "Психолог, учитель, HR-менеджер",
    "2": "Инженер, программист, системный администратор",
    "3": "Маркетолог, дизайнер, предприниматель",
    "4": "Технический писатель, иллюстратор, механик",
    "5": "Бомж, никто, бездомный, дворник, Алкаш, человек без определённого места жительства"
}

descriptions = {
    "1": "Ты больше ориентирован на работу с людьми, любишь стабильность и помогать другим. Тебе подойдут гуманитарные профессии.",
    "2": "Ты технарь: логика, точность, уверенность и стремление к сложным задачам — это про тебя.",
    "3": "Ты креативный, не боишься риска, любишь общение и творчество. Это путь предпринимателя или дизайнера.",
    "4": "Ты интроверт, тихий мастер своего дела, любишь технику и стабильность. Подойдут технические профессии.",
    "5": "По твоим ответам выходит, что пока нет ярко выраженных предпочтений или ты не хочешь работать вообще. Впрочем, это тоже путь… но может, попробуешь пройти тест заново? 🙂"
}

@bot.message_handler(commands=['start', 'retry'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'step': 0, 'answers': []}
    bot.send_message(chat_id, "Привет! Я помогу тебе подобрать профессию. Ответь на несколько вопросов.")
    send_question(chat_id, 0)

def send_question(chat_id, step):
    q = questions[step]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for opt in q["options"]:
        markup.add(KeyboardButton(opt))
    bot.send_message(chat_id, q["text"], reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "Напиши /start, чтобы начать.")
        return

    data = user_data[chat_id]
    step = data['step']

    valid_options = [opt.lower().strip() for opt in questions[step]["options"]]
    user_answer = message.text.lower().strip()

    if user_answer not in valid_options:
        bot.send_message(chat_id, "Пожалуйста, выбери вариант из кнопок.")
        return

    data['answers'].append(user_answer)
    data['step'] += 1

    if data['step'] < len(questions):
        send_question(chat_id, data['step'])
    else:
        key, result_text, reason = process_answers(data['answers'])
        bot.send_message(chat_id, f"🔍 {reason}")
        bot.send_message(chat_id, f"💼 Подходящие профессии для тебя: {result_text}")
        bot.send_message(chat_id, "Если хочешь пройти тест заново, напиши /start")
        del user_data[chat_id]

def process_answers(answers):
    best_score = -1
    best_key = "1"

    for key, vals in options.items():
        score = 0
        for i in range(len(answers)):
            user_ans = answers[i].strip().lower()
            correct_ans = vals[i].strip().lower()

            if user_ans == correct_ans:
                score += 1
            elif user_ans == "+/-" or correct_ans == "+/-" or "средние" in user_ans and "средние" in correct_ans:
                score += 0.5

        if score > best_score:
            best_score = score
            best_key = key

    return best_key, results[best_key], descriptions[best_key]

bot.polling()
