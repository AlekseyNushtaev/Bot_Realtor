from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, StateFilter

from bot import bot
from config import ADMIN_ID
from keyboard_creator import create_kb

router =Router()
dct_for_mes = {"studio_buy": "Студия",
               "apart_2_buy": "2-ух комнатная квартира",
               "apart_3_buy": "3-ех комнатная квартира и больше",
               "studio_rent": "Студия",
               "apart_2_rent": "2-ух комнатная квартира",
               "apart_3_rent": "3-ех комнатная квартира и больше",
               "money_1": "До 50 000$",
               "money_2": "От 50 00$ до 75 000$",
               "money_3": "От 75 000$"}


class FSMFillForm(StatesGroup):
    fill_name = State()


@router.message(CommandStart())
async def process_start_command(mes: Message):
    await mes.answer_photo(
        photo=FSInputFile("main.jpg"),
        caption="Здравствуйте, я телеграмм бот от гастропроекта Cork в Батуми. "
                "Я помогу Вам решить вопрос с поиском недвижимости в Батуми. "
                "Все просто, выберите подходящий запрос и мы подберем для Вас "
                "самые лучшие варианты. Попробуем?",
        reply_markup=create_kb(
            1,
            buy="Покупка недвижимости 🏠",
            rent="Аренда недвижимости 🏙️",
            sell="Продажа недвижимости 💵",
        )
    )


@router.callback_query(F.data == "yes")
async def restart(cb: CallbackQuery):
    await bot.send_photo(
        cb.from_user.id,
        photo=FSInputFile("main.jpg"),
        caption="Здравствуйте, я телеграмм бот от гастропроекта Cork в Батуми. "
                "Я помогу Вам решить вопрос с поиском недвижимости в Батуми. "
                "Все просто, выберите подходящий запрос и мы подберем для Вас "
                "самые лучшие варианты. Попробуем?",
        reply_markup=create_kb(
            1,
            buy="Покупка недвижимости 🏠",
            rent="Аренда недвижимости 🏙️",
            sell="Продажа недвижимости 💵",
        )
    )


@router.callback_query(F.data.in_({"buy"}))
async def contacts(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer(
        text="Выберите квартиру своей мечты:",
        reply_markup=create_kb(
            1,
            studio_buy="Студия (до 40 метров)",
            apart_2_buy="2-х комнатная (до 60 метров)",
            apart_3_buy="3-х комнатная (до 90 метров)"
        )
    )


@router.callback_query(F.data.in_({"rent"}))
async def contacts(cb: CallbackQuery):
    await cb.message.answer(
        text="Выберите квартиру в аренду, которая Вам необходима для комфортной жизни в Батуми:",
        reply_markup=create_kb(
            1,
            studio_rent="Студия (до 40 метров)",
            apart_2_rent="2-х комнатная (до 60 метров)",
            apart_3_rent="3-х комнатная (до 90 метров)"
        )
    )


@router.callback_query(F.data == "sell")
async def contacts(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer(text="Введите пожалуйста Ваше имя и наш специалист в самое ближайшее время свяжется с Вами ♥️")
    await bot.send_message(
        chat_id=ADMIN_ID,
        text="Обратился:\n"
             f"Username: @{cb.from_user.username}\n"
             f"Услуга: Продажа\n"
    )
    await state.set_state(FSMFillForm.fill_name)


@router.callback_query(F.data.in_({"studio_rent", "apart_2_rent", "apart_3_rent"}))
async def contacts(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer(text="Введите пожалуйста Ваше имя и наш специалист в самое ближайшее время свяжется с Вами ♥️")
    await bot.send_message(
        chat_id=ADMIN_ID,
        text="Обратился:\n"
             f"Username: @{cb.from_user.username}\n"
             f"Услуга: Аренда\n"
             f"Тип: {dct_for_mes[cb.data]}\n"
    )
    await state.set_state(FSMFillForm.fill_name)


@router.callback_query(F.data.in_({"studio_buy", "apart_2_buy", "apart_3_buy"}))
async def contacts(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer(
        text="Какой бюджет на покупку квартиры Вашей мечты?",
        reply_markup=create_kb(
            1,
            money_1="До 50 000$",
            money_2="От 50 00$ до 75 000$",
            money_3="От 75 000$"
        )
    )
    await state.update_data(house=cb.data)


@router.callback_query(F.data.in_({"money_1", "money_2", "money_3"}))
async def contacts(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer(text="Введите пожалуйста Ваше имя и наш специалист в самое ближайшее время свяжется с Вами ♥️")
    dct = await state.get_data()
    await bot.send_message(
        chat_id=ADMIN_ID,
        text="Обратился:\n"
             f"Username: @{cb.from_user.username}\n"
             f"Услуга: Покупка\n"
             f"Тип: {dct_for_mes[dct['house']]}\n"
             f"Бюджет: {dct_for_mes[cb.data]}",
    )
    await state.set_state(FSMFillForm.fill_name)


@router.message(StateFilter(FSMFillForm.fill_name))
async def process_name_sent(message: Message, state: FSMContext):
    await bot.forward_message(chat_id=ADMIN_ID,
                              from_chat_id=message.chat.id,
                              message_id=message.message_id)
    await message.answer(text='Спасибо! Скоро мы напишем Вам\n\nХотите снова сделать заявку?',
                         reply_markup=create_kb(1, yes="Сделать новую заявку"))
    await state.set_state(default_state)


