#/==================================================================\#
#                                                                    #
#\==================================================================/#

#\==================================================================/#
#/========================/ installed libs \========================\#

from typing import Set
import telebot, traceback, time, schedule

from telebot         import types
from multiprocessing import Process

#--------------------------\ project files /-------------------------#
import debug

from variables import * 
from data      import *
from emj       import *

#\==================================================================/#

TOKEN = '5394154180:AAFqG4zOj5ayVjDLn5Yeib4rGeh-p1TEo28'

bot = telebot.TeleBot(TOKEN)

#\==================================================================/#

#\==================================================================/#
directory = Directory() 

catalog = Catalog(MAINCAT_CONST)

status = f'{EMJ_RAISING_HAND} Начать'

handling_process = None

u_ids : Set[int] = set()
#\==================================================================/#

#\==================================================================/#
@bot.message_handler(commands=['start'])
def start(msg):
    global u_ids
    try:
        u_ids |= {msg.chat.id}
        keyboard = set_keyboard([status,
            f'{EMJ_NOTE} Категории', f'{EMJ_DISK} Каталог'
        ])
        bot.send_message(msg.chat.id, 
            f'{EMJ_HOUSE} Вы в главном меню!', reply_markup=keyboard
        )

    except:
        debug.saveLogs(f"[start]-->{traceback.format_exc()}")
        bot.send_message(msg.chat.id, 'Проблемы с начальной секцией!')
#\==================================================================/#

#\==================================================================/#
def send_msg(_ids : Set[int], _msg, markup = None) -> bool:
    try:
        for _id in _ids:
            bot.send_message(_id, _msg, reply_markup=markup)
    except:
        debug.saveLogs(f"[send_msg]-->{traceback.format_exc()}")
        return False
    return True
#\==================================================================/#

#\==================================================================/#
def init_handling():
    global directory, handling_process, u_ids

    try:
        handling_process = Process(
            target = handle_updates, 
            args=(u_ids, directory)
        )
        handling_process.start()
    except:
        debug.saveLogs(f"[init_handling]-->{traceback.format_exc()}")

def kill_handling():
    global handling_process

    try:
        if handling_process:
            handling_process.kill()
    except:
        debug.saveLogs(f"[kill_handling]-->{traceback.format_exc()}")

def send_directory(msg):
    global directory
    bot.send_message(msg.chat.id, directory)
        
def send_status(_status : str, _msg : str, key = [f'{EMJ_NOTE} Категории',
                                                  f'{EMJ_DISK} Каталог']):
    return _status, send_msg(u_ids, _msg, set_keyboard([_status] + key))

def config_directory(msg):
    global status, directory, handling_process, u_ids

    if len(catalog):
        txt = f'Получение данных по {catalog if len(catalog) < 10 else f"{len(catalog)} элементам"}'
        send_msg(u_ids, txt, types.ReplyKeyboardRemove())
        try:
            for _api_key, ind in zip(API_KEY_SET, range(len(API_KEY_SET))):
                send_msg(u_ids, f'Пробую парсить по {ind + 1} из {len(API_KEY_SET)} ключу.')
                directory.set_directory(catalog, _api_key)
                if directory.parsing:
                    status, _ = send_status(f'{EMJ_CROSS} Остановить', 
                                            f'Запросы получены!'     )
                    break
            else:
                directory.clear()
                status, _ = send_status(f'{EMJ_RAISING_HAND} Начать', 
                    f'Парсинг не доступен! '
                    f'Количество запросов превысило 500 за день.'
                )
                start(msg)
        except:
            debug.saveLogs(
                f"[config_directory]-->{traceback.format_exc()}"
            )
            status, _ = send_status(f'{EMJ_RAISING_HAND} Начать', 
                'Проблемы с конфигурированием каталога!'
            )

    else:
        bot.send_message(msg.chat.id, 
            'Для запуска добавьте категории в каталог. '
            'Категории -> Добавить.'
        )
    
    init_handling()

