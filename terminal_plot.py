'''
This is a (very) barebones plaintext plotting utility, for when you can't
import matplotlib. The idea is that you can use this on basically anything
that runs Python and can output plain text, and it's all self contained.

The functions don't do any error checking because it's a barebones command
line plotting utility, so make sure you're feeding them sensible inputs.

Features:
 - Python 2.7 compatible. Probably Python 2.6 compatible but I've
   never tried Python 2.6.
 - No GUI required. Can be used through any environment where you can view
   strings, like the command line, printing on paper, your teletype, or
   whatever.
 - No imports required. Works better if you can import os, but os isn't
   necessary in case your Python build is really weird. Doesn't use
   __future__ in case that somehow doesn't work.
 - You can copy-paste the whole thing into a command line. I find that when
   copy-pasting Python into a command line, it gets mad if I don't add some
   extra newlines here and there, so I added all of those newlines here.
 - Only uses ASCII characters.
 - It just works

Demonstration:
import numpy as np
x = np.linspace(0,1, 200)
y = np.cos(20*x)
plot(y)
plot(x, y, width=60, height=20)
plot(x*1e-9, y, stem=True)
horizontal_bar_chart(x*1e-9, y**2)
horizontal_bar_chart(y**2)

License: This file may be freely used, reproduced, distributed, etc.
         Go wild with it.
'''
# print(x) is valid in Python 2 - it's equivalent to print (x)
try: # In case you somehow don't have the os module
    import os
except:
    pass

_dummy = object()
# modified from https://stackoverflow.com/a/63947444
def _format_float(x, width=8, left=True):
    maxnum = int('9'*(width - 1))
    minnum = -int('9'*(width - 2))
    if x > minnum and x < maxnum and (x == 0 or abs(x) > 1e-3):
        if not left:
            o = ('{:' + str(width-1) + '}').format(x)
        else:
            o = ('{:<' + str(width - 1) + '}').format(x)
        if len(o) > width:
            o = str(round(x, width - 1 - str(x).index('.')))
            if len(o) < width:
                o+=(width-len(o))*'0'
    else:
        for n in range(max(width, 5) - 5, 0, -1):
            fill = '.' + str(n) + 'e'
            o = ('{:' + fill + '}').format(x).replace('+0', '+').replace('-0', '-')
            if len(o) == width:
                break
        else:
            raise ValueError('Number is too large to fit in ' + str(width) + ' characters', x)
    return o

def horizontal_bar_chart(x, y=None, dummy_arg=_dummy, width=None, return_text=False):
    '''
    This function makes a horizontal bar chart using plain text, ie
    >>> horizontal_bar_chart([x**2 for x in range(5)], width=16)
    0| 0
    1|* 1
    2|**** 4
    3|********* 9
    4|**************** 16

    I find that this is useful for some numerical work where you need to
    visually skim through a large array while still being able to see
    exact values. Requires lots of scrolling for large arrays.

    x: A list (or numpy array or whatever) of real numbers.
    y: None, an integer, or a list-like of containing real numbers or strings
      If y is not provided, this plots x where the labels are array indices.
      If y is an integer, this plots x where the labels are array indices,
      starting at y.
      If y is a list-like, this plots y where the labels are the x values.
      If all y values are non-negative or non-positive, this function works
      normally. If there are values on both sides of 0, there may be odd
      behavior.
    width: Optional, the maximum number of * in a line. If not provided,
           tries to auto-detect terminal width, otherwise defaulting to 50.
    return_text: If False, this prints to console and returns None. If True,
                 prints nothing and returns the string that would be printed.
    '''
    if dummy_arg is not _dummy: # Python 2 compatible
        raise TypeError('horizontal_bar_chart takes 1-2 positional arguments but 3 were given.')
    start = 0
    values = x
    labels = None
    if y is not None:
        if not hasattr(y, '__len__'):
            start = y
        else:
            values = y
            labels = x
    if labels is not None:
        index_length = len(str(max(labels, key=lambda x: len(str(x)))))
        index_length = min(index_length, 15)
    else:
        index_length = max(len(str(start)), len(str(len(values)+start)))
    if width is None:
        try:
            width = os.get_terminal_size()[0]-16-15-index_length
        except:
            width = 50
    min_val = min(values)
    max_val = max(values)
    increment = max(abs(max_val), abs(min_val))/(1.0*width)
    text = ''
    for i, v in zip(range(len(values)), values):
        val = int(v/increment)
        if max_val <= 0:
            val = -val
        if labels is not None:
            out = str(labels[i])[:15]
            if index_length == 15 and not isinstance(labels[i], str):
                out = _format_float(labels[i], 15, left=False)
            out = out.rjust(index_length, ' ')
        else:
            out = str(i+start).rjust(index_length, ' ')
        out += '|' + '*'*val + ' ' + _format_float(v, 12)
        text += out + '\n'
    if return_text:
        return text
    print(text[:-1])
    return None

