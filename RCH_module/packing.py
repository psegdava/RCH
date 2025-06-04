import json
from typing import List, Tuple, Dict


def score_point(
    x: int,
    y: int,
    z: int,
    l: int,
    w: int,
    h: int,
    current_solution: List[Tuple[int, Tuple[int, int, int, int, int, int]]]
) -> int:
    """
    Calculate the score for a potential point based on its position and support.
    A point is scored based on whether it has support from walls or other boxes.
    A higher score indicates better support.

    Parameters:
        x (int): x-coordinate of the potential point.
        y (int): y-coordinate of the potential point.
        z (int): z-coordinate of the potential point.
        l (int): length of the box.
        w (int): width of the box.
        h (int): height of the box.
        current_solution (List[Tuple[int, Tuple[int, int, int, int, int, int]]]):
    """
    left_support = False
    right_support = False

    # Check for wall support
    if y == 0 or y + w == 0:        # Left wall
        left_support = True
    if y + w == 244 or y == 244:    # Right wall
        right_support = True

    left_support = any(
        (y2 == y + w or y2 + w2 == y) and z < z2 + h2 and x2 < x + l and x2 + l2 > x
        for _, (x2, y2, z2, l2, w2, h2) in current_solution
    )
    right_support = any(
        (y2 == y + w or y2 + w2 == y) and z < z2 + h2 and x2 < x + l and x2 + l2 > x
        for _, (x2, y2, z2, l2, w2, h2) in current_solution
    )

    # Higher score for positions with support on both sides
    return (2 if left_support and right_support else 1 if left_support or right_support else 0)


def sort_PPs(
    box: Tuple[int, int, int],
    PPs: List[Tuple[int, int, int, int, int]],
    load_type: int,
    solutions: List[Tuple[int, Tuple[int, int, int, int, int, int]]]
) -> List[Tuple[int, int, int, int, int]]:
    """
    Sorts the potential points (PPs) based on their coverage and support for a given box.
    The sorting is done in descending order of coverage and support, with a preference for
    points that are on the sides of the container.
    The function also assigns a type to each potential point based on its position.
    If the load type is 3, it sorts by type and then by the z-coordinate of the potential point.
    If the load type is not 3, it sorts by type and then by coverage.

    Parameters:
        box (Tuple[int, int, int]): A tuple representing the box dimensions (length, width, height).
        PPs (List[Tuple[int, int, int, int, int]]): A list of potential points where boxes can be placed.
        load_type (int): The type of load being processed (e.g., 3 for special handling).
        solutions (List[Tuple[int, Tuple[int, int, int, int, int, int]]]): Current loaded solutions.
    """
    # Potential points sorting
    PPs_coverage = []

    for pp in PPs:
        box_area = box[0] * box[1]
        pp_area = abs(pp[3] * pp[4])  # Calculate the area of the potential point

        # support = 100*score_point(pp[0], pp[1], pp[2], box[0], box[1], box[2], solutions)
        support = 1
        # In this case, coverage is the ratio of widths
        if pp_area > 0:
            coverage = box_area/pp_area * 100
        else:
            coverage = 0

        scoring = coverage+support
        # We want to prioritize loading the sides of the containers so any PPs that are on the side of the container are given type 1
        if pp[1] == 0 or pp[1] == 244 or 244 - (pp[1] + box[1]) < 6:
            pp_type = 1
        else:
            pp_type = 0

        PPs_coverage.append((pp, scoring, pp_type))

    # Depending on the load type we sort one way or another
    if load_type == 3:
        PPs_coverage = sorted(PPs_coverage, key=lambda x: (x[2], -x[0][2]), reverse=True)
        sorted_PPs = [x[0] for x in PPs_coverage]

    else:
        # Sort PPs by type and then coverage in descending order
        PPs_coverage = sorted(PPs_coverage, key=lambda x: (x[2], x[1] - x[0][0]), reverse=True)
        sorted_PPs = [x[0] for x in PPs_coverage]

    return sorted_PPs


