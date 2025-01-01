from .constants import translations
from typing import Optional, Union, Dict
import requests
import os
import zipfile

def create_directory_if_not_exists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(link: str, file_name: str, dst_dir: Optional[str] = '.') -> None:
    try:
        response = requests.get(link)
        with open(f"{dst_dir}/{file_name}", "wb") as file:
            file.write(response.content)
    except Exception as e:
        print(type(e))
        print('Erro:', e)

def get_translation_dict_by_abrev(translation_abrev: str) -> Union[Dict[str, str], None]:
    return next((translation for translation in translations if translation.get('abrev') == translation_abrev), None)

def download_translation(translation: str) -> None:
    dst_dir: str = f'./translations/{translation}'
    create_directory_if_not_exists(dst_dir)
    translation_dict = get_translation_dict_by_abrev(translation)
    if translation_dict is not None:
        drive_url: str = f"https://drive.google.com/uc?export=download&id={translation_dict.get('google_drive_id')}"
        download_file(drive_url, f"{translation}.zip", dst_dir)
    else:
        raise Exception(f'Não há a tradução {translation}.')

def unzip_translation(translation: str) -> None:
    with zipfile.ZipFile(f"./translations/{translation}/{translation}.zip", "r") as zip_ref:
            zip_ref.extractall(f"./translations/{translation}")
    os.remove(f"./translations/{translation}/{translation}.zip")

def download_all_translations() -> None:
    for translation in translations:
        translation_abrev: str = translation.get('abrev')
        download_translation(translation_abrev)
        unzip_translation(translation_abrev)
        print(f'Downloaded {translation_abrev}')