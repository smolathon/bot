import asyncio
import logging
import json
import datetime
from aiogram import Bot, Dispatcher, types, F, html
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from requests import get, post
#from aiogram.filters.callback_data import CallbackData
#from aiogram.types import CallbackQuery
import calendar
#from calendar.types import SimpleCalendarCallback, SimpleCalendarAction, WEEKDAYS
#from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime, timedelta


URL = "https://f12b-212-3-142-182.ngrok.io"
logging.basicConfig(level=logging.INFO)
bot = Bot(token="")
dp = Dispatcher()


class Form(StatesGroup):
    nickname = State()
    mail = State()
    password = State()
    reg_flag = State()
    rec_flag = State()
    surname = State()
    get_route_num = State()

def show_start_buttons():
        start_buttons = [
            [types.InlineKeyboardButton(text="Истоки в VK", url="https://vk.com/club.istoki"),
             types.InlineKeyboardButton(text="Музей-заповедник Гнёздово", url="https://vk.com/gnezdovomuseum")
             ],
            [types.InlineKeyboardButton(text="Запись на мероприятия", callback_data="record"),
             types.InlineKeyboardButton(text="Регистрация", callback_data="registration"),
             types.InlineKeyboardButton(text="Вход", callback_data="log_in")
             ],
            [types.InlineKeyboardButton(text="Маршруты/точки", callback_data="map_route_point"),
             types.InlineKeyboardButton(text="Календарь мероприятий", callback_data="calendar")
             ],
            [types.InlineKeyboardButton(text='Краткая информация об "Истоках"', callback_data="show_info_istoki")
             ],
            [types.InlineKeyboardButton(text="Краткая информация о Гнёздово", callback_data="show_info_gnezdovo")
             ]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_buttons)
        return keyboard



