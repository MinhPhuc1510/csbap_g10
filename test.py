import csv

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