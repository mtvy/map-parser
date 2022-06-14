#/==================================================================\#
#                                                                    #
#\==================================================================/#

#\==================================================================/#
#/========================/ installed libs \========================\#

import telebot, traceback, time, schedule

from telebot         import types
from multiprocessing import Process

#--------------------------\ project files /-------------------------#
import parsing, debug, path

from variables import * 

#\==================================================================/#

TOKEN = '5048751728:AAEoeJt79rmJhZvXS8do0ndU-hpjysi47zY'

bot = telebot.TeleBot(TOKEN)

#\==================================================================/#

#\==================================================================/#
directory = parsing.Directory()
"""

### Directory

\# Search: [<catalog>]   

> Added: Number    
> BoundedBy: [[<coordinates>]]

"""

catalog = [
    'автомойка Центральный административный округ',
    'автомойка Северный административный округ'
]
#\==================================================================/#

#\==================================================================/#
@bot.message_handler(commands=['start'])
def start(msg):
    try:
        keyboard = set_keyboard(['Начать', 'Категории', 'Словарь'])
        bot.send_message(msg.chat.id, '> init keyboard', reply_markup=keyboard)

    except:
        debug.saveLogs(
            f"[start]-->{traceback.format_exc()}", 
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#
@bot.message_handler(content_types=['text'])
def input_keyboard(msg):
    try:
        if msg.chat.type == 'private':

            if msg.text == 'Словарь':
                bot.send_message(msg.chat.id, directory)
            
            elif msg.text == 'Начать':
                bot.send_message(msg.chat.id, f'Получение данных по {catalog}')

                directory.set_directory(catalog)
                bot.send_message(msg.chat.id, f'Запросы получены!')

    except:
        debug.saveLogs(
            f"[input_keyboard]-->{traceback.format_exc()}", 
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        pass

    except:
        debug.saveLogs(
            f"[call]-->{traceback.format_exc()}",
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#
            
class UpdateHandler:

    def handle_updates():
        
        schedule.every(
            UPDATE_DELAY
        ).seconds.do(UpdateHandler.send_request)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def send_request():
        try: 
            pass
        
        except:
            debug.saveLogs(
                f"[UpdateHandler]-->{traceback.format_exc()}",
                path.log_file
            )
#\==================================================================/#


#\==================================================================/#

def get_keyboard(resize = True):
    return types.ReplyKeyboardMarkup(resize_keyboard = resize)

def get_btn(text):
    return types.KeyboardButton(text)

def gen_btns(btns):
    return (get_btn(txt) for txt in btns)

def set_keyboard(btns, key = get_keyboard()):
    key.add(*gen_btns(btns))
    return key
#\==================================================================/#


#\==================================================================/#
if __name__ == '__main__':
    #Process(target = UpdateHandler.handle_updates, args = ()).start()
    try: 
        bot.polling(none_stop=True)

    except:
        debug.saveLogs(
            f"[error]-->{traceback.format_exc()}", 
            path.log_file
        )
#\==================================================================/#
