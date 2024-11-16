import telebot
from telebot import types
import config 
import sqlite3

# Создаем объект бота, используя токен из файла config / Create a bot object using the token from the config file
bot = telebot.TeleBot(config.Token)

# Подключение к базе данных / Connecting to the database
connection = sqlite3.connect('DB/Music_DB.db')
cursor = connection.cursor()

# Получаем список треков из таблицы Music / Retrieving the list of tracks from the Music table
cursor.execute('SELECT Track, Musical_group, Genre, Album, Duration FROM Music')
tracks = cursor.fetchall()
connection.close() 

# Создаем список имен треков / Creating a list of track names
tracks_name = [track for track, musical_group, genre, album, duration in tracks]

# Создаем словарь, где ключ — название трека, значение — его длительность / Creating a dictionary where the key is the track name and the value is its duration
track_duration = {}

# Добавляем в словарь track_duration треки с их длительностью / Add tracks with their duration to track_duration
for track, musical_group, genre, album, duration in tracks:
    track_duration[track] = duration

# Словари для хранения структуры музыки / Dictionaries for storing the music structure
dct = {} # Структура: группа -> альбом -> список треков / Structure: group -> album -> list of tracks
next_track_dct = {} # Следующий трек в альбоме / Next track in the album
back_track_dct = {} # Предыдущий трек в альбоме / Previous track in the album
next_album_dct = {} # Следующий альбом / Next album
back_album_dct = {} # Предыдущий альбом / Previous album


# Формируем вложенный словарь для треков по группам и альбомам / Creating a nested dictionary for tracks grouped by bands and albums
# Инициализируем ключи для каждой группы / Initialize keys for each musical group
for track, musical_group, genre, album, duration in tracks:
    if musical_group not in dct.keys():
        dct[musical_group] = {}

# Инициализируем ключи для каждого альбома внутри группы / Initialize keys for each album within a group
for track, musical_group, genre, album, duration in tracks:
    if album not in dct[musical_group].keys():
        dct[musical_group][album] = []    

# Добавляем треки в соответствующие группы и альбомы / Add tracks to the corresponding groups and albums
for track, musical_group, genre, album, duration in tracks:
    dct[musical_group][album].append(track)


# Формируем словари для переключения треков / Creating dictionaries for track navigation
for track, musical_group, genre, album, duration in tracks:
    lst_track = dct[musical_group][album]
    if lst_track.index(track) == len(lst_track) - 1: # Если трек последний, следующий — первый / If the track is the last one, the next is the first
        next_track_dct[track] = lst_track[0]
    else: # В противном случае следующий трек — следующий в списке / Otherwise, the next track is the next in the list
        next_track_dct[track] = lst_track[lst_track.index(track) + 1]

for track, musical_group, genre, album, duration in tracks:
    lst_track = dct[musical_group][album]
    if lst_track.index(track) == 0: # Если трек первый, предыдущий — последний / If the track is the first, the previous is the last
        back_track_dct[track] = lst_track[-1]
    else: # В противном случае предыдущий трек — предыдущий в списке / Otherwise, the previous track is the previous in the list
        back_track_dct[track] = lst_track[lst_track.index(track) - 1]

# Формируем словари для переключения альбомов / Creating dictionaries for album navigation
for track, musical_group, genre, album, duration in tracks:
    dct_album = list(dct[musical_group].keys())
    if dct_album.index(album) == len(dct_album) - 1: # Если альбом последний, следующий — первый / If the album is the last, the next is the first
        next_album_dct[track] = dct[musical_group][dct_album[0]][0]
    else: # В противном случае следующий альбом — следующий в списке / Otherwise, the next album is the next in the list
        next_album_dct[track] = dct[musical_group][dct_album[dct_album.index(album) + 1]][0]

for track, musical_group, genre, album, duration in tracks:
    dct_album = list(dct[musical_group].keys())
    if dct_album.index(album) == 0: # Если альбом первый, предыдущий — последний / If the album is the first, the previous is the last
        back_album_dct[track] = dct[musical_group][dct_album[0]][-1]
    else: # В противном случае предыдущий альбом — предыдущий в списке / Otherwise, the previous album is the previous in the list
        back_album_dct[track] = dct[musical_group][dct_album[dct_album.index(album) - 1]][0]


# Обработчик команды /start / Handler for the /start command
@bot.message_handler(commands = ['start'])
def start(message):
    try:
        # Создаем кнопку для поиска / Creating a search button
        markup = types.InlineKeyboardMarkup(row_width=1)
        item = types.InlineKeyboardButton('🔎Поиск', switch_inline_query_current_chat = "")

        markup.add(item)
        
        # Отправляем стикер / Send a sticker
        sti = open('DB/sticker.tgs','rb')
        bot.send_sticker(message.chat.id, sti)
        sti.close()

        # Отправляем приветственное сообщение с кнопкой / Sending a welcome message with a button
        bot.send_message(message.chat.id, 'Привет, {0.first_name}!\nЭто бот для прослушивания музыки'.format(message.from_user), reply_markup=markup)

    except Exception as e: # Логируем ошибки, если возникают / Log errors if they occur
        print("{0.id} {0.first_name} {0.last_name}: {1!s}\n{1!s}".format(message.from_user,type(e), str(e)))


