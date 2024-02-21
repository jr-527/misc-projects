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

License:
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>
'''
# print(x) is valid in Python 2 - it's equivalent to print (x)
try: # In case you somehow don't have the os module
    import os
except:
    pass

_dummy = object()
_NEG_OF = 'negative overflow'
_OF = 'overflow'
_OK = 'okay'

def _round_to_1(x):
    if x < -0.5: return ('0', _NEG_OF)
    if x <= 0.5: return ('0', _OK)
    if x >= 9.5: return ('9', _OF)
    return (str(int(round(x))), _OK)

def _round_to_2(x, leading_zero=False):
    if x <= -9.5: return ('-9', _NEG_OF)
    if x < -0.5: return (str(int(round(x))), _OK)
    if x < 0: return ('-0', _OK)
    if not leading_zero and x < 1:
        if 0.95 <= x: return ('1', _OK)
        if 0.05 >= x: return ('0', _OK)
        return (str(int(round(10*x))/10.0)[1:3], _OK)
    if x >= 99.5: return ('99', _OF)
    return (str(int(round(x))), _OK)

def _round_to_3(x, leading_zero=False):
    if x < 0:
        out = _round_to_2(-x, leading_zero)
        if out[1] == _OF: return ('-99', _NEG_OF)
        return ('-' + out[0], _OK)
    if not leading_zero and x < 1:
        if 0.995 <= x: return ('1', _OK)
        if 0.005 >= x: return ('0', _OK)
        return (str(round(x,2))[1:4], _OK)
    if x < 1:
        return ('0' + _round_to_2(x, False)[0], _OK)
    if x < 9.95: return (str(round(x,1)), _OK)
    if x < 999.5: return (str(int(round(x))), _OK)
    if 999.5 <= x and x < 9.5e9:
        out = format(x, '1e')
        first_digit = int(round(float(out[:3])))
        last_digit = int(out[-1])
        if first_digit == 10:
            last_digit += 1
            first_digit = 1
        return (str(first_digit) + 'e' + str(last_digit), _OK)
    return ('9e9', _OF)

def _round_to_n(x, n, leading_zero=False):
    if n >= 25:
        return (str(x), _OK)
    if n == 3:
        return _round_to_3(x, leading_zero)
    if x < 0:
        out, status = _round_to_n(-x, n-1, leading_zero)
        status = status if status == _OK else _NEG_OF
        return ('-' + out, status)
    if x <= float('0.5e-' + '9'*(n-3)):
        return ('0', _OK)
    if x < float('1.5e-' + '9'*(n-3)):
        return ('1e-' + '9'*(n-3), _OK)
    if x < .001:
        mantissa, exponent = format(x, '.18e').split('e')
        exponent = 'e' + str(int(exponent))
        mantissa = str(round(float(mantissa), max(0,n-len(exponent)-2)))
        mantissa = mantissa[:n-len(exponent)]
        if mantissa[-1] == '.':
            mantissa = mantissa[:-1]
        return (mantissa + exponent, _OK)
    threshold_str = '9'*n + '5'
    for i in range(n+1):
        threshold = float(threshold_str[:i] + '.' + threshold_str[i:])
        if x < threshold:
            out = ''
            if i == 0:
                if not leading_zero:
                    out = str(round(x,n-i-1))[1:]
                else:
                    out = str(round(x,n-i-2))
            if i == n:
                out = str(int(round(x)))[:n]
            else:
                out = str(round(x,n-i-1))[:n]
                if out[-1] == '.':
                    #out = str(round(x,n-i-1))[:n-1]
                    out = out[:-1]
            out = out[:n]
            if out[-1] == '.':
                out = out[:-1]
            return (out, _OK)
    if x < float('9.5e' + '9'*(n-2)):
        mantissa, exponent = format(x, '.17e').split('e')
        exponent = 'e' + str(int(exponent))
        mantissa = str(round(float(mantissa), max(0,n-len(exponent)-2)))
        mantissa = mantissa[:n-len(exponent)]
        if mantissa[-1] == '.':
            mantissa = mantissa[:-1]
        return (mantissa + exponent, _OK)
    return (float('9e' + '9'*(n-2)), _OF)

def _round_to_width(x, width=8, align='left', overflow='saturate', leading_zero=False, underflow='zero'):
    '''
    Returns a string of length width representing a number as close to x as
    possible (prefers '1.2e9' over '123e7' because it's easier to understand)
    x: The number to round
    width: The string's width
    align: If 'left', align the string on the left, ie '3.14   '.
           Otherwise align the string on the right, ie '   3.14'
    overflow: Either 'saturate', 'exception', 'inf', 'nan', or 'word'
             Describes what to do if the number is too big to represent in the
             desired number of characters.
        'saturate': Give the closest possible number, so
                    round_to_width(1e20, 3) gives '9e9'
        'exception': Raise an exception.
        'inf': Return 'inf' or '-inf' (replaced by 'exception' if width < 4)
        'nan': Return 'NaN' or '-NaN' (replaced by 'exception' width < 4)
        'word': Returns text that says something along the lines of 'overflow'
                that won't parse as a number.
    underflow: Either 'zero', 'saturate', 'exception', or 'word'
               Describes what to do if the number is too close to zero to
               represent in the desired number of characters.
        'zero': Return '0'
        'saturate': Give the smallest possible number of the correct sign, so
                    round_to_width(1e-99, 4) gives '1e-9'.
                    Replaced by 'exception' if width < 2.
        'exception': Raise an exception.
        'word': Returns text that says something along the lines of 'eps'
                that won't parse as (part of) a number (so no 'e').
                Replaced by 'exception' if width < 3.
    leading_zero: If True, 0.5 will be formatted as '0.5', otherwise '.5'
    '''
    width = int(width)
    if width == 0:
        # returning '' is a silent failure, which we don't want.
        raise ValueError('width must be > 0')
    overflow = overflow.lower()
    underflow = underflow.lower()
    if underflow in ('raise', 'except'):
        underflow = 'exception'
    if (underflow == 'word' and width < 3) or (underflow == 'word' and width < 2):
        underflow = 'exception'
    if overflow in ('raise', 'except') or (width < 4 and overflow in ('inf', 'nan')):
        overflow = 'exception'
    if overflow not in ('exception', 'saturate', 'inf', 'nan', 'word'):
        raise ValueError("overflow must be one of 'exception', 'saturate', 'inf', 'nan', 'word'")
    if underflow not in ('zero', 'saturate', 'exception', 'word'):
        raise ValueError("underflow must be one of 'zero', 'saturate', 'exception', 'word'")
    out, status = '', ''
    if width == 1:
        out, status = _round_to_1(x)
    elif width == 2:
        out, status = _round_to_2(x, leading_zero)
    else:
        out, status = _round_to_n(x, width, leading_zero)
    if out == '0' and x != 0: # this branch always has status == _OK
        # 'zero' -> do nothing
        if underflow == 'exception':
            raise ValueError('Underflow')
        if underflow == 'saturate':
            # the smallest floating point number is around 1e-308,
            # so we don't have to worry about 1e-999.
            temp_arr = [('1', '1'), ('.1', '1'), ('.01', '0.1'),
                        ('1e-9', '1e-9'), ('1e-99', '1e-99')]
            if x > 0: out = temp_arr[width-1][leading_zero]
            else: out = '-' + temp_arr[width-2][leading_zero]
        elif underflow == 'word':
            out = 'eps'
            if x < 0:
                out = '-ep' if width == 3 else '-eps'
    fmt = '<' if align=='left' else '>'
    out = format(out, fmt+str(int(width)))
    if status != _OK:
        # saturate -> do nothing
        if overflow == 'exception':
            raise ValueError(status)
        if overflow == 'inf':
            out = 'inf' if status == _OF else '-inf'
        elif overflow == 'nan':
            status = 'NaN' if status == _OF else '-NaN'
        elif overflow == 'word':
            if width < 5:
                state = 1 if status == _OF else 0
                return [('N', 'P'), ('-N', 'OF'), ('-OF', 'OVF'), ('-OVF', 'OVER')][width-1][state]
            out = 'OVERFLOW' if status == _OF else '-OVERFLOW'
            out = out[:min(len(out), width)]
    return out

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
                out = _round_to_width(labels[i], 15, align='right')
            out = out.rjust(index_length, ' ')
        else:
            out = str(i+start).rjust(index_length, ' ')
        out += '|' + '*'*val + ' ' + _round_to_width(v, 12)
        text += out + '\n'
    if return_text:
        return text
    print(text[:-1])
    return None

def plot(x, y=None, dummy_arg=_dummy, width=None, height=None, stem=False, return_text=False, xlim=None, ylim=None):
    '''
    This function makes a plot using plain text, ie
    >>> plot([math.cos(i*.5) for i in range(41)], width=40, height=9)
    __________________________________________ 1.0
    |**          **          **          **  |
    |           *  *        *           *  * | 0.556184
    |  *                   *   *            *|
    |          *    *           *      *     |
    |   *                 *                  | -0.10954
    |         *      *           *    *      |
    |    *            *  *                   |
    |     *  *           *        *  *       | -0.77526
    |      **          **          **        |
    -+------------+------------+------------+- -0.9972
    0          13.3333      26.6667      40

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
        of width=69, height=22 to fit in an 80x24 terminal.
    stem: If True, this shades the area under the curve.
          Good for histograms, bar charts, and discrete data.
    return_text: If False, this prints to console and returns None. If True,
                 prints nothing and returns the string that would be printed.
    xlim: None or a tuple (or equivalent) in the form (x_min, x_max) that gives
          upper and lower bounds for the x-axis. Any values that are None will
          be auto-detected from the data.
    ylim: Same as xlim, but for the y-axis.
    '''
    if dummy_arg is not _dummy: # Python 2 compatible
        raise TypeError('plot takes 1-2 positional arguments but 3 were given.')
    text = ''
    if height is None:
        try:
            height = os.get_terminal_size()[1]-4
        except:
            height = 22
    if width is None:
        try:
            width = os.get_terminal_size()[0]-12
        except:
            width = 69
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
    if xlim is not None:
        if xlim[0] is not None:
            x_min = xlim[0]
        if xlim[1] is not None:
            x_max = xlim[1]
    x_range = x_max - x_min
    y_min, y_max = min(y), max(y)
    if ylim is not None:
        if ylim[0] is not None:
            y_min = ylim[0]
        if ylim[1] is not None:
            y_max = ylim[1]
    y_range = y_max - y_min
    # we want a list in the form list[y][x]
    arr = [[0]*width for _ in range(height)]
    print(x_min, x_max)
    print(y_min, y_max)
    for x_pos, y_pos in zip(x, y):
        # in older Python versions, round always returns a floating point value
        # so we cast to int
        if not ((x_min <= x_pos and x_pos <= x_max) and (y_min <= y_pos and y_pos <= y_max)):
            continue
        x_coord = int(round((x_pos - x_min)/(x_range*1.0)*(width-1)))
        y_coord = int(round((y_pos - y_min)/(y_range*1.0)*(height-1)))
        if stem:
            y_0_coord = int(round(-y_min/(y_range*1.0)*(height-1)))
            between = lambda i: (y_0_coord <= i and i <= y_coord) or (y_coord <= i and i <= y_0_coord)
            for i in filter(between, range(0, height)):
                arr[i][x_coord] = max(arr[i][x_coord], 1)
        arr[y_coord][x_coord] += 1
    # print('_'*(width+2), _round_to_width(y_max, 8))
    text += '_'*(width+2) + ' ' + _round_to_width(y_max, 8) + '\n'
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
            string += ' ' + _round_to_width(y_min + y_range * j/(1.0*len(arr)), 8)
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
    #     out = list('\u203e'*(width+2) + ' ' + _round_to_width(y_min, 8))
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
        out = _round_to_width(x_min, 7)
        prev = 5
        for i, fraction in spots[1:]:
            prev = len(out)
            out += ' '*(i-3-prev)
            out += _round_to_width(x_min + fraction*x_range, 7)
        # print(out)
        text += out
    else:
        # text += f'min x:{_round_to_width(x_min, 7)}\n'
        text += 'min x:' + _round_to_width(x_min, 7) + '\n'
        text += 'max x:' + _round_to_width(x_max, 7)
        # text += f'max x:{_round_to_width(x_max, 7)}'
        # print('min x:', _round_to_width(x_min, 7))
        # print('max x:', _round_to_width(x_max, 7))
    if return_text:
        return text + '\n'
    print(text)
    return None
