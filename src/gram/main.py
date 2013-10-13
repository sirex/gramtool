import sys

from .parser import get_grammar_rules
from .utils.grammar import get_grammar_tree
from .views import print_grammar
from .views import print_forms
from .exceptions import UserSideError
from .grammar import Grammar
from .hunspell import get_hunspell_dict


def gram():
    path = sys.argv[1]
    grammar_file = path + 'grammar.yaml'
    rules_file = path + 'lt/grammar'
    hunspell_dic_file = path + 'lt/hunspell.dic'
    hunspell_aff_file = path + 'lt/hunspell.aff'

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
        #print_forms(grammar, u'medis')
        if True:
            print '-' * 72
            print_grammar(grammar)
