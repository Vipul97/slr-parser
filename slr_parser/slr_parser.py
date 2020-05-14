#!/usr/bin/env python3

from graphviz import Digraph
import argparse


class SLRParser:
    def __init__(self, grammar_file, tokens):
        self.grammar = list(filter(None, grammar_file.read().splitlines()))
        self.start = None
        self.G_prime = {}
        self.G_indexed = [['', '']]
        self.terminals = None
        self.nonterminals = None
        self.symbols = None
        self.first_seen = []
        self.follow_seen = []
        self.C = None
        self.parse_table = None
        self.parse_grammar()
        self.items()
        self.construct_table()
        self.print_info()
        self.LR_parser(tokens)

    def parse_grammar(self):
        terminals = set([])
        nonterminals = set([])

        for g in self.grammar:
            head, _, prods = g.partition(' -> ')
            prods = [prod.split() for prod in ' '.join(prods.split()).split('|')]

            if not self.start:
                self.start = f"{head}'"
                self.G_prime[self.start] = [[head]]

            if head not in self.G_prime:
                self.G_prime[head] = []
                nonterminals.add(head)

            for prod in prods:
                self.G_prime[head].append(prod)
                self.G_indexed.append([head, prod])

                for symbol in prod:
                    if not symbol.isupper() and symbol != '^':
                        terminals.add(symbol)
                    elif symbol.isupper():
                        nonterminals.add(symbol)

        self.terminals = [terminal for terminal in terminals]
        self.nonterminals = [nonterminal for nonterminal in nonterminals]
        self.symbols = [symbol for symbol in terminals | nonterminals]

    def FIRST(self, X):
        if X in self.terminals:  # CASE 1
            return {X}
        else:
            first = set([])

            while True:
                self.first_seen.append(X)
                first_len = len(first)

                for prod in self.G_prime[X]:
                    if prod != ['^']:  # CASE 2
                        for symbol in prod:
                            if symbol == X and '^' in first:
                                continue

                            if symbol not in self.first_seen:
                                symbol_first = self.FIRST(symbol)

                                for sf in symbol_first:
                                    if sf != '^':
                                        first.add(sf)

                                if '^' not in symbol_first:
                                    break

                            else:
                                break

                            first.add('^')

                    else:  # CASE 3
                        first.add('^')

                self.first_seen.remove(X)

                if first_len == len(first):
                    return first

    def FOLLOW(self, A):
        follow = set([])
        self.follow_seen.append(A)

        if A == self.start:  # CASE 1
            follow.add('$')

        for head, prods in self.G_prime.items():
            for prod in prods:
                if A in prod[:-1]:  # CASE 2
                    first = self.FIRST(prod[prod.index(A) + 1])
                    follow |= (first - set('^'))

                    if '^' in first and head not in self.follow_seen:  # CASE 3
                        follow |= self.FOLLOW(head)

                elif A in prod[-1] and head not in self.follow_seen:  # CASE 3
                    follow |= self.FOLLOW(head)

        self.follow_seen.remove(A)

        return follow

    def CLOSURE(self, I):
        J = I

        while True:
            item_len = len(J)

            for head, prods in J.copy().items():
                for prod in prods:
                    if '.' in prod[:-1]:
                        symbol_after_dot = prod[prod.index('.') + 1]

                        if symbol_after_dot in self.nonterminals:
                            for G_prod in self.G_prime[symbol_after_dot]:
                                if G_prod == ['^']:
                                    if symbol_after_dot not in J.keys():
                                        J[symbol_after_dot] = [['.']]
                                    elif ['.'] not in J[symbol_after_dot]:
                                        J[symbol_after_dot].append(['.'])
                                else:
                                    if symbol_after_dot not in J.keys():
                                        J[symbol_after_dot] = [['.'] + G_prod]
                                    elif ['.'] + G_prod not in J[symbol_after_dot]:
                                        J[symbol_after_dot].append(['.'] + G_prod)

            if item_len == len(J):
                return J

    def GOTO(self, I, X):
        goto = {}

        for head, prods in I.items():
            for prod in prods:
                if '.' in prod[:-1]:
                    dot_pos = prod.index('.')

                    if prod[dot_pos + 1] == X:
                        for C_head, C_prods in self.CLOSURE(
                                {head: [prod[:dot_pos] + [X, '.'] + prod[dot_pos + 2:]]}).items():
                            if C_head not in goto.keys():
                                goto[C_head] = C_prods
                            else:
                                for C_prod in C_prods:
                                    if C_prod not in goto[C_head]:
                                        goto[C_head].append(C_prod)

        return goto

    def items(self):
        self.C = [self.CLOSURE({self.start: [['.'] + [self.start[:-1]]]})]

        while True:
            item_len = len(self.C)

            for I in self.C.copy():
                for X in self.symbols:
                    if self.GOTO(I, X) and self.GOTO(I, X) not in self.C:
                        self.C.append(self.GOTO(I, X))

            if item_len == len(self.C):
                return

    def construct_table(self):
        self.parse_table = {r: {c: '' for c in self.terminals + ['$'] + self.nonterminals} for r in
                            range(len(self.C))}

        for i, I in enumerate(self.C):
            for head, prods in I.items():
                for prod in prods:
                    if '.' in prod[:-1]:  # CASE 2 a
                        symbol_after_dot = prod[prod.index('.') + 1]

                        if symbol_after_dot in self.terminals:
                            s = f's{self.C.index(self.GOTO(I, symbol_after_dot))}'

                            if s not in self.parse_table[i][symbol_after_dot]:
                                if 'r' in self.parse_table[i][symbol_after_dot]:
                                    self.parse_table[i][symbol_after_dot] += '/'

                                self.parse_table[i][symbol_after_dot] += s

                    elif prod[-1] == '.' and head != self.start:  # CASE 2 b
                        for j, (G_head, G_prod) in enumerate(self.G_indexed):
                            if G_head == head and (G_prod == prod[:-1] or G_prod == ['^'] and prod == ['.']):
                                for f in self.FOLLOW(head):
                                    if self.parse_table[i][f]:
                                        self.parse_table[i][f] += '/'

                                    self.parse_table[i][f] += f'r{j}'

                                break

                    else:  # CASE 2 c
                        self.parse_table[i]['$'] = 'acc'

            for A in self.nonterminals:  # CASE 3
                j = self.GOTO(I, A)

                if j in self.C:
                    self.parse_table[i][A] = self.C.index(j)

    def print_info(self):
        max_G_prime = len(max(self.G_prime.keys(), key=len))

        print('AUGMENTED GRAMMAR:')

        i = 0
        for head, prods in self.G_prime.items():
            for prod in prods:
                print(f'{i:>{len(str(len(self.G_indexed) - 1))}}: {head:>{max_G_prime}} -> {" ".join(prod)}')

                i += 1

        print(f'\n{"TERMINALS:":>13} {", ".join(self.terminals)}')
        print(f'{"NONTERMINALS:":>13} {", ".join(self.nonterminals)}')
        print(f'{"SYMBOLS:":>13} {", ".join(self.symbols)}')

        print('\nFIRST:')
        for head in self.G_prime.keys():
            print(f'{head:>{max_G_prime}} = {{ {", ".join(self.FIRST(head))} }}')

        print('\nFOLLOW:')
        for head in self.G_prime.keys():
            print(f'{head:>{max_G_prime}} = {{ {", ".join(self.FOLLOW(head))} }}')

        width = max(len(c) for c in ['ACTION'] + self.symbols) + 2
        for r in range(len(self.C)):
            max_len = max(len(str(c)) for c in self.parse_table[r].values())

            if width < max_len + 2:
                width = max_len + 2

        print('\nPARSING TABLE:')
        print(
            f'+{"-" * width}+{"-" * ((width + 1) * len(self.terminals + ["$"]) - 1)}+{"-" * ((width + 1) * len(self.nonterminals) - 1)}+')
        print(
            f'|{"":{width}}|{"ACTION":^{(width + 1) * len(self.terminals + ["$"]) - 1}}|{"GOTO":^{(width + 1) * len(self.nonterminals) - 1}}|')
        print(f'|{"STATE":^{width}}+{("-" * width + "+") * len(self.symbols + ["$"])}')
        print(f'|{"":^{width}}|', end=' ')

        for symbol in self.terminals + ['$'] + self.nonterminals:
            print(f'{symbol:^{width - 1}}|', end=' ')

        print(f'\n+{("-" * width + "+") * (len(self.symbols + ["$"]) + 1)}')

        for r in range(len(self.C)):
            print(f'|{r:^{width}}|', end=' ')

            for c in self.terminals + ['$'] + self.nonterminals:
                print(f'{self.parse_table[r][c]:^{width - 1}}|', end=' ')

            print()

        print(f'+{("-" * width + "+") * (len(self.symbols + ["$"]) + 1)}')
        print()

    def generate_automaton(self):
        automaton = Digraph('automaton', node_attr={'shape': 'record'})
        max_G_prime = len(max(self.G_prime.keys(), key=len))

        for i, I in enumerate(self.C):
            I_str = f'<<I>I</I><SUB>{i}</SUB><BR/>'

            for (head, prods) in I.items():
                for prod in prods:
                    I_str += f'<I>{head:>{max_G_prime}}</I> &#8594;'

                    for symbol in prod:
                        if symbol in self.nonterminals:
                            I_str += f' <I>{symbol}</I>'
                        elif symbol in self.terminals:
                            I_str += f' <B>{symbol}</B>'
                        else:
                            I_str += f' {symbol}'

                    I_str += '<BR ALIGN="LEFT"/>'

            automaton.node(f'I{i}', f'{I_str}>')

        for r in range(len(self.C)):
            for c in self.terminals + ['$'] + self.nonterminals:
                if isinstance(self.parse_table[r][c], int):
                    automaton.edge(f'I{r}', f'I{self.parse_table[r][c]}', label=f'<<I>{c}</I>>')

                elif 's' in self.parse_table[r][c]:
                    i = self.parse_table[r][c][self.parse_table[r][c].index('s') + 1:]

                    if '/' in i:
                        i = i[:i.index('/')]

                    automaton.edge(f'I{r}', f'I{i}', label=f'<<B>{c}</B>>' if c in self.terminals else c)

                elif self.parse_table[r][c] == 'acc':
                    automaton.node('acc', '<<B>accept</B>>', shape='none')
                    automaton.edge(f'I{r}', 'acc', label='$')

        automaton.view()

    def LR_parser(self, w):
        def print_line():
            print(f'{"".join(["+" + ("-" * (max_len + 2)) for max_len in max_lens.values()])}+')

        buffer = f'{w} $'.split()
        pointer = 0
        a = buffer[pointer]
        stack = ['0']
        symbols = ['']
        histories = {'step': [''], 'stack': ['STACK'] + stack, 'symbols': ['SYMBOLS'] + symbols, 'input': ['INPUT'],
                     'action': ['ACTION']}

        step = 0
        while True:
            s = int(stack[-1])
            step += 1
            histories['step'].append(f'({step})')
            histories['input'].append(' '.join(buffer[pointer:]))

            if a not in self.parse_table[s].keys():
                histories['action'].append(f'ERROR: unrecognized symbol {a}')

                break

            elif not self.parse_table[s][a]:
                histories['action'].append('ERROR: input cannot be parsed by given grammar')

                break

            elif '/' in self.parse_table[s][a]:
                if self.parse_table[s][a].count('r') > 1:
                    histories['action'].append(f'ERROR: reduce-reduce conflict at state {s}, symbol {a}')
                else:
                    histories['action'].append(f'ERROR: shift-reduce conflict at state {s}, symbol {a}')

                break

            elif self.parse_table[s][a].startswith('s'):
                histories['action'].append('shift')
                stack.append(self.parse_table[s][a][1:])
                symbols.append(a)
                histories['stack'].append(' '.join(stack))
                histories['symbols'].append(' '.join(symbols))
                pointer += 1
                a = buffer[pointer]

            elif self.parse_table[s][a].startswith('r'):
                head, prod = self.G_indexed[int(self.parse_table[s][a][1:])]
                histories['action'].append(f'reduce by {head} -> {" ".join(prod)}')

                if prod != ['^']:
                    stack = stack[:-len(prod)]
                    symbols = symbols[:-len(prod)]

                stack.append(str(self.parse_table[int(stack[-1])][head]))
                symbols.append(head)
                histories['stack'].append(' '.join(stack))
                histories['symbols'].append(' '.join(symbols))

            elif self.parse_table[s][a] == 'acc':
                histories['action'].append('accept')

                break

        max_lens = {key: max(len(value) for value in histories[key]) for key in histories.keys()}
        justs = {'step': '>', 'stack': '', 'symbols': '', 'input': '>', 'action': ''}

        print_line()
        print(''.join(
            [f'| {history[0]:^{max_len}} ' for history, max_len in zip(histories.values(), max_lens.values())]) + '|')
        print_line()
        for i, step in enumerate(histories['step'][:-1], 1):
            print(''.join([f'| {history[i]:{just}{max_len}} ' for history, just, max_len in
                           zip(histories.values(), justs.values(), max_lens.values())]) + '|')

        print_line()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar_file', type=argparse.FileType('r'), help='text file to be used as grammar')
    parser.add_argument('-g', action='store_true', help='generate automaton')
    parser.add_argument('tokens', help='tokens to be parsed - all tokens are separated with spaces')
    args = parser.parse_args()

    slr_parser = SLRParser(args.grammar_file, args.tokens)

    if args.g:
        slr_parser.generate_automaton()
