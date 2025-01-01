import sqlite3 as sql
from typing import List, Tuple, Dict, Any, Optional, Union
import os
import json

from .download_translations import create_directory_if_not_exists
from .constants import translations, books

def get_connection_for_translation(translation_abrev: Optional[str] = 'ACF') -> sql.Connection:
    return sql.connect(f"./translations/{translation_abrev}/{translation_abrev}.sqlite")

def get_book_abrev(book_name: str) -> str:
    book_dict: Dict[str, str] = next((book for book in books if book.get('name') == book_name), None)
    if book_dict is not None:
        return book_dict.get('abrev')

def get_books_info(conn: sql.Connection, translation_abrev: Optional[str] = 'ACF') -> Dict[str, Any]:
    try:
        books = []
        cursor: sql.Cursor = conn.cursor()
        query: str = 'SELECT * FROM book'
        result: List[Tuple[Any]] = cursor.execute(query).fetchall()

        for book in result:
            books.append({
                "id": book[0],
                "book_reference_id": book[1],
                "testament_reference_id": book[2],
                "name": get_book_abrev(book[3])
            })

        return books
    except Exception as e:
        raise(e)

def get_book_id(books_info: Dict[str, Any], book_abrev: str) -> int:
    book_dict: Dict[str, str] = next((book for book in books_info if book.get('name') == book_abrev), None)
    return book_dict.get('id')

def get_all_verses_from_book(book_abrev: str, translation_abrev: Optional[str] = 'ACF') -> List[Dict[str, Any]]:
    try:
        conn: sql.Connection = get_connection_for_translation(translation_abrev)
        book_id: int = get_book_id(get_books_info(conn, translation_abrev), book_abrev)
        cursor: sql.Cursor = conn.cursor()
        query: str = f'SELECT * FROM verse WHERE book_id={book_id};'
        result: List[Tuple[Any]] = cursor.execute(query).fetchall()

        return {
            "book": book_abrev,
            "verses": [{
                "chapter": verse[2],
                "verse": verse[3],
                "text": verse[4]
            } for verse in result]
        }
    except Exception as e:
        conn.close()
        raise(e)
        

def get_number_of_chapters(verses: List[Dict[str, Any]]) -> int:
    return max(
        verse.get("chapter") for verse in verses
    )

def split_verse_by_chapter(verses: List[Dict[str, Any]]) -> List[Dict[str, List]]:
    chapters: List[Dict[str, Union[List, int]]] = [{
        "chapter": i+1,
        "verses": []
    } for i in range(get_number_of_chapters(verses))]

    for verse in verses:
        chapters[verse.get("chapter") - 1].get("verses").append({
            "verse": verse.get("verse"),
            "text": verse.get("text")
        })

    return chapters

def save_all_verses() -> None:
    for translation in translations:
        try:
            for book in books:
                book_abrev: str = book.get('abrev')
                translation_abrev: str = translation.get('abrev')
                all_verses: Dict = get_all_verses_from_book(book_abrev, translation_abrev)
                splited_chapters: List[Dict] = split_verse_by_chapter(all_verses.get('verses'))

                for chapter in splited_chapters:
                    chapter_number: int = chapter.get("chapter")
                    dst_dir: str = f"./translations/{translation_abrev}/{book_abrev}"
                    create_directory_if_not_exists(dst_dir)
                    with open(f"{dst_dir}/{chapter_number}.json", "w") as file:
                        json.dump(chapter.get("verses"), file, ensure_ascii=False)

            os.remove(f'./translations/{translation.get("abrev")}/{translation.get("abrev")}.sqlite')
            print(f'Finalizado Separação da Tradução {translation.get("abrev")}')

        except Exception as e:
            print(f'Erro ao separar a tradução {translation.get("abrev")}.', e)
