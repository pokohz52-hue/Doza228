from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Здесь будем хранить данные пользователей
users_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Пробный тариф", callback_data='trial'),
         InlineKeyboardButton("Купить VPN (15% скидка 🔥)", callback_data='buy')],
        [InlineKeyboardButton("Профиль", callback_data='profile'),
         InlineKeyboardButton("Скоро...", callback_data='soon')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Привет 👋'
        'В CashVPN ты можешь приобрести VPN по низким ценам '
        'или активировать пробный тариф!'
        'Выбирай кнопку ниже ⏬',
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    has_trial_tag = users_data.get(user_id, {}).get('trial_tag', False)
    
    if query.data == 'trial':
        # Если пользователь уже получал пробный тариф — выводим соответствующее сообщение
        if has_trial_tag:
            await query.edit_message_text(text='Извините, вы уже получали демо подписку.')
        else:
            # Иначе даем возможность оплатить 1 рубль для активации пробного тарифа
            trial_keyboard = [[
                InlineKeyboardButton('Оплатить 1 руб.', url="http://t.me/send?start=IVyOwIKIS7Th"),
                InlineKeyboardButton('Проверить оплату', callback_data='check_payment')
            ]]
            
            reply_markup = InlineKeyboardMarkup(trial_keyboard)
            await query.edit_message_text(
                text='Чтобы избежать спама, подтвердите ваш аккаунт.'
                    'Оплатите 1 рубль, после мы выдадим вам на 1 день доступ к VPN.',
                reply_markup=reply_markup
            )
    
    elif query.data == 'check_payment':
        # Ставим пользователю тег БЫЛ после проверки оплаты
        users_data.setdefault(user_id, {})['trial_tag'] = True
        await query.edit_message_text(text='Хорошо, если вы не оплатили, то вы не получите демо VPN,'
                                          'а если оплатите, он уже у вас.')
    
    elif query.data == 'buy':
        # Сначала проверяем, получил ли пользователь пробный тариф
        if not has_trial_tag:
            # Если нет — предлагаем оплатить 1 рубль для подтверждения аккаунта
            buy_keyboard = [[
                InlineKeyboardButton('Оплатить 1 руб.', url="http://t.me/send?start=IVyOwIKIS7Th"),
                InlineKeyboardButton('Проверить оплату', callback_data='check_payment_buy')
            ]]
            
            reply_markup = InlineKeyboardMarkup(buy_keyboard)
            await query.edit_message_text(
                text='Чтобы избежать спама, подтвердите ваш аккаунт.'
                     'Оплатите 1 рубль, после мы откроем полный доступ к покупке VPN.',
                reply_markup=reply_markup
            )
        else:
            # Создаем клавиатуру выбора срока подписки
            vpn_keyboard = [
                [InlineKeyboardButton('30 дней (170 ₽)', url="http://t.me/send?start=IVEOaNCS5RqC")],
                [InlineKeyboardButton('2 месяца (340 ₽)', url="http://t.me/send?start=IVGH1qsOqA2N")],
                [InlineKeyboardButton('3 месяца (500 ₽)', url="http://t.me/send?start=IVSKDwbOm98Y")],
                [InlineKeyboardButton('12 месяцев (2000 ₽)', url="http://t.me/send?start=IVipocGRtZFF")]
            ]
            
            reply_markup = InlineKeyboardMarkup(vpn_keyboard)
            await query.edit_message_text(
                text='Выберите срок подписки:',
                reply_markup=reply_markup
            )
    
    elif query.data == 'check_payment_buy':
        # После проверки оплаты ставим пользователю тег БЫЛ
        users_data.setdefault(user_id, {})['trial_tag'] = True
        await query.edit_message_text(text='Теперь вы можете выбрать срок подписки на VPN.')
    
    elif query.data == 'profile':
        # Информация профиля
        user_id = query.from_user.id
        first_name = query.from_user.first_name
        last_name = query.from_user.last_name or ''
        username = query.from_user.username or ''
        
        profile_info = f'Ваш ID: {user_id}' \
                       f'Имя: {first_name} {last_name}' \
                       f'Username: @{username}'
        await query.edit_message_text(profile_info)
    
    elif query.data == 'soon':
        # Кнопка скоро...
        await query.edit_message_text(text='Эта функция пока недоступна.')

def main():
    application = ApplicationBuilder().token('8579044660:AAFtSIirUYljRe3ctnU4VQMxivEFK7tgi8U').build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    
    application.run_polling()

if __name__ == '__main__':
    main()
