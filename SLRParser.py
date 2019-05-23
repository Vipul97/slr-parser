def parse_grammar():
    G_prime = {}
    G_indexed = {}
    start = ""
    terminals = set([])
    nonterminals = set([])
    grammars = open("grammar.txt")

    i = 1
    for grammar in grammars:
        if grammar == '\n':
            continue

        head = grammar.split()[0]
        prods = ' '.join(grammar[grammar.index("->") + 2:].split()).split(' | ')

        if not start:
            start = head + "'"
            G_prime[start] = [head]

        if head not in G_prime:
            G_prime[head] = []
            nonterminals.add(head)

        for prod in prods:
            G_prime[head].append(prod)
            G_indexed[i] = head + " -> " + prod
            i += 1

            for symbol in prod.split():
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
        first_seen.append(X)

        for prod in G_prime[X]:
            if prod == ['^']:  # CASE 3
                first.add('^')

            else:  # CASE 2
                for (i, symbol) in enumerate(prod.split()):
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

    for (heads, prods) in G_prime.items():
        for prod in prods:
            prod = prod.split()

            if A in prod[:-1]:  # CASE 2
                first = FIRST(prod[prod.index(A) + 1])
                follow |= (first - set('^'))

                if '^' in first and heads not in follow_seen:  # CASE 3
                    follow |= FOLLOW(heads)

            elif A in prod[-1]:  # CASE 3
                if heads not in follow_seen:
                    follow |= FOLLOW(heads)

    follow_seen.remove(A)

    return follow


def CLOSURE(I):
    J = I

    while True:
        item_len = len(J)

        for item in J.copy():
            item = item.split()

            if '.' in item[:-1]:
                symbol_after_dot = item[item.index('.') + 1]

                if symbol_after_dot in nonterminals:
                    for prod in G_prime[symbol_after_dot]:
                        J.add(symbol_after_dot + ' -> . ' + prod)

        if item_len == len(J):
            return J


def GOTO(I, X):
    goto = set([])

    for item in I:
        item = item.split()

        if '.' in item[:-1]:
            dot_pos = item.index('.')

            if item[dot_pos + 1] == X:
                [goto.add(item) for item in CLOSURE({' '.join(item[:dot_pos] + [X] + ['.'] + item[dot_pos + 2:])})]

    return goto


def items():
    C = [CLOSURE({start + " -> . " + start[:-1]})]

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

    for i in range(len(C)):
        for a in terminals + ['$']:
            for item in C[i]:
                item = item.split()

                if '.' in item[:-1] and a in terminals:  # CASE 1 a
                    if item[item.index('.') + 1] == a:
                        if "r" in parse_table[i][a]:
                            print("ERROR: Shift-Reduce Conflict at State " + str(i) + ", Symbol " + a)
                            exit(1)

                        parse_table[i][a] = "s" + str(C.index(GOTO(C[i], a)))
                elif item[-1] == '.':  # CASE 1 b
                    head = item[0]

                    if head != start:
                        idx = -1

                        for j in G_indexed:
                            if G_indexed[j] == ' '.join(item[:-1]):
                                idx = str(j)

                                break

                        for f in FOLLOW(head):
                            if "s" in parse_table[i][f]:
                                print("ERROR: Shift-Reduce Conflict at State " + str(i) + ", Symbol " + f)
                                exit(1)

                            elif parse_table[i][f] and parse_table[i][f] != "r" + idx:
                                print("ERROR: Reduce-Reduce Conflict at State " + str(i) + ", Symbol " + f)
                                exit(1)

                            parse_table[i][f] = "r" + idx
                    else:  # CASE 1 c
                        parse_table[i]['$'] = "acc"

        for A in nonterminals:  # CASE 2
            j = GOTO(C[i], A)

            if j in C:
                parse_table[i][A] = C.index(j)

    return parse_table


def print_info():
    def print_border():
        print(("+" + "-" * 8) * (len(symbols) + 2) + "+")

    print("AUGMENTED GRAMMAR:")

    i = 0
    for (head, prods) in G_prime.items():
        for prod in prods:
            print("{:>{width}}:".format(str(i), width=len(str(sum(len(v) for v in G_prime.values()) - 1))), end=' ')
            print("{:>{width}} ->".format(head, width=len(max(G_prime.keys(), key=len))), end=' ')
            print(prod)

            i += 1

    print()
    print("%13s" % "TERMINALS:", ', '.join(terminals))
    print("%13s" % "NONTERMINALS:", ', '.join(nonterminals))
    print("%13s" % "SYMBOLS:", ', '.join(symbols))

    print("\nFIRST:")
    for head in G_prime.keys():
        print("{:>{width}} =".format(head, width=len(max(G_prime.keys(), key=len))), end=' ')
        print("{ " + ', '.join(FIRST(head)) + " }")

    print("\nFOLLOW:")
    for head in G_prime.keys():
        print("{:>{width}} =".format(head, width=len(max(G_prime.keys(), key=len))), end=' ')
        print("{ " + ', '.join(FOLLOW(head)) + " }")

    print("\nITEMS:")
    for (i, items) in enumerate(C):
        print('I' + str(i) + ':')

        for item in items:
            item = item.split()

            print("{:>{width}}".format(item[0], width=len(max(G_prime.keys(), key=len))), end=' ')
            print(' '.join(item[1:]))

        print()

    print("PARSING TABLE:")
    print_border()
    print("|{:^8}|".format('STATE'), end=' ')

    for symbol in terminals + ['$'] + nonterminals:
        print("{:^7}|".format(symbol), end=' ')

    print()
    print_border()

    for r in range(len(C)):
        print("|{:^8}|".format(r), end=' ')

        for c in terminals + ['$'] + nonterminals:
            print("{:^7}|".format(parse_table[r][c]), end=' ')

        print()

    print_border()


def LR_parser(w, parse_table):
    def print_border():
        print("+" + "-" * 8 + ("+" + "-" * 28) * 2 + "+" + "-" * 11 + "+")

    buffer = (w + " $").split()
    pointer = 0
    a = buffer[pointer]
    stack = ['0']

    print()
    print_border()
    print("|{:^8}|{:^28}|{:^28}|{:^11}|".format("STEP", "STACK", "INPUT", "ACTION"))
    print_border()

    step = 0
    while True:
        s = int(stack[-1])
        step += 1

        print("|{:^8}| {:27}| {:>26} | ".format(step, ''.join(stack), ''.join(buffer[pointer:])), end=' ')

        if a not in parse_table[s].keys():
            print("ERROR: Unrecognized Symbol", a, "|")

            break

        elif parse_table[s][a][0] == "s":
            print("{:^9}|".format(parse_table[s][a]))

            stack.append(a)
            stack.append(parse_table[s][a][1:])
            pointer += 1
            a = buffer[pointer]

        elif parse_table[s][a][0] == "r":
            print("{:^9}|".format(parse_table[s][a]))

            grammar = G_indexed[int(parse_table[s][a][1:])].split()

            if grammar[-1] != '^':
                stack = stack[:-(2 * len(grammar[grammar.index('->') + 1:]))]
                s = int(stack[-1])
                head = grammar[0]
                stack.append(head)
                stack.append(str(parse_table[s][head]))

        elif parse_table[s][a] == "acc":
            print("{:^9}|".format("ACCEPTED"))

            break

    print_border()


G_prime, G_indexed, start, terminals, nonterminals, symbols = parse_grammar()
C = items()
parse_table = construct_table()
print_info()

LR_parser(input("\nEnter Input: "), parse_table)
