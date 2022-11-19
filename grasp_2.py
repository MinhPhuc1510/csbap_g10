import math
import random
import sys
import time
from test import *

import numpy as np
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt

np.set_printoptions(threshold=sys.maxsize)

L4 = 200
L5 = 25

# np.random.seed(2)

def calculate_objective(input, output):
    result = 0
    for i in range(len(input)):
        w_i = input[i][4]
        c_i = output[i][1] + input[i][3]
        a_i = input[i][2]
        result += w_i * (c_i - a_i)
    return result


def generate_diagram(input, output, s, t):

    if input.shape[0] != 0 and output.shape[0] != 0:
        if t <= np.max(output[:, 1]) + np.max(input[:, 3]):
            t = np.max(output[:, 1]) + np.max(input[:, 3]) + 1
        diagram = np.ones((s, t))
        for i in range(input.shape[0]):
            diagram[output[i][2]: output[i][2] + input[i][1], output[i][1]: output[i][1] + input[i][3]] = 0
    else :
        diagram = np.ones((s, t))
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
    for i in range(s + 1):
        for j in range(an, t + 1):
            class_temp = [result_pad[i + 1, j + 1], result_pad[i + 1, j], result_pad[i, j], result_pad[i, j + 1]]
            if class_temp == [0, 0, 0, 1] or class_temp == [0, 1, 0, 1]:
                class_1_top.append((i, j))

            elif class_temp == [1, 0, 0, 0] or class_temp == [1, 0, 1, 0]:
                class_1_bot.append((i, j))

            elif class_temp == [0, 1, 1, 1]:
                class_3_left_up.append((i, j))
                for k in range(j, -1, -1):
                    if [result_pad[i + 1, k + 1], result_pad[i + 1, k], result_pad[i, k], result_pad[i, k + 1]] == [1,
                                                                                                                    0,
                                                                                                                    0,
                                                                                                                    1]:
                        class_1_top.append((i, k))
                        break

            elif class_temp == [1, 1, 1, 0]:
                class_3_left_down.append((i, j))
                for k in range(j, -1, -1):
                    if [result_pad[i + 1, k + 1], result_pad[i + 1, k], result_pad[i, k], result_pad[i, k + 1]] == [1,
                                                                                                                    0,
                                                                                                                    0,
                                                                                                                    1]:
                        class_1_bot.append((i, k))
                        break

            elif class_temp == [1, 0, 1, 1]:
                class_3_down.append((i, j))
                for k in range(i, -1, -1):
                    if [result_pad[k + 1, j + 1], result_pad[k + 1, j], result_pad[k, j], result_pad[k, j + 1]] == [1,
                                                                                                                    1,
                                                                                                                    0,
                                                                                                                    0]:
                        class_1_bot.append((k, j))
                        break

            elif class_temp == [1, 1, 0, 1]:
                class_3_up.append((i, j))
                for k in range(i, s + 1):
                    if [result_pad[k + 1, j + 1], result_pad[k + 1, j], result_pad[k, j], result_pad[k, j + 1]] == [0,
                                                                                                                    0,
                                                                                                                    1,
                                                                                                                    1]:
                        class_1_bot.append((k, j))
                        break

    for y1, x1 in class_3_left_down:
        for y2, x2 in class_3_down:
            if x1 > x2 and y1 < y2:
                class_1_bot.append((x2, y1))

    for y1, x1 in class_3_left_up:
        for y2, x2 in class_3_up:
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

        if (top[0] - input[1]) < 0:
            return False

        if top[1] + input[3] > diagram.shape[1]:
            if not np.all(diagram[top[0] - input[1]:top[0], top[1]:]):
                return False
        else:
            for m in range(top[0] - input[1], top[0]):
                for n in range(top[1], top[1] + input[3]):
                    if diagram[m, n] == 0:
                        return False

    if bot:
        for i in break_berths:
            if bot[0] + input[1] > i > bot[0]:
                return False

        if (bot[0] + input[1]) > berth_lenght:
            return False

        if bot[1] + input[3] > diagram.shape[1]:
            if not np.all(diagram[bot[0]: bot[0] + input[1], bot[1]:]):
                return False
        else:
            if not np.all(diagram[bot[0]: bot[0] + input[1], bot[1]:bot[1] + input[3]]):
                return False
    return True


