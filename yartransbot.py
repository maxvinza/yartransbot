# -*- coding: utf-8 -*-
import urllib.request
import re
import os
import logging
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import BaseFilter


class MyCommandFilter(BaseFilter):
    def filter(self, message):
        return message.text.startswith('/m')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TOKEN = os.environ.get('TOKEN', 'TOKEN')
PORT = int(os.environ.get('PORT', '8443'))
APP_NAME = 'yar-transport-tg-bot'


def razbor_msg(mess):
    mess = mess.lower()
    mess = (mess.replace(" ", ""))
    mess = (mess.replace("автобус", "а"))
    mess = (mess.replace("ав", "а"))
    mess = (mess.replace("троллейбус", "тр"))
    mess = (mess.replace("тб", "тр"))
    mess = (mess.replace("маршрутка", "мт"))
    mess = (mess.replace("трамвай", "тм"))
    return mess


def pars(mess):
    print(mess)
    need_try_mt = 0
    if mess[0] == '/':
        return command_bot(mess)
    num = re.sub(r'[^0-9]', '', mess)
    vt = re.sub(r"\d+", "", mess, flags=re.UNICODE)
    if vt == 'а':
        vt = 1
    elif vt == 'тр':
        vt = 2
    elif vt == 'тм':
        vt = 3
    elif vt == 'мт':
        vt = 4
    elif vt == '':
        vt = only_num(num)
        if vt == 0:
            return "Уточните вид трансорта, например а" + num + " - это будет соответствовать автобусу " + num
    else:
        need_try_mt = 1
    url = "http://ot76.ru/mob/getroutestr.php?vt=" + str(vt) + "&nmar=" + str(num)
    if need_try_mt == 1:
        url = kostili_marsh(mess)
        if url == "err":
            return "Вы ввели несуществующую комманду или несуществующий маршрут"
    htext = stand_replace(url)
    if len(htext) < 2:
        htext = 'Опять от тебя сбежала последняя электричка. Скорее всего, на маршруте сейчас никого.'
    return htext


# Определение вида транспорта по номеру
def only_num(num):
    num = int(num)
    if num < 10:
        if num == 2:
            return 1
        else:
            return 0
    else:
        if num > 9 and num < 36:
            return 1
        elif num > 35 and num < 40:
            return 4
        elif num > 39 and num < 45:
            return 1
        elif num > 44 and num < 52 and num != 49:
            return 4
        elif num == 49:
            return 1
        elif num > 51 and num < 61:
            return 1
        elif num > 60 and num < 69:
            return 4
        elif num == 70 or num == 77 or num == 78:
            return 1
        else:
            return 0


# Разбор нетепичных маршрутов - вроде тех, которы с литерами
def kostili_marsh(mess):
    if mess == 'а18к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=18k"
    elif mess == 'а2к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=2k"
    elif mess == 'а18м':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=18m"
    elif mess == 'а19к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=18k"
    elif mess == 'а4а':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=4a"
    elif mess == 'а21б':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=21b"
    elif mess == 'а21т':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=21t"
    elif mess == 'а22с':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=22c"
    elif mess == 'а29к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=29k"
    elif mess == 'а35д':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=35d"
    elif mess == 'а40к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=40k"
    elif mess == 'а41а':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=41a"
    elif mess == 'а41б':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=41b"
    elif mess == 'а44к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=44k"
    elif mess == 'а93г':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=93g"
    elif mess == 'а55к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=55k"
    elif mess == 'а55г':
        url = "http://ot76.ru/mob/getroutestr.php?vt=1&nmar=55g"
    elif mess == 'мт35м':
        url = "http://ot76.ru/mob/getroutestr.php?vt=4&nmar=35m"
    elif mess == 'мт85д':
        url = "http://ot76.ru/mob/getroutestr.php?vt=4&nmar=85d"
    elif mess == 'мт85к':
        url = "http://ot76.ru/mob/getroutestr.php?vt=4&nmar=85k"
    else:
        url = "err"
    return url


