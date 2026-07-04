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

FIXED_TIME = "18:00"

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_name = message.from_user.first_name or "друг"
   
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Выбрать дату встречи"))
   
    bot.send_message(message.chat.id, f"Привет, {user_name}!\n\nДавай выберем дату нашей встречи.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Выбрать дату встречи")
def show_dates(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for key, label in DATES.items():
        markup.add(types.InlineKeyboardButton(label, callback_data=f"date_{key}"))
   
    bot.send_message(message.chat.id, "Выбери удобную дату:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("date_"))
def handle_date(call):
    date_key = call.data.split("_")[1]
    date_label = DATES.get(date_key, date_key)
   
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
   
    bot.send_message(call.message.chat.id, f"Отлично! Жду тебя {date_label} в {FIXED_TIME}.\n\nВот место встречи:")
   
    bot.send_location(call.message.chat.id, latitude=LATITUDE, longitude=LONGITUDE)
   
    maps_text = (
        "🚗 <b>Построить маршрут до места встречи:</b>\n\n"
        f"🔗 <a href='https://www.google.com/maps/dir/?api=1&destination={LATITUDE},{LONGITUDE}'>Google Карты</a>\n"
        f"🔗 <a href='https://yandex.ru/maps/?rtext=\~{LATITUDE},{LONGITUDE}&rtt=auto'>Яндекс Карты</a>"
    )
    bot.send_message(call.message.chat.id, maps_text)
   
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Я приду", callback_data="confirm_yes"),
        types.InlineKeyboardButton("Не смогу", callback_data="confirm_no")
    )
    bot.send_message(call.message.chat.id, "Подтверди, пожалуйста:", reply_markup=markup)
   
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_yes")
def confirm_yes(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
   
    bot.send_message(call.message.chat.id, f"Отлично! Жду тебя в {FIXED_TIME}. До встречи!")

@bot.callback_query_handler(func=lambda call: call.data == "confirm_no")
def confirm_no(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
   
    bot.send_message(call.message.chat.id, "Жаль... Ты не увидишь что я придумал)) Если передумаешь ты знаешь кому написать))")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text != "Выбрать дату встречи":
        bot.send_message(message.chat.id, f"Спасибо! Запомнил твой комментарий:\n\n«{message.text}»")

if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling(skip_pending=True)