# SLR-Parser
Implementation of Simple LR (SLR) Parser in Python 2.7.

## Grammar
The grammar can be edited in grammar.txt.

### Grammar Syntax
* For every production, the head and the body of the production is separated by ```->```.
* Capitalized symbols are treated as non-terminals and non-capitalized symbols are treated as terminals.
* All symbols in the body of the production are separated by spaces. Multicharacter symbols can be used by not including spaces between the characters.
* The choice operator ```|``` can be used in the body of the production to match either the expression before or the expression after the operator.

## Instructions
* Input the grammar in grammar.txt.
* Run SLRParser.py.
* Input tokens to be parsed. All tokens are separated by spaces.
