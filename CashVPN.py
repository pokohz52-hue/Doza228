import asyncio
from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "8579044660:AAFtSIirUYljRe3ctnU4VQMxivEFK7tgi8U"
ADMIN_CHAT_ID = "@MrFixTop"

users_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Пробный тариф", callback_data='trial'),
            InlineKeyboardButton("Купить VPN (15% скидка 🔥)", callback_data='buy')
        ],
        [
            InlineKeyboardButton("Профиль", callback_data='profile'),
            InlineKeyboardButton("Скоро...", callback_data='soon')
        ],
        [
            InlineKeyboardButton("О боте", callback_data='about_bot')
        ]
    ]

    await update.message.reply_text(
        "Привет 👋\n\n"
        "В CashVPN ты можешь приобрести VPN по низким ценам\n"
        "или активировать пробный тариф!\n\n"
        "Выбирай кнопку ниже ⏬",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    users_data.setdefault(user_id, {})
    has_trial_tag = users_data[user_id].get('trial_tag', False)

    if query.data == 'trial':
        if has_trial_tag:
            await query.edit_message_text("❌ Вы уже получали демо подписку.")
        else:
            trial_keyboard = [[
                InlineKeyboardButton('Оплатить 1 руб.', url="http://t.me/send?start=IVyOwIKIS7Th"),
                InlineKeyboardButton('Проверить оплату', callback_data='check_payment')
            ]]

            await query.edit_message_text(
                "Подтвердите аккаунт платёжом 1 рубль.",
                reply_markup=InlineKeyboardMarkup(trial_keyboard)
            )

    elif query.data == 'check_payment':
        users_data[user_id]['trial_tag'] = True
        await query.edit_message_text("✅ Оплата успешно зарегистрирована!")

    elif query.data == 'buy':
        if not has_trial_tag:
            buy_keyboard = [[
                InlineKeyboardButton('Оплатить 1 руб.', url="http://t.me/send?start=IVyOwIKIS7Th"),
                InlineKeyboardButton('Проверить оплату', callback_data='check_payment_buy')
            ]]

            await query.edit_message_text(
                "Оплатите 1 рубль для подтверждения аккаунта.",
                reply_markup=InlineKeyboardMarkup(buy_keyboard)
            )
        else:
            vpn_keyboard = [
                [InlineKeyboardButton('30 дней (170 ₽)', url="http://t.me/send?start=IVEOaNCS5RqC")],
                [InlineKeyboardButton('2 месяца (340 ₽)', url="http://t.me/send?start=IVGH1qsOqA2N")],
                [InlineKeyboardButton('3 месяца (500 ₽)', url="http://t.me/send?start=IVSKDwbOm98Y")],
                [InlineKeyboardButton('12 месяцев (2000 ₽)', url="http://t.me/send?start=IVipocGRtZFF")]
            ]

            await query.edit_message_text(
                "Выберите тариф VPN:",
                reply_markup=InlineKeyboardMarkup(vpn_keyboard)
            )

    elif query.data == 'check_payment_buy':
        users_data[user_id]['trial_tag'] = True
        await query.edit_message_text("✅ Теперь вы можете выбрать срок подписки.")

    elif query.data == 'profile':
        first_name = query.from_user.first_name or ""
        last_name = query.from_user.last_name or ""
        username = query.from_user.username or "не указан"

        profile_info = (
            f"👤 Ваш профиль\n\n"
            f"🆔 ID: {user_id}\n"
            f"📛 Имя: {first_name} {last_name}\n"
            f"🔗 Username: @{username}\n"
            f"🎟 Пробный доступ: {'Да' if has_trial_tag else 'Нет'}"
        )

        await query.edit_message_text(profile_info)

    elif query.data == 'soon':
        await query.edit_message_text("⏳ Эта функция временно недоступна.")

    elif query.data == 'about_bot':
        await query.edit_message_text(
            "📜 Правила использования бота:\n\n"
            "1. Запрещённые цели — блокировка.\n"
            "2. VPN на одно устройство.\n"
            "3. Доп. подключения оплачиваются отдельно."
        )


async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    report = f"📊 Отчёт:\nПользователей: {len(users_data)}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report)


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    job_queue = application.job_queue
    job_queue.run_repeating(send_daily_report, interval=timedelta(days=1), first=10)

    application.run_polling()


if __name__ == "__main__":
    main()