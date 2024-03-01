from aiogram import Bot, types


async def send_message_cron(bot:Bot,message: types.Message):
    await bot.send_message(message.from_user.id,"Привет сейчас 20:00?")