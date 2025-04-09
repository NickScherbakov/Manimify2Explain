"""
Модуль для обработки таблиц с использованием OpenCV и pytesseract.
Предназначен для извлечения текста из изображений таблиц.
"""

import cv2
import numpy as np
import pytesseract
from typing import Union


def ocr_table(image: Union[np.ndarray, bytes]) -> str:
    """
    Извлекает текст из изображения, содержащего таблицу.
    
    Args:
        image (Union[np.ndarray, bytes]): Изображение таблицы в формате numpy array или bytes.
        
    Returns:
        str: Извлеченный текст из таблицы.
    """
    try:
        # Если изображение в формате байтов, преобразуем его в numpy array
        if isinstance(image, bytes):
            image = np.asarray(bytearray(image), dtype=np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        
        # Преобразуем изображение в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Применяем бинаризацию для улучшения качества OCR
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Применяем небольшую морфологическую операцию для удаления шума
        kernel = np.ones((1, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Используем pytesseract для извлечения текста
        # --oem 3 - использование LSTM OCR Engine
        # --psm 6 - предполагаем, что это один блок текста
        config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(binary, config=config)
        
        return text.strip()
        
    except Exception as e:
        print(f"Ошибка при OCR таблицы: {e}")
        return ""


def detect_table(image: Union[np.ndarray, bytes]) -> bool:
    """
    Определяет, содержит ли изображение таблицу.
    
    Args:
        image (Union[np.ndarray, bytes]): Изображение для анализа.
        
    Returns:
        bool: True, если найдена таблица, иначе False.
    """
    try:
        # Если изображение в формате байтов, преобразуем его в numpy array
        if isinstance(image, bytes):
            image = np.asarray(bytearray(image), dtype=np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        
        # Преобразуем изображение в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Применяем бинаризацию
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Находим горизонтальные и вертикальные линии
        # Настраиваем размеры структурных элементов
        horizontal_size = gray.shape[1] // 30
        vertical_size = gray.shape[0] // 30
        
        # Создаем структурные элементы
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
        
        # Выделяем горизонтальные и вертикальные линии
        horizontal = cv2.erode(binary, h_kernel)
        horizontal = cv2.dilate(horizontal, h_kernel)
        
        vertical = cv2.erode(binary, v_kernel)
        vertical = cv2.dilate(vertical, v_kernel)
        
        # Объединяем горизонтальные и вертикальные линии
        table_lines = cv2.add(horizontal, vertical)
        
        # Подсчитываем количество линий
        contours, _ = cv2.findContours(table_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Если найдено достаточное количество линий и пересечений, считаем, что это таблица
        return len(contours) > 5
        
    except Exception as e:
        print(f"Ошибка при обнаружении таблицы: {e}")
        return False
