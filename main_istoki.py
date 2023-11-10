import asyncio
import logging
import calendar
import datetime
from aiogram import Bot, Dispatcher, types, F, html
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import calendar

from datetime import datetime, timedelta


logging.basicConfig(level=logging.INFO)
bot = Bot(token="")
dp = Dispatcher()


class Form(StatesGroup):
    nickname = State()
    mail = State()
    password = State()
    reg_flag = State()
    rec_flag = State()
    surn_name = State()


def show_start_buttons():
        start_buttons = [
            [types.InlineKeyboardButton(text="Истоки в VK", url="https://vk.com/club.istoki"),
             types.InlineKeyboardButton(text="Музей-заповедник Гнёздово", url="https://vk.com/gnezdovomuseum")
             ],
            [types.InlineKeyboardButton(text="Запись на мероприятия", callback_data="record"),
             types.InlineKeyboardButton(text="Регистрация", callback_data="registration")
             ],
            [types.InlineKeyboardButton(text="Маршруты/точки", callback_data="map_route_point"),
             types.InlineKeyboardButton(text="Календарь мероприятий", callback_data="calendar")
             ],
            [types.InlineKeyboardButton(text='Краткая информация об "Истоках"', callback_data="show_info_istoki")
             ],
            [types.InlineKeyboardButton(text="Краткая информация о Смоленске", callback_data="show_info_smolensk")
             ]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_buttons)
        return keyboard



@dp.message(Command("start"))
async def start_info(message: types.Message, state: FSMContext):
    #builder = InlineKeyboardBuilder()

    #await bot.set_chat_menu_button(menu_button="")
    await state.update_data(rec_flag=False)
    await state.update_data(reg_flag=False)
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


@dp.callback_query(F.data == "map_route_point")
async def show_point(callback: types.CallbackQuery):
    await bot.send_venue(callback.message.chat.id, 54.7858485323177, 31.87947811552349,
                         "Гнёздовские курганы. Куган Л-13", 'Музей-заповедник "Гнёздово"')
    await callback.message.answer("Курган Л-13, раскопанный в 1949 г. экспедицией под руководством выдающегося археолога Д.А. Авдусина, также располагается в Лесной группе курганного могильника Гнездово. Название группы, думаю, понятно откуда. Раскопано в том полевом сезоне было 42 курганные насыпи, многие из которых дали весьма интересный материал. Однако все внимание археологического сообщества, безусловно, было обращено именно на курган №13. Все дело, конечно же, в надписи, которая является до сих древнейшей кириллической надписью на нашей территории. За это рекультивированный после раскопок курган Л-13 удостоился памятника, красующегося на его вершине.")



@dp.message(F.text == "Изменить")
async def change_record(message: types.Message, state: FSMContext):
    await state.update_data(reg_flag=False)
    await message.answer("Введите свои никнейм, почту и"
                         " пароль через запятую. Например: \nЯЛюблюСмоленск, "
                         "ilovesmolensk@mail.ru, 67ilovesmolensk2023")


@dp.message(F.text == "Подтвердить")
async def get_last_reg_data(message: types.Message, state: FSMContext):
    await state.update_data(reg_flag=True)
    await message.answer("Аккаунт создан.", reply_markup=show_start_buttons())


@dp.message(F.text)
async def get_rig_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    check = [
        [types.KeyboardButton(text="Подтвердить"),
         types.KeyboardButton(text="Изменить")
         ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=check,
                                         resize_keyboard=True,
                                         input_field_placeholder="Подтвердите данные"
                                         )
    if not data["reg_flag"]:
        nickname, mail, password = message.text.split(",")
        await state.update_data(nickname=nickname)
        await state.update_data(mail=mail)
        await state.update_data(password=password)
        await message.answer(f"Проверьте ваши данные.\nНикнейм: {nickname}\nПочта:{mail}\nПароль:{password}",
                             reply_markup=keyboard)
    if data["reg_flag"] and not data["rec_flag"]:
        await state.update_data(surn_name=message.text)
        await state.update_data(rec_flag=message.text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
