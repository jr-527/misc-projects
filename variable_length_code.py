# This file's purpose is to encode English sentences into nonsensical sentences
# of English words that hopefully use less words, and then go back.
# The idea is that nonsensical sentence conveys 18 bits per word, but the
# original sentence conveys less than 18 bits per word because some words are
# more common than others.
# To encode:
# python variable_length_code.py encode o that this too too solid flesh would melt
# To decode:
# python variable_length_code.py decode informatizing cragginess heterokont flattener spetznazes pomeroys circummured
# The printed string is the encoded/decoded sentence
import pandas as pd
import collections
import sys
import time

SIMPLE_WORDS = 2**18

# word_freqs.csv taken from https://github.com/harshnative/words-dataset
freqs = pd.read_csv('word_freqs.csv').drop('index', axis=1).set_index('word')
legal = pd.read_csv('dictionary.txt', names=['word']) # Collins Scrabble Words 2019
legal['word'] = legal['word'].str.lower()
legal = legal.set_index('word')
table = freqs.reset_index()
legal = legal.reset_index()
# We use ; as an EOF symbol with frequency assumed to be 1/25
table.loc[len(table)] = ';', table['frequency'].sum()//24
table = table.sort_values('frequency', ascending=False, ignore_index=True).loc[:SIMPLE_WORDS-2]
temp = table['frequency']
table['frequency'] = table['frequency'].cumsum()
table['lower'] = table['frequency'] - temp
table['lower'] /= table['frequency'].iloc[-1]
table['frequency'] /= table['frequency'].iloc[-1]
# table is sorted in descending order of a word's probability.
# it has columns 'word' (the word, a string),
# 'frequency' (the cumulative probability, including that word)
# 'lower' (the cumulative probabilitiy, not including that word)

def get_index(word):
    l = table[table['word'] == word].index
    if len(l) == 1:
        return l[0]
    return None

def get_lower(word):
    if type(word) == type(''):
        word = get_index(word)
    return table['lower'].iloc[word]

def get_upper(word):
    if type(word) == type(''):
        word = get_index(word)
    return table['frequency'].iloc[word]

def decode_bits(bits):
    lower = 0.0
    upper = 1.0
    run = 0
    lower_index = 0
    upper_index = len(table)-1
    out = []
    for bit in bits:
        if bit == ' ':
            continue
        bit = bool(int(bit))
        run += 1
        if bit:
            lower += 2 ** -run
        else:
            upper -= 2 ** -run
        upper_index = table['lower'].searchsorted(upper)
        lower_index = table['lower'].searchsorted(lower, 'right')
        if upper_index == lower_index:
            out.append(table['word'].iloc[upper_index-1])
            lower = 0.0
            upper = 1.0
            run = 0
            lower_index = 0
            upper_index = len(table)-1
    return out

def encode_word(word):
    word = word.lower()
    try:
        word_lower = get_lower(word)
    except Exception as e:
        print(f'Could not encode "{word}": not in dictionary')
        return None
    word_upper = get_upper(word)
    q = collections.deque()
    # (lower, upper, depth, string)
    q.appendleft((0.0, 1.0, 0, ''))
    while len(q) > 0:
        lower, upper, depth, string = q.pop()
        l_half = (lower, lower + 2**(-(depth+1)), depth+1, string+'0')
        u_half = (lower + 2**(-(depth+1)), upper, depth+1, string+'1')
        if lower >= word_upper or upper <= word_lower:
            continue
        elif lower >= word_lower and upper <= word_upper:
            return string
        elif lower <= word_lower:
            if upper >= word_upper:
                q.appendleft(l_half)
                q.appendleft(u_half)
            elif upper <= word_upper:
                q.appendleft(u_half)
        else: # lower > word_lower,
            q.appendleft(l_half)
            # if upper <= word_upper:
            #     return string
            # elif upper > word_upper:
            #     q.appendleft(l_half)


def encode(sentence):
    sentence = sentence.split()
    sentence.append(';')
    binary = ''
    for word in sentence:
        x = encode_word(word)
        binary += encode_word(word)
    binary = binary + '0'*(18-len(binary) % 18)
    out = []
    for i in range(len(binary)//18):
        eighteen_bits = binary[18*i:18*(i+1)]
        out.append(legal['word'].iloc[int(eighteen_bits, 2)])
    return ' '.join(out)

def decode(sentence):
    sentence = sentence.split()
    binary = ''
    for word in sentence:
        word_index = (legal[legal['word'] == word].index)[0]
        word_binary = bin(word_index)[2:]
        binary += word_binary.rjust(18, '0')
    temp = decode_bits(binary)
    if ';' in temp:
        return ' '.join(temp[:temp.index(';')])
    return ' '.join(decode_bits(binary))

if __name__ == '__main__':
    instruction = sys.argv[1]
    sentence = ' '.join(sys.argv[2:])
    if instruction.lower() == 'encode':
        print(encode(sentence))
    elif instruction.lower() == 'decode':
        print(decode(sentence))
    else:
        print('invalid instruction')