def check_intersection(
    box1: Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]],
    box2: Tuple[int, int, int, int, int, int]
) -> bool:
    """
    Check if two boxes intersect in 3D space.
    Parameters:
        box1 (Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]): The first box represented as a tuple
            containing its identifier and its dimensions (x, y, z, length, width, height).
        box2 (Tuple[int, int, int, int, int, int]): The second box represented as a tuple of its dimensions
            (x, y, z, length, width, height).

    Returns:
        bool: True if the boxes intersect, False otherwise.
    """
    # Extract dimensions from the boxes
    x1, y1, z1, l1, w1, h1 = box1[1][0:6]
    x2, y2, z2, l2, w2, h2 = box2[0:6]

    # Calculate the maximum and minimum coordinates for box1
    y1_min = y1
    y1_max = y1 + w1 if w1 > 0 else y1
    y1_min = y1 + w1 if w1 < 0 else y1

    # Calculate the maximum and minimum coordinates for box2
    y2_min = y2
    y2_max = y2 + w2 if w2 > 0 else y2
    y2_min = y2 + w2 if w2 < 0 else y2

    # Check for overlap along the x-axis
    overlap_x = x2 < x1 + l1 and x2 + l2 > x1

    # Check for overlap along the y-axis
    overlap_y = y2_min < y1_max and y2_max > y1_min

    # Check for overlap along the z-axis
    overlap_z = z2 < z1 + h1 and z2 + h2 > z1

    # Check for intersection in all three dimensions
    intersection = overlap_x and overlap_y and overlap_z

    return intersection


def is_feasible(
    pp: Tuple[int, int, int, int, int, int],
    l: int,
    w: int,
    h: int,
    solutions: List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]
) -> bool:
    """
    Check if a box can be placed in a potential point (PP) without exceeding the container dimensions
    and without intersecting with other boxes already placed in the container.

    Parameters:
        pp (Tuple[int, int, int, int, int, int]): A tuple representing the potential point
            (x, y, z, length, width, height).
        l (int): Length of the box to be placed.
        w (int): Width of the box to be placed.
        h (int): Height of the box to be placed.
        solutions (List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]): List of already placed boxes.

    Returns:
        bool: True if the box can be placed in the potential point without exceeding dimensions or intersecting,
              False otherwise.
    """
    # For a box to be in a feasible PP it has to fit and there can be no intersections with other boxes
    x, y, z = pp[0:3]

    # If it doesn't fit we don't even have to check for intersections
    if pp[3] < l or abs(pp[4]) < abs(w) or pp[5] < h:
        return False

    # Check for intersections with the boxes that are already loaded
    for i in range(len(solutions)):
        box1 = solutions[i]
        box2 = [x, y, z, l, w, h]

        intersection = check_intersection(box1, box2)

        # If there is at least one intersection we stop checking
        if intersection is True:
            return False

    return True


def merge(
    pp: Tuple[int, int, int, int, int, int, str],
    PPs: List[Tuple[int, int, int, int, int, int, str]]
) -> Tuple[Tuple[int, int, int, int, int, int, str], Tuple[int, int, int, int, int, int, str]]:
    """
    Merges a potential point (PP) with adjacent spaces in the list of potential points (PPs).
    This function checks if the given PP can be merged with any existing PPs based on their positions
    and dimensions. If a merge is possible, it returns the new merged PP and the old PP that was merged.
    If no merge is possible, it returns the original PP and None.

    Parameters:
        pp (Tuple[int, int, int, int, int, int, str]): The potential point to be merged.
        PPs (List[Tuple[int, int, int, int, int, int, str]]): List of existing potential points.

    Returns:
        Tuple[Tuple[int, int, int, int, int, int, str], Tuple[int, int, int, int, int, int, str]]:
        - The new merged potential point if a merge is possible.
        - The old potential point that was merged with the new one.
        If no merge is possible, returns the original PP and None.
    """
    # Merging algorithm for top spaces
    x2, y2, z2, l2, w2, h2, direction2 = pp

    for pp1 in PPs:
        x1, y1, z1, l1, w1, h1, direction1 = pp1

        # We merge two spaces if they are adjacent and the z value is similar enough
        if x1 < x2 and y1 == y2 and abs(z1-z2) < 6 and x2 - (x1+l1) < 6:

            if direction1 == "left":
                new_pp = (x1, y1, z1, l1 + l2, min(w1, w2), h1, direction1)
                return new_pp, pp1
            else:
                new_pp = (x1, y1, z1, l1 + l2, max(w1, w2), h1, direction1)
                return new_pp, pp1

        if x1 == x2 and y1 < y2 and abs(z1 - z2) < 7 and y2 - (y1 + w1) < 6:
            new_pp = (x1, y1, z1, min(l1, l2), w1 + w1, h1, direction1)
            return new_pp, pp1

    return pp, None


