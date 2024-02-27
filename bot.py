import asyncio
import logging

import aioschedule
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor

from config.config import TOKEN
from constants.settings import DB_DATA, ROOT_DIR
from database.databese import Database
from io import BytesIO
from base64 import b64decode as dec64

#заводим журнал логов с тэгом
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Bot_')

#создаем объект бота с определенным токеном
bot = Bot(token=TOKEN)#,proxy='http://10.128.0.90:8080')
#создаем объект диспетчера
dp = Dispatcher(bot)

#создаем объект базы данных и передаем путь до места ее сохранения
DB=Database(db_path=DB_DATA)

#функция на случай если надо удалить какую-то из таблиц
#DB.drop_table('Users')
#DB.drop_table('Image')

#создаем таблицы
DB.create_user_table()
DB.create_tag_table()



#функция для записи информации в словарь для бд,
# на вход принимает обязательно сообщение от пользователя и бд
# и не обязательно картинку и тэг
def add_info_to_db(message,DB,tag=None,img=None):
    #это словарь
    info_dir={'id': message.from_user.id,
              'user_id': message.from_user.id,
              'first_name': message.from_user.first_name,
              'last_name': message.from_user.last_name,
              'img':img,
              'tag':tag}

    #вызов функций для записи в таблицы
    DB.add_new_user(user_info=info_dir)
    DB.add_new_img(user_info=info_dir)
    #вызов функции для распечатки результатов из таблицы пользователей
    # (нужна только для отладки)
    DB.get_all_records(table_name='Users')
    # DB.get_image_by_tag('cat')

#функция для преобрахования картинки в двоичный формат
def convert_to_binary_data(filename):
        # Преобразование данных в двоичный формат
        with open(filename, 'rb') as file:
            blob_data = file.read()
        return blob_data

#функция для преобразования двоичного формата в картинку
def confert_to_img_file(bin):
    image=BytesIO(dec64(bin))
    return image
async def start_mailing():  # Функция рассылки
    for i in DB.all_users():
        print(i,i[1])
        try:
            await bot.send_message(chat_id=i[1],text="ПРИВЕТ")#photo=(confert_to_img_file(DB.get_image_by_tag(i[-1]))))
        except:
            pass

async def scheduler():
    aioschedule.every(1).minutes.do(start_mailing)  # Тут говорим, что рассылка будет раз в день, отсчет начинается с момента запуска кода
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
async def onstart(_):
    asyncio.create_task(scheduler())
#хэндлер для обработки команды старт
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Тут ты можешь просматривать картинки по категориям.")
    #проверяем записан ли пользователь в бд, если нет, то записываем
    if not DB.firstSeen(message.from_user.id):
        await message.reply("С возвращением!")
    else:
        add_info_to_db(message,DB)
        await message.reply("Приятно познакомиться!!")

#хэндлер для обработки команды загрузка
@dp.message_handler(commands=['download'])
async def process_start_command(message: types.Message):
    await message.reply("Отправьте фото для загрузки в базу данных")
    await message.reply("Отправьте tag, которым можно описать данную фотографию")
    add_info_to_db(message,DB)




#хэндлер для обработки некоторых слов, поступающих от пользователя
@dp.message_handler()
async def hello_response(msg: types.Message):
    if 'привет' in msg.text.lower():
        await bot.send_message(msg.from_user.id, f"Здравствуй, {msg.from_user.first_name}!")
        # await bot.send_sticker(msg.chat.id, sticker=stickers["Puppy"])
    elif 'пока' in msg.text.lower():
        await bot.send_message(msg.from_user.id, f"Прощай, {msg.from_user.first_name}!")
        # await bot.send_sticker(msg.chat.id, sticker=stickers["Sad"])
    elif 'до свидания' in msg.text.lower():
        await bot.send_message(msg.from_user.id, f"До новых встреч, {msg.from_user.first_name}!")

    #если получили слово в формате tag:кактой-то_тэг
    elif 'tag' in msg.text.lower():
        #разделяем слово по :
        tag_split=msg.text.split(':')
        #из полученного списка записываем 1 элемент
        tag=str(tag_split[1])
        #пишем в бд
        add_info_to_db(msg,DB,tag,convert_to_binary_data('img.png'))
        await bot.send_message(msg.from_user.id,"Фото загружено! Спасибо!")

    elif 'cat' in msg.text.lower():
        if DB.get_image_by_tag('cat')==False:
            await bot.send_message(msg.from_user.id, "Нет результата")
        else:
            photo=confert_to_img_file(DB.get_image_by_tag('cat'))
            with open('pr.png', 'wb') as file:
                file.write(DB.get_image_by_tag('cat'))
            photo1 = InputFile("pr.png")
            await bot.send_photo(chat_id=msg.chat.id, photo=photo1)


#хэндлер для обработки фото, полученного от пользователя
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def fileHandle(message: types.Message):
    await message.reply(text='файл получен...')
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "img.png")
    await bot.send_message(message.from_user.id, "Отправьте tag в формате tag:ваш_tag")


    # file_info = await bot.get_file(message.photo[-1].file_id)
    # await message.photo[-1].download(file_info.file_path.split('img.png')[1])




#это конец файла!!!!!
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
