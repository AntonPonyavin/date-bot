#!/usr/bin/env python3
"""
Telegram-бот для свидания
"""

import telebot
from telebot import types
import os

TOKEN = os.environ.get("TOKEN")

bot = telebot.TeleBot(TOKEN)

LATITUDE = 56.191175
LONGITUDE = 47.707693

DATES = {
    "12.07": "12 июля",
    "19.07": "19 июля",
    "26.07": "26 июля",
    "02.08": "2 августа"
}

@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message):
    user_name = message.from_user.first_name or "друг"
   
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Выбрать дату встречи"))
   
    text = (
        f"Привет, {user_name}!\n\n"
        "Давай выберем удобную дату нашей встречи.\n"
        "Нажми кнопку ниже."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def cmd_help(message: types.Message):
    bot.send_message(
        message.chat.id,
        "Нажми «Выбрать дату встречи» → выбери день → при желании добавь комментарий → подтверди."
    )

@bot.message_handler(func=lambda m: m.text == "Выбрать дату встречи")
def show_dates(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2)
   
    buttons = []
    for key, label in DATES.items():
        btn = types.InlineKeyboardButton(label, callback_data=f"date_{key}")
        buttons.append(btn)
   
    markup.add(*buttons)
   
    bot.send_message(
        message.chat.id,
        "Выбери удобную дату нашей встречи:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("date_"))
def handle_date_selection(call: types.CallbackQuery):
    date_key = call.data.split("_")[1]
    date_label = DATES.get(date_key, date_key)
   
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
   
    bot.send_message(
        call.message.chat.id,
        f"Отлично! Жду тебя {date_label}.\n\nВот место встречи:"
    )
   
    bot.send_location(call.message.chat.id, latitude=LATITUDE, longitude=LONGITUDE)
   
    maps_text = (
        "Место встречи:\n\n"
        f"Google Карты: https://www.google.com/maps?q={LATITUDE},{LONGITUDE}\n"
        f"Яндекс Карты: https://yandex.ru/maps/?ll={LONGITUDE},{LATITUDE}&z=17"
    )
    bot.send_message(call.message.chat.id, maps_text)
   
    skip_markup = types.InlineKeyboardMarkup()
    skip_markup.add(types.InlineKeyboardButton("Пропустить", callback_data="skip_comment"))
   
    bot.send_message(
        call.message.chat.id,
        "Хочешь добавить комментарий к встрече? Напиши его сейчас или нажми «Пропустить».",
        reply_markup=skip_markup
    )
   
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "skip_comment")
def skip_comment(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
   
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
   
    show_confirmation_buttons(call.message.chat.id)

def show_confirmation_buttons(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Я приду", callback_data="confirm_yes"),
        types.InlineKeyboardButton("Не смогу", callback_data="confirm_no")
    )
   
    bot.send_message(
        chat_id,
        "Подтверди, пожалуйста:",
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def handle_text(message: types.Message):
    if message.text != "Выбрать дату встречи":
        bot.send_message(
            message.chat.id,
            f"Спасибо! Я запомнил твой комментарий:\n\n«{message.text}»"
        )
        show_confirmation_buttons(message.chat.id)
    else:
        show_dates(message)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_yes")
def confirm_yes(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
   
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
   
    bot.send_message(
        call.message.chat.id,
        "Отлично! Жду тебя. До встречи!"
    )

@bot.callback_query_handler(func=lambda call: call.data == "confirm_no")
def confirm_no(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
   
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
   
    bot.send_message(
        call.message.chat.id,
        "Жаль... Если передумаешь, просто нажми /start и выбери другую дату. Я буду здесь."
    )

if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling(skip_pending=True)