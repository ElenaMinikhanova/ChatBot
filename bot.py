from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, MessageHandler, filters, CommandHandler

from gpt import *
from util import *
from credentials import *
import openai
import asyncio

count = 0


# декоратор для обработки ошибок работы токена
def my_decorator(func):
    async def wrapper(update, context):
        try:
            await func(update, context)
        except openai.AuthenticationError:
            await  send_text(update, context, "Ошибка токена")
        except openai.APIConnectionError:
            await  send_text(update, context, "Нет GPT токена")
        except openai.RateLimitError:
            await  send_text(update, context, "Ошибка токена")

    return wrapper


# декоратор создания пароля бота
def my_decorator1(func):
    async def wrapper1(update, context):
        global count
        if password.mode == "password":
            await func(update, context)
        else:
            password.mode = update.message.text
            await asyncio.wait_for(send_text(update, context, "🔐"), timeout=1)
            if password.mode == "password":
                await send_text(update, context, "Пароль верный, можете пользоваться ботом")
            elif count == 0:
                await send_text(update, context, "Введите пароль: ")
                count += 1
            else:
                await send_text(update, context, "Пароль не верный, попробуйте еще раз")
                await send_text(update, context, "Введите пароль: ")
                count += 1

    return wrapper1


# главное меню бота
@my_decorator1
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
        'quiz': 'Поучаствовать в квизе ❓',
        'translation': 'Переводчик 🌍'
        # Добавить команду в меню можно так:
        # 'command': 'button text'
    })


# рандомный факт от чата gpt
@my_decorator1
@my_decorator
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


# общение с чатом gpt на любую тему
@my_decorator1
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "gpt"
    text = load_message('gpt')
    prompt = load_prompt("gpt")
    await send_image(update, context, 'gpt')
    await send_text(update, context, text)
    chat_gpt.set_prompt(prompt)


@my_decorator
async def gpt_dialog(update, context):
    dialog.mode = "gpt"
    text = update.message.text
    answer = await  chat_gpt.add_message(text)
    await  send_text(update, context, answer)


# викторина с чатом gpt
@my_decorator1
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "quiz"
    text1 = load_message("quiz")
    await send_image(update, context, "quiz")
    await send_text_buttons(update, context, text1, {
        "quiz_1": "Тема: История России",
        "quiz_2": "Тема: Гарри Поттер",
        "quiz_3": "Тема: Фильмы"})


async def quiz_button_button(update, context):
    dialog.mode = "quiz"
    text1 = load_message("quiz")
    await send_image(update, context, "quiz")
    await send_text_buttons(update, context, text1, {
        "quiz_11": "Тема: История России",
        "quiz_22": "Тема: Гарри Поттер",
        "quiz_33": "Тема: Фильмы"})


@my_decorator
async def quiz_button(update, context):
    dialog.mode = "quiz"
    query = update.callback_query.data
    if query == "quiz_1" or query == "quiz_2" or query == "quiz_3":
        await  update.callback_query.answer()
        await  send_text(update, context, "Ответь на вопрос: ")
        prompt = load_prompt("quiz")
        chat_gpt.set_prompt(prompt)
        answer = await  chat_gpt.add_message(query)
        await  send_text(update, context, answer)
    elif query == "quiz_11" or query == "quiz_22" or query == "quiz_33":
        await  update.callback_query.answer()
        await  send_text(update, context, "Ответь на вопрос: ")
        answer = await  chat_gpt.add_message(query)
        await  send_text(update, context, answer)
    elif query == "quiz_more":
        await  update.callback_query.answer()
        await  send_text(update, context, "Ответь на вопрос: ")
        answer = await  chat_gpt.add_message(query)
        await  send_text(update, context, answer)
    elif query == "quiz_new":
        await quiz_button_button(update, context)
    elif query == "quiz_start":
        await start(update, context)


