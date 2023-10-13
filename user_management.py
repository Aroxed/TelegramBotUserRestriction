from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot, ChatPermissions, ChatMember
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, CallbackContext

BOT_TOKEN = "YOUR_TOKEN"
# https://api.telegram.org/bot6493901072:AAHD-tBq9Aj7-MEuGiJFw5Eby_lW7sag5pA/getUpdates
CHAT_ID = -1001725069092


async def is_user_admin(update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = CHAT_ID
    chat_member = await context.bot.get_chat_member(chat_id, user_id)
    return chat_member.status in [ChatMember.OWNER, ChatMember.ADMINISTRATOR]


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Allow messaging", callback_data="allowed"),
            InlineKeyboardButton("Restrict messaging", callback_data="restricted"),
        ],

    ]
    if update.effective_chat.id == CHAT_ID:
        await update.message.reply_text("Sorry, this command is not allowed in the chat")
        return

    user_is_admin = await is_user_admin(update, context)
    if user_is_admin:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Sorry, this option is only for admins.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    bot = Bot(token=BOT_TOKEN)
    await bot.restrict_chat_member(CHAT_ID, 6528329113,
                                   ChatPermissions(can_send_messages=query.data == "allowed", can_invite_users=False))
    await query.edit_message_text(text=f"Action applied: {query.data}")


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("begin", begin))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
