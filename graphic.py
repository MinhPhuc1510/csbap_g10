import random

import matplotlib.patches as mpatch
import matplotlib.pyplot as plt


def graphic(lines, berth_breaks):
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
# def main():
#     graphic()
# if __name__ == "__main__":
#     main()