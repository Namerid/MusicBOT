import sqlite3
import os
from mutagen import File

def get_list_files(file_path):
    return os.listdir(file_path)

def get_audio_metadata(file_path):
    audio_file = File(file_path, easy=True)

    metadata = [
        file_path[6:-4],
        audio_file.get('genre', ['Неизвестно'])[0],
        audio_file.get('artist', ['Неизвестно'])[0],
        audio_file.get('album', ['Неизвестно'])[0],
        str(int(audio_file.info.length))
    ]
    return metadata

def main():
    conn = sqlite3.connect('Music_DB.db')

    cur = conn.cursor()

    for name in get_list_files(r'music'):
        cur.execute("""INSERT INTO Music(
                    Track, Genre, Musical_group, Album, Duration)
                    VALUES(?, ?, ?, ?, ?)""", get_audio_metadata(f'music/{name}'))

        conn.commit()

    conn.close()

main()