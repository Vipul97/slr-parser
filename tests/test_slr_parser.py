from slr_parser.grammar import Grammar
from slr_parser.slr_parser import SLRParser, first_follow
import unittest


class TestSLRParser(unittest.TestCase):
    def setUp(self):
        with open('tests/test_grammar.txt') as grammar_file:
            self.G = Grammar(grammar_file.read())
            self.slr_parser = SLRParser(self.G)

    def test_first_follow(self):
        grammar_tests = [
            {
                'grammar':
                    """
                        E -> E + T
                        E -> T
                        T -> T * F | F
                        F -> ( E )
                        F -> id
                    """,
                'expected_first': {
                    'E': {'(', 'id'},
                    'T': {'(', 'id'},
                    'F': {'(', 'id'}
                },
                'expected_follow': {
                    'E': {'$', '+', ')'},
                    'T': {'$', '+', '*', ')'},
                    'F': {'$', '+', '*', ')'}
                }
            },
            {
                'grammar':
                    """
                        E -> T E'
                        E' -> + T E' | ^
                        T -> F T'
                        T' -> * F T' | ^
                        F -> ( E ) | id
                    """,
                'expected_first': {
                    'E': {'(', 'id'},
                    'T': {'(', 'id'},
                    'F': {'(', 'id'},
                    "E'": {'+', '^'},
                    "T'": {'*', '^'}
                },
                'expected_follow': {
                    'E': {')', '$'},
                    "E'": {')', '$'},
                    'T': {')', '$', '+'},
                    "T'": {')', '$', '+'},
                    'F': {')', '$', '+', '*'}
                }
            },
            {
                'grammar':
                    """
                        E -> T X
                        X -> + E
                        X -> ^
                        T -> int Y
                        T -> ( E )
                        Y -> * T
                        Y -> ^
                    """,
                'expected_first': {
                    '(': {'('},
                    ')': {')'},
                    '+': {'+'},
                    '*': {'*'},
                    'int': {'int'},
                    'Y': {'^', '*'},
                    'X': {'^', '+'},
                    'T': {'int', '('},
                    'E': {'int', '('}
                },
                'expected_follow': {
                    'Y': {')', '$', '+'},
                    'X': {')', '$'},
                    'T': {')', '$', '+'},
                    'E': {')', '$'}
                }
            },
            {
                'grammar':
                    """
                        S -> a B D h
                        B -> c C
                        C -> b C | ^
                        D -> E F
                        E -> g | ^
                        F -> f | ^
                    """,
                'expected_first': {
                    'S': {'a'},
                    'B': {'c'},
                    'C': {'b', '^'},
                    'D': {'g', 'f', '^'},
                    'E': {'g', '^'},
                    'F': {'f', '^'}
                },
                'expected_follow': {
                    'S': {'$'},
                    'B': {'g', 'f', 'h'},
                    'C': {'g', 'f', 'h'},
                    'D': {'h'},
                    'E': {'f', 'h'},
                    'F': {'h'}
                }
            },
            {
                'grammar':
                    """
                        S -> A
                        A -> a B | A d
                        B -> b
                        C -> g
                    """,
                'expected_first': {
                    'S': {'a'},
                    'A': {'a'},
                    'B': {'b'},
                    'C': {'g'},
                },
                'expected_follow': {
                    'S': {'$'},
                    'A': {'$', 'd'},
                    'B': {'$', 'd'},
                    'C': set()
                }
            },
            {
                'grammar':
                    """
                        S -> ( L ) | a
                        L -> S L'
                        L' -> , S L' | ^
                    """,
                'expected_first': {
                    'S': {'(', 'a'},
                    'L': {'(', 'a'},
                    "L'": {',', '^'}
                },
                'expected_follow': {
                    'S': {'$', ',', ')'},
                    'L': {')'},
                    "L'": {')'}
                }
            },
            {
                'grammar':
                    """
                        S -> A a A b | B b B a
                        A -> ^
                        B -> ^
                    """,
                'expected_first': {
                    'S': {'a', 'b'},
                    'A': {'^'},
                    'B': {'^'}
                },
                'expected_follow': {
                    'S': {'$'},
                    'A': {'a', 'b'},
                    'B': {'a', 'b'}
                }
            },
            {
                'grammar':
                    """
                        S -> A C B | C b B | B a
                        A -> d a | B C
                        B -> g | ^
                        C -> h | ^
                    """,
                'expected_first': {
                    'S': {'d', 'g', 'h', '^', 'b', 'a'},
                    'A': {'d', 'g', 'h', '^'},
                    'B': {'g', '^'},
                    'C': {'h', '^'}
                },
                'expected_follow': {
                    'S': {'$'},
                    'A': {'h', 'g', '$'},
                    'B': {'$', 'a', 'h', 'g'},
                    'C': {'g', '$', 'b', 'h'}
                }
            }
        ]

        for test in grammar_tests:
            with self.subTest(grammar_str=test['grammar']):
                G = Grammar(test['grammar'])
                first, follow = first_follow(G)

                for non_terminal, expected_first in test['expected_first'].items():
                    self.assertSetEqual(first[non_terminal], expected_first)

                for non_terminal, expected_follow in test['expected_follow'].items():
                    self.assertSetEqual(follow[non_terminal], expected_follow)

    def test_CLOSURE(self):
        expected_closure = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        self.assertEqual(self.slr_parser.CLOSURE([(0, 0)]), expected_closure)

        grammar_str = """E -> + E"""
        with self.subTest(grammar_str=grammar_str):
            G = Grammar(grammar_str)
            slr_parser = SLRParser(G)
            self.assertEqual(slr_parser.CLOSURE([(0, 0)]), [(0, 0), (1, 0)])

    def test_GOTO(self):
        expected_goto = [(1, 2), (3, 0), (4, 0), (5, 0), (6, 0)]
        self.assertEqual(self.slr_parser.GOTO([(0, 1), (1, 1)], '+'), expected_goto)

    def test_items(self):
        expected_items = [
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)],
            [(2, 1), (3, 1)],
            [(4, 1)],
            [(0, 1), (1, 1)],
            [(5, 1), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)],
            [(6, 1)],
            [(3, 2), (5, 0), (6, 0)],
            [(1, 2), (3, 0), (4, 0), (5, 0), (6, 0)],
            [(5, 2), (1, 1)],
            [(3, 3)],
            [(1, 3), (3, 1)],
            [(5, 3)]
        ]
        self.assertCountEqual(self.slr_parser.items(self.slr_parser.G_prime), expected_items)

    def test_construct_parsing_table(self):
        self.slr_parser.construct_parsing_table()

    def test_LR_parser(self):
        expected_results = ['ERROR: unrecognized symbol -', 'ERROR: input cannot be parsed by given grammar', 'accept']

        for i, w in enumerate(['id - id', '+ id', 'id + id * id']):
            with self.subTest(w=w):
                results = self.slr_parser.LR_parser(w)
                self.assertEqual(expected_results[i], results['action'][-1])

        grammar_strs = [
            """
                S -> L = R | R
                L -> * R | id
                R -> L
            """,
            """
                E -> T | F
                T -> id
                F -> id
            """
        ]
        expected_results = ['ERROR: shift-reduce conflict at state ', 'ERROR: reduce-reduce conflict at state ']

        for i, w in enumerate(['id = id', 'id']):
            with self.subTest(w=w):
                G = Grammar(grammar_strs[i])
                slr_parser = SLRParser(G)
                results = slr_parser.LR_parser(w)
                self.assertIn(expected_results[i], results['action'][-1])


if __name__ == '__main__':
    unittest.main()
