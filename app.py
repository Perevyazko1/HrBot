from aiogram import types, Dispatcher
# __________последние изменения
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ContentType, Message
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
import admins_id
from aiogram.types import ReplyKeyboardRemove
import markups as nav
import sqlite3 as sq
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
storage = MemoryStorage()
import qwestions
import re

bot = Bot(token='5199442094:AAHw7yUztLU981nH7CerRxTOO-sL-c7ZF6s')


dp = Dispatcher(bot, storage=storage)

def clear_text(a):
    a = str(a)
    a = re.sub(r"[',)(]", "", a)
    return a

@dp.message_handler(commands="start")
async def start(message: types.Message):
    # chat_id = message.chat.id
    # text = f'Привет {message.from_user.full_name} нажми на кнопку Старт'
    await message.answer(f'Привет {message.from_user.full_name} \n\n' '<i>Выбери кнопку в меню.</i>',
                          parse_mode=types.ParseMode.HTML,reply_markup=nav.mainMenu)
    sql_start('CREATE TABLE IF NOT EXISTS profile(name TEXT, idname INTEGER PRIMARY KEY, contact TEXT)')
    sql_start('CREATE TABLE IF NOT EXISTS video( number_qwestion TEXT, video TEXT, idprofile INTEGER )')
    sql_start('CREATE TABLE IF NOT EXISTS qwestions( number INTEGER PRIMARY KEY, qwes TEXT)')


#____________________admimenu_____________
@dp.message_handler(commands="adminmenu")
async def admin(message: types.Message):
    text = f'Привет админ {message.from_user.full_name}'
    await message.answer(text=text, reply_markup=nav.admin_menu)
name = ""
bodynowqwestion =""
# ______________________________________отправка видео__________________________________________________
class FSMget_name(StatesGroup): #сохранение запрашиваемого имени в машину состояния
    profile = State()

@dp.message_handler(commands="Получить_видеоответы", state=None)
async def get_name(message: types.Message):

    await FSMget_name.profile.set()
    await message.answer('Введите имя интервьюиромого')
#
@dp.message_handler(state=FSMget_name.profile)
async def load_name_profile(message: types.Message, state: FSMContext):
    if message.text == '/Получить_видеоответы':
        await message.answer(f'<i>Нужно было ввести Имя и Фамилию.</i>\n\n'
                             f' <i>Можешь заново нажать кнопку и</i>\n\n'
                             f' <i>ввести Имя и Фамилию</i>',parse_mode=types.ParseMode.HTML)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['getname'] = message.text
        await message.reply('Имя и фамилия приняты')
        await get_video(state)  # выводил в базу
        await state.finish()


async def get_video(state): # вставка имени в запрос sql
    global base, cur
    base = sq.connect('data.db')
    cur = base.cursor()
    async with state.proxy() as data:
        # await message.reply(str(data))
        profile = str(tuple(data.values()))[2:-3]
        print(profile)

        reqwest = f"select *,(select profile.name from profile where profile.idname=video.idprofile)as new from video where new like '{profile}'"
        bodyreqwest = None
        bodyreqwest = cur.execute(reqwest).fetchall()

        if not bodyreqwest:
            await bot.send_message(admins_id.id_admin, 'Но имя не найдено.', reply_markup=nav.admin_menu)
            test=cur.execute(f"select * from profile where name like '{profile}'").fetchall()
            print(test)
        else:
            for getv in cur.execute(reqwest).fetchall():
                print(getv)
                await bot.send_video(admins_id.id_admin, getv[1],caption=getv[0])
            reqwest_number_phone = f"select * from profile where name like '{profile}'"
            card_profile = cur.execute(reqwest_number_phone).fetchall()
            card_profile = card_profile[0]
            print(f'проверка {card_profile}')
            await bot.send_contact(admins_id.id_admin, card_profile[2], card_profile[0])


async def del_qwes(state):  # удаление вопоса
    global base, cur
    base = sq.connect('data.db')
    cur = base.cursor()
    async with state.proxy() as data:
        num_del = int(str(tuple(data.values()))[2:-3])
        print(num_del)
        cur.execute(f"DELETE FROM qwestions WHERE number ={num_del}")
        base.commit()



# _____________________________________класс для сохранения вопросов___________________________________


class FSMqwestion(StatesGroup):
    number = State()
    qwes = State()

