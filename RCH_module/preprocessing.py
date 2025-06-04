from itertools import combinations
from typing import List, Tuple, Dict
import pandas as pd
import random


def join_box(
    df: pd.DataFrame, container_dimensions: Tuple[int, int, int]
) -> Tuple[pd.DataFrame, Dict[str, List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]]]:
    """
    Joins boxes based on their dimensions and stackability, considering container dimensions and tolerances.

    Args:
        df (pd.DataFrame): DataFrame containing box dimensions and properties.
        container_dimensions (Tuple[int, int, int]): Dimensions of the container (length, width, height).

    Returns:
        Tuple[pd.DataFrame, Dict[str, List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]]]:
            - Updated DataFrame with combined boxes.
            - Hash map with box combinations and their dimensions for visualization.
    """
    container_length, container_width, container_height = container_dimensions

    # Define tolerance in cm
    length_tolerance = 8
    height_tolerance = 15
    volumetric_tolerance = 25

    # Boxes within the tolerance are set to the standard value for a pallet
    df.loc[
        (120 - volumetric_tolerance < df["LargoCm"])
        & (df["LargoCm"] < 120 + volumetric_tolerance)
        & (80 - volumetric_tolerance < df["AnchoCm"])
        & (df["AnchoCm"] < 80 + volumetric_tolerance),
        ["LargoCm", "AnchoCm"],
    ] = [120, 80]

    hmap = {}
    new_boxes = []
    combined_boxes = set()

    # Boxes that are not stackable and weigh more than 200 kg can be considered
    # to occupy the entire height of the container
    for box1, box2 in combinations(df.itertuples(index=False), 2):

        # If any of the 2 boxes have already been combined we skip
        if box1.Partida in combined_boxes or box2.Partida in combined_boxes:
            continue

        if (
            box1.Remontable == 1
            and abs(box1.LargoCm - box2.LargoCm) < volumetric_tolerance
            and abs(box1.AnchoCm - box2.AnchoCm) < volumetric_tolerance
            and box1.AltoCm + box2.AltoCm < container_height
        ):
            new_box = {
                "CodigoViaje": box1.CodigoViaje,
                "FechaCargaContenedor": box1.FechaCargaContenedor,
                "FechaEntradaAlmacen": box1.FechaEntradaAlmacen,
                "Expedicion": box1.Expedicion,
                "Partida": box1.Partida + "/" + box2.Partida + "_H",
                "PesoKg": box1.PesoKg,
                "LargoCm": max(box1.LargoCm, box2.LargoCm),
                "AltoCm": box1.AltoCm + box2.AltoCm,
                "AnchoCm": max(box1.AnchoCm, box2.AnchoCm),
                "TipoPartida": box1.TipoPartida,
                "Remontable": box2.Remontable,
                "Volumen": box1.Volumen + box2.Volumen,
            }

            # We add the _H suffix so we can then know to only change the height for visualization
            hmap_entry = [
                ((box1.Partida, box1.Expedicion), (0, 0, 0, box1.LargoCm, box1.AnchoCm, box1.AltoCm)),
                ((box2.Partida, box2.Expedicion), (0, 0, box1.AltoCm, box2.LargoCm, box2.AnchoCm, box2.AltoCm))
            ]
            hmap[(box1.Partida + "/" + box2.Partida + "_H", box1.Expedicion)] = hmap_entry

            combined_boxes.add(box1.Partida)
            combined_boxes.add(box2.Partida)
            new_boxes.append(new_box)

        elif (
            box2.Remontable == 1
            and abs(box1.LargoCm - box2.LargoCm) < volumetric_tolerance
            and abs(box1.AnchoCm) - abs(box2.AnchoCm) < volumetric_tolerance
            and box1.AltoCm + box2.AltoCm < container_height
        ):
            new_box = {
                "CodigoViaje": box2.CodigoViaje,
                "FechaCargaContenedor": box2.FechaCargaContenedor,
                "FechaEntradaAlmacen": box2.FechaEntradaAlmacen,
                "Expedicion": box2.Expedicion,
                "Partida": box2.Partida + "/" + box1.Partida + "_H",
                "PesoKg": box1.PesoKg,
                "LargoCm": max(box1.LargoCm, box2.LargoCm),
                "AltoCm": box1.AltoCm + box2.AltoCm,
                "AnchoCm": max(box1.AnchoCm, box2.AnchoCm),
                "TipoPartida": box1.TipoPartida,
                "Remontable": box1.Remontable,
                "Volumen": box1.Volumen + box2.Volumen,
            }

            # We add the _H suffix so we can then know to only change the height for visualization
            hmap_entry = [
                ((box2.Partida, box2.Expedicion), (0, 0, 0, box2.LargoCm, box2.AnchoCm, box2.AltoCm)),
                ((box1.Partida, box1.Expedicion), (0, 0, box2.AltoCm, box1.LargoCm, box1.AnchoCm, box1.AltoCm))
            ]
            hmap[(box2.Partida + "/" + box1.Partida + "_H", box2.Expedicion)] = hmap_entry

            combined_boxes.add(box1.Partida)
            combined_boxes.add(box2.Partida)
            new_boxes.append(new_box)

    df = df[~df["Partida"].isin(combined_boxes)]

    # Add the newly created boxes to the main dataframe
    new_boxes_df = pd.DataFrame(new_boxes)
    df = pd.concat([df, new_boxes_df])

    new_boxes = []
    combined_boxes = set()
    """
    # Iterate over all possible combinations of 2 boxes
    for box1, box2 in combinations(df.itertuples(index=False), 2):

        # If any of the 2 boxes have already been combined we skip
        if box1.Partida in combined_boxes or box2.Partida in combined_boxes:
            continue

        # Case1: Width of box 1 + Width of box 2 is close to container width.
        if (
            0 <= (container_width - (box1.AnchoCm + box2.AnchoCm)) < length_tolerance
            and abs(box1.LargoCm - box2.LargoCm) < length_tolerance
            and abs(box1.AltoCm - box2.AltoCm) < height_tolerance
        ):
            new_box = {
                "CodigoViaje": box1.CodigoViaje,
                "FechaCargaContenedor": max(box1.FechaCargaContenedor, box2.FechaCargaContenedor),
                "FechaEntradaAlmacen": max(box1.FechaEntradaAlmacen, box2.FechaEntradaAlmacen),
                "Expedicion": box1.Expedicion,
                "Partida": box1.Partida + "/" + box2.Partida + "_W",
                "PesoKg": box1.PesoKg + box2.PesoKg,
                "LargoCm": box1.AnchoCm + box2.AnchoCm,
                "AltoCm": max(box1.AltoCm, box2.AltoCm),
                "AnchoCm": max(box1.LargoCm, box2.LargoCm),
                "TipoPartida": box1.TipoPartida,
                "Remontable": min(box1.Remontable, box2.Remontable),
                "Volumen": box1.Volumen + box2.Volumen,
            }

            # Create the hash map entry which has the same structure as the solutions to ease visualization
            hmap_entry = [
                ((box1.Partida, box1.Expedicion), (0, 0, 0, box1.LargoCm, box1.AnchoCm, box1.AltoCm)),
                ((box2.Partida, box2.Expedicion), (0, box1.AnchoCm, 0, box2.LargoCm, box2.AnchoCm, box2.AltoCm))
            ]
            hmap[(box1.Partida + "/" + box2.Partida + "_W", box1.Expedicion)] = hmap_entry

            # Add new combined boxe to the new_boxes
            new_boxes.append(new_box)

            # Add both combined boxes to the combined_boxes set so we don't combine them again
            combined_boxes.add(box1.Partida)
            combined_boxes.add(box2.Partida)

        # Case 2: Width of box 1 + Length of box 2 is close to container width
        if (
            0 <= (container_width - (box1.AnchoCm + box2.LargoCm)) < length_tolerance
            and abs(box1.LargoCm - box2.AnchoCm) < length_tolerance
            and abs(box1.AltoCm - box2.AltoCm) < height_tolerance
        ):
            new_box = {
                "CodigoViaje": box1.CodigoViaje,
                "FechaCargaContenedor": max(box1.FechaCargaContenedor, box2.FechaCargaContenedor),
                "FechaEntradaAlmacen": max(box1.FechaEntradaAlmacen, box2.FechaEntradaAlmacen),
                "Expedicion": box1.Expedicion,
                "Partida": box1.Partida + "/" + box2.Partida + "_W",
                "PesoKg": box1.PesoKg + box2.PesoKg,
                "LargoCm": box1.AnchoCm + box2.LargoCm,
                "AltoCm": max(box1.AltoCm, box2.AltoCm),
                "AnchoCm": max(box1.LargoCm, box2.AnchoCm),
                "TipoPartida": box1.TipoPartida,
                "Remontable": min(box1.Remontable, box2.Remontable),
                "Volumen": box1.Volumen + box2.Volumen,
            }
            hmap_entry = [
                ((box1.Partida, box1.Expedicion), (0, 0, 0, box1.LargoCm, box1.AnchoCm, box1.AltoCm)),
                ((box2.Partida, box2.Expedicion), (0, box1.AnchoCm, 0, box2.AnchoCm, box2.LargoCm, box2.AltoCm))
            ]
            hmap[(box1.Partida + "/" + box2.Partida + "_W", box1.Expedicion)] = hmap_entry

            new_boxes.append(new_box)

            combined_boxes.add(box1.Partida)
            combined_boxes.add(box2.Partida)

        # Case 3: Length of box 1 + Width of box 2 is close to container width
        if (
            0 <= (container_width - (box1.LargoCm + box2.AnchoCm)) < length_tolerance
            and abs(box1.AnchoCm - box2.LargoCm) < length_tolerance
            and abs(box1.AltoCm - box2.AltoCm) < height_tolerance
        ):
            new_box = {
                "CodigoViaje": box1.CodigoViaje,
                "FechaCargaContenedor": max(box1.FechaCargaContenedor, box2.FechaCargaContenedor),
                "FechaEntradaAlmacen": max(box1.FechaEntradaAlmacen, box2.FechaEntradaAlmacen),
                "Expedicion": box1.Expedicion,
                "Partida": box1.Partida + "/" + box2.Partida + "_W",
                "PesoKg": box1.PesoKg + box2.PesoKg,
                "LargoCm": box1.LargoCm + box2.AnchoCm,
                "AltoCm": max(box1.AltoCm, box2.AltoCm),
                "AnchoCm": max(box1.AnchoCm, box2.LargoCm),
                "TipoPartida": box1.TipoPartida,
                "Remontable": min(box1.Remontable, box2.Remontable),
                "Volumen": box1.Volumen + box2.Volumen,
            }
            hmap_entry = [
                ((box1.Partida, box1.Expedicion), (0, 0, 0, box1.AnchoCm, box1.LargoCm, box1.AltoCm)),
                ((box2.Partida, box2.Expedicion), (0, box1.LargoCm, 0, box2.LargoCm, box2.AnchoCm, box2.AltoCm))
            ]
            hmap[(box1.Partida + "/" + box2.Partida + "_W", box1.Expedicion)] = hmap_entry

            new_boxes.append(new_box)

            combined_boxes.add(box1.Partida)
            combined_boxes.add(box2.Partida)

        # Case 3: Length of box 1 + Length of box 2 is close to container width
        if (
            0 <= (container_width - (box1.LargoCm + box2.LargoCm)) < length_tolerance
            and abs(box1.AnchoCm - box2.AnchoCm) < length_tolerance
            and abs(box1.AltoCm - box2.AltoCm) < height_tolerance
        ):
            new_box = {
                "CodigoViaje": box1.CodigoViaje,
                "FechaCargaContenedor": max(box1.FechaCargaContenedor, box2.FechaCargaContenedor),
                "FechaEntradaAlmacen": max(box1.FechaEntradaAlmacen, box2.FechaEntradaAlmacen),
                "Expedicion": box1.Expedicion,
                "Partida": box1.Partida + "/" + box2.Partida + "_W",
                "PesoKg": box1.PesoKg + box2.PesoKg,
                "LargoCm": box1.LargoCm + box2.LargoCm,
                "AltoCm": max(box1.AltoCm, box2.AltoCm),
                "AnchoCm": max(box1.AnchoCm, box2.AnchoCm),
                "TipoPartida": box1.TipoPartida,
                "Remontable": min(box1.Remontable, box2.Remontable),
                "Volumen": box1.Volumen + box2.Volumen,
            }
            hmap_entry = [
                ((box1.Partida, box1.Expedicion), (0, 0, 0, box1.AnchoCm, box1.LargoCm, box1.AltoCm)),
                ((box2.Partida, box2.Expedicion), (0, box1.LargoCm, 0, box2.AnchoCm, box2.LargoCm, box2.AltoCm))
            ]
            hmap[(box1.Partida + "/" + box2.Partida + "_W", box1.Expedicion)] = hmap_entry

            new_boxes.append(new_box)


            combined_boxes.add(box1.Partida)
            combined_boxes.add(box2.Partida)

    # Filter df to exclude instances where the "Partida" value is in the combined_boxes set
    # we do this to make sure we don't have both the combined boxes and the singular box on its own
    df = df[~df["Partida"].isin(combined_boxes)]

    # Add the newly created boxes to the main dataframe
    new_boxes_df = pd.DataFrame(new_boxes)
    df = pd.concat([df, new_boxes_df])

    # Combining 3 boxes
    # We create a dictionary which for each value of length found it has all the boxes with that length
    length_groups = {}
    for box in df.itertuples():
        length = box.LargoCm
        if length not in length_groups:
            length_groups[length] = []

        length_groups[length].append(box)

    # Sort the groups by length
    length_groups = sorted(length_groups.items(), key=lambda x: x[0])
    length_groups = dict(length_groups)

    valid_combinations = []
    combined_boxes = set()
    new_boxes = []

    # For each length group we generate all the possible combinations of 3 boxes
    for length, group in length_groups.items():
        for combo in combinations(group, 3):
            box1, box2, box3 = combo

            # If any of the boxes are already combined we skip this combination
            if box1.Partida in combined_boxes or box2.Partida in combined_boxes or box3.Partida in combined_boxes:
                continue
            if (
                (box1.Partida, box1.Expedicion) in hmap
                or (box2.Partida, box2.Expedicion) in hmap
                or (box3.Partida, box3.Expedicion) in hmap
            ):
                continue

            total_width = sum(box.AnchoCm for box in combo)

            # Check if the heights are within the tolerance range
            if abs(box1.AltoCm - box2.AltoCm) > height_tolerance:
                continue
            elif abs(box1.AltoCm - box3.AltoCm) > height_tolerance:
                continue
            elif abs(box2.AltoCm - box3.AltoCm) > height_tolerance:
                continue

            # Check if the total width (sum of all widths) is within the tolerance range
            if 0 < (container_width - total_width) < length_tolerance:

                new_box = {
                    "CodigoViaje": box1.CodigoViaje,
                    "FechaCargaContenedor": max(box1.FechaCargaContenedor, box2.FechaCargaContenedor, box3.FechaCargaContenedor),
                    "FechaEntradaAlmacen": max(box1.FechaEntradaAlmacen, box2.FechaEntradaAlmacen, box3.FechaEntradaAlmacen),
                    "Expedicion": box1.Expedicion,
                    "Partida": box1.Partida + "/" + box2.Partida + "/" + box3.Partida + "_W",
                    "PesoKg": box1.PesoKg + box2.PesoKg + box3.PesoKg,
                    "LargoCm": max(box1.LargoCm, box2.LargoCm, box3.LargoCm),
                    "AltoCm": max(box1.AltoCm, box2.AltoCm, box3.AltoCm),
                    "AnchoCm": box1.AnchoCm + box2.AnchoCm + box3.AnchoCm,
                    "TipoPartida": box1.TipoPartida,
                    "Remontable": min(box1.Remontable, box2.Remontable, box3.Remontable),
                    "Volumen": box1.Volumen + box2.Volumen + box3.Volumen,
                }

                # Generate hashmap entry
                hmap_entry = [
                    ((box1.Partida, box1.Expedicion), (0, 0, 0, box1.LargoCm, box1.AnchoCm, box1.AltoCm)),
                    ((box2.Partida, box2.Expedicion), (0, box1.AnchoCm, 0, box2.LargoCm, box2.AnchoCm, box2.AltoCm)),
                    ((box3.Partida, box3.Expedicion), (0, box1.AnchoCm+box2.AnchoCm, 0, box3.LargoCm, box3.AnchoCm, box3.AltoCm))
                ]
                hmap[(box1.Partida + "/" + box2.Partida + "/" + box3.Partida + "_W", box1.Expedicion)] = hmap_entry

                valid_combinations.append(combo)
                new_boxes.append(new_box)

                combined_boxes.add(box1.Partida)
                combined_boxes.add(box2.Partida)
                combined_boxes.add(box3.Partida)

    df = df[~df["Partida"].isin(combined_boxes)]

    new_boxes_df = pd.DataFrame(new_boxes)
    df = pd.concat([df, new_boxes_df])
    """
    # Reset the index to make sure there are no repeated indices in the dataframe
    df = df.reset_index(drop=True)

    return df, hmap