@my_decorator
async def quiz_dialog(update, context):
    dialog.mode = "quiz"
    text = update.message.text
    answer = await  chat_gpt.add_message(text)
    await  send_text(update, context, answer)
    await send_text_buttons(update, context, "Продолжим?", {
        "quiz_more": "Вопрос на ту же тему",
        "quiz_new": "Выбор новой темы",
        "quiz_start": "Выход из Квиза"})


# общение с известной личностью
@my_decorator1
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "talk"
    text = load_message("talk")
    await send_image(update, context, "talk")
    await send_text_buttons(update, context, text, {
        "talk_cobain": "Курт Кобейн",
        "talk_hawking": "Стивен Хокинг",
        "talk_nietzsche": "Фридрих Ницше",
        "talk_queen": "Королева Елизавета II",
        "talk_tony_stark": "Тони Старк"})


@my_decorator
async def talk_dialog(update, context):
    dialog.mode = "talk"
    text = update.message.text
    answer = await  chat_gpt.add_message(text)
    await  send_text(update, context, answer)


@my_decorator
async def talk_button(update, context):
    dialog.mode = "talk"
    query = update.callback_query.data
    await  update.callback_query.answer()
    await  send_image(update, context, query)
    await  send_text(update, context, "Отличный выбор! Можешь начать диалог.")
    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)


# переводчик
@my_decorator1
async def translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "translation"
    text1 = load_message("translation")
    await send_image(update, context, "translation")
    await send_text_buttons(update, context, text1, {
        "translation_en": "Перевод с английского языка на русский",
        "translation_ru": "Перевод с русского языка на английский"})


@my_decorator
async def translation_button(update, context):
    dialog.mode = "translation"
    query = update.callback_query.data
    if query == "translation_en":
        prompt = load_prompt(query)
        chat_gpt.set_prompt(prompt)
        await  send_text(update, context, "Напиши текст на английском языке: ")
    elif query == "translation_ru":
        prompt = load_prompt(query)
        chat_gpt.set_prompt(prompt)
        await  send_text(update, context, "Напиши текст на русском языке: ")
    elif query == "translation_no":
        await  send_text(update, context, "Напиши новый текст: ")
    elif query == "translation_yes":
        await translation(update, context)
    elif query == "translation_start":
        await start(update, context)


@my_decorator
async def translation_dialog(update, context):
    dialog.mode = "translation"
    text = update.message.text
    answer = await  chat_gpt.add_message(text)
    await  send_text(update, context, answer)
    await send_text_buttons(update, context, "Поменять язык перевода?", {
        "translation_yes": "Да",
        "translation_no": "Нет",
        "translation_start": "Выход"
    })


@my_decorator1
async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "random":
        await random(update, context)
    elif dialog.mode == "talk":
        await talk_dialog(update, context)
    elif dialog.mode == "quiz":
        await quiz_dialog(update, context)
    elif dialog.mode == "translation":
        await translation_dialog(update, context)
    else:
        await send_text(update, context, "Привет")
        await send_image(update, context, "avatar_main")
        await send_text_buttons(update, context, "Запустить процесс", {
            "start": "Запустить",
            "stop": "Остановить"})


async def hello_button(update, context):
    query = update.callback_query.data
    if query == "start":
        await start(update, context)
    else:
        await  send_text(update, context, "Процесс остановлен")


dialog = Dialog()
dialog.mode = None

password = Password()
password.mode = None

chat_gpt = ChatGptService(token=ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(CommandHandler("translation", translation))

app.add_handler(CallbackQueryHandler(random_button, pattern="^random_.*"))
app.add_handler(CallbackQueryHandler(talk_button, pattern="^talk_.*"))
app.add_handler(CallbackQueryHandler(quiz_button, pattern="^quiz_.*"))
app.add_handler(CallbackQueryHandler(translation_button, pattern="^translation_.*"))
app.add_handler(CallbackQueryHandler(hello_button))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