def lateral_support(
    current_solution: List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]],
    pending: List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]],
    container_width: int
) -> List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]:
    """
    Check if pending boxes have sufficient lateral support (either from walls or other boxes).

    Parameters:
        current_solution (List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]):
            The current loaded boxes in the container.
        pending (List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]):
            The boxes that are pending to be placed.
        container_width (int): The width of the container.

    Returns:
        List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]:
            The updated list of pending boxes after checking for lateral support.
    """
    to_remove = []

    for id, box in pending:
        support1 = False  # Left-side support
        support2 = False  # Right-side support

        x, y, z, l, w, h = box

        # Check for wall support
        if y == 0 or y + w == 0:  # Left wall
            support1 = True
        if y + w == container_width or y == container_width:  # Right wall
            support2 = True

        # Check for support from other boxes
        for id2, solution in current_solution:
            x2, y2, z2, l2, w2, h2 = solution

            # Left-side support (box placed to the left of the current box)
            if (
                (y2 == y + w or y2 + w2 == y)   # Adjacent on the left
                and z < z2 + h2                 # Vertical overlap
                and x < x2 + l2 and x + l > x2  # Horizontal overlap
            ):
                support1 = True

            # Right-side support (box placed to the right of the current box)
            if (
                (y2 == y + w or y2 + w2 == y)   # Adjacent on the right
                and z < z2 + h2                 # Vertical overlap
                and x < x2 + l2 and x + l > x2  # Horizontal overlap
            ):
                support2 = True

            # Exit early if both supports are found
            if support1 and support2:
                break

        # If both supports are found, mark for removal
        if support1 and support2:
            to_remove.append((id, box))

    # Remove validated boxes from pending
    for item in to_remove:
        pending.remove(item)

    return pending


