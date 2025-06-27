import pandas as pd
import numpy as np
import random
import json
from tqdm import tqdm
from typing import List, Tuple, Dict

from .preprocessing import join_box
from .sorting import sort_boxes
from .packing import load_boxes
from .postprocessing import separate_boxes, separate_not_loaded
from .rendering import show_boxes


NUM_SOLUTIONS = 15000
SHOWN_SOLUTIONS = 5


def RCH(
    container_dimensions: Tuple[int, int, int],
    df: pd.DataFrame,
    hmap: Dict[Tuple[str, str], List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int, int, int]]]],
    load_type: int,
    solution: List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]] = None,
    PPs: List[Tuple[int, int, int, int, int, int, str]] = None,
) -> Tuple[float, float, float, List[Tuple[str, List[float]]], List[str], List[str]]:
    """
    Implements the RCH algorithm to load boxes into a container.

    Args:
        container_dimensions (Tuple[int, int, int]): Dimensions of the container in the format
            (length, width, height).
        df (pd.DataFrame): DataFrame containing box data with columns "Partida", "Expedicion",
            "LargoCm", "AnchoCm", "AltoCm", "Remontable".
        hmap (Dict[Tuple[str, str], List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int, int, int]]]]):
            A hashmap where keys are tuples of identifiers and values are lists of tuples containing box identifiers
        load_type (int): The type of loading strategy to use.
        solution (List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]], optional): Initial solution to start packing from.
            Defaults to None.
        PPs (List[Tuple[int, int, int, int, int, int, str]], optional): List of potential points (PPs) to use in the loading process.
            Defaults to None.

    Returns:

        Tuple: A tuple containing:
            - pctg_volume (float): Percentage of the total volume used.
            - pctg_floor (float): Percentage of the container floor area used.
            - x_axis (float): The length of all loaded boxes.
            - final_solution (List[Tuple[str, List[float]]]): The final loaded boxes with their positions and dimensions.
            - not_loaded (List[str]): List of box IDs that were not loaded.
            - PPs (List[str]): List of potential points (PPs) used in the loading process.
    """
    # Get provided container dimensions
    container_length, container_width, container_height = container_dimensions

    # Create boxes dictionary from DataFrame
    # The keys are tuples of (Partida, Expedicion) and the values are lists containing
    # [length, width, height, priority, remontable]
    boxes = {}
    for i in range(len(df)):
        box_id = df["Partida"][i]
        box_group = df["Expedicion"][i]
        r = random.random()

        # DUDA 3: Esto no se mas sencillo con un if elif else?
        fixed = 0
        id = (box_id, box_group)

        # If we can fill the width of the container in one of the given directions we choose it.
        if int(df["LargoCm"][i]) > container_width or 0 <= (container_width - int(df["AnchoCm"][i])) < 8:
            boxes[id] = [int(df["LargoCm"][i]), int(df["AnchoCm"][i]), int(df["AltoCm"][i]), 2, int(df["Remontable"][i])]
            fixed = 1

        if int(df["AnchoCm"][i]) > container_width or 0 <= (container_width - int(df["LargoCm"][i])) < 8:
            boxes[id] = [int(df["AnchoCm"][i]), int(df["LargoCm"][i]), int(df["AltoCm"][i]), 2, int(df["Remontable"][i])]
            fixed = 1

        # The rest of boxes are given a random orientation
        if fixed == 0:
            if r < 0.5:
                boxes[id] = [int(df["AnchoCm"][i]), int(df["LargoCm"][i]), int(df["AltoCm"][i]), 2, int(df["Remontable"][i])]
            else:
                boxes[id] = [int(df["LargoCm"][i]), int(df["AnchoCm"][i]), int(df["AltoCm"][i]), 2, int(df["Remontable"][i])]

    # If the box fills the container width we give it priority 1
    for id, box in boxes.items():
        if container_width - box[1] < 15:
            box[3] = 1

    # Sort the boxes by priority and volume (length * width * height)
    sorted_boxes = sort_boxes(boxes)

    # Packing step of the algorithm where the solution is generated
    solution, not_loaded, PPs = load_boxes(sorted_boxes, container_dimensions, load_type, solution, PPs)

    solution = [x for x in solution if x is not False]

    # Separate the boxes for visualization
    final_solution = separate_boxes(solution, hmap)
    not_loaded = separate_not_loaded(not_loaded, hmap)
    final_solution = list(dict.fromkeys(final_solution))

    used_volume = 0
    used_floor = 0

    # Calculate the total floor area and volume used in the container
    for id, box in final_solution:
        if box[2] == 0:
            box_floor = box[3] * abs(box[4])
            used_floor += box_floor

        box_volume = box[3] * abs(box[4]) * box[5]
        used_volume += box_volume

    # X_axis represents the length of all of the loaded boxes (last box + last box length)
    last_box = max(final_solution, key=lambda x: x[1][0] + x[1][3])[1]
    x_axis = last_box[0] + last_box[3]

    # Pctg_floor is the percentage of the area of the container floor that is used
    pctg_floor = used_floor / (container_length * container_width) * 100

    # Pctg_volume represents the percentage of the total volume that is used
    pctg_volume = used_volume / (container_length * container_width * container_height) * 100

    return (pctg_volume, pctg_floor, x_axis, final_solution, not_loaded, PPs)


