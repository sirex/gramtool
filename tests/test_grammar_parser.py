import unittest

from io import StringIO

from gramtool.parser import Parser
from gramtool.grammar import Grammar


class FakeHunspell(object):
    pass


def get_all_forms(grammar, stem='(stem)'):
    lines = []
    for key, rule in grammar.rules.items():
        lines.append('@rule %s' % key)
        for form in rule.forms.values():
            if form.spec.startswith('%'):
                continue
            word = '-'.join(form.prefixes + [form.stem or stem] + form.suffixes)
            word = word.replace('+-', ' ').replace('-+', ' ').replace('+', ' ')
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

    def test_levels_macro(self):
        self.assertMultiLineEqual(*genforms('''
        @macro prefixes
        +  @ xn     ne .  x***-
        +1 @ x*b    is .  x***-
        +1 @ x**p   su .  x***-

        @rule galvoti
        x     . ti
        x---s . tis
        +* prefixes
        +2 . ****s <si . !x---*

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

    def test_english_verbs(self):
        self.maxDiff = None
        self.assertMultiLineEqual(*genforms('''
        @macro empty
        xs1   .      .    # I
        xs2   .      .    # you
        xs3   .      .    # he
        xp1   .      .    # we
        xp2   .      .    # you
        xp3   .      .    # they

        @macro s
        xs1   .      .    # I
        xs2   .      .    # you
        xs3   .      s    # he
        xp1   .      .    # we
        xp2   .      .    # you
        xp3   .      .    # they

        @macro am
        xs1   am+    .    # I
        xs2   are+   .    # you
        xs3   is+    .    # he
        xp1   are+   .    # we
        xp2   are+   .    # you
        xp3   are+   .    # they

        @macro was
        xs1   was+   .    # I
        xs2   where+ .    # you
        xs3   was+   .    # he
        xp1   where+ .    # we
        xp2   where+ .    # you
        xp3   where+ .    # they

        @macro have
        xs1   have+  .    # I
        xs2   have+  .    # you
        xs3   has+   .    # he
        xp1   have+  .    # we
        xp2   have+  .    # you
        xp3   have+  .    # they

        @rule regular-verbs
        + s     ***p    .           .
        + am    ***pc   .           ing
        + empty ***ss   .           ed
        + was   ***sc   .           ing
        + have  ***pp   .           ed
        + have  ***ppc  been+       .
        + empty ***sp   had+        ed
        + empty ***spc  had+been+   ed
        + empty ***f    will+       .
        + empty ***fc   will+be+    ing
        + empty ***fp   will+have+  ed
        + empty ***p-C  would+      .

        @macro irregular-verb
        # Present
        + @     xs1p    .           .   %xs1p
        + @     xs2p    .           .   %xs1p
        + @     xs3p    .           .   %xs3p
        + @     xp1p    .           .   %xs1p
        + @     xp2p    .           .   %xs1p
        + @     xp3p    .           .   %xs1p

        # Present continuous
        + @     xs1pc   am+         .   %xs1pc
        + @     xs2pc   are+        .   %xs1pc
        + @     xs3pc   is+         .   %xs1pc
        + @     xp1pc   are+        .   %xs1pc
        + @     xp2pc   are+        .   %xs1pc
        + @     xp3pc   are+        .   %xs1pc

        # Simple past
        + @     xs1ss   .           .   %xs1ss
        + @     xs2ss   .           .   %xs1ss
        + @     xs3ss   .           .   %xs1ss
        + @     xp1ss   .           .   %xs1ss
        + @     xp2ss   .           .   %xs1ss
        + @     xp3ss   .           .   %xs1ss

        # Past continuous
        + @     xs1sc   was+        .   %xs1pc
        + @     xs2sc   were+       .   %xs1pc
        + @     xs3sc   was+        .   %xs1pc
        + @     xp1sc   were+       .   %xs1pc
        + @     xp2sc   were+       .   %xs1pc
        + @     xp3sc   were+       .   %xs1pc

        # Present perfect
        + @     xs1pp   have+       .   %xs1pp
        + @     xs2pp   have+       .   %xs1pp
        + @     xs3pp   has+        .   %xs1pp
        + @     xp1pp   have+       .   %xs1pp
        + @     xp2pp   have+       .   %xs1pp
        + @     xp3pp   have+       .   %xs1pp

        @rule   go
        %xs1p   go
        %xs3p   goes
        %xs1pc  going
        %xs1ss  went
        %xs1pp  gone

        +* irregular-verb

        --------------------------------
        @rule regular-verbs
        xs1p-- learn
        xs2p-- learn
        xs3p-- learn-s
        xp1p-- learn
        xp2p-- learn
        xp3p-- learn
        xs1pc- am learn-ing
        xs2pc- are learn-ing
        xs3pc- is learn-ing
        xp1pc- are learn-ing
        xp2pc- are learn-ing
        xp3pc- are learn-ing
        xs1ss- learn-ed
        xs2ss- learn-ed
        xs3ss- learn-ed
        xp1ss- learn-ed
        xp2ss- learn-ed
        xp3ss- learn-ed
        xs1sc- was learn-ing
        xs2sc- where learn-ing
        xs3sc- was learn-ing
        xp1sc- where learn-ing
        xp2sc- where learn-ing
        xp3sc- where learn-ing
        xs1pp- have learn-ed
        xs2pp- have learn-ed
        xs3pp- has learn-ed
        xp1pp- have learn-ed
        xp2pp- have learn-ed
        xp3pp- have learn-ed
        xs1ppc have been learn
        xs2ppc have been learn
        xs3ppc has been learn
        xp1ppc have been learn
        xp2ppc have been learn
        xp3ppc have been learn
        xs1sp- had learn-ed
        xs2sp- had learn-ed
        xs3sp- had learn-ed
        xp1sp- had learn-ed
        xp2sp- had learn-ed
        xp3sp- had learn-ed
        xs1spc had been learn-ed
        xs2spc had been learn-ed
        xs3spc had been learn-ed
        xp1spc had been learn-ed
        xp2spc had been learn-ed
        xp3spc had been learn-ed
        xs1f-- will learn
        xs2f-- will learn
        xs3f-- will learn
        xp1f-- will learn
        xp2f-- will learn
        xp3f-- will learn
        xs1fc- will be learn-ing
        xs2fc- will be learn-ing
        xs3fc- will be learn-ing
        xp1fc- will be learn-ing
        xp2fc- will be learn-ing
        xp3fc- will be learn-ing
        xs1fp- will have learn-ed
        xs2fp- will have learn-ed
        xs3fp- will have learn-ed
        xp1fp- will have learn-ed
        xp2fp- will have learn-ed
        xp3fp- will have learn-ed
        xs1p-C would learn
        xs2p-C would learn
        xs3p-C would learn
        xp1p-C would learn
        xp2p-C would learn
        xp3p-C would learn

        @rule go
        xs1p-- go
        xs2p-- go
        xs3p-- goes
        xp1p-- go
        xp2p-- go
        xp3p-- go
        xs1pc- am going
        xs2pc- are going
        xs3pc- is going
        xp1pc- are going
        xp2pc- are going
        xp3pc- are going
        xs1ss- went
        xs2ss- went
        xs3ss- went
        xp1ss- went
        xp2ss- went
        xp3ss- went
        xs1sc- was going
        xs2sc- were going
        xs3sc- was going
        xp1sc- were going
        xp2sc- were going
        xp3sc- were going
        xs1pp- have gone
        xs2pp- have gone
        xs3pp- has gone
        xp1pp- have gone
        xp2pp- have gone
        xp3pp- have gone

        ''', 'learn'))
