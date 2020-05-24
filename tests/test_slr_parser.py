from slr_parser.slr_parser import SLRParser
import unittest


class TestSLRParser(unittest.TestCase):
    def setUp(self):
        with open('test_grammar.txt') as grammar_file:
            self.slr_parser = SLRParser(grammar_file, 'id + id * id')

    def test_parse_grammar(self):
        self.assertEqual("E'", self.slr_parser.start)
        self.assertDictEqual({"E'": [['E']], 'E': [['E', '+', 'T'], ['T']], 'T': [['T', '*', 'F'], ['F']],
                              'F': [['(', 'E', ')'], ['id']]}, self.slr_parser.G_prime)
        self.assertListEqual([['', ''], ['E', ['E', '+', 'T']], ['E', ['T']], ['T', ['T', '*', 'F']], ['T', ['F']],
                              ['F', ['(', 'E', ')']], ['F', ['id']]], self.slr_parser.G_indexed)
        self.assertSetEqual({'+', '*', '(', ')', 'id'}, set(self.slr_parser.terminals))
        self.assertSetEqual({'E', 'T', 'F'}, set(self.slr_parser.nonterminals))
        self.assertSetEqual({'+', '*', '(', ')', 'id', 'E', 'T', 'F'}, set(self.slr_parser.symbols))

    def test_FIRST(self):
        self.assertEqual({'id'}, self.slr_parser.FIRST('id'))
        self.assertEqual({'(', 'id'}, self.slr_parser.FIRST('E'))

    def test_FOLLOW(self):
        self.assertEqual({'$'}, self.slr_parser.FOLLOW(self.slr_parser.start))

    def test_CLOSURE(self):
        self.assertDictEqual(
            {"E'": [['.', 'E']], 'E': [['.', 'E', '+', 'T'], ['.', 'T']], 'T': [['.', 'T', '*', 'F'], ['.', 'F']],
             'F': [['.', '(', 'E', ')'], ['.', 'id']]},
            self.slr_parser.CLOSURE({self.slr_parser.start: [['.'] + [self.slr_parser.start[:-1]]]}))

    def test_GOTO(self):
        self.assertDictEqual({"E'": [['E', '.']]}, self.slr_parser.GOTO({"E'": [['.', 'E']]}, 'E'))


if __name__ == "__main__":
    unittest.main()
