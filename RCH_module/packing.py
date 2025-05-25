import json

def score_point(x, y, z, l, w, h, current_solution):
    left_support = False
    right_support = False

    # Check for wall support
    if y == 0 or y + w == 0:  # Left wall
        left_support = True
    if y + w == 244 or y == 244:  # Right wall
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

def sort_PPs(box, PPs, load_type, solutions):
    # Potential points sorting
    PPs_coverage = []

    for pp in PPs:
        box_area = box[0] * box[1]
        pp_area = abs(pp[3] * pp[4])  # Calculate the area of the potential point

        #support = 100*score_point(pp[0], pp[1], pp[2], box[0], box[1], box[2], solutions)
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
        PPs_coverage = sorted(PPs_coverage, key=lambda x: (x[2], x[1] -x[0][0]), reverse=True)
        sorted_PPs = [x[0] for x in PPs_coverage]

    return sorted_PPs

def check_intersection(box1, box2):
    x1, y1, z1, l1, w1, h1 = box1[1][0:6]
    x2, y2, z2, l2, w2, h2 = box2[0:6]

    y1_min = y1
    y1_max = y1 + w1 if w1 > 0 else y1
    y1_min = y1 + w1 if w1 < 0 else y1

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

def is_feasible(pp, l, w, h, solutions):
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
        if intersection == True:
            return False

    return True

def merge(pp, PPs):
    # Merging algorithm for top spaces
    x2, y2, z2, l2, w2, h2, direction2 = pp

    for pp1 in PPs:
        x1, y1, z1, l1, w1, h1, direction1 = pp1

        # We merge two spaces if they are adjacent and the z value is similar enough
        if x1 < x2 and y1 == y2 and abs(z1-z2) < 6 and x2 - (x1+l1) < 6:

            if direction1 == 'left':
                new_pp = (x1, y1, z1, l1+l2, min(w1,w2), h1, direction1)
                return new_pp, pp1
            else:
                new_pp = (x1, y1, z1, l1+l2, max(w1,w2), h1, direction1)
                return new_pp, pp1

        if x1 == x2 and y1 < y2 and abs(z1-z2) < 7 and y2 - (y1+w1) < 6:
            new_pp = (x1, y1, z1, min(l1,l2), w1+w1, h1, direction1)
            return new_pp, pp1

    return pp, None

def lateral_support(current_solution, pending, container_width):
    """
    Check if pending boxes have sufficient lateral support (either from walls or other boxes).

    Parameters:
        current_solution (list): List of tuples (id, box) already placed in the container.
        pending (list): List of tuples (id, box) pending to be validated for lateral support.
        container_width (int): Total width of the container to handle wall conditions.

    Returns:
        pending (list): Updated pending list with boxes that lack sufficient lateral support.
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
            if ((y2 == y + w or y2 + w2 == y) and  # Adjacent on the left
                z < z2 + h2 and  # Vertical overlap
                x < x2 + l2 and x + l > x2):  # Horizontal overlap
                support1 = True

            # Right-side support (box placed to the right of the current box)
            if ((y2 == y + w or y2 + w2 == y) and  # Adjacent on the right
                z < z2 + h2 and  # Vertical overlap
                x < x2 + l2 and x + l > x2):  # Horizontal overlap
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

def retry(not_loaded, PPs, load_type, solutions, container_dimensions, boxes):

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

            if pp[6] == 'right':
                l, w, h = box[1], -box[0], box[2]
            else:
                l, w, h = box[1], box[0], box[2]
            
            # If the PP, box combination is feasible we will place the box
            if is_feasible(pp, l, w, h, solutions):
                
                # Generate the solution
                solution = (id,(x, y, z, l, w, h))
                
                PPs.remove(pp)

                # Create the new PPs to be added to the list
                front_pp = (x + l, y, z, pp[3]-l, pp[4], pp[5], pp[6])
                side_pp = (x, y + w, z, l, pp[4]-w, pp[5], pp[6])
                top_pp = (x, y, z + h, l, w, pp[5]-h, pp[6])
                right_corner_pp = (x + l, container_width, z, container_length-(x+l), -244, pp[5], 'right')

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
    box1 = []
    box2 = []
    for pp in PPs:
        if pp[0] + pp[3] >= current_pp[0] and pp[2] == current_pp[2]:
            pass

def load_boxes(boxes, container_dimensions, load_type, viaje):
    container_length, container_width, container_height = container_dimensions

    # Initialize two PPs for the container
    if load_type == 4:

        # Load the JSON file
        with open(f"soluciones/output_{viaje}.json", "r") as file:
            loaded_output = json.load(file)
        
        # Convert solutions lists back to tuples
        solutions = loaded_output['solution']
        solutions = [(tuple(item[0]), tuple(item[1])) for item in solutions]

        PPs = loaded_output['PPs']
        PPs = [tuple(item) for item in PPs]

        last_box = max(solutions, key= lambda x: x[1][0] + x[1][3])[1]
        x_axis = last_box[0] + last_box[3]

        not_loaded = {}

    else:
        PPs = [(0, container_width, 0, container_length, -container_width, container_height, 'right'), (0, 0, 0, container_length, container_width, container_height, 'left')]
        
        solutions = []
        not_loaded = {}

    pending = []
    # Loop over each box and try to place it
    for id, box in boxes.items():

        suffix = id[0][-2:len(id[0])]
        if suffix == '_W':
            combined = True
        else:
            combined = False

        # Sort the PPs according to the current box
        sorted_PPs = sort_PPs(box, PPs, load_type, solutions)
        solution = None

        # Loop over each PP to try to place the box in it
        for pp in sorted_PPs:
            x, y, z = pp[0:3]

            if pp[6] == 'right':
                l, w, h = box[0], -box[1], box[2]
            else:
                l, w, h = box[0], box[1], box[2]

            # If the PP, box combination is feasible we will place the box
            if is_feasible(pp, l, w, h, solutions):
                
                # Generate the solution
                '''if combined == True:
                    solution = break_combination()
                else:
                    solution = (id,(x, y, z, l, w, h))'''
                
                solution = (id,(x, y, z, l, w, h))
                
                PPs.remove(pp)

                # Create the new PPs to be added to the list
                front_pp = (x + l, y, z, pp[3]-l, pp[4], pp[5], pp[6])
                side_pp = (x, y + w, z, l, pp[4]-w, pp[5], pp[6])
                top_pp = (x, y, z + h, l, w, pp[5]-h, pp[6])
                right_corner_pp = (x + l, container_width, z, container_length-(x+l), -244, pp[5], 'right')
                left_corner_pp = (x + l, 0, z, container_length-(x+l), 244, pp[5], 'left')

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
                
                if (y + w) < 30 and z == 0 and pp[6] == 'right':
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