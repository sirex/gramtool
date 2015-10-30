import functools
import pathlib
import pkg_resources as pres

from gramtool.parser import get_grammar_rules
from gramtool.utils.grammar import get_grammar_tree, get_frequency_list
from gramtool.grammar import Grammar, change_spec
from gramtool.hunspell import get_hunspell_dict


class GramTool(object):

    def __init__(self, data_dir: pathlib.Path=None, language='lt'):
        self.data_dir = data_dir or pathlib.Path(pres.resource_filename('gramtool', 'data'))
        self.language = language

    @functools.lru_cache()
    def hunspell(self):
        hunspell_dic_file = self.data_dir / self.language / 'hunspell.dic'
        hunspell_aff_file = self.data_dir / self.language / 'hunspell.aff'
        return get_hunspell_dict(str(hunspell_aff_file), str(hunspell_dic_file))

    @functools.lru_cache()
    def symbols(self):
        grammar_file = self.data_dir / 'grammar.yaml'
        return get_grammar_tree(str(grammar_file))

    @functools.lru_cache()
    def grammar(self):
        symbols = self.symbols()
        rules_file = self.data_dir / self.language / 'grammar'
        rules = get_grammar_rules(symbols, str(rules_file))
        return Grammar(self.hunspell(), symbols, rules)

    @functools.lru_cache()
    def frequency(self):
        frequency_file = self.data_dir / self.language / 'frequency'
        return get_frequency_list(str(frequency_file))

    def _get_word_lemma(self, word):
        result = []
        frequency = self.frequency()
        for lemma, lexeme in self.grammar().iter_rules(word):
            lemma = str(lemma)
            try:
                index = frequency.index(lemma)
            except ValueError:
                index = float('inf')
            result.append((index, lemma))

        for index, lemma in sorted(result):
            return lemma

    def get_lemma(self, phrase):
        words = phrase.split()
        lemma = self._get_word_lemma(words[-1])
        if lemma:
            return ' '.join(words[:-1] + [lemma])
        else:
            return None

    def change_form(self, word, **kwargs):
        spec = None
        candidates = {}
        grammar = self.grammar()
        symbols = self.symbols()
        for stem, suffix, rule in grammar.find_rules(word):
            forms = rule.build_forms(stem)
            if grammar.check_spelling(forms):
                for form in rule.forms.values():
                    candidate = form.get_word(stem)
                    if word == candidate:
                        spec = form.spec
                    candidates[form.spec.lower()] = candidate
                if spec:
                    return candidates[change_spec(symbols, spec, **kwargs).lower()]


gt = GramTool()
get_lemma = gt.get_lemma
change_form = gt.change_form
