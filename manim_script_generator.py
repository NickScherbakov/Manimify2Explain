"""
Модуль для генерации Python-скриптов для Manim
на основе извлечённого текста, таблиц и графов.
"""

import networkx as nx
from typing import Optional


def generate_manim_script(text: str, table_text: Optional[str] = None, graph: Optional[nx.Graph] = None) -> None:
    """
    Генерирует Python-скрипт для Manim на основе предоставленных данных.
    
    Args:
        text (str): Основной текст из PDF-документа.
        table_text (Optional[str]): Текст, извлеченный из таблиц.
        graph (Optional[nx.Graph]): Граф, извлеченный из изображений.
        
    Returns:
        None: Функция создает файл generated_manim_scene.py с кодом Manim.
    """
    try:
        # Начинаем формировать скрипт для Manim
        script_lines = ["from manim import *\n\n"]
        
        # Добавляем класс сцены
        script_lines.append("class AutoScene(Scene):")
        script_lines.append("    def construct(self):")
        
        # Если текст не пустой, добавляем его отображение
        if text and text.strip():
            # Для длинного текста берем только первые 500 символов
            display_text = text[:500] if len(text) > 500 else text
            
            script_lines.append("        # Отображение основного текста")
            script_lines.append(f'        main_text = Text("""')
            script_lines.append(f'{display_text}')
            script_lines.append(f'        """, font_size=24)')
            script_lines.append("        main_text.to_edge(UP)")
            script_lines.append("        self.play(Write(main_text))")
            script_lines.append("        self.wait(2)\n")
        
        # Если есть текст таблицы, отображаем его
        if table_text and table_text.strip():
            script_lines.append("        # Отображение таблицы")
            script_lines.append(f'        table_content = Text("""')
            script_lines.append(f'{table_text}')
            script_lines.append(f'        """, font_size=20)')
            script_lines.append("        table_content.next_to(main_text, DOWN, buff=0.5)")
            script_lines.append("        self.play(FadeIn(table_content))")
            script_lines.append("        self.wait(2)\n")
        
        # Если есть граф и в нем есть узлы, визуализируем его
        if graph and graph.number_of_nodes() > 0:
            script_lines.append("        # Создание и отображение графа")
            script_lines.append("        vertices = {}")
            script_lines.append("        edges = []")
            
            # Добавляем узлы
            for node in graph.nodes():
                # Получаем позицию узла из атрибутов графа
                pos = graph.nodes[node].get('pos', (0, 0))
                # Нормализуем координаты для Manim (от -4 до 4 по обеим осям)
                norm_x = (pos[0] / 500 - 0.5) * 8
                norm_y = (pos[1] / 500 - 0.5) * 8
                script_lines.append(f'        vertices["{node}"] = [{norm_x}, {norm_y}, 0]')
            
            # Добавляем ребра
            for u, v in graph.edges():
                script_lines.append(f'        edges.append(("{u}", "{v}"))')
            
            # Создаем объект графа в Manim
            script_lines.append("\n        # Создаем граф Manim")
            script_lines.append('        manim_graph = Graph(vertices=list(vertices.keys()), edges=edges, layout=vertices,')
            script_lines.append('                           vertex_config={"radius": 0.2}, edge_config={"stroke_width": 2})')
            
            # Если есть текст или таблица, располагаем граф под ними
            if text or table_text:
                reference = "table_content" if table_text else "main_text"
                script_lines.append(f"        manim_graph.next_to({reference}, DOWN, buff=1)")
            else:
                script_lines.append("        manim_graph.move_to(ORIGIN)")
            
            # Анимируем появление графа
            script_lines.append("        self.play(Create(manim_graph))")
            script_lines.append("        self.wait(3)")
        
        # Заключительное ожидание перед завершением анимации
        script_lines.append("\n        # Финальная пауза")
        script_lines.append("        self.wait(2)")
        
        # Записываем сгенерированный скрипт в файл
        with open('generated_manim_scene.py', 'w', encoding='utf-8') as f:
            for line in script_lines:
                f.write(line + '\n')
        
        print("Manim-скрипт успешно сгенерирован и сохранен в файл 'generated_manim_scene.py'")
        
    except Exception as e:
        print(f"Ошибка при генерации Manim-скрипта: {e}")
