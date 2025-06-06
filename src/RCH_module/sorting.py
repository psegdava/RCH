from typing import Dict, Tuple, List
import random


def sort_boxes(
    boxes: Dict[Tuple[str, str], List[int]],
) -> Dict[Tuple[str, str], List[int]]:
    """
    Sorts the boxes based on their volume and priority, with some randomization in the order.

    Args:
        boxes (Dict[Tuple[str, str], List[int]]): A dictionary where keys are tuples of
            (container, partida) and values are lists containing [length, width, height,
            priority, stackable].

    Returns:
        Dict[Tuple[str, str], List[int]]: A dictionary with the same structure as input
            but sorted and possibly randomized.
    """
    # First step is to do a simple sorting of the boxes, we sort first by
    # priority (box[3]) and then by volume
    sorted_boxes = dict(sorted(boxes.items(), key=lambda x: (x[1][2], x[1][0]), reverse=True))

    # DUDA 1: El comentario dice que se ordena por prioridad y volumen, pero el código no es así
    # ¿No debería de ser de esta manera?
    sorted_boxes = dict(
        sorted(
            boxes.items(),
            key=lambda item: (item[1][3], item[1][0] * item[1][1] * item[1][2]),
            reverse=True,
        )
    )
    final_order = {}

    # Second step is adding some randomization to the order, if two boxes
    # next to each other in the order have a similar enough volume then with
    # a probability of 0.5 we swap them
    sorted_list = list(sorted_boxes.items())

    for i in range(0, len(sorted_list), 2):
        j = i + 1

        # If there is a next box, we check if the volumes are similar enough to swap them
        # and if they have the same priority, if not we just add the box to the final order
        if j < len(sorted_boxes):
            vol1 = sorted_list[i][1][0] * sorted_list[i][1][1] * sorted_list[i][1][2]
            vol2 = sorted_list[j][1][0] * sorted_list[j][1][1] * sorted_list[j][1][2]
            prio1 = sorted_list[i][1][3]
            prio2 = sorted_list[j][1][3]
            r = random.random()

            # DUDA 2: Aqui no se está usando una probabilidad de 0.5, se está usando una probabilidad de 0.7
            # Check if the ratio of volumes is within 30% and the a probability of 0.5
            if 0.7 <= vol1 / vol2 and vol1 / vol2 <= 1.3 and r < 0.5 and prio1 == prio2:
                final_order[sorted_list[j][0]] = sorted_list[j][1]
                final_order[sorted_list[i][0]] = sorted_list[i][1]
            else:
                final_order[sorted_list[i][0]] = sorted_list[i][1]
                final_order[sorted_list[j][0]] = sorted_list[j][1]
        else:
            final_order[sorted_list[i][0]] = sorted_list[i][1]

    # Return the final order of the boxes after sorting and swapping
    return final_order
