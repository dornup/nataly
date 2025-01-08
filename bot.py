# разбираемся с aiogram
import os
from typing import Dict, Any
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router, html
from aiogram.types.input_file import FSInputFile
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
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from lxml.html.soupparser import fromstring
from calendar import monthrange

m = {
    '1': 'Января',
    '2': 'Февраля',
    '3': 'Марта',
    '4': 'Апреля',
    '5': 'Мая',
    '6': 'Июня',
    '7': 'Июля',
    '8': 'Августа',
    '9': 'Сентября',
    '10': 'Октября',
    '11': 'Ноября',
    '12': 'Декабря',
}

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

# driver = WebDriver(service=ChromeService())
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
    data = await state.update_data(month=message.text)
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
async def hour(message: types.Message, state: FSMContext):
    await state.update_data(day = message.text)
    await state.set_state(Form.hour)
    await message.answer("Хорошо, введите час своего рождения")

@form_router.message(Form.hour)
async def hour(message: types.Message, state: FSMContext):
    await state.update_data(hour = message.text)
    await state.set_state(Form.minute)
    await message.answer("Продолжим, введите минуту своего рождения")

@form_router.message(Form.minute)
async def country(message: types.Message, state: FSMContext):
    await state.update_data(minute = message.text)
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
    driver = WebDriver(service=ChromeService())
    name = data['name']
    year = data['year']
    month = data['month']
    day = data['day']
    hour = data['hour']
    minute = data['minute']
    country = data['country']
    state = data['state']
    city = data['cityplan']
    driver.get('https://geocult.ru/natalnaya-karta-onlayn-raschet')
    await asyncio.sleep(2)
    name_s = driver.find_element(by = By.CSS_SELECTOR, value = 'input[name="fn"]')
    name_s.send_keys(name)
    day_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fd"]')
    day_s.send_keys(day)
    month_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fm"]')
    month_s.send_keys(m[month]) # родительный падеж TODO: СДЕЛАТЬ ЗАМЕНУ ЦИФРЫ НА МЕСЯЦ В РОДИТЕЛЬНОМ ПАДЕЖЕ
    year_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fy"]')
    year_s.send_keys(year)
    hour_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fh"]')
    hour_s.send_keys(hour)
    minute_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fmn"]')
    minute_s.send_keys(minute)
    country_s = driver.find_element(value='country')
    country_s.send_keys(country)
    await asyncio.sleep(1)
    state_s = driver.find_element(value='state')
    state_s.send_keys(state)
    await asyncio.sleep(2)
    cityplan_s = driver.find_element(value='cityplan')
    await asyncio.sleep(2)
    cityplan_s.send_keys(city)
    button = driver.find_element(By.CLASS_NAME, 'natal_button')
    button.click()
    driver.switch_to.window(driver.window_handles[1])
    natal = requests.get(driver.current_url)
    spaces = BeautifulSoup(natal.text, 'html.parser')
    search_space = fromstring(str(spaces))
    # link = search_space.xpath('//a[contains(@class, "fancybox")]/@href')[0]
    link = search_space.xpath('//*[@id="r660"]/@href')[0]
    print(link)
    img = requests.get(link)
    if img.status_code == 200:
        with open("natal.jpg", "wb") as file:
            file.write(img.content)
            print("Картинка успешно скачана")
            photo = FSInputFile('natal.jpg')
            await bot.send_photo(chat_id=message.chat.id, photo=photo)
    else:
        print("Не удалось скачать картинку")
        await message.answer('Не удалось скачать картинку, попробуйте повторить позже(')
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.close()



async def main():

    # начинаем принимать новые сообщения
    await dp.start_polling(bot)  


if __name__ == '__main__':
    asyncio.run(main())
