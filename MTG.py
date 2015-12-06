# -*- coding: cp1251 -*-
import re
import collections
import json
import random


class CreateStatistics(object):
    def __init__(self, open_file):
        self.open_file = open_file

    def extract_data(self):
        symbols = re.compile(u'[а-яА-Я-]+|[.,:;?!]+')
        data = open(self.open_file)
        for line in data:
            line = line.decode('utf-8').lower()
            for word in symbols.findall(line):
                yield word

    def form_triples(self):
        words = self.extract_data()
        first, second = '*', '*'
        for third in words:
            yield first, second, third
            if third in '.?!':
                yield second, third, '*'
                yield third, '*', '*'
                first, second = '*', '*'
            else:
                first, second = second, third

    def create_statistics(self):
        triples = self.form_triples()
        words_count = collections.defaultdict(float)
        pairs_count = collections.defaultdict(float)
        triples_count = collections.defaultdict(float)
        for first, second, third in triples:
            words_count[first] += 1
            pairs_count[first, second] += 1
            triples_count[first, second, third] += 1
        word_statistics = dict()
        pairs_statistics = dict()
        for (first, second, third), count in triples_count.iteritems():
            if "%s" % first in word_statistics:
                word_statistics["%s" % first].append((second, pairs_count[first, second]))
            else:
                word_statistics["%s" % first] = [(second, pairs_count[first, second])]

            if "%s, %s" % (first, second) in pairs_statistics:
                pairs_statistics["%s, %s" % (first, second)].append((third, count))
            else:
                pairs_statistics["%s, %s" % (first, second)] = [(third, count)]
        words_output = open("word_statistics.txt", "w")
        pairs_output = open("pairs_statistics.txt", "w")
        json.dump(word_statistics, words_output, encoding='utf-8')
        json.dump(pairs_statistics, pairs_output, encoding='utf-8')
        words_output.close(), pairs_output.close()


class GenerateText(object):
    def __init__(self, text_length):
        self.text_length = text_length
        self.word_statistics = {}
        self.pairs_statistics = {}

    def open_statistics(self):
        f = open('word_statistics.txt', 'r')
        g = open('pairs_statistics.txt', 'r')
        self.word_statistics = json.load(f)
        self.pairs_statistics = json.load(g)

    @staticmethod
    def distribute(cases):
        max_value = len(cases)
        rand_value = random.randint(0, max_value - 1)
        return cases[rand_value][0]

    @staticmethod
    def make_str(first, second):
        first_second_words_string = ''
        first_second_words_string += first + ','
        first_second_words_string += ' ' + second
        return first_second_words_string

    def generate_text(self):
        self.open_statistics()
        text = ''
        first_second_words_string = "*, *"
        current_length = 0
        while current_length < self.text_length:
            sentence = ''
            current_word = self.distribute(self.pairs_statistics[first_second_words_string])
            sentence += current_word
            current_length += 1
            next_word = self.distribute(self.word_statistics[current_word])
            if (next_word == '*') or (next_word in '.?!'):
                if next_word != '*':
                    sentence += next_word
                    first_second_words_string = self.make_str(current_word, next_word)
                continue
            else:
                if next_word in ',:;':
                    sentence += next_word
                else:
                    if current_word == '-':
                        sentence += ' ' + next_word.capitalize()
                        current_length += 1
                    else:
                        sentence += ' ' + next_word
                        current_length += 1
                while 1:
                    current_next_string = self.make_str(current_word, next_word)
                    current_word, next_word = next_word, self.distribute(self.pairs_statistics[current_next_string])
                    if next_word == '*':
                        break
                    else:
                        if (next_word in ',:;') or (next_word in '.?!'):
                            sentence += next_word
                        else:
                            sentence += ' ' + next_word
                            current_length += 1
            text += sentence.capitalize() + ' '
            current_next_string = self.make_str(current_word, next_word)
            current_word, next_word = next_word, self.distribute(self.pairs_statistics[current_next_string])
            first_second_words_string = self.make_str(current_word, next_word)
        return text


def main(text_length):
    statistics = CreateStatistics('sample.txt')
    CreateStatistics.create_statistics(statistics)
    generator = GenerateText(text_length)
    text = GenerateText.generate_text(generator)
    output = open('result.txt', 'w')
    output.write(text.encode('utf-8'))


if __name__ == '__main__':
    main(10)