def create_calendar():
    year = datetime.now().year
    month = datetime.now().month
    calendar_butt = []
    days_count = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    calendar_butt.append([types.InlineKeyboardButton(text="<<", callback_data=" "),
                          types.InlineKeyboardButton(text=str(year) + ', ' + str(month), callback_data=" "),
                          types.InlineKeyboardButton(text=">>", callback_data=" ")])
    calendar_butt.append([types.InlineKeyboardButton(text=x, callback_data=" ")
                          for x in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']])
    if (year % 4 == 0 and year % 100 != 0 and year % 400 != 0) or year % 400 == 0:
        days_count[2] = 29
    days = []
    day_countdown = datetime(year, month, 1)
    for i in range(day_countdown.weekday()):
        days.append(" ")
    for i in range(days_count[month]):
        days.append(str(i+1))
    for i in range(7 - len(days) % 7):
        days.append(" ")
    for w in range((len(days)+6)//7):
        week = []
        for d in range(7):
            #if str(d+w*7) not in events_days:
            week.append(types.InlineKeyboardButton(text=days[d+w*7], callback_data="show_no_event"))
            '''
            else:
                week.append(types.InlineKeyboardButton(text=days[d+w*7],
                                                       callback_data=f"show_event,{year} {month} {d+w*7}"))'''
        calendar_butt.append(week)
    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=calendar_butt)
    return inline_kb


@dp.message(Command("start"))
async def start_info(message: types.Message, state: FSMContext):
    #builder = InlineKeyboardBuilder()

    c1 = types.BotCommand(command='start', description='Запуск')
    await bot.set_my_commands([c1])
    await bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands(type='commands'))

    #await bot.set_chat_menu_button(menu_button=types.MenuButtonCommands(type='commands'))
    await state.update_data(rec_flag=False)
    await state.update_data(reg_flag=False)
    await state.update_data(get_route_name=False)
    await message.answer(f"Здравствуйте, {html.quote(message.from_user.full_name)}! Истоки рады приветствовать Вас!",
                         reply_markup=show_start_buttons()
                         )


@dp.callback_query(F.data == "registration")
async def record(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(reg_flag=False)
    await state.update_data(rec_flag=False)
    await callback.message.answer("Введите свои никнейм, почту и"
                                  " пароль через запятую. Например: \nЯЛюблюСмоленск, "
                                  "ilovesmolensk@mail.ru, 67ilovesmolensk2023")
    await callback.answer()


@dp.callback_query(F.data == "record")
async def record(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(rec_flag=False)
    if (await state.get_data())["reg_flag"]:
        await callback.message.answer("Введите свои фамилию и имя. "
                                      "Например: Иванов Иван")
        await callback.answer()
    else:
        await callback.message.answer("Для записи на мероприятия необходимо быть зарегистрированным.")
        await callback.message.answer("Введите свои никнейм, почту и"
                                      " пароль через запятую. Например: \nЯЛюблюСмоленск, "
                                      "ilovesmolensk@mail.ru, 67ilovesmolensk2023")
        await callback.answer()


@dp.callback_query(F.data == "log_in")
async def log_in(callback: types.CallbackQuery):
    await callback.message.answer("Введите никнейм, почту и пароль.")


@dp.callback_query(F.data == "map_route_point")
async def show_point(callback: types.CallbackQuery, state: FSMContext):
    ans = json.loads(get(f"{URL}/route/0").content)
    x = 1
    for route in ans['routes']:
        await callback.message.answer(str(x) + ')' + ' ' + route['title'] + '\n' + route['description'])
        x += 1
    await callback.message.answer("Введите номер маршрута")
    await state.update_data(get_route_num=True)
    #await bot.send_venue(callback.message.chat.id, 54.7858485323177, 31.87947811552349,
     #                    "Гнёздовские курганы. Куган Л-13", 'Музей-заповедник "Гнёздово"')
    #await callback.message.answer("Курган Л-13, раскопанный в 1949 г. экспедицией под руководством выдающегося археолога Д.А. Авдусина, также располагается в Лесной группе курганного могильника Гнездово. Название группы, думаю, понятно откуда. Раскопано в том полевом сезоне было 42 курганные насыпи, многие из которых дали весьма интересный материал. Однако все внимание археологического сообщества, безусловно, было обращено именно на курган №13. Все дело, конечно же, в надписи, которая является до сих древнейшей кириллической надписью на нашей территории. За это рекультивированный после раскопок курган Л-13 удостоился памятника, красующегося на его вершине.")


@dp.callback_query(F.data == "calendar")
async def show_calendar(callback: types.CallbackQuery):
    await callback.message.answer("<u><b>Календарь мероприятий</b></u>",
                                  reply_markup=create_calendar(), parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "show_info_istoki")
async def show_info_istoki(callback: types.CallbackQuery):
    await callback.message.answer("Клуб занимается исторической реконструкцией материальной культуры и быта периода IX-XI веков. Участники клуба реконструируют костюмы и предметы быта Древней Скандинавии, Руси, Ирландии, Хазарского каганата, балтских племен. \nКлуб периодически проводит тематические выставки реконструкций по периоду раннего Средневековья. \nУчастники клуба по мере сил занимаются популяризацией истории в рамках своего официального ютуб канала - https://www.youtube.com/user/istokismol")


@dp.callback_query(F.data == "show_info_gnezdovo")
async def show_info_gnezdovo(callback: types.CallbackQuery):
    await callback.message.answer('Гнёздово – это название многое значит для тех, кого интересует история России, кто бережно и с уважением относится к ее памятникам. \nНа обоих берегах Днепра в 10-12 км к западу от Смоленска расположился Гнёздовский комплекс археологических памятников – курганный могильник, когда-то насчитывавший 3500-4000 курганов и несколько поселений, в том числе укрепленных. \nК настоящему времени сохранилось около 2500 курганов и одно поселение. \nЭто крупнейший на территории России и Европы комплекс археологических памятников, относящихся к периоду образования древнерусского государства – его площадь составляет чуть более 200 га. n\В соответствии с Постановлением Совета Министров РСФСР от 30.08.1960 № 1327 комплекс принят на государственную охрану как памятник археологии государственного (федерального) значения. \n31.12.2010 г. для содержания и охраны Гнёздовского комплекса был создан историко-археологический и природный музей-заповедник "Гнёздово".')


@dp.callback_query(F.data == "change")
async def change_record(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(reg_flag=False)
    await callback.message.answer("Введите свои никнейм, почту и"
                         " пароль через запятую. Например: \nЯЛюблюСмоленск, "
                         "ilovesmolensk@mail.ru, 67ilovesmolensk2023")


@dp.callback_query(F.data == "confirm")
async def get_last_reg_data(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(reg_flag=True)
    data = await state.get_data()
    username, email, password = data["nickname"], data["mail"],  data["password"]
    err = post(f"{URL}/user/login",
               json={"username": username,
                "password": password
                }
               )
    if err.status_code == 200:
        await callback.message.answer("Вы успешно вошли")
    else:
        err = post(f"{URL}/user",
             json={"username": str(username),
                   "email": str(email),
                   "password": str(password),
                   "role": "User",
                   "image": ""
                   })
        if err.status_code != 200:
            await callback.message.answer("Неверно введённые данные.", reply_markup=show_start_buttons())
        else:
            await callback.message.answer("Аккаунт создан.", reply_markup=show_start_buttons())


@dp.callback_query(F.data == "show_no_event")
async def show_no_info(callback: types.CallbackQuery):
    await callback.message.answer("На этот день не запланировано никаких мероприятий")




@dp.message(F.text)
async def get_rig_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    check = [
        [types.InlineKeyboardButton(text="Подтвердить", callback_data="confirm"),
         types.InlineKeyboardButton(text="Изменить", callback_data="change")
         ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=check)
    if data["get_route_num"]:
        ans = json.loads(get(f"{URL}/route/0").content)['routes'][int(message.text)-1]
        await message.answer(ans['title'] + '\n' + ans['description'] + '\n Ваш маршрут с описанием.')
        await bot.send_photo(message.chat.id, ans['image'])
        points_ans = json.loads(get(f"{URL}/point/{ans['id']}").content)['points']
        for point in points_ans:
            await bot.send_venue(message.chat.id, point['location'][0], point['location'][1],
                                 point['title'], point['description'])
            await bot.send_photo(message.chat.id, point['image'])


        await state.update_data(get_route_num=False)
    elif not data["reg_flag"]:
        nickname, mail, password = message.text.split(",")
        await state.update_data(nickname=nickname)
        await state.update_data(mail=mail)
        await state.update_data(password=password)
        await message.answer(f"Проверьте ваши данные.\nНикнейм: {nickname}\nПочта:{mail}\nПароль:{password}",
                             reply_markup=keyboard)
    else:
        today = datetime.now()
        ans = json.loads(get(f"https://89ef-212-3-142-182.ngrok.io/user/test_user").content)
        response = post("https://89ef-212-3-142-182.ngrok.io/ticket",
                         json={"name": message.text,
                         "reg_date": [today.year, today.month, today.day],
                         "event_id": 1,
                         "user_id": ans['id']
                         })

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())