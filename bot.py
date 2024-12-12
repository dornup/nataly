# разбираемся с aiogram
import os
from typing import Dict, Any
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router, html
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import requests
from bs4 import BeautifulSoup
from very_secret_info import token
from aiogram.filters.command import Command
import time
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from lxml.html.soupparser import fromstring
from calendar import monthrange


# настраиваем логирование
logging.basicConfig(level='INFO')
# создаем объект бота
bot = Bot(token=token)
# создаем диспетчера
dp = Dispatcher()
# создаем рутер
form_router = Router()
# добавляем рутер для заполнения формы
dp.include_router(form_router)

# все, что происходит далее - чистой воды прикол ради прикола 
# не судите меня строго, зато я изучаю http запросы и методы

# форма для заполнения данных о пользователе
class Form(StatesGroup):
    name = State()
    year = State()
    month = State()
    day = State()
    hour = State()
    minute = State()
    country = State()
    state = State()
    cityplan =State()

driver = WebDriver(service=ChromeService())
# driver_path = ChromeDriverManager().install()
# # с библиотекой какой-то косяк из-за новой версии chrome, поэтому пришлось вставить сюда этот костыль
# if driver_path:
#         driver_name = driver_path.split('/')[-1]
#         if driver_name != "chromedriver":
#             driver_path = "/".join(driver_path.split('/')[:-1] + ["chromedriver.exe"])
#             if '/' in driver_path:
#                 driver_path = driver_path.replace('/', '\\')
#             os.chmod(driver_path, 0o755)
# driver = webdriver.Chrome(service=ChromeService(driver_path))

# обработчик команды start
@dp.message(Command('start'))  # будет работать только после команды start
async def bot_start(message: types.Message):
    await message.answer('Привет! Это бот для расчета натальной карты. Чтобы составить космограмму напишите команду /natal_chart. Если вы захотите прекратить астрологическую процедуру отправьте команду /cancel.')  # обычное сообщение


# команда для начала заполнения натальной карты
@form_router.message(Command('natal_chart')) 
async def bot_natal_chart(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer('''
Расчет вашей натальной карты
                         
В этой функции мы рассмотрим, как сошлись звезды во время вашего рождения, и расскажем вам, что значат по астрологии эти соединения небесных тел
Для начала скажи, как тебя зовут?
                         ''')
    
@form_router.message(Command('cancel'))
async def cancel(message: types.Message):
    pass
    
@form_router.message(Form.name)
async def year(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.year)
    await message.answer(f'Приятно познакомиться, {html.quote(message.text)}.\n Укажите год своего рождения')

@form_router.message(Form.year)
async def month(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(Form.month)
    await message.answer('Отлично! введите месяц своего рождения цифрой от 1 до 12')

@form_router.message(Form.month)
async def day(message: types.Message, state: FSMContext):
    data = await state.update_data(mont=message.text)
    d = dict(data)
    await state.set_state(Form.day)
    try:
        await message.answer('Выберите день своего рождения', 
                            reply_markup=types.ReplyKeyboardMarkup(
                                keyboard=[[types.KeyboardButton(text=str(i))] for i in range(1, monthrange(int(d['year']), int(message.text))[1] + 1)]
                            ))
    except Exception:
        await message.answer('Вы ввели что-то неверно, вам лучше попробовать еще раз.\nВведите команду /natal_chart чтобы внести данные заново')

@form_router.message(Form.day)
async def country(message: types.Message, state: FSMContext):
    await state.update_data(day = message.text)
    await state.set_state(Form.country)
    await message.answer('Идем дальше! \nВведите название страны, в которой вы родились')

@form_router.message(Form.country)
async def state(message: types.Message, state: FSMContext):
    await state.update_data(country = message.text)
    await state.set_state(Form.state)
    await message.answer('Введите область')

@form_router.message(Form.state)
async def cityplan(message: types.Message, state: FSMContext):
    await state.update_data(state = message.text)
    await state.set_state(Form.cityplan)
    await message.answer('Введите город') 

@form_router.message(Form.cityplan)
async def city(message: types.Message, state: FSMContext):
    data = await state.update_data(cityplan = message.text)
    await state.clear()
    await message.answer('Начинаем обработку данных...')
    await send_data(message, data)


async def send_data(message: types.Message, data: Dict[str, Any]):
    name = data['name']
    year = data['year']
    month = data['month']
    day = data['day']
    hour = data['hour']
    minute = data['minute']
    country = data['country']
    state = data['state']
    city = data['cityplan']
    await driver.get('https://geocult.ru/natalnaya-karta-onlayn-raschet')
    asyncio.sleep(2)
    name_s = await driver.find_element(by = By.CSS_SELECTOR, value = 'input[name="fn"]')
    await name_s.send_keys('name')
    day_s = await driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fd"]')
    await day_s.send_keys('18')
    month_s = await driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fm"]')
    await month_s.send_keys('Мая') # родительный падеж
    year_s = await driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fy"]')
    await year_s.send_keys('2009')
    hour_s = await driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fh"]')
    await hour_s.send_keys('15')
    minute_s = await driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fmn"]')
    await minute_s.send_keys('27')
    country_s = await driver.find_element(value='country')
    await country_s.send_keys('Россия')
    asyncio.sleep(1)
    state_s = await driver.find_element(value='state')
    await state_s.send_keys('Новосибирская область')
    asyncio.sleep(2)
    cityplan_s = await driver.find_element(value='cityplan')
    asyncio.sleep(2)
    await cityplan_s.send_keys('Новосибирск')
    button = await driver.find_element(By.CLASS_NAME, 'natal_button')
    await button.click()
    await driver.switch_to.window(driver.window_handles[1])
    natal = await requests.get(driver.current_url)
    spaces = await BeautifulSoup(natal.text, 'html.parser')
    search_space = await fromstring(str(spaces))
    link = await search_space.xpath('//a[contains(@class, "fancybox")]/@href')[0]
    img = await requests.get(link)
    if img.status_code == 200:
        with await open("natal.jpg", "wb") as file:
            await file.write(img.content)
            await print("Картинка успешно скачана")
    else:
        await print("Не удалось скачать картинку")


async def main():

    # начинаем принимать новые сообщения
    await dp.start_polling(bot)  


if __name__ == '__main__':
    asyncio.run(main())
