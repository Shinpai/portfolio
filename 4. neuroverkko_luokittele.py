#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, timeit, json, datetime, unittest
import numpy as np
from nltk.stem.snowball import FinnishStemmer
stemmer = FinnishStemmer()


training_data = []
with open('nn_training_data.dat', 'r') as f:
    for line in f:
        training_data.append(eval(line))


class TestNN(unittest.TestCase):
    def test_n(self):
        with open('nn_test_data.dat', 'r') as input:
            amm_ilm = [eval(line) for line in input]
        for i in amm_ilm:
            ammatti = i[0]
            teksti = luokittele(i[1])
            with self.subTest(i=i):
                try:
                    print('Got:',teksti[0][0],': expected', ammatti)
                    self.assertEqual(teksti[0][0], ammatti)
                except IndexError:
                    print(teksti)


regex = re.compile('<.*?>')


def clear():
    name = os.name
    if name == 'posix':
        os.system('clear')
    elif name == 'nt' or name == 'dos':
        os.system('cls')
    else:
        print("\n" * 30)


def nonlin(x,deriv=False):
    if deriv is True:
        return x*(1-x)
    return 1/(1+np.exp(-x))


def train(X, Y, hidden_neurons=10, alpha=1, epochs=50000, dropout=False, dropout_percent=0.5):
    # based on https://machinelearnings.co/text-classification-using-neural-networks-f5cd7b8765c6
    print("Training with %s neurons, alpha:%s, dropout:%s %s" % (hidden_neurons, str(alpha), dropout, dropout_percent if dropout else ''))
    print("Input matrix: %sx%s Output matrix: %sx%s" % (len(X), len(X[0]), 1, len(classes)))
    # seed random numbers to make calculation (deterministic)
    np.random.seed(1)
    last_mean_error = 1

    # randomly initialize weights with mean 0
    syn0 = 2*np.random.random((len(X[0]), hidden_neurons)) - 1
    syn1 = 2*np.random.random((hidden_neurons, len(classes))) - 1

    prev_syn0_weight_update = np.zeros_like(syn0)
    prev_syn1_weight_update = np.zeros_like(syn1)

    syn0_direction_count = np.zeros_like(syn0)
    syn1_direction_count = np.zeros_like(syn1)

    for j in iter(range(epochs + 1)):
        layer0 = X
        layer1 = nonlin(np.dot(layer0, syn0))
        if dropout:
            layer1 *= np.random.binomial([np.ones((len(X), hidden_neurons))], 1 - dropout_percent)[0] * (1.0 / (1 - dropout_percent))
        layer2 = nonlin(np.dot(layer1, syn1))
        layer2_error = Y - layer2
        if (j % 10000) == 0 and j > 5000:
            if np.mean(np.abs(layer2_error)) < last_mean_error:
                print('Error after',str(j),'iterations:',str(np.mean(np.abs(layer2_error))))
                last_mean_error = np.mean(np.abs(layer2_error))
            else:
                print('break:', np.mean(np.abs(layer2_error)), ">", last_mean_error)
                break
        layer2_delta = layer2_error * nonlin(layer2,deriv=True)
        layer1_error = layer2_delta.dot(syn1.T)
        layer1_delta = layer1_error * nonlin(layer1, deriv=True)

        syn1_weight_update = (layer1.T.dot(layer2_delta))
        syn0_weight_update = (layer0.T.dot(layer1_delta))

        if j > 0:
            syn0_direction_count += np.abs(((syn0_weight_update > 0) + 0) - ((prev_syn0_weight_update > 0) + 0))
            syn1_direction_count += np.abs(((syn1_weight_update > 0) + 0) - ((prev_syn1_weight_update > 0) + 0))

        syn1 += alpha * syn1_weight_update
        syn0 += alpha * syn0_weight_update

        prev_syn0_weight_update = syn0_weight_update
        prev_syn1_weight_update = syn1_weight_update

    # tallennetaan synapse
    now = datetime.datetime.now()
    synapse = {'syn0': syn0.tolist(),'syn1': syn1.tolist(),
               'datetime': now.strftime('%Y-%m-%d %H:%M'),
               'words': words,
               'classes': classes}
    synapse_file = 'synapses.json'

    with open(synapse_file, 'w') as f:
        json.dump(synapse, f, indent=4, sort_keys=True)
    print('Saved synapses to:', synapse_file)


