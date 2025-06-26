import plotly.graph_objects as go
from typing import List, Tuple
import random

def generate_color_map(expedition_codes):
    """
    Generates a color map assigning a unique RGB color to each expedition code.
    """
    random.seed(42)
    color_map = {}
    for code in expedition_codes:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color_map[code] = f'rgb({r},{g},{b})'
    return color_map


def show_boxes(solutions: List[Tuple[Tuple[str, str], List[int]]], idx: int = None, cont_dims: Tuple[int, int, int] = (1350, 246, 259)) -> str:
    """
    Visualizes the loaded boxes in a 3D plot in a web browser using Plotly.

    Args:
        solutions (List[Tuple[Tuple[str, str], List[int]]]): A list of tuples
            where each tuple contains a box ID and a list of its dimensions
            and position in the format: (id, [x, y, z, length, width, height]).
        idx (int, optional): Index of the solution to visualize. If None, visualizes all solutions.
        cont_dims (Tuple[int, int, int]): Dimensions of the container in the format (length, width, height).

    Returns:
        str: HTML string of the rendered 3D plot.
    """
    # 1. Obtain the unique expedition codes from the solutions
    expeditions = set(exp_id for (_, exp_id), _ in solutions)

    # 2. Assign a unique color to each expedition code
    color_map = generate_color_map(expeditions)

    fig = go.Figure()

    for (box_id, exp_code), box_solution in solutions:
        x, y, z = box_solution[0:3]
        length, width, height = box_solution[3:6]

        color = color_map[exp_code]
        hover_text = (
            f"{box_id} (Exp: {exp_code})<br>"
            f"Dimensions: {length}x{width}x{height}<br>"
            f"Position: ({x}, {y}, {z})"
        )

        fig.add_trace(go.Mesh3d(
            x=[x, x + length, x + length, x, x, x + length, x + length, x],
            y=[y, y, y + width, y + width, y, y, y + width, y + width],
            z=[z, z, z, z, z + height, z + height, z + height, z + height],
            i=[7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
            name=f"{box_id}",
            hovertext=hover_text,
            color=color
        ))

    # Layout
    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            xaxis=dict(range=[0, cont_dims[0]]),
            yaxis=dict(range=[0, cont_dims[1]]),
            zaxis=dict(range=[0, cont_dims[2]]),
            aspectmode="data",
        ),
        title=f"Visualización de carga - Solución {idx}" if idx else "Visualización de carga",
    )
    html_figure = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html_figure
