import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import plotly.graph_objects as go
import random
import json

from .preprocessing import join_box
from .sorting import sort_boxes
from .packing import load_boxes
from .postprocessing import separate_boxes


def show_boxes(solutions):
    fig = go.Figure()
    for id, box_solution in solutions:
            x, y, z = box_solution[0:3]
            length, width, height = box_solution[3:6]
                
            hover_text = f'{id}<br>Dimensions: {length}x{width}x{height}<br>Position: ({x}, {y}, {z})'
            fig.add_trace(go.Mesh3d(
                x=[x, x + length, x + length, x, x, x + length, x + length, x],
                y=[y, y, y + width, y + width, y, y, y + width, y + width],
                z=[z, z, z, z, z + height, z + height, z + height, z + height],
                i= [7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
                j= [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k= [0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
                name=f'{id}',
                hovertext=hover_text                  
                ))
                
            # Set layout properties
            fig.update_layout(
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z',
                    aspectmode='data')
                )
        

    # Show the interactive plot
    fig.show(renderer = 'browser')

def RCH(container_dimensions, df, hmap, load_type, viaje):
    # Get provided container dimensions
    container_length, container_width, container_height = container_dimensions

    # Create boxes dictionary from DataFrame
    boxes = {}
    for i in range(len(df)):

        box_id = df['Partida'][i]
        box_group = df['Expedicion'][i]
        r = random.random()

        fixed = 0
        id = (box_id, box_group)

        # If we can fill the width of the container in one of the given directions we choose it.
        if int(df['LargoCm'][i]) > container_width or 0 <= (container_width - int(df['AnchoCm'][i])) < 8:
            boxes[id] = [int(df['LargoCm'][i]), int(df['AnchoCm'][i]), int(df['AltoCm'][i]), 2, int(df['Remontable'][i])]
            fixed = 1

        if int(df['AnchoCm'][i]) > container_width or 0 <= (container_width - int(df['LargoCm'][i])) < 8:
            boxes[id] = [int(df['AnchoCm'][i]), int(df['LargoCm'][i]), int(df['AltoCm'][i]), 2, int(df['Remontable'][i])]
            fixed = 1

        # The rest of boxes are given a random orientation
        if fixed == 0:
                
            if r < 0.5:
                boxes[id] = [int(df['AnchoCm'][i]), int(df['LargoCm'][i]), int(df['AltoCm'][i]), 2, int(df['Remontable'][i])]
                    
            else:
                boxes[id] = [int(df['LargoCm'][i]), int(df['AnchoCm'][i]), int(df['AltoCm'][i]), 2, int(df['Remontable'][i])]
    
    # If the box fills the container width we give it priority 1
    for id, box in boxes.items():
        if container_width - box[1] < 15:
            box[3] = 1

    # Sort the boxes by priority and volume (length * width * height)
    sorted_boxes = sort_boxes(boxes)

    # Packing step of the algorithm where the solution is generated
    solution, not_loaded, PPs = load_boxes(sorted_boxes, container_dimensions, load_type, viaje)

    solution = [x for x in solution if x != False]

    # Separate the boxes for visualization 
    final_solution = separate_boxes(solution, hmap)
    final_solution = list(dict.fromkeys(final_solution))

    used_volume = 0
    used_floor = 0
    
    # Calculate the total floor area and volume used in the container
    for id, box in final_solution:
        if box[2] == 0:
            box_floor = box[3]*abs(box[4])
            used_floor += box_floor

        box_volume = box[3]*abs(box[4])*box[5]
        used_volume += box_volume

    # X_axis represents the length of all of the loaded boxes (last box + last box length)
    last_box = max(final_solution, key= lambda x: x[1][0] + x[1][3])[1]
    x_axis = last_box[0] + last_box[3]

    # Pctg_floor is the percentage of the area of the container floor that is used
    pctg_floor = used_floor/(container_length*container_width) * 100

    # Pctg_volume represents the percentage of the total volume that is used
    pctg_volume = used_volume/(container_length*container_width*container_height) * 100

    return (pctg_volume, pctg_floor, x_axis, final_solution, not_loaded, PPs)

def get_volumes(viaje, load_type=1, file_path=None):
    # 4 types of load type:
    #   1. Maximize volume and floor
    #   2. Minimize X axis 
    #   3. Maximize only floor
    #   4. Resume loading from previous solution

    # Set the container dimensions
    container_dimensions = [1350, 246, 259]

    # Read the input excel
    df = pd.read_excel(file_path)
    
    # Preprocess the boxes to generate bigger boxes, we also generate a hmap to be able to separate the boxes later
    df, hmap = join_box(df, container_dimensions)

    # For each solution we store the solution and the boxes not loaded in a dictionary with the scores as the key
    all_solutions = {}
    for i in range(15000):

        pctg_volume, pctg_floor, x_axis, solution, not_loaded, PPs = RCH(container_dimensions, df, hmap, load_type, viaje)
        all_solutions[(pctg_volume, pctg_floor, x_axis)] = (solution, not_loaded, PPs)

    # We sort the keys depending on which score we want to minimize/maximize
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
    elif load_type ==4:
        sorted_keys = x_sorted_keys

    # We visualize the best solutions based on whichever score we prefer
    for i in range(5):
        show_boxes(all_solutions[sorted_keys[i]][0])
        print('Scores: ', sorted_keys[i])
        print('Not loaded: ', len(all_solutions[sorted_keys[i]][1]))
    
    # Calculate the average loaded volume
    all_pctg = [x[0] for x in floor_sorted_keys]
    avg_pctg = np.mean(all_pctg)

    # Create an excel file with the boxes that haven't been loaded
    not_loaded_best = pd.DataFrame.from_dict(all_solutions[volume_sorted_keys[0]][1], orient='index', columns=['LargoCm', 'AnchoCm', 'AltoCm', 'Prioridad', 'Remontable'])
    not_loaded_best.index.name = 'Partida'
    not_loaded_best.to_excel('not_loaded.xlsx')

    # If we are uing load_type 2 we save the solution as a json file to use it later
    if load_type == 2:
        output = {}
        output['solution'] = all_solutions[x_sorted_keys[0]][0]
        output['PPs'] = all_solutions[x_sorted_keys[0]][2]
        with open(f'soluciones/output_{viaje}.json', 'w') as file:
            json.dump(output, file)

    return avg_pctg, floor_sorted_keys[0], volume_sorted_keys[0], len(not_loaded_best)

#get_volumes('VBCN2403418', load_type=2, file_path='input_RCH/primera_VBCN2403418.xlsx')
#get_volumes('VBCN2403418', load_type=4, file_path='input_RCH/resto_VBCN2403418.xlsx')   
viaje = 'VBCN2403750'
#print(get_volumes(viaje, load_type=1, file_path=f'viajes_prueba/test_{viaje}.xlsx'))