def show_categories_keyboard(msg):
    try:
        keyboard = set_keyboard([
            f'{EMJ_BACK_ARROW} Назад'   , 
            f'{EMJ_MAGNIFIER} Показать'  , 
            f'{EMJ_PLUS} Добавить'        , 
            f'{EMJ_BASKET} Удалить'       
        ])
        bot.send_message(
            msg.chat.id, 
            f'{EMJ_FILE_BOX} Вы в разделе "Категории"', 
            reply_markup=keyboard
        )
    except:
        debug.saveLogs(
            f"[show_categories_keyboard]-->{traceback.format_exc()}"
        )
        bot.send_message(msg.chat.id, 
            'Проблемы с выводом кнопок для категорий!'
        )

def show_categories(msg):
    global directory

    try:
        bot.send_message(msg.chat.id, 
            f'Загруженный: \n{len(directory.catalog)}', 
            reply_markup=types.ReplyKeyboardRemove()
        )
    except:
        bot.send_message(msg.chat.id, 
             'Загруженный (слишком много элементов для вывода): \n'
            f'{len(directory.catalog)}', 
            reply_markup=types.ReplyKeyboardRemove())
    try:
        keyboard = set_keyboard([
            f'{EMJ_BACK_ARROW} Назад', 
            f'{EMJ_MAGNIFIER} Показать', 
            f'{EMJ_PLUS} Добавить', 
            f'{EMJ_BASKET} Удалить'
        ])
        bot.send_message(msg.chat.id, f'Полный:\n{len(catalog)}')
        for ind, item in zip(range(len(catalog)), catalog):
            bot.send_message(msg.chat.id, f'{ind + 1}. {item}\n')
        bot.send_message(msg.chat.id, 
            f'Вывод закончен!', reply_markup=keyboard
        )
    except:
        bot.send_message(msg.chat.id, 
             'Полный (слишком много элементов для вывода):'
            f'\n{len(catalog)}', 
            reply_markup=keyboard
        )

def stop_handling(msg):
    global status, handling_process

    try:
        status = f'{EMJ_RAISING_HAND} Начать'

        directory.clear()

        kill_handling()

        keyboard = set_keyboard([status, 
            f'{EMJ_NOTE} Категории', f'{EMJ_DISK} Каталог'
        ])
        bot.send_message(msg.chat.id, 
            f'{EMJ_CROSS} Мониторинг запросов отключен!', 
            reply_markup=keyboard
        )
    except:
        debug.saveLogs(
            f"[stop_handling]-->{traceback.format_exc()}"
        )
        bot.send_message(msg.chat.id, 
            'Проблемы с остановкой обновлений категории!'
        )

def _add_category(msg):
    global status, directory, catalog

    try:
        catalog += msg.text
        bot.send_message(msg.chat.id, 
            f'{EMJ_DONE} Категория: "{msg.text}" добавлена в каталог!'
        )
        if status == f'{EMJ_CROSS} Остановить':

            kill_handling()

            bot.send_message(msg.chat.id, 
                f'Получение данных по {msg.text}', 
                reply_markup=types.ReplyKeyboardRemove()
            )
            directory.set_items(msg.text)
            if directory.parsing:
                keyboard = set_keyboard([status, 
                    f'{EMJ_NOTE} Категории', 
                    f'{EMJ_DISK} Каталог'
                ])
                bot.send_message(msg.chat.id, 
                    f'Запросы получены!', 
                    reply_markup=keyboard
                )
                init_handling()
            else:
                status = f'{EMJ_RAISING_HAND} Начать'
                bot.send_message(msg.chat.id, 
                    f'Парсинг не доступен! '
                     'Количество запросов превысило 500 за день.'
                )
                start(msg)
    except:
        debug.saveLogs(f"[_add_category]-->{traceback.format_exc()}")
        bot.send_message(msg.chat.id,
            'Проблемы с добавлением категории!'
        )

def add_category(msg):
    try:
        waiter = bot.send_message(msg.chat.id, 
            'Введите категорию для добавления в каталог поиска:'
        )
        bot.register_next_step_handler(waiter, _add_category)
    except:
        debug.saveLogs(f"[add_category]-->{traceback.format_exc()}")
        bot.send_message(msg.chat.id, 
            'Проблемы с добавлением категории!'
        )