def retry(
    not_loaded: Dict[Tuple[str, str], List[int]],
    PPs: List[Tuple[int, int, int, int, int, int, str]],
    load_type: int,
    solutions: List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]],
    container_dimensions: Tuple[int, int, int],
    boxes: Dict[Tuple[str, str], List[int]]
) -> Tuple[List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]], Dict[Tuple[str, str], List[int]], List[Tuple[int, int, int, int, int]]]:
    """
    This function attempts to place boxes that could not be loaded in the first pass
    by checking the available potential points (PPs) and the dimensions of the container.
    If a box can be placed, it updates the solutions and PPs accordingly.

    Parameters:
        not_loaded (Dict[Tuple[str, str], List[int]]): A dictionary of boxes that could not be loaded.
        PPs (List[Tuple[int, int, int, int, int, int, str]]): A list of potential points where boxes can be placed.
        load_type (int): The type of load being processed.
        solutions (List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]]): Current loaded solutions.
        container_dimensions (Tuple[int, int, int]): Dimensions of the container (length, width, height).
        boxes (Dict[Tuple[str, str], List[int]]): Dictionary of all boxes with their dimensions.

    Returns:
        Tuple[List[Tuple[Tuple[str, str], Tuple[int, int, int, int, int, int]]], Dict[Tuple[str, str], List[int]], List[Tuple[int, int, int, int, int]]]:
        - A list of solutions representing the boxes placed in the container.
        - A dictionary of boxes that could not be loaded.
        - A list of potential points (PPs) representing available space in the container.
    """
    container_length, container_width, container_height = container_dimensions
    pending = []
    final_not_loaded = {}

    for id, box in not_loaded.items():
        # Sort the PPs according to the current box
        sorted_PPs = sort_PPs(box, PPs, 3, solutions)
        solution = None

        # Loop over each PP to try to place the box in it
        for pp in sorted_PPs:
            x, y, z = pp[0:3]

            # DUDA 5: Aqui es diferente a la función load_boxes, porque aquí se está usando el ancho y largo de la caja
            if pp[6] == "right":
                l, w, h = box[1], -box[0], box[2]
            else:
                l, w, h = box[1], box[0], box[2]

            # If the PP, box combination is feasible we will place the box
            if is_feasible(pp, l, w, h, solutions):
                # Generate the solution
                solution = (id, (x, y, z, l, w, h))

                PPs.remove(pp)

                # Create the new PPs to be added to the list
                front_pp = (x + l, y, z, pp[3] - l, pp[4], pp[5], pp[6])
                side_pp = (x, y + w, z, l, pp[4] - w, pp[5], pp[6])
                top_pp = (x, y, z + h, l, w, pp[5] - h, pp[6])
                right_corner_pp = (x + l, container_width, z, container_length - (x + l), -244, pp[5], "right")

                # Top pp is merged with adjacent spaces
                top_pp, old_pp = merge(top_pp, PPs)

                if old_pp is not None:
                    PPs.remove(old_pp)

                # We add the front and side PPs to the available PPs list
                PPs.append(front_pp)
                PPs.append(side_pp)

                # The top PP only gets added to the available list if the box is stackable
                if box[4] == 1:
                    PPs.append(top_pp)

                if 244 - (y + w) < 30 and z == 0:
                    PPs.append(right_corner_pp)

                solutions.append(solution)

                if z > 0 and l > w and h > w:
                    pending.append(solution)

                pending = lateral_support(solutions, pending, container_width)

                break

        # If the box is not loaded we add it to the not_loaded dictionary
        if solution is None:
            final_not_loaded[id] = box

    for item in pending:
        final_not_loaded[item[0]] = boxes[item[0]]
        solutions.remove(item)

    return solutions, final_not_loaded, PPs


def break_combination(id, current_pp, PPs, hmap):
    """
    DUDA 4: Esto no esta completo y no se usa
    """
    box1 = []
    box2 = []
    for pp in PPs:
        if pp[0] + pp[3] >= current_pp[0] and pp[2] == current_pp[2]:
            pass


