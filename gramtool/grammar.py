import logging

from collections import defaultdict
from collections import OrderedDict


logger = logging.getLogger(__name__)


class Form(object):
    def __init__(self, rule, spec, level, stem=None):
        self.rule = rule
        self.spec = spec
        self.prefixes = []
        self.suffixes = []
        self.level = level
        self.stem = stem

    def get_word(self, stem):
        return ''.join(self.prefixes) + (self.stem or stem) + ''.join(self.suffixes)


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
        self.stems, self.suffixes = self.create_indexes(rules)

    def find_rules(self, word):
        for rule in self.stems.get(word, []):
            yield word, '', self.rules[rule]

        for suffix, rules in self.suffixes:
            if word.endswith(suffix):
                if suffix != '':
                    stem = word[:-len(suffix)]
                for rule in rules:
                    yield stem, suffix, self.rules[rule]

    def create_indexes(self, rules):
        stems = defaultdict(list)
        suffixes = defaultdict(list)
        for key, rule in self.rules.items():
            for form in rule.forms.values():
                if form.suffixes:
                    for suffix in form.suffixes:
                        if key not in suffixes[suffix]:
                            suffixes[suffix].append(key)
                elif key not in stems[form.stem]:
                    stems[form.stem].append(key)

        sort_by_len = lambda k: len(k[0])  # noqa
        suffixes = sorted(suffixes.items(), key=sort_by_len, reverse=True)
        return stems, suffixes

    def check_spelling(self, words):
        for word in words:
            if not self.hs.spell(word):
                logger.debug("  %s is not supported by hunspell", word)
                return False
        return True

    def iter_rules(self, word):
        for stem, suffix, rule in self.find_rules(word):
            logger.debug("rule: %s", rule.name)
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

    def __str__(self):
        return self.form.get_word(self.stem)

    def __repr__(self):
        return '<Word %s (%s)>' % (
            self.form.get_word(self.stem),
            self.form.spec,
        )


def check_spec(symbols, spec, **kwargs):
    pos = symbols['pos'][spec[0]]
    properties = ['pos'] + symbols['grammar'][pos]
    for key, value in kwargs.items():
        if key in properties:
            code = spec[properties.index(key)]
            name = symbols[key][code]
            if value not in symbols[key].values():
                raise ValueError("Unknown symbol '%s' of '%s'." % (value, key))
            elif name not in (value, value + '-only'):
                return False
        elif key not in symbols:
            raise ValueError("Unknown symbol '%s'." % key)
    return True


def change_spec(symbols, spec, **kwargs):
    spec = list(spec)
    pos = symbols['pos'][spec[0]]
    properties = ['pos'] + symbols['grammar'][pos]
    for key, value in kwargs.items():
        if key in properties:
            idx = properties.index(key)
            for k, v in symbols[key].items():
                if v == value:
                    spec[idx] = k
                    break
            else:
                raise ValueError("Unknown symbol '%s' of '%s'." % (value, key))
        elif key not in symbols:
            raise ValueError("Unknown symbol '%s'." % key)
    return ''.join(spec)


def get_properties(symbols, spec):
    spec = list(spec)
    try:
        pos = symbols['pos'][spec[0]]
    except KeyError:
        raise ValueError("Unknown symbol %r of 'pos'." % spec[0])
    except IndexError:
        raise ValueError("Unknown 'pos' symbol.")
    properties = OrderedDict([('pos', pos)])
    for i, prop in enumerate(symbols['grammar'][pos], 1):
        try:
            symbol = spec[i]
        except IndexError:
            raise ValueError("Unknown %r symbol." % prop)
        try:
            value = symbols[prop][symbol]
        except KeyError:
            raise ValueError("Unknown symbol %r of %r." % (symbol, prop))
        value = value.replace('-only', '')
        properties[prop] = value
    return properties
