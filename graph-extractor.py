"""
Скрипт для извлечения из PDF-документа min-ege1.pdf.pdf только изображений графов.
Извлечение изображений выполняется функцией extract_images из [pdf_extractor.py](pdf_extractor.py),
а определение, является ли изображение графом, — функцией is_graph_image из [graph_processor.py](graph_processor.py).
Найденные графы сохраняются в папку extr-graphs.
"""

import os
import cv2
import numpy as np
from pdf_extractor import extract_images  # [pdf_extractor.extract_images](pdf_extractor.py)
from graph_processor import is_graph_image  # [graph_processor.is_graph_image](graph_processor.py)

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Преобразует изображение из байтов в numpy array.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")
        return np.array([])

def save_image(image: np.ndarray, output_dir: str, base_name: str, index: int) -> None:
    """
    Сохраняет изображение в указанную директорию.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_path = os.path.join(output_dir, f"{base_name}_{index}.png")
    cv2.imwrite(file_path, image)
    print(f"Сохранено графическое изображение: {file_path}")

def main(pdf_path: str, output_dir: str) -> None:
    """
    Основная функция для извлечения и сохранения всех изображений из PDF.
    """
    print(f"Извлечение изображений из PDF: {pdf_path}")
    images = extract_images(pdf_path)
    print(f"Всего извлечено изображений из PDF: {len(images)}")
    
    # Если проблема в том, что изображения не извлекаются вообще
    if len(images) == 0:
        print("ВНИМАНИЕ: Из PDF не извлечено ни одного изображения!")
        return
    
    # Создаем выходной каталог, если он не существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Сохраняем все изображения
    for i, img_data in enumerate(images):
        print(f"\nСохранение изображения {i+1}/{len(images)}")
        print(f"  - Формат изображения: {img_data['ext']}")
        print(f"  - Номер страницы: {img_data['page_num']}")
        
        image = preprocess_image(img_data['image'])
        if image.size == 0:
            print("  - ПРОПУСК: Ошибка при обработке изображения")
            continue
        
        # Сохраняем изображение
        file_path = os.path.join(output_dir, f"image_{img_data['page_num']}_{i}.png")
        cv2.imwrite(file_path, image)
        print(f"  - Сохранено изображение: {file_path}")
    
    print(f"\nВсего сохранено изображений: {len(images)}")
    print("Извлечение завершено.")

if __name__ == "__main__":
    pdf_file = "textbooks/min-ege1.pdf"
    output_directory = "extr-graphs"
    main(pdf_file, output_directory)