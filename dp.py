# import sqlite3 as sq
#
# def sql_start():
#     global base, cur
#     base = sq.connect('data.dp')
#     cur = base.cursor()
#     if base:
#         print('База подключена')
#     base.execute('CREATE TABLE IF NOT EXIST profile(name TEXT, idname TEXT PRIMARY KEY')
#     base.commit()
#
#
# async def sql_add_command(state)
#     async with state.proxy() as data
#       cur.execute('INSERT INTO profile VALUES (?,?)', tuple(data.values()))
#       base.commit()