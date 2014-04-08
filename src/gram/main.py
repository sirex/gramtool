"""Grammar analysis tool.

Usage:
  gram <word> [-d <path>] [-l <lang>]

Options:
  <word>                A lexeme from morphology database.
  -h --help             Show this screen.
  -d --data-dir=<path>  Data directory [default: data].
  -l --lang=<lang>      Data directory [default: lt].

"""

import docopt
import os.path

from .parser import get_grammar_rules
from .utils.grammar import get_grammar_tree
from .views import print_forms
from .exceptions import UserSideError
from .grammar import Grammar
from .hunspell import get_hunspell_dict


def gram():
    args = docopt.docopt(__doc__)
    lang = args['--lang']
    data_dir = args['--data-dir']
    data = lambda *args: os.path.join(data_dir, *args)
    word = args['<word>'].decode('utf-8')

    grammar_file = data('grammar.yaml')
    rules_file = data(lang, 'grammar')
    hunspell_dic_file = data(lang, 'hunspell.dic')
    hunspell_aff_file = data(lang, 'hunspell.aff')

    try:
        tree = get_grammar_tree(grammar_file)
        rules = get_grammar_rules(tree, rules_file)
        hunspell = get_hunspell_dict(hunspell_aff_file, hunspell_dic_file)
        grammar = Grammar(hunspell, tree, rules)
    except UserSideError as e:
        try:
            print unicode(e).encode('utf-8')
        except UnicodeDecodeError:
            print e
    else:
        print_forms(grammar, word)
