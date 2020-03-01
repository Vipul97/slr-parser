from graphviz import Digraph


def parse_grammar():
    G_prime = {}
    G_indexed = [['', '']]
    start = ''
    terminals = set([])
    nonterminals = set([])
    grammars = open('grammar.txt')

    for grammar in grammars:
        if grammar == '\n':
            continue

        head, _, prods = grammar.partition(' -> ')
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

    grammars.close()

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
        first_seen.append(X)

        for prod in G_prime[X]:
            if prod == ['^']:  # CASE 3
                first.add('^')

            else:  # CASE 2
                for i, symbol in enumerate(prod):
                    if symbol not in first_seen:
                        symbol_first = FIRST(symbol)

                        for sf in symbol_first:
                            if sf in terminals:
                                first.add(sf)

                        if '^' not in symbol_first:
                            break
                    else:
                        break

                    if i + 1 == len(prod):
                        first.add('^')

        first_seen.remove(X)

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

            elif A in prod[-1]:  # CASE 3
                if head not in follow_seen:
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

                    if symbol_after_dot in terminals and f's{C.index(GOTO(I, symbol_after_dot))}' not in parse_table[i][
                        symbol_after_dot]:
                        if 'r' in parse_table[i][symbol_after_dot]:
                            parse_table[i][symbol_after_dot] += '/'

                        parse_table[i][symbol_after_dot] += f's{C.index(GOTO(I, symbol_after_dot))}'

                elif prod[-1] == '.' and head != start:  # CASE 2 b
                    for j, (G_head, G_prod) in enumerate(G_indexed):
                        if head == G_head and G_prod == prod[:-1]:
                            for f in FOLLOW(head):
                                if parse_table[i][f]:
                                    if f'r{j}' not in parse_table[i][f]:
                                        parse_table[i][f] += f'/r{j}'
                                else:
                                    parse_table[i][f] = f'r{j}'

                            break

                else:  # CASE 2 c
                    parse_table[i]['$'] = 'acc'

        for A in nonterminals:  # CASE 3
            j = GOTO(I, A)

            if j in C:
                parse_table[i][A] = C.index(j)

    return parse_table


def print_info():
    def print_line():
        print(('+' + '-' * (width + 1)) * (len(symbols) + 2) + '+')

    max_G_prime = len(max(G_prime.keys(), key=len))

    print('AUGMENTED GRAMMAR:')

    i = 0
    for head, prods in G_prime.items():
        for prod in prods:
            print(
                f'{i:>{len(str(sum(len(v) for v in G_prime.values()) - 1))}}: {head:>{max_G_prime}} -> {" ".join(prod)}')

            i += 1

    print()
    print(f'{"TERMINALS:":>13} {", ".join(terminals)}')
    print(f'{"NONTERMINALS:":>13} {", ".join(nonterminals)}')
    print(f'{"SYMBOLS:":>13} {", ".join(symbols)}')

    print('\nFIRST:')
    for head in G_prime.keys():
        print(f'{head:>{max_G_prime}} = {{ {", ".join(FIRST(head))} }}')

    print('\nFOLLOW:')
    for head in G_prime.keys():
        print(f'{head:>{max_G_prime}} = {{ {", ".join(FOLLOW(head))} }}')

    width = max(len(c) for c in ['STATE', '$'] + terminals + nonterminals) + 1

    print('\nPARSING TABLE:')
    print_line()
    print(f'|{"STATE":^{width + 1}}|', end=' ')

    for symbol in terminals + ['$'] + nonterminals:
        print(f'{symbol:^{width}}|', end=' ')

    print()
    print_line()

    for r in range(len(C)):
        print(f'|{r:^{width + 1}}|', end=' ')

        for c in terminals + ['$'] + nonterminals:
            print(f'{parse_table[r][c]:^{width}}|', end=' ')

        print()

    print_line()

    automaton = Digraph('automaton', node_attr={'shape': 'record'})

    for i, I in enumerate(C):
        I_str = f'<<I>I</I><SUB>{i}</SUB><BR/>'

        for (head, prods) in I.items():
            for prod in prods:
                I_str += f'{head:>{max_G_prime}} &#8594; {" ".join(prod)} <BR ALIGN="LEFT"/>'
                automaton.node(f'I{i}', f'{I_str}>')

    for r in range(len(C)):
        for c in terminals + ['$'] + nonterminals:
            if isinstance(parse_table[r][c], int):
                automaton.edge(f'I{r}', f'I{parse_table[r][c]}', label=f'<<I>{c}</I>>')

            elif 's' in parse_table[r][c]:
                i = parse_table[r][c][parse_table[r][c].index('s') + 1:]

                if '/' in i:
                    i = i[:i.index('/')]

                automaton.edge(f'I{r}', f'I{i}', label=c)

            elif parse_table[r][c] == 'acc':
                automaton.node('acc', '<<B>accept</B>>', shape='none')
                automaton.edge(f'I{r}', 'acc', label='$')

    automaton.view()


