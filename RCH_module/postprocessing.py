def separate_boxes(solution, hmap):
    # This function aims to separate the groups of boxes created in preprocessing into single boxes
    final_solution = []

    # We check all of the solutions and if any of the solutions is contained in the hmap it means that the solution is a group of boxes
    while solution:
        i = solution.pop(0)
        id = i[0]
        sol = i[1]

        suffix = id[0][-2:len(id[0])]
        if id in hmap:
            
            # If the solution is in the hmap we iterate over local solution contained in the hmap of where each box is located
            # relative to the other boxes in its group
            for box, position in hmap[id]:
                
                # We have different cases of how the local solution gets added to the global solution, if the global solution
                # has a negative width, it means it has been placed on the right wall so the width of individual boxes
                # will also be negative. We also have the case where we only want to change the height of the box, these boxes have an added
                # _H to the id to make them identifiable.
                if suffix == '_H':
                    new_position = (sol[0], sol[1], position[2], sol[3], sol[4], position[5])

                elif sol[4] < 0:
                    if position[1] > 0:
                        new_position = (position[0]+sol[0], sol[1]-position[1], position[2]+sol[2], position[3], -position[4], position[5])
                    else:
                        new_position = (position[0]+sol[0], position[1]+sol[1], position[2]+sol[2], position[3], -position[4], position[5])

                else:
                    new_position = (position[0]+sol[0], position[1]+sol[1], position[2]+sol[2], position[3], position[4], position[5])
                    
                new_sol = (box, new_position)
                
                solution.append(new_sol)

                if box not in hmap:
                    final_solution.append(new_sol)
        else:
            final_solution.append(i)

    return final_solution
        