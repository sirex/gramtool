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
        self.symbols = get_grammar_tree(str(self.data_dir / 'grammar.yaml'))
        self.hunspell = self._get_hunspell()
        self.frequency = get_frequency_list(str(self.data_dir / self.language / 'frequency'))
        self.grammar = self._get_grammar()

    def _get_hunspell(self):
        hunspell_dic_file = self.data_dir / self.language / 'hunspell.dic'
        hunspell_aff_file = self.data_dir / self.language / 'hunspell.aff'
        return get_hunspell_dict(str(hunspell_aff_file), str(hunspell_dic_file))

    def _get_grammar(self):
        rules_file = self.data_dir / self.language / 'grammar'
        rules = get_grammar_rules(self.symbols, str(rules_file))
        return Grammar(self.hunspell, self.symbols, rules)

    def _get_word_lemma(self, word):
        result = []
        for lemma, lexeme in self.grammar.iter_rules(word):
            lemma = str(lemma)
            try:
                index = self.frequency.index(lemma)
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
        for stem, suffix, rule in self.grammar.find_rules(word):
            forms = rule.build_forms(stem)
            if self.grammar.check_spelling(forms):
                for form in rule.forms.values():
                    candidate = form.get_word(stem)
                    if word == candidate:
                        spec = form.spec
                    candidates[form.spec.lower()] = candidate
                if spec:
                    return candidates[change_spec(self.symbols, spec, **kwargs).lower()]


gt = GramTool()
get_lemma = gt.get_lemma
change_form = gt.change_form
