# разбираемся с aiogram
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router, html
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
driver.get('https://geocult.ru/natalnaya-karta-onlayn-raschet')
time.sleep(2)
name_s = driver.find_element(by = By.CSS_SELECTOR, value = 'input[name="fn"]')
name_s.send_keys('name')
day_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fd"]')
day_s.send_keys('18')
month_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fm"]')
month_s.send_keys('Мая') # родительный падеж
year_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fy"]')
year_s.send_keys('2009')
hour_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fh"]')
hour_s.send_keys('15')
minute_s = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fmn"]')
minute_s.send_keys('27')
country_s = driver.find_element(value='country')
country_s.send_keys('Россия')
time.sleep(1)
state_s = driver.find_element(value='state')
state_s.send_keys('Новосибирская область')
time.sleep(2)
cityplan_s = driver.find_element(value='cityplan')
time.sleep(2)
cityplan_s.send_keys('Новосибирск')
button = driver.find_element(By.CLASS_NAME, 'natal_button')
button.click()
driver.switch_to.window(driver.window_handles[1])
natal = requests.get(driver.current_url)
spaces = BeautifulSoup(natal.text, 'html.parser')
search_space = fromstring(str(spaces))
link = search_space.xpath('//a[contains(@class, "fancybox")]/@href')[0]
img = requests.get(link)
if img.status_code == 200:
    with open("natal.jpg", "wb") as file:
        file.write(img.content)
        print("Картинка успешно скачана")
else:
    print("Не удалось скачать картинку")


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
    print('я выжил')
    await state.update_data(year=message.text)
    await state.set_state(Form.month)
    await message.answer('Отлично! введите месяц своего рождения цифрой от 1 до 12')

async def main():

    # начинаем принимать новые сообщения
    await dp.start_polling(bot)  


if __name__ == '__main__':
    asyncio.run(main())
