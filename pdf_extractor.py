"""
Модуль для извлечения текста и изображений из PDF-файлов.
Использует библиотеку PyMuPDF (fitz) для работы с PDF.
"""

import fitz  # PyMuPDF
import io
from typing import List, Dict, Tuple, Any


def extract_text(pdf_path: str) -> str:
    """
    Извлекает весь текст из PDF-файла.
    
    Args:
        pdf_path (str): Путь к PDF-файлу.
        
    Returns:
        str: Весь извлеченный текст из документа.
    """
    try:
        # Открываем PDF-файл
        doc = fitz.open(pdf_path)
        
        # Список для хранения текста со всех страниц
        text_content = []
        
        # Проходим по всем страницам и извлекаем текст
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content.append(page.get_text())
        
        # Объединяем текст со всех страниц
        full_text = "\n".join(text_content)
        
        # Закрываем документ
        doc.close()
        
        return full_text
    
    except Exception as e:
        print(f"Ошибка при извлечении текста из PDF: {e}")
        return ""


def extract_images(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Извлекает все изображения из PDF-файла двумя способами:
    1. Извлекает встроенные изображения через page.get_images()
    2. Рендерит каждую страницу как растровое изображение
    
    Args:
        pdf_path (str): Путь к PDF-файлу.
        
    Returns:
        List[Dict[str, Any]]: Список словарей с изображениями и их метаданными.
            Каждый словарь содержит:
            - 'image': bytes - само изображение в формате байтов
            - 'ext': str - расширение файла (например, 'jpeg', 'png')
            - 'page_num': int - номер страницы
            - 'source': str - источник изображения ('embedded' или 'rendered')
    """
    try:
        # Открываем PDF-файл
        doc = fitz.open(pdf_path)
        print(f"Открыт PDF-документ: {pdf_path}, страниц: {len(doc)}")
        
        # Список для хранения извлеченных изображений
        images_list = []
        
        # СПОСОБ 1: Извлекаем встроенные изображения
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Получаем список изображений на странице
            image_list = page.get_images(full=True)
            print(f"Встроенных изображений на странице {page_num+1}: {len(image_list)}")
            
            # Обрабатываем каждое изображение
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]  # получаем xref изображения
                    
                    # Извлекаем изображение
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Добавляем информацию об изображении в список
                    images_list.append({
                        'image': image_bytes,
                        'ext': image_ext,
                        'page_num': page_num,
                        'index': img_index,
                        'source': 'embedded'
                    })
                except Exception as e:
                    print(f"Ошибка при извлечении встроенного изображения: {e}")
        
        # СПОСОБ 2: Рендерим каждую страницу как изображение
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            print(f"Рендеринг страницы {page_num+1} как изображение...")
            
            # Рендерим страницу как pixmap (рисунок) с высоким разрешением
            zoom_factor = 2.0  # Увеличиваем разрешение в 2 раза
            matrix = fitz.Matrix(zoom_factor, zoom_factor)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Преобразуем pixmap в bytes изображения (PNG)
            img_bytes = pixmap.tobytes("png")
            
            # Добавляем информацию об изображении в список
            images_list.append({
                'image': img_bytes,
                'ext': 'png',
                'page_num': page_num,
                'index': 0,  # Для рендеринга страницы индекс всегда 0
                'source': 'rendered'
            })
        
        # Закрываем документ
        doc.close()
        
        return images_list
    
    except Exception as e:
        print(f"Ошибка при извлечении изображений из PDF: {e}")
        return []