def _del_category(msg):
    global status, directory, catalog
    
    try:
        if msg.text in catalog: 
            del catalog[msg.text]
            bot.send_message(msg.chat.id, 
                f'{EMJ_BASKET} Категория: "{msg.text}" удалена из каталога!')

        else: 
            bot.send_message(msg.chat.id,
                f'{EMJ_CROSS} Категория: "{msg.text}" нет в каталоге!'
            )

        if msg.text in directory.catalog:
            del directory.catalog[msg.text]

            if status == f'{EMJ_CROSS} Остановить': 
                kill_handling()

                directory.clear()

                config_directory(msg)
    except:
        debug.saveLogs(f"[_del_category]-->{traceback.format_exc()}")
        bot.send_message(msg.chat.id, 'Проблемы с удалением категории!')

def del_category(msg):
    try:
        waiter = bot.send_message(msg.chat.id, 
            'Введите категорию для удаления из каталога поиска:'
        )
        bot.register_next_step_handler(waiter, _del_category)
    except:
        debug.saveLogs(f"[del_category]-->{traceback.format_exc()}")
        bot.send_message(msg.chat.id, 'Проблемы с удалением категории!')

KEYBOARD_FUNC = {
    f'{EMJ_BACK_ARROW} Назад'    : start,
    f'{EMJ_PLUS} Добавить'       : add_category,
    f'{EMJ_BASKET} Удалить'      : del_category,
    f'{EMJ_CROSS} Остановить'    : stop_handling,
    f'{EMJ_DISK} Каталог'        : send_directory,
    f'{EMJ_MAGNIFIER} Показать'  : show_categories,
    f'{EMJ_RAISING_HAND} Начать' : config_directory,
    f'{EMJ_NOTE} Категории'      : show_categories_keyboard
}

@bot.message_handler(content_types=['text'])
def input_keyboard(msg):
    try:
        if msg.text in KEYBOARD_FUNC: KEYBOARD_FUNC[msg.text](msg)
    except:
        debug.saveLogs(f"[input_keyboard]-->{traceback.format_exc()}")
#\==================================================================/#


#\==================================================================/#       
"""
Updating directory
"""
handling_status = True
def handle_updates(_u_ids : Set[int], _directory : Directory) -> None:
    global handling_status

    def _send_req(_u_ids : Set[int], _directory : Directory) -> None:
        global handling_status
    
        try:
            for _api_key, ind in zip(API_KEY_SET, range(len(API_KEY_SET))):
                send_msg(_u_ids, f'Пробую парсить по {ind + 1} из {len(API_KEY_SET)} ключу.')
                items = _directory.update(_api_key)
                if _directory.parsing:
                    send_msg(_u_ids, 
                        f'Добавленно: {len(items)} новых организаций\n'
                    )
                    for ind, item in zip(range(len(items)), items):
                        send_msg(_u_ids, f'{ind + 1}. {item}\n')
                    break
            else:
                send_msg(_u_ids, 
                    'Парсинг не доступен! '
                    'Количество запросов превысило 500 за день.'
                )
                handling_status = False
    
            send_msg(_u_ids, directory)
        except:
            debug.saveLogs(f"[_send_req]-->{traceback.format_exc()}")
            handling_status = False

    try:
        schedule.every(
            UPDATE_DELAY
        ).hours.do(_send_req, _u_ids, _directory)
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            if not handling_status:
                handling_status = True
                break
    except:
        debug.saveLogs(f"[run_pending]-->{traceback.format_exc()}")
        return
#\==================================================================/#


#\==================================================================/#
"""
Making keyboard
"""
def set_keyboard(btns):
    try:
        key = get_keyboard()
        key.add(*gen_btns(btns))
        return key
    except:
        debug.saveLogs(f"[set_keyboard]-->{traceback.format_exc()}")
        key = types.ReplyKeyboardMarkup(resize_keyboard = True)
        key.add(types.KeyboardButton(f'{EMJ_BACK_ARROW} Назад'))
        return key

def get_keyboard(resize = True):
    return types.ReplyKeyboardMarkup(resize_keyboard = resize)

def get_btn(text):
    return types.KeyboardButton(text)

def gen_btns(btns):
    return (get_btn(txt) for txt in btns)
#\==================================================================/#


#\==================================================================/#
if __name__ == '__main__':
    try: 
        bot.polling(none_stop=True)
    except:
        debug.saveLogs(f"[error]-->{traceback.format_exc()}")
#\==================================================================/#
