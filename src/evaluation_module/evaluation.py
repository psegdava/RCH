from typing import List, Tuple, Dict
import pandas as pd
import math


def volume_and_floor_utilization(
    container_dims: Tuple[int, int, int],
    loaded_boxes: List[Tuple[Tuple[str, str], List[int]]]
) -> Tuple[float, float]:
    """
    Calculate the volume and floor utilization of the loaded boxes in a container.

    Args:
        container_dims (Tuple[int, int, int]): Dimensions of the container (length, width, height).
        loaded_boxes (List[Tuple[Tuple[str, str], List[int]]]): List of loaded boxes with their positions and dimensions.

    Returns:
        Tuple[float, float]: A tuple containing the volume utilization and floor utilization.
    """
    # We get the dimensions of the container
    # and calculate the total volume and floor area
    cont_l, cont_w, cont_h = container_dims
    container_volume = cont_l * cont_w * cont_h
    container_floor = cont_l * cont_w

    used_volume = 0
    used_floor = 0

    # For each loaded box, we calculate the volume and floor area used
    for _, (x, y, z, l, w, h) in loaded_boxes:
        used_volume += l * abs(w) * h
        if z == 0:  # Only count the floor area if the box is on the ground
            used_floor += l * abs(w)

    floor_util = used_floor / container_floor
    volume_util = used_volume / container_volume

    return volume_util, floor_util


def maximum_x(
    loaded_boxes: List[Tuple[Tuple[str, str], List[int]]]
) -> float:
    """
    Calculate the maximum x-coordinate of the loaded boxes.

    Args:
        loaded_boxes (List[Tuple[Tuple[str, str], List[int]]]): List of loaded boxes with their positions and dimensions.

    Returns:
        float: The maximum x-coordinate of the loaded boxes.
    """
    max_x = 0
    # Iterate through the loaded boxes to find the maximum x-coordinate
    for _, (x, y, z, l, w, h) in loaded_boxes:
        max_x = max(max_x, x + l)
    return max_x


def weight_distribution(
    container_dims: Tuple[int, int, int],
    loaded_boxes: List[Tuple[Tuple[str, str], List[int]]],
    df: pd.DataFrame
) -> Dict[str, float]:
    """
    Calculate the weight distribution of the loaded boxes in the container.

    Args:
        container_dims (Tuple[int, int, int]): Dimensions of the container (length, width, height).
        loaded_boxes (List[Tuple[Tuple[str, str], List[int]]]): List of loaded boxes with their positions and dimensions.

    Returns:
        Tuple[float, float, float]: A tuple containing the total weight, total deviation from the center of the container,
        and horizontal deviation from the center of the container.
    """
    total_weight = 0
    sum_x = 0
    sum_y = 0
    sum_z = 0

    # Calculate total weight and maximum height used
    cont_l, cont_w, cont_h = container_dims

    for (partida, _), (x, y, z, l, w, h) in loaded_boxes:
        weight = df.loc[df["Partida"] == partida, "PesoKg"].values[0]
        center_x = x + l / 2
        center_y = y + w / 2
        center_z = z + h / 2
        total_weight += weight
        sum_x += weight * center_x
        sum_y += weight * center_y
        sum_z += weight * center_z

    center_of_weight = (
        sum_x / total_weight,
        sum_y / total_weight,
        sum_z / total_weight,
    )

    center_of_container = (
        cont_l / 2,
        cont_w / 2,
        cont_h / 2,
    )

    total_deviation = math.dist(center_of_weight, center_of_container)
    horizontal_deviation = math.dist(
        (center_of_weight[0], center_of_weight[1]),
        (center_of_container[0], center_of_container[1])
    )

    # Return the weight distribution metrics
    return (total_weight, total_deviation, horizontal_deviation)


def evaluate_solution(
    container_dims: Tuple[int, int, int],
    loaded_boxes: List[Tuple[Tuple[str, str], List[int]]],
    filepath: str = ""
) -> Dict[str, float]:
    """
    Evaluate the solution for the container loading problem.
    """
    # Calculate volume and floor utilization
    volume_util, floor_util = volume_and_floor_utilization(container_dims, loaded_boxes)

    # Calculate maximum x-coordinate
    max_x = maximum_x(loaded_boxes)

    # Calculate weight distribution metrics
    # FIXME: Verificar el funcionamiento de esto y que le voy a mandar.
    df = pd.read_excel(filepath)
    total_weight, total_deviation, horizontal_deviation = weight_distribution(container_dims, loaded_boxes, df)

    # Prepare the evaluation results
    evaluation_results = {
        "Volume Utilization": volume_util,
        "Floor Utilization": floor_util,
        "Max X": max_x,
        "Weight Total Deviation": total_deviation,
        "Weight Horizontal Deviation": horizontal_deviation,
        "Not Loaded Box Count": len(df) - len(loaded_boxes),
    }

    return evaluation_results
