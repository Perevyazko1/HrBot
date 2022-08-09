# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram import types
# from app import dp
# class FSMAdmin(StatesGroup)
#     video = State()
#     name = State()
#     idname = State()
#
# # Начало диалога загрузки видео
# @dp.message_handler(commands='Загрузить видео', state=None)
# async def donload_video(message : types.Message)
#     await FSMAdmin.video.set()
#     await message.reply('Сними видео')
#
# # Ловим видео
# @dp.message_handler(content_types=['video'], state=FSMAdmin.video)
#     async def send_video_file_id(message: types.Message, state: FSMContext):
#         async with state.proxy() as data:
#             data['video'] = message.video.file_id
#         # file_id = (message.video.file_id)
#
#         message_text = 'hgj'
#         await bot.send_video(admins_id.id_admin,video=file_id, caption=message_text )
#         await message.answer('Ответ отправлен.')
#         print(message_text,message.caption)
#         await FSMAdmin.next()
#         await message.reply('Видео загружено')
# # Ловим имя
# @dp.message_handler(state=FSMAdmin.name)
# async def load_name(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['name'] = message.text
#     await FSMAdmin.next()
#     await message.reply('Введите ID')
# # Ловим айди
# @dp.message_handler(state=FSMAdmin.idname)
# async def load_idname(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['idname'] = message.text
#     async with state.proxy() as data
#         await message.reply(str(data))
#     await state.finish()
# # Регистрируем хэндлеры
# # def register_handlers_admin(dp:Dispatcher):
# #     dp.register_message_handler(donload_video,commands='Загрузить видео', state=None)
# #     dp.register_message_handler(send_video_file_id,content_types=['video'], state=FSMAdmin.video)
# #     dp.register_message_handler(load_name,state=FSMAdmin.name)
# #     dp.register_message_handler(load_idname,state=FSMAdmin.idname)

# class FSMAdmin(StatesGroup):
#     idvideo = State()
#     idname = State()
#
# @dp.message_handler(commands="video", state=None)
# async def fsm_message_video(message: types.Message):
#     await FSMAdmin.name.set()
#
# # Ловим Видео
# @dp.message_handler(content_types=['video'],state=FSMAdmin.name)
# async def load_video(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['idname'] = message.from_id
#         data['idvideo'] = message.video.file_id
#     await message.reply('Видео принято')
#     # async with state.proxy() as data: # выводил словарь в телегу
#     #     await message.reply(str(data)) # выводил словарь в телегу
#     # await FSMAdmin.next()
#     await sql_add_command(state)
#     await state.finish()
