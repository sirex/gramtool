import unittest

from StringIO import StringIO

from .parser import Parser
from .grammar import Grammar


class FakeHunspell(object):
    pass


def get_all_forms(grammar, stem='(stem)'):
    lines = []
    for key, rule in grammar.rules.items():
        lines.append('@rule %s' % key)
        for form in rule.forms.values():
            word = '-'.join(form.prefixes + [stem] + form.suffixes)
            lines.append(' '.join([form.spec, word]))
        lines.append('')
    return '\n'.join(lines)


def strip(s):
    return '\n'.join([line.strip() for line in s.strip().splitlines()])


def genforms(s, stem='(stem)', strict=False, tree=None):
    tree = tree or {
        'pos': {'x': 'fake'},
        'grammar': {'fake': ['a', 'b', 'c', 'd', 'e']}
    }
    parser = Parser(tree, strict=strict)
    rules, expected_output = s.split('--------------------------------', 1)
    rules = parser.parse(StringIO(strip(rules)), 'rules.gram')
    hunspell = FakeHunspell()
    grammar = Grammar(hunspell, tree, rules)
    forms = get_all_forms(grammar, stem)
    print '-' * 72
    print strip(forms)
    print '-' * 72
    return strip(forms), strip(expected_output)


class MyTest(unittest.TestCase):
    def test_rule_include(self):
        self.assertMultiLineEqual(*genforms('''
        @rule a
        xa . as

        @rule b
        xb . is
        + a

        @rule c
        + b x*c . z>
        x-c . os

        --------------------------------
        @rule a
        xa---- (stem)-as

        @rule b
        xb---- (stem)-is
        xa---- (stem)-as

        @rule c
        x-c--- (stem)-os
        xbc--- (stem)-z-is
        xac--- (stem)-z-as

        '''))

    def test_macro_include(self):
        self.assertMultiLineEqual(*genforms('''
        @macro a
        xa . as

        @macro b
        xb . is
        + a

        @rule c
        + b x*c . z>
        x-c . os

        --------------------------------
        @rule c
        x-c--- (stem)-os
        xbc--- (stem)-z-is
        xac--- (stem)-z-as

        '''))

    def test_levels(self):
        self.assertMultiLineEqual(*genforms('''
        @rule galvoti
        x     . ti
        x---s . tis
        +  . xn     ne .  x***-
        +1 . x*b    is .  x***-
        +1 . x**p   su .  x***-
        +2 . x***s <si . !x---*

        --------------------------------
        @rule galvoti
        x----- galvo-ti
        x---s- galvo-tis
        xn---- ne-galvo-ti
        x-b--- is-galvo-ti
        xnb--- ne-is-galvo-ti
        x--p-- su-galvo-ti
        xn-p-- ne-su-galvo-ti
        xn--s- ne-si-galvo-ti
        x-b-s- is-si-galvo-ti
        xnb-s- ne-is-si-galvo-ti
        x--ps- su-si-galvo-ti
        xn-ps- ne-su-si-galvo-ti

        ''', 'galvo'))
