import json
import os
from typing import Optional, Tuple

from telegram import ChatMember, ChatMemberUpdated, Update, ChatPermissions
from telegram.constants import ParseMode
from telegram.ext import (ApplicationBuilder)
from telegram.ext import (
    ChatMemberHandler,
    ContextTypes,
)

MIN_INVITES = 3
invites = {}
file_name = os.getcwd() + '/invites.json'
if os.path.exists(file_name):
    with open(file_name, "r") as f:
        invites = json.load(f)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    if chat_member_update is None:
        return None
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets new users in chats and announces when someone leaves"""

    if update.effective_user.is_bot:
        return

    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        await update.effective_chat.send_message(
            f"{member_name} was added. Welcome! {member_name}, please add {MIN_INVITES} "
            f"friends and then you can post messages",
            parse_mode=ParseMode.HTML,
        )

        from_user = await context.bot.get_chat_member(chat_id=update.effective_chat.id,
                                                      user_id=update.chat_member.from_user.id)

        if is_member:
            await context.bot.restrict_chat_member(update.effective_chat.id, update.chat_member.new_chat_member.user.id,
                                                   ChatPermissions(can_send_messages=False, can_invite_users=True))
            if from_user.status != 'creator':
                if str(update.chat_member.from_user.id) not in invites:
                    invites[str(update.chat_member.from_user.id)] = 0
                invites[str(update.chat_member.from_user.id)] += 1

                if update.chat_member.from_user.id != update.chat_member.new_chat_member.user.id:
                    if invites[str(update.chat_member.from_user.id)] >= MIN_INVITES:
                        await context.bot.restrict_chat_member(update.effective_chat.id,
                                                               update.chat_member.from_user.id,
                                                               ChatPermissions(can_send_messages=True,
                                                                               can_invite_users=True))

                with open(file_name, "w") as file:
                    json.dump(invites, file)


token = "YOUR_TOKEN"

app = ApplicationBuilder().token(token).build()

app.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))
app.run_polling(allowed_updates=Update.ALL_TYPES)