def organize_loading(
    container_dimensions: Tuple[int, int, int],
    df: pd.DataFrame,
    load_type: int = 1,
    partial_solution: List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]] = None,
    partial_PPs: List[Tuple[int, int, int, int, int, int, str]] = None,
    ):

    # Preprocess the boxes to generate bigger boxes, we also generate a hmap to be able to separate the boxes later
    df, hmap = join_box(df, container_dimensions)

    # For each solution we store the solution and the boxes not loaded in a dictionary with the scores as the key
    all_solutions = {}
    for _ in tqdm(range(NUM_SOLUTIONS), desc="Generating solutions"):
        pctg_volume, pctg_floor, x_axis, solution, not_loaded, PPs = RCH(container_dimensions, df, hmap, load_type, partial_solution, partial_PPs)
        all_solutions[(pctg_volume, pctg_floor, x_axis)] = (solution, not_loaded, PPs)

    # We sort the keys depending on which score we want to minimize/maximize
    # This has to be here because we will use the metrics to sort the solutions
    # TODO: Preguntar si aqui se puede incorporar tambien el x[2] (x_axis).
    volume_sorted_keys = sorted(all_solutions.keys(), key=lambda x: (x[0], x[1]), reverse=True)
    floor_sorted_keys = sorted(all_solutions.keys(), key=lambda x: (x[1], x[0]), reverse=True)
    x_sorted_keys = sorted(all_solutions.keys(), key=lambda x: (-x[2], x[1]), reverse=True)

    # Choose which sorted keys we want to use based on the load type
    if load_type == 1:
        sorted_keys = volume_sorted_keys
    elif load_type == 2:
        sorted_keys = x_sorted_keys
    elif load_type == 3:
        sorted_keys = floor_sorted_keys
    elif load_type == 4:
        sorted_keys = x_sorted_keys

    return all_solutions, sorted_keys


def get_volumes(viaje, load_type=1, file_path=None, save_path="data/outputs/soluciones/"):
    """
    There are 4 types of load type:
      1. Maximize volume and floor
      2. Minimize X axis
      3. Maximize only floor
      4. Resume loading from previous solution

    Args:
        viaje (str): The trip code.
        load_type (int): The type of loading strategy to use.
        file_path (str): The path to the input Excel file containing box data.

    Returns:
        tuple: A tuple containing the average percentage of loaded volume, the best volume score,
            and the number of boxes not loaded.
    """
    # Set the container dimensions
    container_dimensions = (1350, 246, 259)

    # Read the input excel
    df = pd.read_excel(file_path)

    # If we are loading from a previous solution we load the json file
    if load_type == 4:
        # Load the JSON file
        with open(f"{save_path}/output_{viaje}.json", "r") as file:
            loaded_output = json.load(file)

        # Convert solutions lists back to tuples
        solutions = loaded_output["solution"]
        solutions = [(tuple(item[0]), tuple(item[1])) for item in solutions]

        # Convert the potential points (PPs) back to tuples
        PPs = loaded_output["PPs"]
        PPs = [tuple(item) for item in PPs]
        all_solutions, sorted_keys = organize_loading(container_dimensions, df, load_type, solutions, PPs)

    else:
        all_solutions, sorted_keys = organize_loading(container_dimensions, df, load_type)

    # We visualize the best solutions based on whichever score we prefer
    for i in range(SHOWN_SOLUTIONS):
        print(f"Solution {i+1} with score {sorted_keys[i]} and {len(all_solutions[sorted_keys[i]][1])} not loaded boxes:")
        show_boxes(all_solutions[sorted_keys[i]][0], idx=i+1)

    # Calculate the average loaded volume
    all_pctg = [x[0] for x in sorted_keys]
    avg_pctg = np.mean(all_pctg)

    # Create an excel file with the boxes that haven't been loaded
    not_loaded_best = pd.DataFrame.from_dict(
        all_solutions[sorted_keys[0]][1],
        orient="index",
        columns=["LargoCm", "AnchoCm", "AltoCm", "Prioridad", "Remontable"],
    )
    not_loaded_best.index.name = "Partida"
    not_loaded_best.to_excel("data/outputs/not_loaded.xlsx")

    # If we are using load_type 2 we save the solution as a json file to use it later
    if load_type == 2:
        output = {}
        output["solution"] = all_solutions[sorted_keys[0]][0]
        output["PPs"] = all_solutions[sorted_keys[0]][2]
        with open(f"data/outputs/soluciones/output_{viaje}.json", "w") as file:
            json.dump(output, file)

    # else:
    #     output = {}
    #     output["solution"] = all_solutions[volume_sorted_keys[0]][0]
    #     with open(save_path + f"output_{viaje}.json", "w") as file:
    #         json.dump(output, file)

    return avg_pctg, sorted_keys[0], len(not_loaded_best)


# get_volumes("VBCN2403418", load_type=2, file_path="data/inputs/input_RCH/primera_VBCN2403418.xlsx")
# get_volumes("VBCN2403418", load_type=4, file_path="data/inputs/input_RCH/resto_VBCN2403418.xlsx")
viaje = "VBCN2403750"
viaje = "VBCN2501568"
# print(get_volumes(viaje, load_type=1, file_path=fdata/inputs/viajes_prueba/test_{viaje}.xlsx"))
