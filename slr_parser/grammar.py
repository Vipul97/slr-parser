class Grammar:
    def __init__(self, grammar_str):
        self.grammar_str = self._clean_grammar_string(grammar_str)
        self.grammar = {}
        self.start = None
        self.terminals = set()
        self.nonterminals = set()

        self._parse_grammar()
        self.symbols = self.terminals | self.nonterminals

    def _clean_grammar_string(self, grammar_str):
        return '\n'.join(' '.join(line.split()) for line in grammar_str.strip().splitlines() if line.strip())

    def _validate_head(self, head):
        if not head.isupper():
            raise ValueError(f'Nonterminal head \'{head}\' must be uppercase.')

    def _validate_body(self, head, body):
        if not body:
            raise ValueError(f'\'{head} -> \': Cannot have an empty body.')
        if '^' in body and body != ['^']:
            raise ValueError(f'\'{head} -> {" ".join(body)}\': Null symbol \'^\' is not allowed here.')

    def _update_symbols(self, body):
        for symbol in body:
            if symbol.isupper():
                self.nonterminals.add(symbol)
            elif symbol != '^':
                self.terminals.add(symbol)

    def _process_bodies(self, head, bodies):
        for body in bodies:
            self._validate_body(head, body)
            if body not in self.grammar[head]:
                self.grammar[head].append(body)
            self._update_symbols(body)

    def _parse_grammar(self):
        if not self.grammar_str:
            raise ValueError('Grammar definition cannot be empty.')

        for production in self.grammar_str.splitlines():
            head, _, bodies = production.partition(' -> ')
            self._validate_head(head)

            if self.start is None:
                self.start = head

            self.grammar.setdefault(head, [])
            self.nonterminals.add(head)

            bodies = [(body.split()) for body in bodies.split('|')]
            self._process_bodies(head, bodies)
