# SLR Parser [![codecov](https://codecov.io/gh/Vipul97/slr-parser/branch/master/graph/badge.svg)](https://codecov.io/gh/Vipul97/slr-parser) [![Build Status](https://travis-ci.org/Vipul97/slr-parser.svg?branch=master)](https://travis-ci.org/Vipul97/slr-parser) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Implementation of Simple LR (SLR) Parser for educational purposes.

# Installation

## Stable release

To install slr-parser, run this command in your terminal:

```
pip install slr-parser
```

This is the preferred method to install slr-parser, as it will always install the most recent stable release.

If you don't have [pip](https://pip.pypa.io) installed, this [Python installation guide](http://docs.python-guide.org/en/latest/starting/installation/) can guide you through the process.

## From sources

The sources for slr-parser can be downloaded from the [Github repo](https://github.com/Vipul97/slr-parser).

You can either clone the public repository:

```
git clone git://github.com/Vipul97/slr-parser
```

Or download the [tarball](https://github.com/Vipul97/slr-parser/tarball/master):

```
curl -OJL https://github.com/Vipul97/slrparser/tarball/master
```

Once you have a copy of the source, you can install it with:

```
python setup.py install
```

## Dependencies
* Graphviz

## Grammar Syntax
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

# Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code of conduct, and the process for submitting pull requests.

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.