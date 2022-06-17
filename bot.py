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

catalog = parsing.Catalog([
    'автомойка Центральный административный округ',
    'автомойка Северный административный округ'
])

status = 'Начать'
#\==================================================================/#

#\==================================================================/#
@bot.message_handler(commands=['start'])
def start(msg):
    try:
        keyboard = set_keyboard([status, 'Категории', 'Каталог'])
        bot.send_message(msg.chat.id, 'Приветсвую!', reply_markup=keyboard)

    except:
        debug.saveLogs(
            f"[start]-->{traceback.format_exc()}", 
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#
def send_directory(msg):
    global directory
    bot.send_message(msg.chat.id, directory)

def config_directory(msg):
    global status, directory

    bot.send_message(msg.chat.id, f'Получение данных по {catalog}', reply_markup=types.ReplyKeyboardRemove())
    directory.set_directory(catalog)
    status = 'Остановить'
    keyboard = set_keyboard([status, 'Категории', 'Каталог'])
    bot.send_message(msg.chat.id, f'Запросы получены!', reply_markup=keyboard)

def show_categories_keyboard(msg):
    keyboard = set_keyboard(['Назад', 'Показать', 'Добавить', 'Удалить'])
    bot.send_message(msg.chat.id, 'Приветсвую!', reply_markup=keyboard)

def show_categories(msg):
    global directory

    bot.send_message(msg.chat.id, f'Загруженный: \n{directory.catalog}')
    bot.send_message(msg.chat.id, f'Полный:      \n{catalog}')

def stop_handling(msg):
    global status

    status = 'Начать'

    directory.clear()

    keyboard = set_keyboard([status, 'Категории', 'Каталог'])
    bot.send_message(msg.chat.id, f'Мониторинг запросов отключен!', reply_markup=keyboard)

def _add_category(msg):
    global status, directory, catalog

    catalog += msg.text
    bot.send_message(msg.chat.id, f'Категория: "{msg.text}" добавлена в каталог!')
    if status == 'Остановить':
        bot.send_message(msg.chat.id, f'Получение данных по {msg.text}', reply_markup=types.ReplyKeyboardRemove())
        directory.set_items(msg.text)
        keyboard = set_keyboard([status, 'Категории', 'Каталог'])
        bot.send_message(msg.chat.id, f'Запросы получены!', reply_markup=keyboard)

def add_category(msg):
    waiter = bot.send_message(msg.chat.id, 'Введите категорию для добавления в каталог поиска:')
    bot.register_next_step_handler(waiter, _add_category)

def _del_category(msg):
    global status, directory, catalog
    
    if msg.text in catalog: 
        del catalog[msg.text]
        bot.send_message(msg.chat.id, f'Категория: "{msg.text}" удалена из каталога!')

    else: bot.send_message(msg.chat.id, f'Категория: "{msg.text}" нет в каталоге!')

    if msg.text in directory.catalog:
        del directory.catalog[msg.text]

        if status == 'Остановить': config_directory(msg)


def del_category(msg):
    waiter = bot.send_message(msg.chat.id, 'Введите категорию для удаления из каталога поиска:')
    bot.register_next_step_handler(waiter, _del_category)

KEYBOARD_FUNC = {
    'Каталог'   : send_directory,
    'Начать'    : config_directory,
    'Категории' : show_categories_keyboard,
    'Показать'  : show_categories,
    'Назад'     : start,
    'Остановить': stop_handling,
    'Добавить'  : add_category,
    'Удалить'   : del_category
}

@bot.message_handler(content_types=['text'])
def input_keyboard(msg):
    global status

    try:
        bot.send_message(msg.chat.id, str(status))
        if msg.text in KEYBOARD_FUNC: KEYBOARD_FUNC[msg.text](msg)

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

def set_keyboard(btns):
    key = get_keyboard()
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
