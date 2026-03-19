import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InputMediaPhoto,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

# -----------------------------
# НАСТРОЙКИ
# -----------------------------
TOKEN = "8675138964:AAGICCaxVGG3yTa6xhLZg6XRdVQgu_p7hOM"
ADMIN_ID = 5697252704
CHANNEL_ID = -1003859717806

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# -----------------------------
# СОСТОЯНИЯ
# -----------------------------
class PostState(StatesGroup):
    waiting_for_post = State()

class RejectState(StatesGroup):
    waiting_for_reason = State()

# -----------------------------
# ТЕКСТЫ
# -----------------------------
INFO_TEXT = (
    "📜️ Инфа\n\n"
    "ЭЙ-Й-Й-Й ЧУВАК! Я бедный крестьянен поимени @Ran3goka, я создал Бота и фан клуб честь моего императора "
    "https://t.me/VM1_Story чтобы на фармить злата на хлебушек.\n"
    "Этот фан клуб чисто для смешнявки, НИКАКОЙ ЭРОТИКИ!! Или всё же нет🤔\n\n"
    "Если что-то не так пишите: @Ran3goka"
)

REJECT_TEMPLATE = (
    "Эээээй дружок, твой пост полная хуйня.\n"
    "Причина: {reason}"
)

APPROVE_TEXT = "✅ Твой пост одобрен и отправлен на канал!"

# -----------------------------
# КНОПКИ
# -----------------------------
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📤 Отправить работу")],
            [KeyboardButton(text="🖼 Фото Всеволода")],
            [KeyboardButton(text="📜️ Инфа")],
            [KeyboardButton(text="📌 Пример работы")],
        ],
        resize_keyboard=True
    )

cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_post")]
    ]
)

def moderation_kb(user_id: int, chat_id: int, message_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✔️ Опубликовать",
                    callback_data=f"approve:{user_id}:{chat_id}:{message_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject:{user_id}:{chat_id}:{message_id}"
                ),
            ]
        ]
    )

# -----------------------------
# /start
# -----------------------------
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer_photo(
        photo="https://cdn.discordapp.com/attachments/1434894166160183296/1484259747652964415/1f97353ec1321fe8.png?ex=69bd941c&is=69bc429c&hm=18e6666b459727e8b544ab82fa26b80e9260db76fbb4e3a92f7a0b21ebd7085e",
        caption=(
            "Приветик, это ВаноефБОТ!\n\n"
            "БОТ только свежий так что в бота ВОЗМОЖНО будут добовлятся новые плюшки.\n"
            "Тут ты можешь:\n"
            "• 📤 Отправлять свой мемы\n"
            "• 🖼 Взять фотку со мной\n"
            "• 📜 Узнать... ЧТО-ТО!"
        ),
        reply_markup=main_menu_kb()
    )

# -----------------------------
# КНОПКИ МЕНЮ
# -----------------------------
@dp.message(F.text == "📜️ Инфа")
async def info_btn(message: Message):
    await message.answer(INFO_TEXT)

@dp.message(F.text == "📌 Пример работы")
async def example_btn(message: Message):
    await refens_cmd(message)

@dp.message(F.text == "🖼 Фото Всеволода")
async def photo_btn(message: Message):
    await image_cmd(message)

@dp.message(F.text == "📤 Отправить работу")
async def send_work_btn(message: Message, state: FSMContext):
    await post_cmd(message, state)

# -----------------------------
# КОМАНДА /post
# -----------------------------
@dp.message(Command("post"))
async def post_cmd(message: Message, state: FSMContext):
    await message.answer(
        "Окей, кидай сюда свою работу (фото, видео).\n"
        "ТОЛЬКО сначала поглянь на команду Пример работы, отмени и посмотри перед тем как кидать!",
        reply_markup=cancel_kb
    )
    await state.set_state(PostState.waiting_for_post)

# -----------------------------
# ОТМЕНА ОТПРАВКИ
# -----------------------------
@dp.callback_query(F.data == "cancel_post")
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Отправка отменена.")
    await state.clear()

# -----------------------------
# ПРИЁМ РАБОТЫ
# -----------------------------
@dp.message(PostState.waiting_for_post)
async def receive_post(message: Message, state: FSMContext):
    user_id = message.from_user.id
    sender = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    # Формируем подпись
    caption = f"Новая работа от {sender}"
    if message.caption:
        caption += f"\nКомментарий: {message.caption}"

    # Определяем тип сообщения
    if message.photo:
        await bot.send_photo(
            ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
            reply_markup=moderation_kb(user_id, message.chat.id, message.message_id)
        )

    elif message.video:
        await bot.send_video(
            ADMIN_ID,
            video=message.video.file_id,
            caption=caption,
            reply_markup=moderation_kb(user_id, message.chat.id, message.message_id)
        )

    elif message.document:
        await bot.send_document(
            ADMIN_ID,
            document=message.document.file_id,
            caption=caption,
            reply_markup=moderation_kb(user_id, message.chat.id, message.message_id)
        )

    elif message.text:
        await bot.send_message(
            ADMIN_ID,
            f"{caption}\n\nТекст:\n{message.text}",
            reply_markup=moderation_kb(user_id, message.chat.id, message.message_id)
        )

    else:
        await bot.send_message(
            ADMIN_ID,
            f"{caption}\n⚠️ Неизвестный тип сообщения",
            reply_markup=moderation_kb(user_id, message.chat.id, message.message_id)
        )

    await message.answer("✅ Твоя работа проверяется!")
    await state.clear()