def plot(x, y=None, dummy_arg=_dummy, width=None, height=None, stem=False, return_text=False):
    '''
    This function makes a plot using plain text, ie
    >>> plot(np.cos(np.arange(40)/2), width=40, height=9)
    __________________________________________ 1.0
    |**          **           **          ** |
    |           *  *         *           *  *| 0.556184
    |  *                    *   *            |
    |          *    *            *      *    |
    |   *                  *                 | -0.10954
    |         *      *            *    *     |
    |    *            *   *                  |
    |     *  *           *         *  *      | -0.77526
    |      **          **           **       |
    -+------------+------------+------------+- -0.9972
    0          13.0         26.0         39

    x: A list (or numpy array or whatever) of 'shape' (n,) or (n,2).
    y: Numeric array of shape (n,), optional.
       If x has shape (n,2), then it's treated as a list of (x,y) tuples.
       If y is None, then it's treated as a list of y values, with the array
       indices as their x values.
       If y is present, then x and y are treated as the lists
       [x1, x2, ...], [y1, y2, ...]
    width: None or a positive integer. The number of columns in the plot box.
    height: None or a positive integer. The number of rows in the plot box.
        If width or height are missing, this function tries to auto-size the
        plot box to fit the terminal window, otherwise using default values
        of width=70, height=25.
    stem: If True, this shades the area under the curve.
          Good for histograms, bar charts, and discrete data.
    return_text: If False, this prints to console and returns None. If True,
                 prints nothing and returns the string that would be printed.
    '''
    if dummy_arg is not _dummy: # Python 2 compatible
        raise TypeError('plot takes 1-2 positional arguments but 3 were given.')
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
        x_coord = int(round((x_pos - x_min)/(x_range*1.0)*(width-1)))
        y_coord = int(round((y_pos - y_min)/(y_range*1.0)*(height-1)))
        if stem:
            y_0_coord = int(round(-y_min/(y_range*1.0)*(height-1)))
            between = lambda i: (y_0_coord <= i and i <= y_coord) or (y_coord <= i and i <= y_0_coord)
            for i in filter(between, range(0, height)):
                arr[i][x_coord] = max(arr[i][x_coord], 1)
        arr[y_coord][x_coord] += 1
    # print('_'*(width+2), _format_float(y_max, 8))
    text += '_'*(width+2) + ' ' + _format_float(y_max, 8) + '\n'
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
            string += ' ' + _format_float(y_min + y_range * j/(1.0*len(arr)), 8)
        # print(string)
        text += string + '\n'
    fractions = [0, 0.25, 0.5, 0.75, 1]
    if width <= 10:
        fractions = []
    elif width <= 19:
        fractions = [0, 1]
    elif width <= 30:
        fractions = [0, 0.5, 1]
    elif width <= 40:
        fractions = [0, 1.0/3, 2.0/3, 1]
    out = []
    # spots = []
    # try:
    #     if ascii:
    #         raise Exception
    #     out = list('\u203e'*(width+2) + ' ' + _format_float(y_min, 8))
    #     for fraction in fractions:
    #         i = 1+int(round(fraction*(width-1)))
    #         out[i] = '^'
    #         spots.append((i, fraction))
    # except:
    spots = []
    out = list('-'*(width+2) + ' ' + str(round(y_min, 4)))
    for fraction in fractions:
        i = 1+int(round(fraction*(width-1)))
        out[i] = '+'
        spots.append((i, fraction))
    # print(''.join(out))
    text += ''.join(out) + '\n'
    if len(fractions) > 0:
        out = _format_float(x_min, 7)
        prev = 5
        for i, fraction in spots[1:]:
            prev = len(out)
            out += ' '*(i-3-prev)
            out += _format_float(x_min + fraction*x_range, 7)
        # print(out)
        text += out
    else:
        # text += f'min x:{_format_float(x_min, 7)}\n'
        text += 'min x:' + _format_float(x_min, 7) + '\n'
        text += 'max x:' + _format_float(x_max, 7)
        # text += f'max x:{_format_float(x_max, 7)}'
        # print('min x:', _format_float(x_min, 7))
        # print('max x:', _format_float(x_max, 7))
    if return_text:
        return text + '\n'
    print(text)
    return None

horizontal_bar_chart([x**2 for x in range(5)], width=16)
plot([x**2 for x in range(5)], width=16)