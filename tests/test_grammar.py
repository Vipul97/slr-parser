from slr_parser.grammar import Grammar
import unittest


class TestGrammar(unittest.TestCase):
    def test_valid_grammar(self):
        expected_grammar = {
            'E': [['E', '+', 'T'], ['T']],
            'T': [['T', '*', 'F'], ['F']],
            'F': [['(', 'E', ')'], ['id']]
        }

        with open('tests/test_grammar.txt') as grammar_file:
            grammar = Grammar(grammar_file.read())

        self.assertDictEqual(grammar.grammar, expected_grammar)
        self.assertEqual(grammar.start, 'E')
        self.assertSetEqual(grammar.terminals, {'+', '*', '(', ')', 'id'})
        self.assertSetEqual(grammar.nonterminals, {'E', 'T', 'F'})
        self.assertSetEqual(grammar.symbols, {'+', '*', '(', ')', 'id', 'E', 'T', 'F'})

    def test_empty_grammar(self):
        grammar_str = """"""
        with self.assertRaises(ValueError):
            Grammar(grammar_str)

    def test_spaces_in_productions(self):
        grammar_str = """S    ->   A   |    B
                         A ->   a
                         B   ->   b"""
        grammar = Grammar(grammar_str)
        expected_grammar = {
            'S': [['A'], ['B']],
            'A': [['a']],
            'B': [['b']]
        }
        self.assertDictEqual(grammar.grammar, expected_grammar)

    def test_grammar_with_empty_lines(self):
        grammar_str = """
            S -> A | B

            A -> a
            B -> b
        """
        grammar = Grammar(grammar_str)
        expected_grammar = {
            'S': [['A'], ['B']],
            'A': [['a']],
            'B': [['b']]
        }
        self.assertDictEqual(grammar.grammar, expected_grammar)

    def test_head_not_capitalized(self):
        grammar_str = """a -> A"""
        with self.assertRaises(ValueError):
            Grammar(grammar_str)

    def test_empty_body(self):
        grammar_str = """S ->"""
        with self.assertRaises(ValueError):
            Grammar(grammar_str)

    def test_null_symbol_in_body(self):
        grammar_str = """A -> B ^ C"""
        with self.assertRaises(ValueError):
            Grammar(grammar_str)

    def test_single_nonterminal(self):
        grammar_str = """S -> A"""
        grammar = Grammar(grammar_str)
        expected_grammar = {
            'S': [['A']]
        }
        self.assertDictEqual(grammar.grammar, expected_grammar)
        self.assertEqual(grammar.start, 'S')
        self.assertSetEqual(grammar.terminals, set())
        self.assertSetEqual(grammar.nonterminals, {'S', 'A'})

    def test_multiple_terminals(self):
        grammar_str = """S -> a | b | c"""
        grammar = Grammar(grammar_str)
        expected_grammar = {
            'S': [['a'], ['b'], ['c']]
        }
        self.assertDictEqual(grammar.grammar, expected_grammar)
        self.assertEqual(grammar.start, 'S')
        self.assertSetEqual(grammar.terminals, {'a', 'b', 'c'})
        self.assertSetEqual(grammar.nonterminals, {'S'})

    def test_nonterminal_defined_multiple_times(self):
        grammar_str = """
            A -> B
            A -> C
            B -> D
            C -> D
        """
        grammar = Grammar(grammar_str)
        expected_grammar = {
            'A': [['B'], ['C']],
            'B': [['D']],
            'C': [['D']]
        }
        self.assertDictEqual(grammar.grammar, expected_grammar)


if __name__ == '__main__':
    unittest.main()