def load_boxes(
    boxes: Dict[Tuple[str, str], List[int]],
    container_dimensions: Tuple[int, int, int],
    load_type: int,
    viaje: str
) -> Tuple[List[Tuple[str, Tuple[int, int, int, int, int, int]]], Dict[Tuple[str, str], List[int]], List[Tuple[int, int, int, int, int]]]:
    """
    Load boxes into a container based on their dimensions and the available space.
    This function attempts to place boxes in the container, respecting the dimensions and
    constraints of the container and the boxes themselves. It returns a list of solutions
    representing the boxes placed in the container, a dictionary of boxes that could not be loaded,
    and a list of potential points (PPs) representing available space in the container.

    Parameters:
        boxes (Dict[Tuple[str, str], List[int]]): A dictionary where keys are tuples of box identifiers
            and values are lists containing the dimensions of the boxes (length, width, height, priority, stackable).
        container_dimensions (Tuple[int, int, int]): A tuple representing the dimensions of the container
            (length, width, height).
        load_type (int): An integer representing the type of load being processed.
        viaje (str): A string representing the voyage identifier.

    Returns:
        Tuple[List[Tuple[str, Tuple[int, int, int, int, int, int]]], Dict[Tuple[str, str], List[int]], List[Tuple[int, int, int, int, int]]]:
            - A list of tuples where each tuple contains a box identifier and its position in the container.
            - A dictionary of boxes that could not be loaded into the container.
            - A list of potential points (PPs) representing available space in the container.
    """
    container_length, container_width, container_height = container_dimensions

    # If we want to continue from a previous load, we will load the JSON file with the previous solutions
    if load_type == 4:
        # Load the JSON file
        with open(f"soluciones/output_{viaje}.json", "r") as file:
            loaded_output = json.load(file)

        # Convert solutions lists back to tuples
        solutions = loaded_output["solution"]
        solutions = [(tuple(item[0]), tuple(item[1])) for item in solutions]

        # Convert the potential points (PPs) back to tuples
        PPs = loaded_output["PPs"]
        PPs = [tuple(item) for item in PPs]

        last_box = max(solutions, key=lambda x: x[1][0] + x[1][3])[1]
        x_axis = last_box[0] + last_box[3]

        not_loaded = {}

    else:
        # Initialize two PPs for the container (one for the right side and one for the left side)
        PPs = [
            (0, container_width, 0, container_length, -container_width, container_height, "right"),
            (0, 0, 0, container_length, container_width, container_height, "left")
        ]

        solutions = []
        not_loaded = {}

    pending = []
    # Loop over each box and try to place it
    for id, box in boxes.items():
        suffix = id[0][-2:len(id[0])]
        # DUDA 4: Preguntar que es esto y por que esta puesto aquí
        if suffix == "_W":
            combined = True
        else:
            combined = False

        # Sort the PPs according to the current box
        sorted_PPs = sort_PPs(box, PPs, load_type, solutions)
        solution = None

        # Loop over each PP to try to place the box in it
        for pp in sorted_PPs:
            x, y, z = pp[0:3]

            if pp[6] == "right":
                l, w, h = box[0], -box[1], box[2]
            else:
                l, w, h = box[0], box[1], box[2]

            # If the PP, box combination is feasible we will place the box
            if is_feasible(pp, l, w, h, solutions):
                # Generate the solution
                # DUDA 4: Preguntar si esto es necesario, porque no se usa
                """if combined == True:
                    solution = break_combination()
                else:
                    solution = (id,(x, y, z, l, w, h))"""

                solution = (id, (x, y, z, l, w, h))
                PPs.remove(pp)

                # Create the new PPs to be added to the list
                front_pp = (x + l, y, z, pp[3] - l, pp[4], pp[5], pp[6])
                side_pp = (x, y + w, z, l, pp[4] - w, pp[5], pp[6])
                top_pp = (x, y, z + h, l, w, pp[5] - h, pp[6])
                right_corner_pp = (x + l, container_width, z, container_length - (x + l), -244, pp[5], "right")
                left_corner_pp = (x + l, 0, z, container_length - (x + l), 244, pp[5], "left")

                # Top pp is merged with adjacent spaces
                top_pp, old_pp = merge(top_pp, PPs)

                if old_pp is not None:
                    PPs.remove(old_pp)

                # We add the front and side PPs to the available PPs list
                PPs.append(front_pp)
                PPs.append(side_pp)

                # The top PP only gets added to the available list if the box is stackable
                if box[4] == 1:
                    PPs.append(top_pp)

                # If there is enough space on the right side of the container, we add the right corner PP
                if 244 - (y + w) < 30 and z == 0:
                    PPs.append(right_corner_pp)

                # If there is enough space on the left side of the container, we add the left corner PP
                if (y + w) < 30 and z == 0 and pp[6] == "right":
                    PPs.append(left_corner_pp)

                solutions.append(solution)

                if z > 0 and l > w and h > w:
                    pending.append(solution)

                pending = lateral_support(solutions, pending, container_width)

                break

        # If the box is not loaded we add it to the not_loaded dictionary
        if solution is None:
            not_loaded[id] = box

    # Remove not validated boxes from solutions
    for item in pending:
        not_loaded[item[0]] = boxes[item[0]]
        solutions.remove(item)

    solutions, not_loaded, PPs = retry(not_loaded, PPs, load_type, solutions, container_dimensions, boxes)

    return solutions, not_loaded, PPs
