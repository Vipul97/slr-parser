# SLR Parser
Implementation of Simple LR (SLR) Parser in Python 3.8.

## Dependencies
* Graphviz

## Grammar
The grammar can be edited in `slr_parser/grammar.txt`.

### Grammar Syntax
* For every production, the head and the body of the production is separated by ``` -> ```.
* Capitalized symbols are treated as non-terminals and non-capitalized symbols are treated as terminals.
* All symbols in the body of the production are separated by spaces. Multicharacter symbols can be made by not including spaces between the characters.
* The choice operator ``` | ``` can be used in the body of the production to match either the expression before or the expression after the operator.
* ```^``` is treated as the null symbol.

## Instructions
1. Run `slr_parser/slr_parser.py`.

        usage: slr_parser.py [-h] [-g] grammar_file tokens

        positional arguments:
          grammar_file  text file to be used as grammar
          tokens        tokens to be parsed - all tokens are separated with spaces
        
        optional arguments:
          -h, --help    show this help message and exit
          -g            generate automaton

2. Input the tokens to be parsed. All tokens are separated by spaces.
