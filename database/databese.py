#библиотеки
import sqlite3
from sqlite3 import Error
import logging
import random
from io import BytesIO
from base64 import b64decode as dec64


#подключаем журнал логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s: %(message)s',
    filemode='w'
)
#наш основной класс, описывающий базу данных
class Database:
    #конструктор класса, принимает путь до БД. Выполняется сразу, как вы создаете объект класса
    def __init__(self,db_path):
        self.logger=logging.getLogger('BD')  #прописываем тэг логов, чтобы понимать, что речь о БД
        self.db_path=db_path #передаем полученный путь в глобальную переменную
        # self.db_path = '../../ex.db'  #тут указали путь по умолчанию,потом надо это убрать
        #в блок try помещаем код, который может вызвать ошибку
        try:
            # self.con=sqlite3.connect(self.db_path) #создаем контакт с БД
            self.con=sqlite3.connect('data.db') #создаем контакт с БД
            self.cursorObj = self.con.cursor() #созадем курсор для БД
            self.logger.info("Успешное подключение к БД") #Запись в жарнал логов под уровнем INFO
        #В блок except помещаем инструкции на случай ошибки. В данном случае класс Error писывает все возможные ошибки, связанные с БД
        except Error:
            self.logger.error("Подключение к БД прервано") #Запись в жарнал логов под уровнем ERROR

    #функция создания таблицы пользователей в бд
    def create_user_table(self):
        try:
            #запрос на создание таблицы (если такой таблицы еще нет). столбцы id,user_id,first_name,last_name
            self.cursorObj.execute("CREATE TABLE IF NOT EXISTS Users(id integer PRIMARY KEY, user_id integer NOT NULL,first_name text NOT NULL, last_name text)")
            #отправка результата в бд
            self.con.commit()
            self.logger.info("Таблица пользователей создана")
        except Error:
            self.logger.error("Таблица пользователей не создана")

    #функция для создания таблицы для записи картинок и тегов к ним
    def create_tag_table(self):
        try:
            #запрос на создание. Столбцы id,user_id,img,tag
            self.cursorObj.execute("CREATE TABLE IF NOT EXISTS Image(id integer PRIMARY KEY, user_id integer NOT NULL,img BLOB NOT NULL, tag text NOT NULL)")
            self.con.commit()
            self.logger.info("Таблица картинок создана")
        except Error:
            self.logger.error("Таблица картинок не создана")

#функция записи пользователя в БД, на вход получает словарь из данных о пользователе
    def add_new_user(self,user_info):
        #записываем нужные данные из словаря (по ключу) в локальные переменные
        x=user_info['user_id']
        y=user_info['first_name']
        z=user_info['last_name']
        # если в словаре нет ключа id , то запись не возможна
        if 'id' not in user_info:
            raise KeyError('Ключ не найден')

        try:
            # оправляем запрос на запись в бд, передаем данные
            self.cursorObj.execute('INSERT OR IGNORE INTO Users(user_id,first_name,last_name) VALUES(?,?,?)',(x,y,z))
            self.con.commit()
            self.logger.info("Пользователь добавлен")
        except Error as r:
            self.logger.error("Пользователь не был добавлен",r)

    # функция для записи картинки и тэга в бд
    def add_new_img(self,user_info):
        x=user_info['user_id']
        y=user_info['img']
        z=user_info['tag']

        if 'id' not in user_info:
            raise KeyError('Ключ не найден')

        try:
            self.cursorObj.execute('INSERT OR IGNORE INTO Image(user_id,img,tag) VALUES(?,?,?)',(x,y,z))
            self.con.commit()
            self.logger.info("Картинка  добавлена")
        except Error as r:
            self.logger.error("Картинка не была добавлена",r)

    # функция для получения всех данных из таблицы. На вход приходит имя таблицы
    def get_all_records(self,table_name):
        try:
            # запрос на выбор всех данных из таблицы по текущему имени
            self.cursorObj.execute('SELECT *FROM 'f'{table_name}''')
            # запись результата в переменную в виде списка
            all_result=self.cursorObj.fetchall()
            print(all_result)
        except Error:
            self.logger.error("Результат не получен")

    # функция для получения всех пользователей из бд
    def all_users(self):
        try:
            # запрос по таблице Users и столбцу user_id
            self.cursorObj.execute('SELECT user_id, name FROM  Users')
            # запись результата в переменную в виде списка
            user_result = self.cursorObj.fetchall()
            print(user_result)
            # возвращаем список из данных
            return user_result
        except Error:
            self.logger.error("Результат не получен")

    # функция для удаления таблицы . На вход получаем имя таблицы
    def drop_table(self,table_name):
        try:
            # запрос на удаление таблицы по текущему имени
            self.cursorObj.execute('DROP table if exists 'f'{table_name}''')
            self.logger.info('Таблица удалена 'f'{table_name}''')
        except Error:
            self.logger.error('Удаление прервано 'f'{table_name}''')

    # функция, которая достает картинку из бд по тэгу
    def get_image_by_tag(self,tag):
        try:
            # делаем запрос и ищем текущий тэг
            self.cursorObj.execute("SELECT img FROM Image WHERE tag=?", (tag,))
            # записываем результат в переменную в виде списка
            rez = self.cursorObj.fetchall()
            # если рузультат пустой
            if not rez:
                self.logger.info('Таких тэгов нет в БД')
                # возвращаем False
                return False
            else:
                self.logger.info('Результаты по тэгу есть')
                # иначе надо выбрать 1 из списка
                capture=rez[random.randint(0,len(rez)-1)]
                #возвращаем полученную запись
                return capture[0]
        except:
            self.logger.error('Подключение к БД прервано из за картинки')


        # функция, которая проверяет записан ли пользователь в бд. На вход получаем id пользователя
    def firstSeen(self, get_id):
            try:
                # делаем запрос и ищем текущий id
                self.cursorObj.execute("SELECT id FROM Users WHERE user_id=?", (get_id,))
                # записываем результат в переменную
                rez = self.cursorObj.fetchall()

                # если рузультат пустой
                if not rez:
                    self.logger.info('Пользавателя нет в БД')
                    # возвращаем True
                    return True
                else:
                    self.logger.info('Пользаватель уже в БД')
                    # иначе пользователь уже был записан в бд. Возвращаем False
                    return False
            except:
                self.logger.error('Подключение к БД прервано')