def construction_phrase(input, berth_lenght, t, berth_breaks):
    outputs = []
    unpacked_vessels = input.copy()
    packed_vessels = []

    while len(unpacked_vessels) > 0:
        # generate diagram from input and output
        diagram = generate_diagram(np.array(packed_vessels), np.array(outputs), berth_lenght, t)

        # find all possible positions
        possible_poisition = process_input(diagram, unpacked_vessels[0][2])[1]
        tops, bots = possible_poisition["class_1_top"], possible_poisition["class_1_bot"]

        for b in berth_breaks:
            for k in range(len(tops)):
                break_poisition = (b, tops[k][1])
                tops.append(break_poisition)
            tops.append((b, unpacked_vessels[0][2]))
            for m in range(len(bots)):
                break_poisition = (b, bots[m][1])
                bots.append(break_poisition)
            bots.append((b, unpacked_vessels[0][2]))

        costs = []
        max = 0
        valid_position = []

        for loc in list(set(bots)):
            if not validate_berth_break(top=None, bot=loc, input=unpacked_vessels[0], break_berths=berth_breaks,
                                        diagram=diagram, berth_lenght=berth_lenght):
                continue
            else:
                outputs.append([unpacked_vessels[0][0], loc[1], loc[0]])
                packed_vessels.append(unpacked_vessels[0])
                cost = calculate_objective(input=packed_vessels, output=outputs)
                packed_vessels.pop(-1)
                outputs.pop(-1)
                score = 1 / cost
                if score < 0.95 * max:
                    continue
                elif score > max:
                    max = score
                costs.append(score)
                valid_position.append(loc)

        for loc in list(set(tops)):
            if not validate_berth_break(top=loc, bot=None, input=unpacked_vessels[0], break_berths=berth_breaks,
                                        diagram=diagram, berth_lenght=berth_lenght):
                continue
            else:
                outputs.append([unpacked_vessels[0][0], loc[1], loc[0] - unpacked_vessels[0][1]])
                packed_vessels.append(unpacked_vessels[0])
                cost = calculate_objective(input=packed_vessels, output=outputs)
                packed_vessels.pop(-1)
                outputs.pop(-1)
                score = 1 / cost
                if score < 0.95 * max:
                    continue
                elif score > max:
                    max = score
                costs.append(score)
                valid_position.append((loc[0] - unpacked_vessels[0][1], loc[1]))

        if len(valid_position) == 0:
            print("No solutions found")
            return -1, -1

        probability = np.array(costs) / np.sum(np.array(costs))
        index = np.random.choice(range(len(valid_position)), p=probability)
        position = valid_position[index]
        outputs.append([unpacked_vessels[0][0], position[1], position[0]])
        packed_vessels.append(unpacked_vessels[0])
        unpacked_vessels.pop(0)

    cost = calculate_objective(packed_vessels, outputs)
    return outputs, cost


def local_search(L1, L2, L3, L4, L5, input, outputs, cost, berth_lenght, berth_breaks, t):
    best_input = input
    solution_steady_count = 0
    decrease_B = 0
    unchange_count = 0

    for _ in range(L1):
        if solution_steady_count == L2:
            if unchange_count == 0:
                decrease_B += 1
            unchange_count = L3
            solution_steady_count = 0

        swap_input = input.copy()
        m,n = random.sample(range(0, len(outputs)), 2)
        swap_input[m], swap_input[n] = swap_input[n], swap_input[m]
        _, cost_swap = construction_phrase(swap_input, berth_lenght, t, berth_breaks)
        if cost_swap < cost:
            best_input = swap_input
            cost = cost_swap
        else:
            solution_steady_count += 1

        unchange_count = unchange_count - 1 if unchange_count > 0 else 0

    return best_input, decrease_B


def change_output_to_graph(input, outputs):
    graphic_data = []
    for i in range(len(input)):
        graphic_data.append([input[i][0], input[i][1], outputs[i][1], input[i][3], outputs[i][2]])
    return graphic_data