def stand_replace(url):
    htext = pars_replace(url)
    test_text = skobka_perenos(htext)
    soup = BeautifulSoup(test_text, 'html.parser')
    htext = soup.get_text()
    htext = (htext.replace("\n", ""))
    htext = (htext.replace("Прямо", "\nПрямо"))
    htext = (htext.replace("Обрат", "\nОбрат"))
    htext = (htext.replace("Борт", "\nБорт"))
    htext = (htext.replace("Расписание", "\n"))
    htext = (htext.replace("МУП ГПТ \"Яргортранс\"", ""))
    htext = (htext.replace("№БортТекущая остановкаВр.ост.Задержка, мин.", ""))  # getpeinfo.php?vt=
    htext = (htext.replace("getpeinfo.php?vt=", "/m"))
    htext = (htext.replace("None", ""))
    htext = (htext.replace("Прогноз прохождения", "\n\n"))
    htext = (htext.replace("&npe;=", "num"))  # Прогноз прохождения
    htext = (htext.replace(
        "К списку маршрутовнп - Низкопольное ТСпнп - Полунизкопольное ТСм/моб - Высокопольное ТС, оборудованное для перевозки маломобильных групп населениянул. - ТС следует в/из депо",
        ""))
    htext = (htext.replace("===", "\n"))
    return htext


# Другая ветка - разбор сообщения о для вызова комманды бота
def command_bot(mess):
    if len(mess) < 5:
        return "Пустая команда"
    if mess[1] == 'm' and mess[3] == 'n':
        mess = (mess.replace("/m", "getpeinfo.php?vt="))
        mess = (mess.replace("num", "&npe="))
        url = "http://ot76.ru/mob/" + mess
        mess = stand_replace(url)
        if len(mess) < 2:
            mess = "Возможно, что-то пошло не так, или вы ввели не ту комманду"
        return mess
    else:
        return "Неправильная комманда"


def pars_replace(url):
    # try:
    pmd = urllib.request.urlopen(url)
    # except requests.exceptions:
    #    return "Неправильная комманда"
    htext = pmd.read()
    htext = htext.decode('cp1251')
    return htext


# Разбор html-структуры страницы
def skobka_perenos(text):
    soup = BeautifulSoup(text, 'html.parser')
    textl = soup.find_all('tr')
    retstr = ''
    for strk in textl:
        soup = BeautifulSoup(str(strk), 'html.parser')
        retstr = retstr + razbor_td(str(strk))
    return retstr


def razbor_td(tr):
    soup = BeautifulSoup(tr, 'html.parser')
    textl = soup.find_all('td')
    if len(textl) > 2:
        return get_text(str(textl[1])) + " - " + get_text(str(textl[2])) + " - " + get_text(
            str(textl[3])) + " - " + str(make_ts(str(textl[5]))) + "==="  # str(make_ts(str(textl[3]))) + "\n"
    elif len(textl) == 2:
        return get_text(str(textl[0])) + " - " + get_text(str(textl[1])) + "==="
    else:
        return tr


def get_text(tsh):
    soup = BeautifulSoup(tsh, 'html.parser')
    return soup.get_text()


# На будущее - разбор url
def make_ts(tsh):
    soup = BeautifulSoup(tsh, 'html.parser')
    for link in soup.find_all('a'):
        return (link.get('href'))


def send_welcome(bot: Bot, update):
    message = update.message.text
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id,
                     text="Введите номер интересующего маршрута вида а23 или автобус23, тр1, тм1, мт96  ")


def echo_all(bot: Bot, update):
    input_mess = razbor_msg(update.message.text)
    out_mess = pars(input_mess)
    bot.send_message(chat_id=update.message.chat_id, text=out_mess)


my_command_filter = MyCommandFilter()
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', send_welcome))
dispatcher.add_handler(MessageHandler(Filters.text & my_command_filter, echo_all))
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.set_webhook("https://{0}.herokuapp.com/{1}".format(APP_NAME, TOKEN))
updater.idle()