def harjoita_neuronit():
    corpus = []
    global classes
    global words
    words = []
    classes = []
    ignore_words = ['', '&nbsp']
    regex = re.compile('<.*?>')
    for pattern in training_data:
        classes.append(pattern['ammatti'])
        teksti = pattern['teksti']
        ilman_tageja = re.sub(regex, '', teksti)
        sanat = [w.casefold().strip(',.<>!"?_:\n\t\r\\()-=@') for w in ilman_tageja.split()]
        words.extend(sanat)
        corpus.append((sanat, pattern['ammatti']))

    words = [stemmer.stem(w.casefold()) for w in words if w not in ignore_words]
    words = list(set(words))
    classes = list(set(classes))

    print(len(corpus), 'tekstiä harjoitusdatassa')
    print(len(classes), 'luokkaa')
    print(len(words), 'uniikkia sanaa')

    training = []
    output = []
    output_empty = [0] * len(classes)

    for doc in corpus:
        word_bag = []
        pattern_words = doc[0]
        pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
        for w in words:
            word_bag.append(1) if w in pattern_words else word_bag.append(0)

        training.append(word_bag)
        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1
        output.append(output_row)

    X = np.array(training)
    Y = np.array(output)
    start = timeit.default_timer()
    train(X, Y, hidden_neurons=6, alpha=0.2, epochs=100000, dropout=False, dropout_percent=0.1)
    stop = timeit.default_timer()
    print('Prosessointiaika:',(stop - start),'sekuntia')


def putsaa_ja_tokenize(teksti):
    ilman_tageja = re.sub(regex, '', teksti)
    pilkottu = [w.casefold().strip(',.<>!"?_:\n\t\r\\()-=@') for w in ilman_tageja.split()]
    stemmattu = [stemmer.stem(w.casefold()) for w in pilkottu]
    return stemmattu


def bow(raw_text, words, show_details=False):
    text_words = putsaa_ja_tokenize(raw_text)
    bag = [0] * len(words)
    for s in text_words:
        for ind, w in enumerate(words):
            if w == s:
                bag[ind] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def think(raw_text, show_details=False):
    x = bow(raw_text.lower(), words, show_details)
    if show_details:
        print('raw:',raw_text,'\n bow:', x)
    layer0 = x
    layer1 = nonlin(np.dot(layer0, synapse_0))
    layer2 = nonlin(np.dot(layer1, synapse_1))
    return layer2


# probability threshold
ERROR_THRESHOLD = 0.2


def lataa_malli():
    global words
    global classes
    global synapse_0
    global synapse_1
    # load our calculated synapse values
    synapse_file = 'synapses.json'
    with open(synapse_file) as data_file:
        synapse = json.load(data_file)
        synapse_0 = np.asarray(synapse['syn0'])
        synapse_1 = np.asarray(synapse['syn1'])
        words = synapse['words']
        classes = synapse['classes']


def luokittele(raw, show_details=False):
    results = think(raw, show_details)
    results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_results = [[classes[r[0]], r[1]] for r in results]
    #print("\nluokitus: %s" % (return_results))
    return return_results


def ask(question):
    answer = input(question + " [y/n]?")
    return answer in ['y', 'Y', 'Yes', 'YES', 'yes']


def testaa_kaikilla(limit=-1):
    with open('output.dat', 'w') as output, open('tyopaikat.dat', 'r') as input:
        co = 0
        for line in input:
            line = eval(line)
            tulos = luokittele(line[3])
            try:
                print(line[0], ':\n--', tulos[0], '\n', file=output)
            except IndexError:
                pass
            co += 1
            if co == limit:
                break


def main():
    if ask('Harjoita neuronit uudelle training datalle'):
        harjoita_neuronit()
    lataa_malli()
    #unittest.main()
    testaa_kaikilla(limit=50)

##############################################################################


if __name__ == "__main__":
    main()
