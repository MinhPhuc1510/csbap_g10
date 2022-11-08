import numpy as np
import sys
from graphic import graphic
import random
import time


np.set_printoptions(threshold=sys.maxsize)
def calculate_objective(input, output):
    result = 0
    for i in range(len(input)):
        w_i = input[i][4]
        c_i = output[i][1] + input[i][3]
        a_i = input[i][2]
        result += w_i*(c_i - a_i)
    return result

def generate_diagram(input, output, s, t):
    diagram = np.ones((s, t))
    if input.shape[0] !=0 and output.shape[0] !=0:
        for i in range(input.shape[0]):
            diagram[output[i][2]: output[i][2] + input[i][1] , output[i][1]: output[i][1] + input[i][3]] = 0
    return diagram


def process_input(diagram, an):
    
    class_1_top = []
    class_1_bot = []
    class_3_left_up = []
    class_3_left_down = []
    class_3_down = []
    class_3_up = []
    s, t = diagram.shape

    diagram[:, 0:an] = 0
    result_pad = np.pad(diagram, [(1, 1), (1, 1)], mode='constant')
    for i in range(s+1):
        for j in range(t+1):
            class_temp = [result_pad[i + 1, j+1], result_pad[i + 1, j], result_pad[i, j], result_pad[i, j+1]]
            if class_temp == [0, 0, 0, 1] or class_temp == [0, 1, 0, 1]:
                class_1_top.append((i,j))

            elif class_temp == [1, 0, 0, 0] or class_temp == [1, 0, 1, 0]:
                class_1_bot.append((i,j))

            elif class_temp == [0, 1, 1, 1]:
                class_3_left_up.append((i,j))
                for k in range(j,-1,-1):
                    if [result_pad[i+1, k+1], result_pad[i+1, k], result_pad[i, k], result_pad[i, k+1]] == [1, 0, 0, 1]:
                        class_1_top.append((i, k))
                        break

            elif class_temp == [1, 1, 1, 0]:
                class_3_left_down.append((i,j))
                for k in range(j,-1,-1):
                    if [result_pad[i + 1, k+1], result_pad[i + 1, k], result_pad[i, k], result_pad[i, k+1]] == [1, 0, 0, 1]:
                        class_1_bot.append((i, k))
                        break
                
            elif class_temp == [1, 0, 1, 1]:
                class_3_down.append((i,j))
                for k in range(i,-1,-1):
                    if [result_pad[k + 1, j +1], result_pad[k + 1, j], result_pad[k, j], result_pad[k, j +1]] == [1, 1, 0, 0]:
                        class_1_bot.append((k, j))
                        break

            elif class_temp ==  [1, 1, 0, 1]:
                class_3_up.append((i, j))
                for k in range(i, s+1):
                    if [result_pad[k + 1, j + 1], result_pad[k + 1, j], result_pad[k, j], result_pad[k, j +1]] == [0, 0, 1, 1]:
                        class_1_bot.append((k, j))
                        break

    for y1,x1 in class_3_left_down:
        for y2,x2 in class_3_down:
            if x1 > x2 and y1 < y2:
                class_1_bot.append((x2, y1))

    for y1,x1 in class_3_left_up:
        for y2,x2 in class_3_up:
            if x1 > x2 and y1 > y2:
                class_1_top.append((y1, x2))

    
    temp = {
        "class_1_top": class_1_top,
        "class_1_bot": class_1_bot,
        "class_3_left_down": class_3_left_down,
        "class_3_left_up": class_3_left_up,
        "class_3_down": class_3_down,
        "class_3_up": class_3_up,
    }

    return result_pad, temp, diagram

def validate_berth_break(top, bot, input, break_berths, diagram, berth_lenght):
    if top:
        for i in break_berths:
            if top[0] - input[1] < i < top[0]:
                return False

        for m in range(top[0]- input[1], top[0]):
            for n in range(top[1], top[1] + input[3]):
                if (top[0] - input[1]) < 0:
                        return False
                if diagram[m,n] == 0:
                    return False
    if bot:
        for i in break_berths:
            if bot[0] + input[1] > i > bot[0]:
                return False
                    
        for m in range(bot[0], bot[0] + input[1]):
            for n in range(bot[1], bot[1] + input[3]):
                if (bot[0] + input[1]) > berth_lenght:
                    return False
                if diagram[m,n] == 0:
                    return False

    return True


