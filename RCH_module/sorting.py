import random as random
def sort_boxes(boxes):
    # First step is to do a simple sorting of the boxes, we sort first by priority box[3] and then by volume 
    sorted_boxes = dict(sorted(boxes.items(), key=lambda x: (x[1][2], x[1][0]), reverse=True))
    final_order = {}

    # Second step is adding some randomization to the order, if two boxes next to each other in the order have a similar enough
    # order then with a probability of 0.5 we swap them
    sorted_list = list(sorted_boxes.items())

    for i in range(0,len(sorted_list),2):
        j = i+1

        if j < len(sorted_boxes):
            vol1 = sorted_list[i][1][0] * sorted_list[i][1][1] * sorted_list[i][1][2]
            vol2 = sorted_list[j][1][0] * sorted_list[j][1][1] * sorted_list[j][1][2]
            prio1 = sorted_list[i][1][3]
            prio2 = sorted_list[j][1][3]
            r = random.random()

            # Check if the ratio of volumes is within 30% and the a probability of 0.5
            if 0.7 <= vol1/vol2 and vol1/vol2 <= 1.3 and r < 0.7 and prio1 == prio2:
                final_order[sorted_list[j][0]] = sorted_list[j][1]
                final_order[sorted_list[i][0]] = sorted_list[i][1]

            else:
                final_order[sorted_list[i][0]] = sorted_list[i][1]
                final_order[sorted_list[j][0]] = sorted_list[j][1]
        else:
            final_order[sorted_list[i][0]] = sorted_list[i][1]
    
    # Return the final order of the boxes after sorting and swapping
    return final_order