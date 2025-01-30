from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, MessageHandler, filters, CommandHandler

from gpt import *
from util import *
from credentials import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "main"
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓'
        # Добавить команду в меню можно так:
        # 'command': 'button text'
    })


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "quiz"
    text = load_message("quiz")
    await send_image(update, context, "quiz")
    await send_text_buttons(update, context, text, {
        "quiz_1": "Тема: История",
        "quiz_2": "Тема: Искусство",
        "quiz_3": "Тема: Литература"})

async def quiz_button(update, context):
    query = update.callback_query.data
    if query == "quiz_1" or query == "quiz_2" or query == "quiz_3" or query == "quiz_more":
        await  update.callback_query.answer()
        await  send_text(update, context, "Ответь на вопрос: ")
        prompt = load_prompt("quiz")
        chat_gpt.set_prompt(prompt)
        answer = await  chat_gpt.add_message(query)
        await  send_text(update, context, answer)
    elif query == "quiz_new":
        await quiz(update, context)
    elif query == "quiz_start":
        await start(update, context)

async def quiz_dialog(update, context):
    text = update.message.text
    answer = await  chat_gpt.add_message(text)
    await  send_text(update, context, answer)
    await send_text_buttons(update, context, "Продолжим?", {
        "quiz_more": "Вопрос на ту же тему",
        "quiz_new": "Выбор новой темы",
        "quiz_start": "Выход из Квиза"})


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "talk"
    text = load_message("talk")
    await send_image(update, context, "talk")
    await send_text_buttons(update, context, text, {
        "talk_cobain": "Курт Кобейн",
        "talk_hawking": "Стивен Хокинг",
        "talk_nietzsche": "Фридрих Ницше",
        "talk_queen": "Королева Елизавета II",
        "talk_tolkien": "Дж.Р.Р. Толкин"})


async def talk_dialog(update, context):
    text = update.message.text
    answer = await  chat_gpt.add_message(text)
    await  send_text(update, context, answer)

async def talk_button(update, context):
    query = update.callback_query.data
    await  update.callback_query.answer()

    await  send_image(update, context, query)
    await  send_text(update, context, "Отличный выбор! Можешь начать диалог.")

    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "random"
    text = load_message('random')
    await send_image(update, context, 'random')
    await send_text(update, context, text)
    text1 = load_prompt("random")
    answer = await  chat_gpt.add_message(text1)
    await  send_text(update, context, answer)
    await send_text_buttons(update, context, "Рассказать еще один факт?", {
        "random_start": "Закончить",
        "random_random": "Хочу ещё факт"})

async def random_button(update, context):
    query = update.callback_query.data
    if query == "random_start":
        await start(update, context)
    else:
        await random(update, context)


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "gpt"
    text = load_message('gpt')
    await send_image(update, context, 'gpt')
    await send_text(update, context, text)


async  def gpt_dialog(update, context):
    text = update.message.text
    promt = load_prompt("gpt")
    answer = await  chat_gpt.send_question(promt, text)
    await send_text(update, context, answer)


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "random":
        await random(update, context)
    elif dialog.mode == "talk":
        await talk_dialog(update, context)
    elif dialog.mode == "quiz":
        await quiz_dialog(update, context)
    else:
        await send_text(update, context, "Привет")
        await send_image(update, context, "avatar_main")
        await send_text_buttons(update, context, "Запустить процесс", {
            "start":"Запустить",
            "stop": "Остановить" })


async def hello_button(update, context):
    query = update.callback_query.data
    if query == "start":
        await send_text(update, context, "Процесс запущен")
    else:
        await  send_text(update, context, "Процесс остановлен")


dialog = Dialog()
dialog.mode = None


chat_gpt = ChatGptService(token=ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("quiz", quiz))
# Зарегистрировать обработчик коллбэка можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(random_button, pattern="^random.*"))
app.add_handler(CallbackQueryHandler(talk_button, pattern="^talk.*"))
app.add_handler(CallbackQueryHandler(quiz_button, pattern="^quiz.*"))
app.add_handler(CallbackQueryHandler(hello_button))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
