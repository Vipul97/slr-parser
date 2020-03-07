from graphviz import Digraph


def parse_grammar():
    G_prime = {}
    G_indexed = [['', '']]
    start = ''
    terminals = set([])
    nonterminals = set([])

    with open('grammar.txt') as grammar_file:
        grammar = list(filter(None, grammar_file.read().splitlines()))

    for g in grammar:
        head, _, prods = g.partition(' -> ')
        prods = [prod.split() for prod in ' '.join(prods.split()).split('|')]

        if not start:
            start = f"{head}'"
            G_prime[start] = [[head]]

        if head not in G_prime:
            G_prime[head] = []
            nonterminals.add(head)

        for prod in prods:
            G_prime[head].append(prod)
            G_indexed.append([head, prod])

            for symbol in prod:
                if not symbol.isupper() and symbol != '^':
                    terminals.add(symbol)
                elif symbol.isupper():
                    nonterminals.add(symbol)

    return G_prime, G_indexed, start, [terminal for terminal in terminals], [nonterminal for nonterminal in
                                                                             nonterminals], [symbol for symbol in
                                                                                             terminals | nonterminals]


first_seen = []


def FIRST(X):
    if X in terminals:  # CASE 1
        return {X}
    else:
        global first_seen
        first = set([])

        while True:
            first_seen.append(X)
            first_len = len(first)

            for prod in G_prime[X]:
                if prod != ['^']:  # CASE 2
                    for symbol in prod:
                        if symbol == X and '^' in first:
                            continue

                        if symbol not in first_seen:
                            symbol_first = FIRST(symbol)

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

            first_seen.remove(X)

            if first_len == len(first):
                return first


follow_seen = []


def FOLLOW(A):
    global follow_seen
    follow = set([])
    follow_seen.append(A)

    if A == start:  # CASE 1
        follow.add('$')

    for head, prods in G_prime.items():
        for prod in prods:
            if A in prod[:-1]:  # CASE 2
                first = FIRST(prod[prod.index(A) + 1])
                follow |= (first - set('^'))

                if '^' in first and head not in follow_seen:  # CASE 3
                    follow |= FOLLOW(head)

            elif A in prod[-1] and head not in follow_seen:  # CASE 3
                follow |= FOLLOW(head)

    follow_seen.remove(A)

    return follow


def CLOSURE(I):
    J = I

    while True:
        item_len = len(J)

        for head, prods in J.copy().items():
            for prod in prods:
                if '.' in prod[:-1]:
                    symbol_after_dot = prod[prod.index('.') + 1]

                    if symbol_after_dot in nonterminals:
                        for G_prod in G_prime[symbol_after_dot]:
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


def GOTO(I, X):
    goto = {}

    for head, prods in I.items():
        for prod in prods:
            if '.' in prod[:-1]:
                dot_pos = prod.index('.')

                if prod[dot_pos + 1] == X:
                    for C_head, C_prods in CLOSURE({head: [prod[:dot_pos] + [X, '.'] + prod[dot_pos + 2:]]}).items():
                        if C_head not in goto.keys():
                            goto[C_head] = C_prods
                        else:
                            for C_prod in C_prods:
                                if C_prod not in goto[C_head]:
                                    goto[C_head].append(C_prod)

    return goto


def items():
    C = [CLOSURE({start: [['.'] + [start[:-1]]]})]

    while True:
        item_len = len(C)

        for I in C.copy():
            for X in symbols:
                if GOTO(I, X) and GOTO(I, X) not in C:
                    C.append(GOTO(I, X))

        if item_len == len(C):
            return C


def construct_table():
    parse_table = {r: {c: '' for c in terminals + ['$'] + nonterminals} for r in range(len(C))}

    for i, I in enumerate(C):
        for head, prods in I.items():
            for prod in prods:
                if '.' in prod[:-1]:  # CASE 2 a
                    symbol_after_dot = prod[prod.index('.') + 1]

                    if symbol_after_dot in terminals:
                        s = f's{C.index(GOTO(I, symbol_after_dot))}'

                        if s not in parse_table[i][symbol_after_dot]:
                            if 'r' in parse_table[i][symbol_after_dot]:
                                parse_table[i][symbol_after_dot] += '/'

                            parse_table[i][symbol_after_dot] += s

                elif prod[-1] == '.' and head != start:  # CASE 2 b
                    for j, (G_head, G_prod) in enumerate(G_indexed):
                        if G_head == head and (G_prod == prod[:-1] or G_prod == ['^'] and prod == ['.']):
                            for f in FOLLOW(head):
                                if parse_table[i][f]:
                                    parse_table[i][f] += '/'

                                parse_table[i][f] += f'r{j}'

                            break

                else:  # CASE 2 c
                    parse_table[i]['$'] = 'acc'

        for A in nonterminals:  # CASE 3
            j = GOTO(I, A)

            if j in C:
                parse_table[i][A] = C.index(j)

    return parse_table


