import cv2
import numpy as np
from pytubefix import YouTube
from termcolor import colored
import os
import subprocess
import shutil
import time

ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']
COLOR_PRESETS = {
    'green': 'green',
    'white': 'white',
    'red': 'red',
    'blue': 'blue',
    'yellow': 'yellow',
    'cyan': 'cyan',
    'magenta': 'magenta',
    'black': 'white'
}

TRANSLATIONS = {
    'en': {
        'enter_url': "Enter YouTube video URL: ",
        'enable_audio': "Enable audio? (y/n): ",
        'available_colors': "Available colors:",
        'choose_color': "Choose color number: ",
        'downloading': "Downloading video...",
        'playing': "Playing video...",
        'ffplay_not_found': "FFplay not found. Audio will not be played.",
    },
    'zh': {
        'enter_url': "输入YouTube视频链接：",
        'enable_audio': "启用音频？(y/n)：",
        'available_colors': "可用颜色：",
        'choose_color': "选择颜色编号：",
        'downloading': "正在下载视频...",
        'playing': "正在播放视频...",
        'ffplay_not_found': "未找到FFplay。将不会播放音频。",
    },
    'ru': {
        'enter_url': "Введи ссылку на видео YouTube: ",
        'enable_audio': "Включить аудио? (y/n): ",
        'available_colors': "Доступные цвета:",
        'choose_color': "Выберите номер цвета: ",
        'downloading': "Загрузка видео...",
        'playing': "Воспроизведение видео...",
        'ffplay_not_found': "FFplay не найден. Аудио не будет воспроизводиться.",
    }
}

def get_ffplay_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_ffplay = os.path.join(script_dir, 'ffplay.exe')
    if os.path.exists(local_ffplay):
        return local_ffplay
    return 'ffplay'

def download_video(url, audio=False):
    yt = YouTube(url)
    if audio:
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    else:
        stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
    
    output_path = stream.download(filename='video.mp4')
    return output_path

def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows

def resize_frame(frame, new_width, new_height):
    return cv2.resize(frame, (new_width, new_height))

def frame_to_ascii(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ascii_frame = []
    for row in frame:
        ascii_row = [ASCII_CHARS[int(pixel / 25)] for pixel in row]
        ascii_frame.append(''.join(ascii_row))
    return '\n'.join(ascii_frame)

def play_video(video_path, audio=False, color='green'):
    cap = cv2.VideoCapture(video_path)
    
    if audio:
        ffplay_path = get_ffplay_path()
        try:
            subprocess.Popen([ffplay_path, '-nodisp', '-autoexit', video_path], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("FFplay не найден. Аудио не будет воспроизводиться.")
    
    columns, rows = get_terminal_size()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        new_columns, new_rows = get_terminal_size()
        if new_columns != columns or new_rows != rows:
            columns, rows = new_columns, new_rows
        
        ascii_frame = frame_to_ascii(resize_frame(frame, columns, rows))
        print('\033[H\033[J', end='')
        if color == 'black':
            print(colored(ascii_frame, 'white', 'on_black'), end='')
        else:
            print(colored(ascii_frame, color), end='')
        
        time.sleep(0.04)
    
    cap.release()

if __name__ == "__main__":
    print("Select language / Выберите язык / 选择语言:")
    print("1. English")
    print("2. 中文")
    print("3. Русский")
    lang_choice = input("Enter number / Введите номер / 输入数字: ")
    lang = ['en', 'zh', 'ru'][int(lang_choice) - 1]
    t = TRANSLATIONS[lang]

    url = input(t['enter_url'])
    audio = input(t['enable_audio']).lower() == 'y'
    
    print(t['available_colors'])
    for i, color in enumerate(COLOR_PRESETS.keys(), 1):
        print(f"{i}. {color}")
    
    color_choice = input(t['choose_color'])
    color = list(COLOR_PRESETS.keys())[int(color_choice) - 1]
    
    print(t['downloading'])
    video_path = download_video(url, audio)
    print(t['playing'])
    play_video(video_path, audio, COLOR_PRESETS[color])
    os.remove(video_path)