# Обработчик inline-запросов / Handler for inline queries
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def get_text(query):
    try:    
        answ_list = [] # Список для хранения результатов / List to store results
        counter = 1 # Счетчик для уникальных идентификаторов результатов / Counter for unique result IDs

        # Перебираем треки и фильтруем их по тексту запроса / Iterate through tracks and filter by query text
        for track, musical_group, genre, album, duration in tracks:
            if track.lower().startswith(query.query.lower()): # Фильтруем треки по запросу / Filtering tracks by query
                # Описание трека / Track description
                description=f"Жанр: {genre}\nГруппа: {musical_group}\nАльбом: {album}" 

                # Добавляем результат в список / Add result to the list
                answ_list.append(types.InlineQueryResultArticle(
                                        id=f"{counter}", 
                                        title=f"{track}",
                                        description=description,
                                        input_message_content=types.InputTextMessageContent(
                                        message_text="{!s}".format(track))))
                counter += 1

        # Максимальное количество результатов / Maximum number of results
        n = 50 
        if counter < n: # Ограничиваем количество ответов, если их меньше n / Limit responses if less than n
            n = counter

        # Отправляем до n результатов / Sending up to n results
        bot.answer_inline_query(query.id, answ_list[:n]) 
  
    except Exception as e: # Логируем ошибки, если возникают / Log errors if they occur
        print("{0.id} {0.first_name} {0.last_name}: {1!s}\n{1!s}".format(query.from_user,type(e), str(e)))


# Обработчик текстовых сообщений / Handler for text messages
@bot.message_handler(content_types = ['text'])
def text_request(message):
    try:   
        text = message.text

        if text in tracks_name: # Проверяем, что трек существует / Checking that the track exists
            # Формируем путь к аудиофайлу трека/ Construct the file path to the audio track
            file_path = f'DB/music/{text}.mp3'

            # Создаем кнопки для переключения треков и альбомов / Creating buttons for track and album navigation
            markup = types.InlineKeyboardMarkup(row_width=4)
            item1 = types.InlineKeyboardButton('⏮', callback_data=back_album_dct[text])
            item2 = types.InlineKeyboardButton('⏪', callback_data=back_track_dct[text])
            item3 = types.InlineKeyboardButton('⏩', callback_data=next_track_dct[text])
            item4 = types.InlineKeyboardButton('⏭', callback_data=next_album_dct[text])

            markup.add(item1,item2,item3,item4)

            # Отправляем аудиофайл / Sending the audio file
            file = open(file_path, 'rb')
            bot.send_audio(message.chat.id, file, title=text, duration=track_duration[text], reply_markup=markup)
            file.close()

    except Exception as e:
        print("{0.id} {0.first_name} {0.last_name}: {1!s}\n{1!s}".format(message.from_user,type(e), str(e)))


# Обработчик callback-кнопок / Handler for callback buttons
@bot.callback_query_handler(func=lambda call: True)
def button(call):
    try: 
        if call.message:		
            if call.data in tracks_name: # Проверяем, что трек существует / Checking that the track exists
                # Формируем путь к аудиофайлу трека/ Construct the file path to the audio track
                file_path = f'DB/music/{call.data}.mp3'
                
                # Создаем кнопки для переключения треков и альбомов / Creating buttons for track and album navigation
                markup = types.InlineKeyboardMarkup(row_width=4)
                item1 = types.InlineKeyboardButton('⏮', callback_data=back_album_dct[call.data])
                item2 = types.InlineKeyboardButton('⏪', callback_data=back_track_dct[call.data])
                item3 = types.InlineKeyboardButton('⏩', callback_data=next_track_dct[call.data])
                item4 = types.InlineKeyboardButton('⏭', callback_data=next_album_dct[call.data])

                markup.add(item1,item2,item3,item4)

                # Отправляем аудиофайл / Sending the audio file
                file = open(file_path, 'rb')
                bot.send_audio(call.message.chat.id, file, title=call.data, duration=track_duration[call.data], reply_markup=markup)
                file.close()

                # Удаляем старое сообщение / Deleting the old message with buttons
                bot.delete_message(call.message.chat.id, call.message.message_id)
    
    except Exception as e: # Логируем ошибки, если возникают / Log errors if they occur
        print("{0.id} {0.first_name} {0.last_name}: {1!s}\n{1!s}".format(call.message.from_user,type(e), str(e)))


# Запуск бота / Starting the bot
bot.polling (none_stop=True)