def Construction_phrase(input, berth_lenght, t, berth_breaks):
        
        outputs = []
        input = np.array(input)
        for i in range(input.shape[0]):
            # generate diagram from input and output
            diagram = generate_diagram(np.array(input[0:i]), np.array(outputs), berth_lenght, t)

            # find all possible positions
            possible_poisition = process_input(diagram, input[i][2])[1]
            tops, bots = possible_poisition["class_1_top"], possible_poisition["class_1_bot"]
        
            for  b in berth_breaks:
                for k in range(len(tops)):
                    break_poisition =(b, tops[k][1])  
                    tops.append(break_poisition)
                    tops.append((b, input[i][2]))
                for m in range(len(bots)):
                    break_poisition =(b, bots[m][1])
                    bots.append(break_poisition)
                    bots.append((b, input[i][2])) 
            costs = []
            max = 0
            valid_position = []

            for loc in bots:
                if not validate_berth_break(top=None, bot=loc, input=input[i],break_berths=berth_breaks,
                diagram=diagram, berth_lenght=berth_lenght):
                    continue
                else:
                    outputs.append([input[i][0], loc[1], loc[0]])
                    cost = calculate_objective(input=input[0:i+1], output=outputs)
                    outputs.pop(-1)
                    if 1/(cost + 0.000001) < 0.9*max:
                        continue
                    else:
                        max = 1/cost
                    valid_position.append(loc)

            for loc in tops:
                if not validate_berth_break(top=loc, bot=None, input=input[i],break_berths=berth_breaks,
                diagram=diagram, berth_lenght=berth_lenght):
                        continue
                else:
                    outputs.append([input[i][0], loc[1], loc[0]-input[i][1]])
                    cost = calculate_objective(input=input[0:i+1], output=outputs)
                    outputs.pop(-1)
                    if 1/(cost + 0.000001) < 0.9*max:
                        continue
                    else:
                        max = 1/cost
                    valid_position.append((loc[0]-input[i][1], loc[1]))
            if len(valid_position) == 0:
                print("No solutions found")
                exit(-1)
            
            
            for loc in valid_position:
                outputs.append([input[i][0], loc[1], loc[0]])
                cost = calculate_objective(input=input[0:i+1], output=outputs)
                outputs.pop(-1)
                costs.append(1/(cost + 0.000001))

            probability = np.array(costs)/np.sum(np.array(costs))
            index = np.random.choice(range(len(valid_position)), p=probability)
            position = valid_position[index]
            outputs.append([input[i][0], position[1], position[0]])
        
        cost = calculate_objective(input,outputs)
        return outputs, cost
     
def local_search(L1, input, outputs, cost, berth_lenght, berth_breaks, t):
    best_input = input
    swap_input = input.copy()
    for _ in range(L1):
        swap_input = input.copy()
        M = random.randint(0, len(outputs) -2)
        swap_input[M+1], swap_input[M]= swap_input[M], swap_input[M+1]
        _, cost_swap = Construction_phrase(swap_input, berth_lenght, t, berth_breaks)
        if cost_swap < cost:
            best_input = swap_input
            cost = cost_swap   
    return best_input

def change_output_to_graph(input, outputs):
    graphic_data = []
    for i in range(len(input)):
        graphic_data.append([input[i][0], input[i][1], outputs[i][1], input[i][3], outputs[i][2]])
    return graphic_data
    
def a_star_like_tree_search(input, B, berth_lenght, t, berth_breaks):
    
    # Need to implement
    return input


if __name__ == '__main__':
    start_time = time.time()
    berth_lenght = 35
    berth_breaks = [20, 32]
    
    input = [
        [1,10, 10, 10, 1],
        [2,15, 5, 9, 2], 
        [3,6, 0, 5, 1],
        [4,20,2, 10, 3],
        [5,5, 15, 5, 1],
        [6,15, 12, 8, 1],
        [7,7, 8, 10, 3]
    ]
    t= sum([i[3] for i in input])*4

    # Sort increasing order according to  vessels arrival time.
    input = sorted(input, key=lambda x:x[2])

    # Greedy_Randomized_Construction
    outputs, cost = Construction_phrase(input, berth_lenght, t, berth_breaks)

    # Local_Search
    input = local_search(10, input, outputs, cost, berth_lenght, berth_breaks, t)
    best_solution = a_star_like_tree_search(input, len(input)//2, berth_lenght, t, berth_breaks)
    output_final = Construction_phrase(best_solution, berth_lenght, t, berth_breaks)

    print(f"Solution: {output_final[0]}, with cost is: {output_final[1]}")
    print(f"Time to process: {time.time() - start_time} s")

    # Covert to graphic_data
    graphic_data = change_output_to_graph(best_solution, output_final[0])
    graphic(lines=graphic_data, berth_breaks=berth_breaks)