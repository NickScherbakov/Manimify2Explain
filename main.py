"""
Главный модуль проекта Manimify2Explain.
Объединяет все компоненты и реализует общий пайплайн обработки PDF
и генерации Manim-сцены.
"""

import os
import sys
import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import networkx as nx

# Импортируем функции из наших модулей
from pdf_extractor import extract_text, extract_images
from table_processor import ocr_table, detect_table
from graph_processor import extract_graph_structure, is_graph_image
from manim_script_generator import generate_manim_script


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Преобразует изображение из байтов в формат numpy array.
    
    Args:
        image_bytes (bytes): Изображение в формате байтов.
        
    Returns:
        np.ndarray: Изображение в формате numpy array.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")
        return np.array([])


def process_images(images: List[Dict[str, Any]]) -> Tuple[str, Optional[nx.Graph]]:
    """
    Обрабатывает список изображений, извлекая текст таблиц и графовые структуры.
    
    Args:
        images (List[Dict[str, Any]]): Список изображений и их метаданных.
        
    Returns:
        Tuple[str, Optional[nx.Graph]]: Текст таблиц и объект графа (если найден).
    """
    table_texts = []
    best_graph = None
    max_nodes = 0
    
    for img_data in images:
        # Преобразуем изображение из байтов
        image = preprocess_image(img_data['image'])
        if image.size == 0:
            continue
        
        # Проверяем, является ли изображение таблицей
        if detect_table(image):
            # Если это таблица, извлекаем текст
            table_text = ocr_table(image)
            if table_text.strip():
                page_info = f"[Таблица со страницы {img_data['page_num'] + 1}]:\n"
                table_texts.append(page_info + table_text + "\n")
        
        # Проверяем, является ли изображение графом
        elif is_graph_image(image):
            # Извлекаем структуру графа
            graph = extract_graph_structure(image)
            
            # Выбираем граф с наибольшим количеством узлов
            if graph.number_of_nodes() > max_nodes:
                max_nodes = graph.number_of_nodes()
                best_graph = graph
    
    # Объединяем тексты всех таблиц
    combined_table_text = "\n".join(table_texts)
    
    return combined_table_text, best_graph


def main(pdf_path: str) -> None:
    """
    Основная функция для обработки PDF-документа и генерации Manim-скрипта.
    
    Args:
        pdf_path (str): Путь к PDF-файлу.
        
    Returns:
        None
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(pdf_path):
            print(f"Файл '{pdf_path}' не найден")
            return
        
        # Шаг 1: Извлекаем текст из PDF
        print("Извлекаем текст из PDF...")
        text = extract_text(pdf_path)
        
        # Шаг 2: Извлекаем изображения из PDF
        print("Извлекаем изображения из PDF...")
        images = extract_images(pdf_path)
        
        if not images:
            print("Изображения не найдены в PDF")
        
        # Шаг 3: Обрабатываем изображения
        print(f"Обрабатываем {len(images)} изображений...")
        table_text, graph = process_images(images)
        
        # Шаг 4: Генерируем Manim-скрипт
        print("Генерируем Manim-скрипт...")
        generate_manim_script(text, table_text, graph)
        
        print("Обработка завершена! Скрипт Manim сохранен в файле 'generated_manim_scene.py'")
        print("Чтобы запустить рендеринг, выполните команду:")
        print("manim -p -ql generated_manim_scene.py AutoScene")
        
    except Exception as e:
        print(f"Произошла ошибка в процессе выполнения: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python main.py <путь_к_pdf_файлу>")
    else:
        main(sys.argv[1])
