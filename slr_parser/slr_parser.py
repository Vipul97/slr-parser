#!/usr/bin/env python3

from graphviz import Digraph
from slr_parser.grammar import Grammar
import argparse


def first_follow(G):
    def union(set_1, set_2):
        original_size = len(set_1)
        set_1.update(set_2)
        return original_size != len(set_1)

    first = {symbol: set() for symbol in G.symbols}
    first.update((terminal, {terminal}) for terminal in G.terminals)
    follow = {symbol: set() for symbol in G.nonterminals}
    follow[G.start].add('$')

    while True:
        updated = False

        for head, bodies in G.grammar.items():
            for body in bodies:
                for symbol in body:
                    if symbol != '^':
                        updated |= union(first[head], first[symbol] - {'^'})
                        if '^' not in first[symbol]:
                            break
                    else:
                        updated |= union(first[head], {'^'})
                else:
                    updated |= union(first[head], {'^'})

                aux = follow[head]
                for symbol in reversed(body):
                    if symbol == '^':
                        continue
                    if symbol in follow:
                        updated |= union(follow[symbol], aux - {'^'})
                    if '^' in first[symbol]:
                        aux = aux | first[symbol]
                    else:
                        aux = first[symbol]

        if not updated:
            return first, follow


class SLRParser:
    def __init__(self, G):
        self.G_prime = Grammar(f"{G.start}' -> {G.start}\n{G.grammar_str}")
        self.max_nonterminal_len = max(len(nonterminal) for nonterminal in self.G_prime.nonterminals)
        self.G_indexed = [
            {'head': head, 'body': body}
            for head, bodies in self.G_prime.grammar.items()
            for body in bodies
        ]
        self.first, self.follow = first_follow(self.G_prime)
        self.C = self.items(self.G_prime)
        self.action = list(self.G_prime.terminals) + ['$']
        self.goto = self.G_prime.nonterminals - {self.G_prime.start}
        self.parsing_table_symbols = self.action + list(self.goto)
        self.parsing_table = self.construct_parsing_table()

    def CLOSURE(self, I):
        J = I.copy()

        while True:
            original_size = len(J)

            for i, dot_pos in J:
                body = self.G_indexed[i]['body']
                if dot_pos < len(body):
                    symbol_after_dot = body[dot_pos]
                    if symbol_after_dot in self.G_prime.nonterminals:
                        for body in self.G_prime.grammar[symbol_after_dot]:
                            new_item = (self.G_indexed.index({'head': symbol_after_dot, 'body': body}), 0)
                            if new_item not in J:
                                J.append(new_item)

            if len(J) == original_size:
                return J

    def GOTO(self, I, X):
        goto = []

        for i, dot_pos in I:
            body = self.G_indexed[i]['body']
            if dot_pos < len(body) and body[dot_pos] == X:
                for new_item in self.CLOSURE([(i, dot_pos + 1)]):
                    if new_item not in goto:
                        goto.append(new_item)

        return goto

    def items(self, G_prime):
        C = [self.CLOSURE([(0, 0)])]

        while True:
            original_size = len(C)

            for I in C:
                for X in G_prime.symbols:
                    goto = self.GOTO(I, X)
                    if goto and goto not in C:
                        C.append(goto)

            if len(C) == original_size:
                return C

    def construct_parsing_table(self):
        parsing_table = {r: {c: '' for c in self.parsing_table_symbols} for r in range(len(self.C))}

        for i, I in enumerate(self.C):
            for j, dot_pos in I:
                head = self.G_indexed[j]['head']
                body = self.G_indexed[j]['body']
                body = [] if body == ['^'] else body

                if dot_pos < len(body):  # CASE 2a: Symbol after dot
                    symbol_after_dot = body[dot_pos]
                    if symbol_after_dot in self.G_prime.terminals:
                        j = self.GOTO(I, symbol_after_dot)
                        s = f's{self.C.index(j)}'

                        if s not in parsing_table[i][symbol_after_dot]:
                            if 'r' in parsing_table[i][symbol_after_dot]:
                                parsing_table[i][symbol_after_dot] += '/'
                            parsing_table[i][symbol_after_dot] += s

                elif dot_pos == len(body):  # CASE 2b: Dot is at the end
                    if head != self.G_prime.start:
                        for a in self.follow[head]:
                            if parsing_table[i][a]:
                                parsing_table[i][a] += '/'
                            parsing_table[i][a] += f'r{j}'
                    else:  # CASE 2c: If it's the start production
                        parsing_table[i]['$'] = 'acc'

            # CASE 3: Handle the transitions for non-terminals
            for A in self.G_prime.nonterminals:
                j = self.GOTO(I, A)
                if j in self.C:
                    parsing_table[i][A] = str(self.C.index(j))

        return parsing_table

    def print_info(self):
        def fprint(text, variable):
            print(f'{text:>12}: {", ".join(variable)}')

        def print_line():
            print(f'+{("-" * width + "+") * ((len(self.parsing_table_symbols)) + 1)}')

        def symbols_width(symbols):
            return (width + 1) * len(symbols) - 1

        print('AUGMENTED GRAMMAR:')
        for i, production in enumerate(self.G_indexed):
            print(
                f'{i:>{len(str(len(self.G_indexed) - 1))}}: {production['head']:>{self.max_nonterminal_len}} -> {" ".join(production['body'])}')

        print()
        fprint('TERMINALS', self.G_prime.terminals)
        fprint('NONTERMINALS', self.G_prime.nonterminals)
        fprint('SYMBOLS', self.G_prime.symbols)

        print('\nFIRST:')
        for head in self.G_prime.grammar:
            print(f'{head:>{self.max_nonterminal_len}} = {{ {", ".join(self.first[head])} }}')

        print('\nFOLLOW:')
        for head in self.G_prime.grammar:
            print(f'{head:>{self.max_nonterminal_len}} = {{ {", ".join(self.follow[head])} }}')

        width = max(len(c) for c in {'ACTION'} | self.G_prime.symbols) + 2
        for r in range(len(self.C)):
            max_len = max(len(str(c)) for c in self.parsing_table[r].values())
            width = max(width, max_len + 2)

        print('\nPARSING TABLE:')
        print_line()
        print(f'|{"":{width}}|{"ACTION":^{symbols_width(self.action)}}|{"GOTO":^{symbols_width(self.goto)}}|')
        print(f'|{"STATE":^{width}}+{("-" * width + "+") * len(self.parsing_table_symbols)}')
        print(f'|{"":^{width}}|', end=' ')

        for symbol in self.parsing_table_symbols:
            print(f'{symbol:^{width - 1}}|', end=' ')

        print()
        print_line()

        for r in range(len(self.C)):
            print(f'|{r:^{width}}|', end=' ')
            for c in self.parsing_table_symbols:
                print(f'{self.parsing_table[r][c]:^{width - 1}}|', end=' ')
            print()

        print_line()
        print()

    def generate_automaton(self):
        automaton = Digraph('automaton', node_attr={'shape': 'record'})

        def format_symbol(symbol):
            if symbol in self.G_prime.nonterminals:
                return f'<I>{symbol}</I>'
            elif symbol in self.G_prime.terminals:
                return f'<B>{symbol}</B>'
            return symbol

        for i, I in enumerate(self.C):
            I_html_parts = [f'<<I>I</I><SUB>{i}</SUB><BR/>']

            for j, dot_pos in I:
                head = self.G_indexed[j]['head']
                body = self.G_indexed[j]['body'].copy()
                body = [] if body == ['^'] else body
                body.insert(dot_pos, '.')
                I_html_parts.append(f'<I>{head:>{self.max_nonterminal_len}}</I> &#8594; ')
                I_html_parts.append(' '.join(format_symbol(symbol) for symbol in body))
                I_html_parts.append('<BR ALIGN="LEFT"/>')

            I_html = ''.join(I_html_parts)
            automaton.node(f'I{i}', f'{I_html}>')

        for r in range(len(self.C)):
            for c in self.parsing_table_symbols:
                cell = self.parsing_table[r][c]

                if 's' in cell:
                    i = cell.split('s')[1].split('/')[0]
                    label = f'<<B>{c}</B>>' if c in self.G_prime.terminals else c
                    automaton.edge(f'I{r}', f'I{i}', label=label)

                elif cell == 'acc':
                    automaton.node('acc', '<<B>accept</B>>', shape='none')
                    automaton.edge(f'I{r}', 'acc', label='$')

                elif cell.isnumeric():
                    automaton.edge(f'I{r}', f'I{cell}', label=f'<<I>{c}</I>>')

        automaton.view()

    def LR_parser(self, w):
        buffer = f'{w} $'.split()
        pointer = 0
        a = buffer[pointer]
        stack = ['0']
        symbols = ['']
        results = {
            'step': [''],
            'stack': ['STACK'] + stack,
            'symbols': ['SYMBOLS'] + symbols,
            'input': ['INPUT'],
            'action': ['ACTION']
        }

        step = 0
        while True:
            s = int(stack[-1])
            step += 1
            results['step'].append(f'({step})')
            results['input'].append(' '.join(buffer[pointer:]))

            if a not in self.parsing_table[s]:
                results['action'].append(f'ERROR: unrecognized symbol {a}')
                break

            action = self.parsing_table[s][a]

            if not action:
                results['action'].append('ERROR: input cannot be parsed by given grammar')
                break

            elif '/' in action:
                conflict_type = 'reduce' if action.count('r') > 1 else 'shift'
                results['action'].append(f'ERROR: {conflict_type}-reduce conflict at state {s}, symbol {a}')
                break

            elif action.startswith('s'):
                stack.append(action[1:])
                symbols.append(a)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))
                results['action'].append('shift')
                pointer += 1
                a = buffer[pointer]

            elif action.startswith('r'):
                production = self.G_indexed[int(action[1:])]
                head = production['head']
                body = production['body']

                if body != ['^']:
                    stack = stack[:-len(body)]
                    symbols = symbols[:-len(body)]

                stack.append(str(self.parsing_table[int(stack[-1])][head]))
                symbols.append(head)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))
                results['action'].append(f'reduce by {head} -> {" ".join(body)}')

            elif action == 'acc':
                results['action'].append('accept')
                break

        return results

    def print_LR_parser(self, results):
        def print_line():
            line = '+' + '+'.join([('-' * (max_len + 2)) for max_len in max_lens.values()]) + '+'
            print(line)

        max_lens = {key: max(len(value) for value in results[key]) for key in results}
        justifications = {
            'step': '>',
            'stack': '',
            'symbols': '',
            'input': '>',
            'action': ''
        }

        print_line()
        header = ''.join(
            [f'| {history[0]:^{max_len}} ' for history, max_len in zip(results.values(), max_lens.values())]) + '|'
        print(header)
        print_line()
        for i in range(1, len(results['step'])):
            row = ''.join([f'| {history[i]:{justification}{max_len}} ' for history, justification, max_len in
                           zip(results.values(), justifications.values(), max_lens.values())]) + '|'
            print(row)

        print_line()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar_file', type=argparse.FileType('r'), help='Path to the text file used as grammar')
    parser.add_argument('-g', action='store_true', help='Generate automaton')
    parser.add_argument('tokens', help='Tokens to be parsed, separated by spaces')
    args = parser.parse_args()

    G = Grammar(args.grammar_file.read())
    slr_parser = SLRParser(G)
    slr_parser.print_info()
    results = slr_parser.LR_parser(args.tokens)
    slr_parser.print_LR_parser(results)

    if args.g:
        slr_parser.generate_automaton()


if __name__ == '__main__':
    main()
