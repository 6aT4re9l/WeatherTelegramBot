import keyboards as kb
from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
import API_Meteo as API
from aiogram.utils.keyboard import InlineKeyboardBuilder

user_private_router = Router()

class Customers(StatesGroup):
    start = State()
    city = State()
    change_city = State()
    add_favorite = State()
    remove_favorite = State()

# Стартовая команда
@user_private_router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Customers.start)
    await message.answer('Привет! Введите название города, чтобы узнать погоду.')

# Обработка ввода города
@user_private_router.message(StateFilter(Customers.start, Customers.change_city))
async def cmd_city(message: Message, bot: Bot, state: FSMContext):
    city = message.text
    if message.text.upper() == "СПБ" or message.text == "ПИТЕР" :
        city = "Санкт-Петербург"
    if message.text.upper() == "МСК":
        city = "Москва"
    if message.text.upper() == "КРД":
        city = "Краснодар"
    if message.text.upper() == "ЕКБ":
        city = "Екатеринбург"
    weather_answer = await API.get_weather_today(city)
    if not weather_answer:
        await message.answer(f'"{city}" не найден. Пожалуйста, проверьте название и попробуйте снова.')
        return
    await message.answer(text=weather_answer, reply_markup=kb.get_callback_btns(
        btns={
            'Сегодня': 'NULL',
            'Завтра': 'tomorrow',
            'На 3 дня': 'three_days',
            'На 5 дней': 'five_days',
            'На неделю': 'week',
            'Избранное': 'favorites_menu',
            'Изменить город': 'change_city'
        },
        sizes=[3, 2, 1, 1]))
    await state.update_data(city=city)
    await state.set_state(Customers.city)

# Обработка нажатий на кнопки
async def process_weather(callback: CallbackQuery, state: FSMContext, days: int):
    state_data = await state.get_data()
    city = state_data.get("city")
    if days == 1:
        weather_answer = await API.get_weather_today(city)
    elif days == 2:
        weather_answer = await API.get_weather_tomorrow(city)
    elif days == 3:
        weather_answer = await API.get_weather_for_x_days(city, 3)
    elif days == 5:
        weather_answer = await API.get_weather_for_x_days(city, 5)
    elif days == 7:
        weather_answer = await API.get_weather_for_x_days(city, 7)
    await callback.answer('')
    await callback.message.edit_text(text=weather_answer, reply_markup=kb.get_callback_btns(
        btns={
            'Сегодня': 'today' if days != 1 else 'NULL',
            'Завтра': 'tomorrow' if days != 2 else 'NULL',
            'На 3 дня': 'three_days' if days != 3 else 'NULL',
            'На 5 дней': 'five_days' if days != 5 else 'NULL',
            'На неделю': 'week' if days != 7 else 'NULL',
            'Избранное': 'favorites_menu',
            'Изменить город': 'change_city'
        }, sizes=[3, 2, 1, 1]))

@user_private_router.callback_query(F.data == 'today', StateFilter(Customers.city))
async def callback_today(callback: CallbackQuery, state: FSMContext):
    await process_weather(callback, state, 1)

@user_private_router.callback_query(F.data == 'tomorrow', StateFilter(Customers.city))
async def callback_tomorrow(callback: CallbackQuery, state: FSMContext):
    await process_weather(callback, state, 2)

@user_private_router.callback_query(F.data == 'three_days', StateFilter(Customers.city))
async def callback_three_days(callback: CallbackQuery, state: FSMContext):
    await process_weather(callback, state, 3)

@user_private_router.callback_query(F.data == 'five_days', StateFilter(Customers.city))
async def callback_five_days(callback: CallbackQuery, state: FSMContext):
    await process_weather(callback, state, 5)

@user_private_router.callback_query(F.data == 'week', StateFilter(Customers.city))
async def callback_week(callback: CallbackQuery, state: FSMContext):
    await process_weather(callback, state, 7)

@user_private_router.callback_query(F.data == 'change_city', StateFilter(Customers.city))
async def callback_change_city(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text(text="Введите название другого города.")
    await state.set_state(Customers.change_city)

# Обработка избранных городов
def favorites_menu_buttons(favorites):
    keyboard = InlineKeyboardBuilder()
    for city in favorites:
        keyboard.row(InlineKeyboardButton(text=city, callback_data=f"show_{city}"))
    keyboard.row(
        InlineKeyboardButton(text="Добавить город", callback_data="add_favorite"),
        InlineKeyboardButton(text="Назад", callback_data="back_to_main")
    )
    return keyboard.as_markup()

@user_private_router.callback_query(F.data == 'favorites_menu', StateFilter(Customers.city))
async def show_favorites_menu(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    favorites = state_data.get('favorites', [])
    await callback.message.edit_text("Избранное:", reply_markup=favorites_menu_buttons(favorites))

@user_private_router.callback_query(F.data == 'add_favorite', StateFilter(Customers.city))
async def add_favorite(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Customers.add_favorite)
    await callback.message.edit_text("Введите название города для добавления в избранное:")

@user_private_router.message(StateFilter(Customers.add_favorite))
async def process_add_favorite(message: Message, state: FSMContext):
    city = message.text
    if message.text.upper() == "СПБ" or message.text == "ПИТЕР" :
        city = "Санкт-Петербург"
    if message.text.upper() == "МСК":
        city = "Москва"
    if message.text.upper() == "КРД":
        city = "Краснодар"
    if message.text.upper() == "ЕКБ":
        city = "Екатеринбург"
    state_data = await state.get_data()
    favorites = state_data.get('favorites', [])
    if city not in favorites:
        favorites.append(city)
        await state.update_data(favorites=favorites)
        await message.answer(f"{city} добавлен в избранное.", reply_markup=favorites_menu_buttons(favorites))
    else:
        await message.answer(f"{city} уже в избранном.", reply_markup=favorites_menu_buttons(favorites))
    await state.set_state(Customers.city)


@user_private_router.callback_query(F.data == 'back_to_main', StateFilter(Customers.city))
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    city = state_data.get("city")
    weather_answer = await API.get_weather_today(city)
    await callback.message.edit_text(text=weather_answer, reply_markup=kb.get_callback_btns(
        btns={
            'Сегодня✓': 'NULL',
            'Завтра': 'tomorrow',
            'На 3 дня': 'three_days',
            'На 5 дней': 'five_days',
            'На неделю': 'week',
            'Избранное': 'favorites_menu',
            'Изменить город': 'change_city'
        },
        sizes=[3, 2, 1, 1]))

# Обработка нажатия на город из избранного
@user_private_router.callback_query(StateFilter(Customers.city))
async def callback_show_city_weather(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("show_"):
        city = callback.data[len("show_"):]
        weather_answer = await API.get_weather_today(city)
        await callback.answer('')
        await callback.message.edit_text(text=weather_answer, reply_markup=kb.get_callback_btns(
            btns={
                'Сегодня✓': 'NULL',
                'Завтра': 'tomorrow',
                'На 3 дня': 'three_days',
                'На 5 дней': 'five_days',
                'На неделю': 'week',
                'Избранное': 'favorites_menu',
                'Изменить город': 'change_city'
            }, sizes=[3, 2, 1, 1]))
        await state.update_data(city=city)
        await state.set_state(Customers.city)
