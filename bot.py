# разбираемся с aiogram
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
import requests
from bs4 import BeautifulSoup
from very_secret_info import token
from aiogram.filters.command import Command
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from lxml.html.soupparser import fromstring

# все, что происходит далее - чистой воды прикол ради прикола 
# не судите меня строго, зато я изучаю http запросы и методы

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) 
driver.get('https://geocult.ru/natalnaya-karta-onlayn-raschet')
time.sleep(2)
name = driver.find_element(by = By.CSS_SELECTOR, value = 'input[name="fn"]')
name.send_keys('name')
day = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fd"]')
day.send_keys('18')
month = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fm"]')
month.send_keys('Мая') # родительный падеж
year = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fy"]')
year.send_keys('2009')
hour = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fh"]')
hour.send_keys('15')
minute = driver.find_element(by = By.CSS_SELECTOR, value = 'select[name="fmn"]')
minute.send_keys('27')
country = driver.find_element(value='country')
country.send_keys('Россия')
time.sleep(1)
state = driver.find_element(value='state')
state.send_keys('Новосибирская область')
time.sleep(2)
cityplan = driver.find_element(value='cityplan')
time.sleep(2)
cityplan.send_keys('Новосибирск')
button = driver.find_element(By.CLASS_NAME, 'natal_button')
button.click()
driver.switch_to.window(driver.window_handles[1])
natal = requests.get(driver.current_url)
spaces = BeautifulSoup(natal.text, 'html.parser')
search_space = fromstring(str(spaces))
link = search_space.xpath('//a[contains(@class, "fancybox")]/@href')[0]
img = requests.get(link)
if img.status_code == 200:
    with open("img.jpg", "wb") as file:
        file.write(img.content)
        print("Картинка успешно скачана")
else:
    print("Не удалось скачать картинку")


# pic = driver.find_element(By.CSS_SELECTOR, 'a.fancybox img')

# настраиваем логирование
logging.basicConfig(level='INFO')
# создаем объект бота
bot = Bot(token=token)
# создаем диспетчера
dp = Dispatcher()


# обработчик команды start
@dp.message(Command('start'))  # будет работать только после команды start
async def bot_start(message: types.Message):
    await message.answer('Hello')  # обычное сообщение

@dp.message(Command('natal_chart')) # команда для натальной карты
async def bot_natal_chart(message: types.Message):
    await message.answer('''
Расчет вашей натальной карты
                         
В этой функции мы рассмотрим, как сошлись звезды во время вашего рождения, и расскажем вам, что значат по астрологии эти соединения небесных тел
                         ''')


async def main():
    await dp.start_polling(bot)  # начинаем принимать новые сообщения


if __name__ == '__main__':
    asyncio.run(main())
