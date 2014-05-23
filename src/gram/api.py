# coding: utf-8

import os.path

from .parser import get_grammar_rules
from .utils.grammar import get_grammar_tree
from .grammar import Grammar
from .hunspell import get_hunspell_dict


_dicts = {}


class Wrapper(object):
    def __init__(self, lang):
        path = '..', '..', '..', 'data'
        data_dir = os.path.abspath(os.path.join(__file__, *path))
        data = lambda *args: os.path.join(data_dir, *args)

        grammar_file = data('grammar.yaml')
        rules_file = data(lang, 'grammar')
        hunspell_dic_file = data(lang, 'hunspell.dic')
        hunspell_aff_file = data(lang, 'hunspell.aff')

        self.tree = get_grammar_tree(grammar_file)
        self.rules = get_grammar_rules(self.tree, rules_file)
        self.hunspell = get_hunspell_dict(hunspell_aff_file, hunspell_dic_file)
        self.grammar = Grammar(self.hunspell, self.tree, self.rules)



def load(lang):
    global _dicts
    if lang not in _dicts:
        _dicts[lang] = Wrapper(lang)
    return _dicts[lang]


def _get_lemma(word, lang):
    d = load(lang)
    for lemma, lexeme in d.grammar.iter_rules(word):
        return lemma.form.get_word(lemma.stem)


def _get_stem(word, lang):
    d = load(lang)
    stems = d.hunspell.stem(word)
    if stems:
        return stems[0]


def lemma(word, lang='lt'):
    u"""

    >>> print lemma(u'namo')
    namas

    >>> print lemma(u'žmoguje')
    žmogus

    >>> print lemma(u'zmogaus')
    žmogus

    >>> print lemma(u'zmogas')
    smogas

    """
    #d = load(lang)

    lemma = _get_lemma(word, lang) or _get_stem(word, lang)
    #if lemma is None:
    #    suggestions = d.hunspell.suggest(word)
    #    if suggestions:
    #        word = suggestions[0]
    #        lemma = _get_lemma(word, lang) or _get_stem(word, lang)

    return lemma or word
