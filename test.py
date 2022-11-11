import csv
import math
import time

from grasp_1 import *
from graphic import graphic
from save_graphic import graphic_save

def get_input(filename):
    berth_lenght = 0
    berth_breaks = []
    input = []
    file = open('input/' + filename + '.csv')
    type(file)
    csvreader = csv.reader(file)
    index = 0
    for row in csvreader:
        if index == 0:
            berth_lenght = int(row[0])
        elif index == 1:
            berth_breaks = row
        else:
            input.append(row)
        index += 1
    file.close()
    berth_breaks = list(map(int, berth_breaks))
    for i in range(len(input)):
        input[i] = list(map(int, input[i]))
    return (berth_lenght, berth_breaks, input)

def test(inputList):
    for _input in inputList:
        print(_input)
        berth_lenght, berth_breaks, input = get_input(_input)
        print(f"Number of vessels: {len(input)}")

        start_time = time.time()
        t = max([i[2] for i in input]) + int(sum([i[3] for i in input])*(3/4))

        B = math.floor(max((7/8)*len(input), len(input) - 20))
        L1= 3

        # Sort increasing order according to  vessels arrival time.
        input = sorted(input, key=lambda x:x[2])

        # Greedy_Randomized_Construction
        time_fre = time.time()
        outputs, cost = construction_phrase(input, berth_lenght, t, berth_breaks)

        if (outputs == -1):
            with open('./output/' + _input + '.csv', 'w', newline = '') as f:
                write = csv.writer(f)
                
                write.writerow(['No solutions found'])

            continue

        print(f'Greedy_Randomized_Construction {time.time() - time_fre} s')

        # Local_Search
        time_search = time.time()
        input = local_search(L1, input, outputs, cost, berth_lenght, berth_breaks, t)

        best_input, best_solution, cost = a_star_like_tree_search(input, B, berth_lenght, t, berth_breaks)
        print(f'Local_Search {time.time() - time_search} s')

        # print(f"Solution: {best_solution}, with cost is: {cost}")
        print(f"Time to process: {time.time() - start_time} s")

        header = ['index', 'mooring time', 'starting berth position occupied']

        with open('./output/' + _input + '.csv', 'w', newline = '') as f:
            write = csv.writer(f)
            
            write.writerow(header)
            write.writerows(best_solution)
            write.writerow(["Cost", cost])
            write.writerow(["Time to process", time.time() - start_time])

        if len(inputList) == 1:
            # Covert to graphic_data
            graphic_data = change_output_to_graph(best_input, best_solution) 
            graphic(lines=graphic_data, berth_breaks=berth_breaks)
        else:
            # Covert to graphic_data
            graphic_data = change_output_to_graph(best_input, best_solution) 
            graphic_save(lines=graphic_data, berth_breaks=berth_breaks, input=_input)

def test_all():
    inputList = ['input_' + str(i) for i in range(17, 21)]
    test(inputList)

if __name__ == '__main__':
    test_all()
    test(['input_1'])
    test(['input_1', 'input_2'])