def print_info():
    max_G_prime = len(max(G_prime.keys(), key=len))

    print('AUGMENTED GRAMMAR:')

    i = 0
    for head, prods in G_prime.items():
        for prod in prods:
            print(f'{i:>{len(str(len(G_indexed) - 1))}}: {head:>{max_G_prime}} -> {" ".join(prod)}')

            i += 1

    print(f'\n{"TERMINALS:":>13} {", ".join(terminals)}')
    print(f'{"NONTERMINALS:":>13} {", ".join(nonterminals)}')
    print(f'{"SYMBOLS:":>13} {", ".join(symbols)}')

    print('\nFIRST:')
    for head in G_prime.keys():
        print(f'{head:>{max_G_prime}} = {{ {", ".join(FIRST(head))} }}')

    print('\nFOLLOW:')
    for head in G_prime.keys():
        print(f'{head:>{max_G_prime}} = {{ {", ".join(FOLLOW(head))} }}')

    width = max(len(c) for c in ['ACTION'] + symbols) + 2
    for r in range(len(C)):
        max_len = max(len(str(c)) for c in parse_table[r].values())

        if width < max_len + 2:
            width = max_len + 2

    print('\nPARSING TABLE:')
    print(
        f'+{"-" * width}+{"-" * ((width + 1) * len(terminals + ["$"]) - 1)}+{"-" * ((width + 1) * len(nonterminals) - 1)}+')
    print(
        f'|{"":{width}}|{"ACTION":^{(width + 1) * len(terminals + ["$"]) - 1}}|{"GOTO":^{(width + 1) * len(nonterminals) - 1}}|')
    print(f'|{"STATE":^{width}}+{("-" * width + "+") * len(symbols + ["$"])}')
    print(f'|{"":^{width}}|', end=' ')

    for symbol in terminals + ['$'] + nonterminals:
        print(f'{symbol:^{width - 1}}|', end=' ')

    print(f'\n+{("-" * width + "+") * (len(symbols + ["$"]) + 1)}')

    for r in range(len(C)):
        print(f'|{r:^{width}}|', end=' ')

        for c in terminals + ['$'] + nonterminals:
            print(f'{parse_table[r][c]:^{width - 1}}|', end=' ')

        print()

    print(f'+{("-" * width + "+") * (len(symbols + ["$"]) + 1)}')


def generate_automaton():
    automaton = Digraph('automaton', node_attr={'shape': 'record'})
    max_G_prime = len(max(G_prime.keys(), key=len))

    for i, I in enumerate(C):
        I_str = f'<<I>I</I><SUB>{i}</SUB><BR/>'

        for (head, prods) in I.items():
            for prod in prods:
                I_str += f'<I>{head:>{max_G_prime}}</I> &#8594;'

                for symbol in prod:
                    if symbol in nonterminals:
                        I_str += f' <I>{symbol}</I>'
                    elif symbol in terminals:
                        I_str += f' <B>{symbol}</B>'
                    else:
                        I_str += f' {symbol}'

                I_str += '<BR ALIGN="LEFT"/>'

        automaton.node(f'I{i}', f'{I_str}>')

    for r in range(len(C)):
        for c in terminals + ['$'] + nonterminals:
            if isinstance(parse_table[r][c], int):
                automaton.edge(f'I{r}', f'I{parse_table[r][c]}', label=f'<<I>{c}</I>>')

            elif 's' in parse_table[r][c]:
                i = parse_table[r][c][parse_table[r][c].index('s') + 1:]

                if '/' in i:
                    i = i[:i.index('/')]

                automaton.edge(f'I{r}', f'I{i}', label=f'<<B>{c}</B>>' if c in terminals else c)

            elif parse_table[r][c] == 'acc':
                automaton.node('acc', '<<B>accept</B>>', shape='none')
                automaton.edge(f'I{r}', 'acc', label='$')

    automaton.view()


def LR_parser(w):
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

        if a not in parse_table[s].keys():
            histories['action'].append(f'ERROR: unrecognized symbol {a}')

            break

        elif not parse_table[s][a]:
            histories['action'].append('ERROR: input cannot be parsed by given grammar')

            break

        elif '/' in parse_table[s][a]:
            if parse_table[s][a].count('r') > 1:
                histories['action'].append(f'ERROR: reduce-reduce conflict at state {s}, symbol {a}')
            else:
                histories['action'].append(f'ERROR: shift-reduce conflict at state {s}, symbol {a}')

            break

        elif parse_table[s][a].startswith('s'):
            histories['action'].append('shift')
            stack.append(parse_table[s][a][1:])
            symbols.append(a)
            histories['stack'].append(' '.join(stack))
            histories['symbols'].append(' '.join(symbols))
            pointer += 1
            a = buffer[pointer]

        elif parse_table[s][a].startswith('r'):
            head, prod = G_indexed[int(parse_table[s][a][1:])]
            histories['action'].append(f'reduce by {head} -> {" ".join(prod)}')

            if prod != ['^']:
                stack = stack[:-len(prod)]
                symbols = symbols[:-len(prod)]

            stack.append(str(parse_table[int(stack[-1])][head]))
            symbols.append(head)
            histories['stack'].append(' '.join(stack))
            histories['symbols'].append(' '.join(symbols))

        elif parse_table[s][a] == 'acc':
            histories['action'].append('accept')

            break

    max_lens = {'step': max(len(step) for step in histories['step']),
                'stack': max(len(stack) for stack in histories['stack']),
                'symbols': max(len(symbols) for symbols in histories['symbols']),
                'input': max(len(input) for input in histories['input']),
                'action': max(len(action) for action in histories['action'])}
    justs = {'step': '>', 'stack': '', 'symbols': '', 'input': '>', 'action': ''}

    print_line()
    print(''.join(
        [f'| {history[0]:^{max_len}} ' for history, max_len in zip(histories.values(), max_lens.values())]) + '|')
    print_line()
    for i, step in enumerate(histories['step'][:-1], 1):
        print(''.join([f'| {history[i]:{just}{max_len}} ' for history, just, max_len in
                       zip(histories.values(), justs.values(), max_lens.values())]) + '|')

    print_line()


G_prime, G_indexed, start, terminals, nonterminals, symbols = parse_grammar()
C = items()
parse_table = construct_table()
print_info()
generate_automaton()

LR_parser(input('\nEnter Input: '))
