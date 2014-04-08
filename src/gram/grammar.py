from collections import defaultdict
from collections import OrderedDict


class Form(object):
    def __init__(self, rule, spec, level, stem=None):
        self.rule = rule
        self.spec = spec
        self.prefixes = []
        self.suffixes = []
        self.level = level
        self.stem = stem

    def get_word(self, stem):
        return u''.join(self.prefixes) + stem + u''.join(self.suffixes)


class Rule(object):
    def __init__(self, lineno, key, name, macro=False):
        self.lineno = lineno
        self.key = key
        self.name = name
        self.macro = macro
        self.forms = OrderedDict()
        self.includes = defaultdict(list)

    def __str__(self):
        return self.name or self.key

    def __repr__(self):
        return ('<Rule %s: "%s">' % (self.key, self.name))

    def match(self, word):
        pass

    def build_forms(self, stem):
        for form in self.forms.values():
            yield form.get_word(stem)


class Grammar(object):
    def __init__(self, hs, tree, rules):
        self.hs = hs
        self.tree = tree
        self.rules = rules
        self.suffixes = self.get_suffixes(rules)

    def find_rules(self, word):
        for suffix, rules in self.suffixes:
            if word.endswith(suffix):
                if suffix != '':
                    stem = word[:-len(suffix)]
                for rule in rules:
                    yield stem, suffix, self.rules[rule]

    def get_suffixes(self, rules):
        suffixes = defaultdict(set)
        for key, rule in self.rules.items():
            for form in rule.forms.values():
                for suffix in form.suffixes:
                    suffixes[suffix].add(key)

        sort_by_len = lambda k: len(k[0])
        suffixes = sorted(suffixes.items(), key=sort_by_len, reverse=True)
        return suffixes

    def check_spelling(self, words):
        for word in words:
            if not self.hs.spell(word):
                return False
        return True

    def iter_rules(self, word):
        for stem, suffix, rule in self.find_rules(word):
            forms = rule.build_forms(stem)
            if self.check_spelling(forms):
                lemma = None
                for form in rule.forms.values():
                    _word = form.get_word(stem)
                    if lemma is None:
                        lemma = Word(form, stem)
                    if _word == word:
                        yield lemma, Word(form, stem)


class Word(object):
    def __init__(self, form, stem):
        self.form = form
        self.stem = stem

    def __unicode__(self):
        return self.form.get_word(self.stem)

    def __repr__(self):
        return u'<Word %s (%s)>' % (
            self.form.get_word(self.stem),
            self.form.spec,
        )