# -----------------------------
# ОДОБРЕНИЕ
# -----------------------------
@dp.callback_query(F.data.startswith("approve:"))
async def approve_post(callback: CallbackQuery):
    _, user_id_str, chat_id_str, msg_id_str = callback.data.split(":")
    user_id = int(user_id_str)
    from_chat_id = int(chat_id_str)
    original_message_id = int(msg_id_str)

    await bot.copy_message(
        chat_id=CHANNEL_ID,
        from_chat_id=from_chat_id,
        message_id=original_message_id
    )

    try:
        await bot.send_message(user_id, APPROVE_TEXT)
    except:
        pass

    await callback.message.edit_text("✅ Пост проверян и отправлен в канал.")
    await callback.answer()

# -----------------------------
# ОТКЛОНЕНИЕ
# -----------------------------
@dp.callback_query(F.data.startswith("reject:"))
async def reject_post(callback: CallbackQuery, state: FSMContext):
    _, user_id_str, chat_id_str, msg_id_str = callback.data.split(":")
    user_id = int(user_id_str)

    await state.update_data(reject_user_id=user_id)

    await callback.message.answer("Напиши причину отказа для этого поста.")
    await callback.answer()
    await state.set_state(RejectState.waiting_for_reason)

# -----------------------------
# ПРИЧИНА ОТКАЗА
# -----------------------------
@dp.message(RejectState.waiting_for_reason)
async def receive_reject_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reject_user_id")

    reason = message.text.strip()
    text_to_user = REJECT_TEMPLATE.format(reason=reason)

    try:
        await bot.send_message(user_id, text_to_user)
    except:
        pass

    await message.answer("❌ Отказ отправлен пользователю.")
    await state.clear()

# -----------------------------
# ПРИМЕР РАБОТЫ
# -----------------------------
@dp.message(Command("refens"))
async def refens_cmd(message: Message):
    await message.answer_photo(
        photo="https://cdn.discordapp.com/attachments/1434894166160183296/1484282488627925023/42d1ccb6a1ef3af3.png?ex=69bda949&is=69bc57c9&hm=e5eb2e8b860110f7900aed0097b5f1bbc04bbe7de97e46f8077e7c1207fdcc97",
        caption="НИФИГА СЕБЕ ВАНОЕФ ПОБЕЛЕЛ!!! (Комнтарий, желательно).\n"
        "Автор: АнтонКрасный (Автор, не обезательно)."
    )

# -----------------------------
# ФОТО ВСЕВОЛОДА
# -----------------------------
@dp.message(Command("image"))
async def image_cmd(message: Message):
    photos = [
        "https://cdn.discordapp.com/attachments/1434894166160183296/1484270595012034761/image.png?ex=69bd9e36&is=69bc4cb6&hm=34a7c7a19f2d54c0a30fc8e6c4423ddaffcd82924bb1c85eaa2a2280093d3fab&",
        "https://cdn.discordapp.com/attachments/1434894166160183296/1484270759802310736/image.png?ex=69bd9e5d&is=69bc4cdd&hm=5c963a612185bf78bf2bd37e9514cb647912def5a3ce77698109ab51b8313a55&",
        "https://cdn.discordapp.com/attachments/1434894166160183296/1484270816148324473/image.png?ex=69bd9e6a&is=69bc4cea&hm=64ac92a82c1f1d30cd22652095966b46a52e9ba91453f28c9c4ec25d65c8ee23&",
        "https://cdn.discordapp.com/attachments/1434894166160183296/1484271134278160505/image.png?ex=69bd9eb6&is=69bc4d36&hm=01e148fe9dd5c4e47cef91cd76d88d5efcfabc4381d01eed3d82a1a76dcda2de&",
        "https://cdn.discordapp.com/attachments/1434894166160183296/1484271431146536961/image.png?ex=69bd9efd&is=69bc4d7d&hm=92d73e889ffa2ab65e0e0b99410d22298bc21a226fcc51d7a1c049933fef964a&"
    ]

    media = [InputMediaPhoto(media=url) for url in photos]
    await message.answer_media_group(media)

# -----------------------------
# ЗАПУСК
# -----------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

