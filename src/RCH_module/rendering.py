import plotly.graph_objects as go
from typing import List, Tuple


def show_boxes(solutions: List[Tuple[Tuple[str, str], List[int]]], idx: int = 1) -> None:
    """
    Visualizes the loaded boxes in a 3D plot in a web browser using Plotly.

    Args:
        solutions (List[Tuple[Tuple[str, str], List[int]]]): A list of tuples
            where each tuple contains a box ID and a list of its dimensions
            and position in the format: (id, [x, y, z, length, width, height]).
    """
    fig = go.Figure()
    for id, box_solution in solutions:
        x, y, z = box_solution[0:3]
        length, width, height = box_solution[3:6]

        hover_text = f"{id}<br>Dimensions: {length}x{width}x{height}<br>Position: ({x}, {y}, {z})"
        fig.add_trace(go.Mesh3d(
            x=[x, x + length, x + length, x, x, x + length, x + length, x],
            y=[y, y, y + width, y + width, y, y, y + width, y + width],
            z=[z, z, z, z, z + height, z + height, z + height, z + height],
            i=[7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
            name=f"{id}",
            hovertext=hover_text
        ))

        # Set layout properties
        fig.update_layout(
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                aspectmode="data"
            )
        )

    # Show the interactive plot
    fig.write_html(f"data/outputs/graphic_display/solution_{idx}.html", auto_open=True)