@dp.message_handler(commands="Загрузка_вопроса", state=None)
async def fsm_number_qwes(message: types.Message):
    await FSMqwestion.number.set()
    await message.reply('Введите номер вопроса')

@dp.message_handler(state=FSMqwestion.number)
async def load_number(message: types.Message, state: FSMContext):
    testmessage = message.text
    testmessage = testmessage.isdigit()
    if not testmessage:
        await message.answer(f'<i>Нужно было ввести номер вопроса.</i>\n\n'
                         f' <i>Можешь заново нажать кнопку и</i>\n\n'
                         f' <i>ввести номер вопроса</i>', parse_mode=types.ParseMode.HTML)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['number'] = message.text
        await FSMqwestion.next()
        await message.reply('Номер вопроса записан, введите сам вопрос')

@dp.message_handler(state=FSMqwestion.qwes)
async def load_qwes(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['qwes'] = message.text
    await sql_add_command(state,'INSERT OR REPLACE INTO qwestions VALUES (?,?)')  # выводил в базу
    await state.finish()
    await message.reply('Вопрос записан.')


# _____________________________________класс для сохранения ID и Имени___________________________________


class FSMAdmin(StatesGroup):
    name = State()
    idname = State()
    contact = State()

@dp.message_handler(commands="Изменить_имя", state=None)
async def fsm_message(message: types.Message):
    await message.reply('Введите Имя и Фамилию', reply_markup=ReplyKeyboardRemove())
    await FSMAdmin.name.set()


# Ловим имя и id
@dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    global name
    name = message.text
    print(name)
    async with state.proxy() as data:
        data['name'] = message.text
        data['idname'] = message.from_id
    await FSMAdmin.contact.set()
    await message.answer('Имя и фамилия сохранены для отправки контактных данных нажмите кнопку отправить контакт.', reply_markup=nav.contactmenu)

@dp.message_handler(content_types=types.ContentType.CONTACT,state=FSMAdmin.contact)
async def load_contact(message: types.Message, state: FSMContext):

    test=message.contact.phone_number
    print(type(test))
    async with state.proxy() as data:
        data['contact'] = message.contact.phone_number
    await message.answer(f'Ваше имя: <u><b>{name}</b></u>\n\n'
                f'➡️ Далее необходимо нажимать на кнопки вопросов. \n\n'
                f'➡️ После этого жмем на кнопку для записи видеответа. \n\n '
                f'❗️<u><b>Для видеоответа дается только одна попытка!</b></u>❗️', reply_markup=nav.qwestionMenu,parse_mode=types.ParseMode.HTML)
    await sql_add_command(state,'INSERT OR REPLACE INTO profile VALUES (?,?,?)')  # выводил в базу
    await state.finish()





# _____________________________________класс для удаления вопроса___________________________________


class FSMAdelete(StatesGroup):
    delete_num_qwes = State()

@dp.message_handler(commands="Удалить_вопрос", state=None)
async def fsm_delete_qwes(message: types.Message):
    await FSMAdelete.delete_num_qwes.set()
    await message.reply('Введите номер вопроса для удаления')
# Ловим номер вопроса
@dp.message_handler(state=FSMAdelete.delete_num_qwes)
async def load_name(message: types.Message, state: FSMContext):
    testmessage = message.text
    testmessage = testmessage.isdigit()
    if not testmessage:
        await message.answer(f'<i>Нужно было ввести номер вопроса.</i>\n\n'
                         f' <i>Можешь заново нажать кнопку и</i>\n\n'
                         f' <i>ввести номер вопроса для удаления</i>',reply_markup=nav.admin_menu, parse_mode=types.ParseMode.HTML)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['delete_num_qwes'] = message.text
        await message.reply('Вопрос удален', reply_markup=nav.admin_menu)
        await del_qwes(state)  # выводил в базу
        await state.finish()
#____________________Получение списка вопросов_______________

@dp.message_handler(commands='Получить_список_вопросов') # запрос вопроса из бд
async def get_qwestions_list(message: types.Message):
    global base, cur
    base = sq.connect('data.db')
    cur = base.cursor()
    qwestion = cur.execute('SELECT * FROM qwestions').fetchall()
    print(qwestion)
    result = ""
    for qwestion_list in qwestion:
        result += f" {qwestion_list}\n"
        result = clear_text(result)
    await message.answer(result)


# ____________________________________Получение вопросов_________________________
@dp.message_handler() # запрос вопроса из бд
async def get_qwestions(message: types.Message):
    global bodynowqwestion
    global base, cur
    base = sq.connect('data.db')
    cur = base.cursor()
    quantitystr=cur.execute('SELECT count (*)from qwestions').fetchall()
    quantitystr=int(str(tuple(quantitystr))[2:-4])
    qwestion=cur.execute('SELECT qwes FROM qwestions').fetchall()

    if message.text == 'Старт':
        await message.answer('Я готов пройти видеоинтервью и соглашаюсь на сохранение видеофайлов с моим участием.', reply_markup=nav.otherMenu)
    elif message.text == 'Да':
        await message.answer('Введите <b>ИМЯ</b> и <b>ФАМИЛИЮ</b> ', reply_markup=ReplyKeyboardRemove(),parse_mode=types.ParseMode.HTML)
        await FSMAdmin.name.set()
    elif message.text == 'Нет':
        await message.answer('Вы в главном меню', reply_markup=nav.mainMenu)
    elif message.text == 'Info':
        await message.answer('<b>Этот бот предназначен для записи и прохождения видеоинтервью с ТЕЛЕФОНА.</b>',parse_mode=types.ParseMode.HTML)
    elif message.text == 'Главное меню':
        await message.answer('Вы в главном меню', reply_markup=nav.mainMenu)
    elif message.text == 'Инструкция':
        await message.answer(qwestions.helper_lines, reply_markup=nav.mainMenu)




    elif quantitystr > 1 and message.text == 'Вопрос №1' :
        await message.answer(f'<b>{clear_text(qwestion[0])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_2,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[0]
        await FSMdonload.video.set()
        # await FSMqwestion.qwestion.set()
    elif quantitystr == 1 and message.text == 'Вопрос №1':
        await message.answer(f'<b>{clear_text(qwestion[0])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[0]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 2 and message.text == 'Вопрос №2' :
        await message.answer(f'<b>{clear_text(qwestion[1])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_3,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[1]
        await FSMdonload.video.set()
    elif quantitystr == 2 and message.text == 'Вопрос №2':
        await message.answer(f'<b>{clear_text(qwestion[1])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[1]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 3 and message.text == 'Вопрос №3' :
        await message.answer(f'<b>{clear_text(qwestion[2])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_4,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[2]
        await FSMdonload.video.set()
    elif quantitystr == 3 and message.text == 'Вопрос №3':
        await message.answer(f'<b>{clear_text(qwestion[2])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[2]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 4 and message.text == 'Вопрос №4' :
        await message.answer(f'<b>{clear_text(qwestion[3])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_5,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[3]
        await FSMdonload.video.set()
    elif quantitystr == 4 and message.text == 'Вопрос №4':
        await message.answer(f'<b>{clear_text(qwestion[3])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[3]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 5 and message.text == 'Вопрос №5' :
        await message.answer(f'<b>{clear_text(qwestion[4])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_6,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[4]
        await FSMdonload.video.set()
    elif quantitystr == 5 and message.text == 'Вопрос №5':
        await message.answer(f'<b>{clear_text(qwestion[4])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[4]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()

    elif quantitystr > 6 and message.text == 'Вопрос №6' :
        await message.answer(f'<b>{clear_text(qwestion[5])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_7,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[5]
        await FSMdonload.video.set()
    elif quantitystr == 6 and message.text == 'Вопрос №6':
        await message.answer(f'<b>{clear_text(qwestion[5])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[5]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 7 and message.text == 'Вопрос №7' :
        await message.answer(f'<b>{clear_text(qwestion[6])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_8,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[6]
        await FSMdonload.video.set()
    elif quantitystr == 7 and message.text == 'Вопрос №7':
        await message.answer(f'<b>{clear_text(qwestion[6])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[6]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 8 and message.text == 'Вопрос №8' :
        await message.answer(f'<b>{clear_text(qwestion[7])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_9,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[7]
        await FSMdonload.video.set()
    elif quantitystr == 8 and message.text == 'Вопрос №8':
        await message.answer(f'<b>{clear_text(qwestion[7])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[7]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 9 and message.text == 'Вопрос №9' :
        await message.answer(f'<b>{clear_text(qwestion[8])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_10,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[8]
        await FSMdonload.video.set()
    elif quantitystr == 9 and message.text == 'Вопрос №9':
        await message.answer(f'<b>{clear_text(qwestion[8])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[8]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()


    elif quantitystr > 10 and message.text == 'Вопрос №10' :
        await message.answer(f'<b>{clear_text(qwestion[9])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>', reply_markup=nav.qwestionMenu_11,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[9]
        await FSMdonload.video.set()
    elif quantitystr == 10 and message.text == 'Вопрос №10':
        await message.answer(f'<b>{clear_text(qwestion[9])}</b>\n\n'
                             f'<i>(нажми на 📎 и запиши видеоответ)</i>\n\n'
                             f'<u>Это был последний вопрос, спасибо за интервью</u>', reply_markup=nav.mainMenu,parse_mode=types.ParseMode.HTML)
        bodynowqwestion = qwestion[9]
        await bot.send_message(admins_id.id_admin, f'Сохранено интервью от: <b>{name}</b>',
                               parse_mode=types.ParseMode.HTML)
        await FSMdonload.video.set()







# _____________________________________класс для сохранения видео_ответов___________________________________

class FSMdonload(StatesGroup):
    number_qwestion = State()
    video = State()
    idprofile = State()



@dp.message_handler(commands="Видеоответ", state=None)
async def fsm_donload_video(message: types.Message):
    await FSMdonload.video.set()

@dp.message_handler(content_types=ContentType.VIDEO_NOTE,state=FSMdonload.video)
async def video_note(message: Message):
    await message.answer('<i>Видеокружки не принимаются, нажмите на 📎 для записи видео</i>',parse_mode=types.ParseMode.HTML)

@dp.message_handler(content_types=ContentType.VOICE,state=FSMdonload.video)
async def voice(message: Message):
    await message.answer('<i>Голосовые сообщения тоже не принимаются 🤦‍, нажмите на 📎 для записи видео.</i>',parse_mode=types.ParseMode.HTML)

@dp.message_handler(content_types=ContentType.PHOTO,state=FSMdonload.video)
async def video_note(message: Message):
    await message.answer('<i>Фото не принимаются, нажмите на 📎 для записи видео</i>',parse_mode=types.ParseMode.HTML)


@dp.message_handler(content_types=ContentType.TEXT,state=FSMdonload.video)
async def text(message: Message, state: FSMContext):
    if message.text == 'Главное меню':
        await state.finish()
        await message.answer('Вы в главном меню', reply_markup=nav.mainMenu)
    else:
        await message.answer('<i>Нажмите на 📎 для записи видео и только потом следующий вопрос</i>',parse_mode=types.ParseMode.HTML)

# Ловим id video and id profile
@dp.message_handler(content_types=['video'] ,state=FSMdonload.video)
async def load_video(message: types.Message, state: FSMContext):

    global bodynowqwestion
    bodynowqwestion = clear_text(bodynowqwestion)
    print(bodynowqwestion)


    async with state.proxy() as data:
        data['number_qwestion'] = bodynowqwestion
        data['video'] = message.video.file_id
        data['idprofile'] = message.from_id

    await message.reply('Видео ответ принят')
    await sql_add_command(state,'INSERT OR REPLACE INTO video VALUES (?,?,?)')  # выводил в базу
    await state.finish()

# __________________________ Создание_базы _____________________

def sql_start(reqwest):
    global base, cur
    base = sq.connect('data.db')
    cur = base.cursor()
    if base:
        print('База подключена')
    base.execute(reqwest)
    base.commit()

# _________________________Запись в базу______________________
async def sql_add_command(state,request):
    global base, cur
    base = sq.connect('data.db')
    cur = base.cursor()
    async with state.proxy() as data:
        cur.execute(request, tuple(data.values()))
        base.commit()
#_____________________________________________________________

# ______________________________________Ответ на  VIDEO без ответа на ввопрос__________________________
@dp.message_handler(content_types=ContentType.VIDEO)
async def send_video_file_id(message: Message):
    await message.answer('<i>Видео не принято, выберете сначала вопрос</i>',parse_mode=types.ParseMode.HTML)

@dp.message_handler(content_types=ContentType.VIDEO_NOTE)
async def send_video_note_file_id(message: Message):
    await message.answer('<i>Видеокружки не принимаются, выберете сначала вопрос и нажмите на 📎 для записи</i>',parse_mode=types.ParseMode.HTML)

@dp.message_handler(content_types=ContentType.PHOTO)
async def send_video_note_file_id(message: Message):
    await message.answer('<i>Фото не принимаются, выберете сначала вопрос и нажмите на 📎 для записи</i>',parse_mode=types.ParseMode.HTML)

executor.start_polling(dp)