def a_star_like_tree_search(input, B, berth_lenght, t, berth_breaks):
    best_input = input[:B].copy()
    temp = input[B:].copy()
    for _ in range(len(input) - B):
        cost = []
        outputs = []
        for m in temp:
            split_input = best_input.copy()
            split_input.append(m)
            output, cost_value = construction_phrase(split_input, berth_lenght, t, berth_breaks)
            cost.append(cost_value)
            outputs.append(output)

        index = cost.index(min(cost))
        best_input.append(temp[index])
        temp.pop(index)
        if len(temp) == 0:
            break

    return best_input, outputs[index], min(cost)


def graphic(lines, berth_breaks, file_output):
    fig, ax = plt.subplots()
    colors = ['yellow', 'red', '#0099FF', '#EB70AA', 'green', 'blue', 'purple', "brown", "pink"]
    # with open('result.txt') as txtfile:
    #     data = txtfile.read()
    #     lines = data.split("\n")
    #     lines.remove('stt size    arrival time    processing time wharf')
    #     txtfile.close()
    rectangles = {}
    max_x = 0
    max_y = 0
    for i in range(0, len(lines)):
        # mpatch.Rectangle((arrival time ,wharf), processing time , length of ship),
        name = lines[i][0]
        data = lines[i]
        for j in range(0, 5):
            if j == 0:
                continue
            elif j == 1:
                lenght_of_ship = int(data[j])
            elif j == 2:
                arrival_time = int(data[j])
            elif j == 3:
                processing_time = int(data[j])
            elif j == 4:
                wharf = int(data[j])
        if (arrival_time + processing_time) > max_x:
            max_x = arrival_time + processing_time
        if (wharf + lenght_of_ship) > max_y:
            max_y = wharf + lenght_of_ship
        tmp = {name: mpatch.Rectangle((arrival_time, wharf), processing_time, lenght_of_ship, color=colors[random.randint(0, len(colors)-1)])}
        rectangles.update(tmp)
    for r in rectangles:
        ax.add_artist(rectangles[r])
        rx, ry = rectangles[r].get_xy()
        cx = rx + rectangles[r].get_width() / 2
        cy = ry + rectangles[r].get_height() / 2
        ax.annotate(r, (cx, cy), color='black', weight='bold', fontsize=10, ha='center', va='center')
    ax.set_xlim((0, max_x + 1))
    ax.set_ylim((0, max_y + 1))
    ax.set_aspect('equal')
    for i in berth_breaks:
        plt.axline((0, i), (max_x, i))
    plt.grid(color='green', linestyle='--', linewidth=0.5)
    plt.xticks(range(0, max_x + 1, ))
    plt.yticks(range(0, max_y + 1))
    plt.show()
    plt.savefig(file_output)

if __name__ == '__main__':
    input_file = 'input_20'
    berth_lenght, berth_breaks, input = get_input(input_file)

    print(berth_lenght)
    print(berth_breaks)
    print(input)

    start_time = time.time()
    t = 1

    B = math.floor(max((7 / 8) * len(input), len(input) - 20))
    LB = math.floor(max((3 / 4) * len(input), len(input) - 40))
    L1 = 3
    L2 = 5
    L3 = 10

    # Greedy_Randomized_Construction
    time_fre = time.time()
    outputs, cost = construction_phrase(input, berth_lenght, t, berth_breaks)

    if outputs == -1:
        print('No solution found!')
    print(f'Greedy_Randomized_Construction {time.time() - time_fre} s')

    # Local_Search
    time_search = time.time()
    input, decrease_B = local_search(L1, L2, L3, L4, L5, input, outputs, cost, berth_lenght, berth_breaks, t)

    B = max(B - decrease_B, LB)

    best_input, best_solution, cost = a_star_like_tree_search(input, B, berth_lenght, t, berth_breaks)
    print(f'Local_Search {time.time() - time_search} s')

    print(f"Solution: {best_solution}, with cost is: {cost}")
    print(f"Time to process: {time.time() - start_time} s")

    # Covert to graphic_data
    graphic_data = change_output_to_graph(best_input, best_solution)
    file_output = input_file.replace('in', 'out')
    graphic(lines=graphic_data, berth_breaks=berth_breaks,
            file_output = './output_grasp_2/' + file_output)