def LR_parser(w):
    def print_line():
        print('+' + '-' * (max_step + 2) + '+' + '-' * (max_stack + 2) + '+' + '-' * (max_symbols + 2) + '+' + '-' * (
                max_input + 2) + '+' + '-' * (max_action + 2) + '+')

    buffer = f'{w} $'.split()
    pointer = 0
    a = buffer[pointer]
    stack = ['0']
    symbols = ['']

    step_history = ['']
    stack_history = ['STACK'] + stack
    symbols_history = ['SYMBOLS'] + symbols
    input_history = ['INPUT']
    action_history = ['ACTION']

    step = 0
    while True:
        s = int(stack[-1])
        step += 1
        step_history.append(f'({step})')
        input_history.append(' '.join(buffer[pointer:]))

        if a not in parse_table[s].keys():
            action_history.append(f'ERROR: unrecognized symbol {a}')

            break

        elif not parse_table[s][a]:
            action_history.append('ERROR: input cannot be parsed by given grammar')

            break

        elif '/' in parse_table[s][a]:
            if parse_table[s][a].count('r') > 1:
                action_history.append(f'ERROR: reduce-reduce conflict at state {s}, symbol {a}')
            else:
                action_history.append(f'ERROR: shift-reduce conflict at state {s}, symbol {a}')

            break

        elif parse_table[s][a].startswith('s'):
            action_history.append('shift')
            stack.append(parse_table[s][a][1:])
            symbols.append(a)
            stack_history.append(' '.join(stack))
            symbols_history.append(' '.join(symbols))
            pointer += 1
            a = buffer[pointer]

        elif parse_table[s][a].startswith('r'):
            head, prod = G_indexed[int(parse_table[s][a][1:])]
            action_history.append(f'reduce by {head} -> {" ".join(prod)}')

            if prod[-1] != '^':
                stack = stack[:-len(prod)]
                stack.append(str(parse_table[int(stack[-1])][head]))
                symbols = symbols[:-len(prod)]
                symbols.append(head)
                stack_history.append(' '.join(stack))
                symbols_history.append(' '.join(symbols))

        elif parse_table[s][a] == 'acc':
            action_history.append('accept')

            break

    max_step = max(len(step) for step in step_history)
    max_stack = max(len(stack) for stack in stack_history)
    max_symbols = max(len(symbols) for symbols in symbols_history)
    max_input = max(len(input) for input in input_history)
    max_action = max(len(action) for action in action_history)

    print_line()
    print(
        f'| {"":^{max_step}} | {stack_history[0]:^{max_stack}} | {symbols_history[0]:^{max_symbols}} | {input_history[0]:^{max_input}} | {action_history[0]:^{max_action}} |')
    print_line()
    for i, step in enumerate(step_history[:-1], 1):
        print(
            f'| {step_history[i]:>{max_step}} | {stack_history[i]:{max_stack}} | {symbols_history[i]:{max_symbols}} | {input_history[i]:>{max_input}} | {action_history[i]:{max_action}} |')
    print_line()


G_prime, G_indexed, start, terminals, nonterminals, symbols = parse_grammar()
C = items()
parse_table = construct_table()
print_info()

LR_parser(input('\nEnter Input: '))
