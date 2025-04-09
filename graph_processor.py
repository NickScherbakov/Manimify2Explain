"""
Модуль для анализа изображений, содержащих графы или диаграммы,
и преобразования их в структуры данных с помощью NetworkX.
"""

import cv2
import numpy as np
import networkx as nx
from typing import Union, Tuple


def extract_graph_structure(image: Union[np.ndarray, bytes]) -> nx.Graph:
    """
    Анализирует изображение, содержащее граф или диаграмму,
    и преобразует его в структуру графа NetworkX.
    
    Args:
        image (Union[np.ndarray, bytes]): Изображение с графом в формате numpy array или bytes.
        
    Returns:
        nx.Graph: Объект графа NetworkX, представляющий структуру из изображения.
    """
    try:
        # Если изображение в формате байтов, преобразуем его в numpy array
        if isinstance(image, bytes):
            image = np.asarray(bytearray(image), dtype=np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        
        # Преобразуем изображение в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Применяем бинаризацию для выделения элементов графа
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Находим контуры на изображении
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Создаем пустой граф
        graph = nx.Graph()
        
        # Фильтруем контуры по площади (оставляем только значимые)
        significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]
        
        # Добавляем узлы в граф
        for i, contour in enumerate(significant_contours):
            # Вычисляем центр контура
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            
            # Добавляем узел в граф с координатами центра
            graph.add_node(i, pos=(cX, cY), contour=contour)
        
        # Определяем связи между узлами (на основе расстояния)
        nodes = list(graph.nodes())
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                node1_pos = graph.nodes[i]['pos']
                node2_pos = graph.nodes[j]['pos']
                
                # Вычисляем евклидово расстояние между центрами
                distance = np.sqrt((node1_pos[0] - node2_pos[0])**2 + 
                                   (node1_pos[1] - node2_pos[1])**2)
                
                # Если расстояние меньше порога, считаем узлы связанными
                # Порог можно адаптировать в зависимости от размера изображения
                threshold = min(image.shape[0], image.shape[1]) / 5
                if distance < threshold:
                    graph.add_edge(i, j, weight=distance)
        
        return graph
    
    except Exception as e:
        print(f"Ошибка при извлечении структуры графа: {e}")
        return nx.Graph()


def is_graph_image(image: Union[np.ndarray, bytes]) -> bool:
    """
    Определяет, содержит ли изображение структуру графа.
    
    Args:
        image (Union[np.ndarray, bytes]): Изображение для анализа.
        
    Returns:
        bool: True, если найдена структура графа, иначе False.
    """
    try:
        # Получаем граф из изображения
        graph = extract_graph_structure(image)
        
        # Если в графе есть узлы и ребра, считаем, что это изображение графа
        return graph.number_of_nodes() > 2 and graph.number_of_edges() > 1
    
    except Exception as e:
        print(f"Ошибка при определении графа на изображении: {e}")
        return False
