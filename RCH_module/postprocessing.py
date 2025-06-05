from typing import List, Tuple, Dict


def separate_boxes(
    solution: List[Tuple[str, Tuple[int, int, int, int, int, int]]],
    hmap: Dict[str, List[Tuple[str, Tuple[int, int, int, int, int, int]]]]
) -> List[Tuple[str, Tuple[int, int, int, int, int, int]]]:
    """
    This function separates the groups of boxes created in preprocessing into single boxes.

    Args:
        solution (List[Tuple[str, Tuple[int, int, int, int, int, int]]]): The list of solutions
            where each solution is a tuple containing an identifier and a position tuple.
        hmap (Dict[str, List[Tuple[str, Tuple[int, int, int, int, int, int]]]]): A hashmap where
            keys are identifiers and values are lists of tuples containing box identifiers and
            their positions.

    Returns:
        List[Tuple[str, Tuple[int, int, int, int, int, int]]]: A list of final solutions where
            each solution is a tuple containing an identifier and its absolute position.
    """
    # This function aims to separate the groups of boxes created in preprocessing into single boxes
    final_solution = []

    # We check all of the solutions
    while solution:
        # We get the next solution from the list
        i = solution.pop(0)
        # We obtain the id and the solution
        id = i[0]
        sol = i[1]

        # If the id is in the hashmap
        if id in hmap:
            # We see how the boxes were grouped in the preprocessing step (with the suffix)
            suffix = id[0][-2:]
            # If the solution is in the hmap we iterate over local solution contained in the hmap of where each box is located
            # relative to the other boxes in its group

            # We iterate over the boxes in the hmap[id] and their relative positions
            for box, position in hmap[id]:
                # Case where a place is on top of another box: change z mantain x and y
                if suffix == "_H":
                    # Case where the box has been rotated
                    if abs(position[3]) > abs(sol[3]) or abs(position[4]) > abs(sol[4]):
                        # We need to change the width and length
                        length = position[4]
                        width = position[3]
                    # Case where the box has not been rotated
                    else:
                        length = position[3]
                        width = position[4]

                    # Case where the box is in the right wall
                    if sol[4] < 0:
                        # We need to change the width to negative
                        width *= -1

                    # Update the position of the box from relative to absolute
                    new_position = (sol[0], sol[1], sol[2] + position[2], length, width, position[5])

                # TODO: Check if the boxes can be rotated
                elif sol[4] < 0:
                    if position[1] > 0:
                        new_position = (position[0] + sol[0], sol[1] - position[1], position[2] + sol[2], position[3], -position[4], position[5])
                    else:
                        new_position = (position[0] + sol[0], position[1] + sol[1], position[2] + sol[2], position[3], -position[4], position[5])

                # TODO: Check here too if the boxes can be rotated
                else:
                    new_position = (position[0] + sol[0], position[1] + sol[1], position[2] + sol[2], position[3], position[4], position[5])

                # We create a new solution with the box id and its new position
                new_sol = (box, new_position)

                # If the resulting box is not a combination of other boxes
                if box not in hmap:
                    # We add it to the final solution
                    final_solution.append(new_sol)
                else:
                    # We reinsert the box into the solution list to process it later
                    solution.append(new_sol)
        else:
            final_solution.append(i)

    return final_solution
