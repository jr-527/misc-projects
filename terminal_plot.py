import os

# modified from https://stackoverflow.com/a/63947444
def format_float(x, width=8, left=True):
    maxnum = int('9'*(width - 1))
    minnum = -int('9'*(width - 2))
    if x > minnum and x < maxnum:
        # o = f'{x:7}'
        if not left:
            o = f'{x:{width - 1}}'
        else:
            o = f'{x:<{width - 1}}'
        if len(o) > width:
            o = str(round(x, width - 1 - str(x).index('.')))
            if len(o) < width:
                o+=(width-len(o))*'0'
    else:
        for n in range(max(width, 5) - 5, 0, -1):
            fill = f'.{n}e'
            o = f'{x:{fill}}'.replace('+0', '+')
            if len(o) == width:
                break
        else:
            raise ValueError(f"Number is too large to fit in {width} characters", x)
    return o

def sideways_bar_plot(values, *, start=0, width=None):
    index_length = max(len(str(start)), len(str(len(values)+start)))
    if width is None:
        try:
            width = os.get_terminal_size()[0]-16-7
        except:
            width = 50
    min_val = min(values)
    max_val = max(values)
    # increment = (max_val - min_val) / 40
    increment = max(abs(max_val), abs(min_val))/width
    for i, v in zip(range(len(values)), values):
        val = int(v/increment)
        if max_val <= 0:
            val = -val
        out = str(i+start).rjust(index_length, ' ')
        out += '|' + '*'*val + ' ' + format_float(v, 12)
        print(out)

def plot_xy(x, y=None, *, width=None, height=None, stem=False, return_text=False):
    text = ''
    if height is None:
        try:
            height = os.get_terminal_size()[1]-4
        except:
            height = 25
    if width is None:
        try:
            width = os.get_terminal_size()[0]-12
        except:
            width = 70
        if width <= 10:
            height -= 2
    # we want:
    # x = [x1, x2, ...], y=[y1, y2, ...]
    # but will also accept:
    # x = [y1, y2, y3, y4, ...]
    # x = [(x1,y1), (x2,y2), ...]
    if y is None:
        if not hasattr(x[0], '__len__'):
            y = x
            x = list(range(len(y)))
        else:
            x, y = zip(*x) # unzip list of tuples
            x, y = list(x), list(y)
    x_min, x_max = min(x), max(x)
    x_range = x_max - x_min
    y_min, y_max = min(y), max(y)
    y_range = y_max - y_min
    # we want a list in the form list[y][x]
    arr = [[0]*width for _ in range(height)]
    for x_pos, y_pos in zip(x, y):
        # in older Python versions, round always returns a floating point value
        # so we cast to int
        x_coord = int(round((x_pos - x_min)/x_range*(width-1)))
        y_coord = int(round((y_pos - y_min)/y_range*(height-1)))
        if stem:
            y_0_coord = int(round(-y_min/y_range*(height-1)))
            between = lambda i: (y_0_coord <= i and i <= y_coord) or (y_coord <= i and i <= y_0_coord)
            for i in filter(between, range(0, height)):
                arr[i][x_coord] = max(arr[i][x_coord], 1)
        arr[y_coord][x_coord] += 1
    # print('_'*(width+2), format_float(y_max, 8))
    text += '_'*(width+2) + ' ' + format_float(y_max, 8) + '\n'
    for i in range(len(arr)):
        j = len(arr)-i-1
        row = arr[j]
        string = '|'
        for count in row:
            if count == 0:
                string += ' '
            elif count == 1:
                string += '*'
            else:
                string += '#'
        string += '|'
        if (i % 3 == 1):# or (i == len(arr)-1):
            string += ' ' + format_float(y_min + y_range * j/len(arr), 8)
        # print(string)
        text += string + '\n'
    spots = []
    fractions = [0, 0.25, 0.5, 0.75, 1]
    if width <= 10:
        fractions = []
    elif width <= 19:
        fractions = [0, 1]
    elif width <= 30:
        fractions = [0, 0.5, 1]
    elif width <= 40:
        fractions = [0, 1/3, 2/3, 1]
    out = []
    try:
        out = list('\u203e'*(width+2) + ' ' + format_float(y_min, 8))
        for fraction in fractions:
            i = 1+int(round(fraction*(width-1)))
            out[i] = '^'
            spots.append((i, fraction))
    except:
        spots = []
        out = list('-'*(width+2) + ' ' + str(round(y_min, 4)))
        for fraction in fractions:
            i = 1+int(round(fraction*(width-1)))
            out[i] = '+'
            spots.append((i, fraction))
    # print(''.join(out))
    text += ''.join(out) + '\n'
    if len(fractions) > 0:
        out = format_float(x_min, 7)
        prev = 5
        for i, fraction in spots[1:]:
            prev = len(out)
            out += ' '*(i-3-prev)
            out += format_float(x_min + fraction*x_range, 7)
        # print(out)
        text += out
    else:
        text += f'min x:{format_float(x_min, 7)}\n'
        text += f'max x:{format_float(x_max, 7)}'
        # print('min x:', format_float(x_min, 7))
        # print('max x:', format_float(x_max, 7))
    if return_text:
        return text + '\n'
    print(text)
    return None

import numpy as np
x = np.linspace(0,1, 200)
y = np.cos(20*x)
plot_xy(x, y, stem=True)