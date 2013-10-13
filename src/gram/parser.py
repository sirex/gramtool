from collections import OrderedDict
from collections import defaultdict

from .grammar import Form
from .grammar import Rule
from .validator import GrammarSyntaxError
from .validator import validate_rule
from .validator import validate_spec
from .exceptions import UserSideError


class Parser(object):
    def __init__(self, tree, strict=True):
        self.tree = tree
        self.rule_id = 0
        self.rule = None
        self.rules = OrderedDict()
        self.lines = []
        self.filename = None
        self.includes = defaultdict(list)
        self.max_include_level = 0
        self.strict = strict

    def strip_comments(self, line):
        if line.startswith('#'):
            return None

        if '#' in line:
            line, comment = line.split('#', 1)
            line = line.strip()

        return line

    def open_rule(self, lineno, line):
        if line.startswith('@rule'):
            macro = False
            name = line[len('@rule'):].strip()
        else:
            macro = True
            name = line[len('@macro'):].strip()
        self.rule_id += 1
        self.rule = Rule(lineno, self.rule_id, name, macro)

    def close_rule(self):
        if self.rule is not None:
            key = self.rule.name or self.rule.key
            validate_rule(self, self.rule, key)
            self.rules[key] = self.rule

    def parse_spec(self, spec):
        pos = spec[0]
        if pos == '*': return spec, None, None
        name = self.tree['pos'][pos]
        if name in self.tree['grammar']:
            props = self.tree['grammar'][name]
        else:
            props = []

        if len(props) > len(spec)-1:
            spec += '-' * (len(props) - (len(spec)-1))
        return spec, name, props

    def add_form(self, lineno, line, rule, spec, prefixes, suffixes, level, stem=None):
        spec, name, props = self.parse_spec(spec)
        if self.strict and name is not None:
            validate_spec(self, lineno, line, spec, name, props)

        if spec in rule.forms:
            raise GrammarSyntaxError(self, lineno,
                'this form "%s" is already defined' % spec
            )

        form = Form(rule, spec, level, stem)

        for prefix in prefixes:
            prefix = '' if prefix == '.' else prefix
            if prefix.startswith('<'):
                if len(form.prefixes) > 0:
                    form.prefixes.append(prefix[1:])
            elif prefix:
                form.prefixes.append(prefix)

        for suffix in reversed(suffixes):
            suffix = '' if suffix == '.' else suffix
            if suffix.endswith('>'):
                suffix = suffix[:-1]
                if len(form.suffixes) > 0:
                    form.suffixes.insert(0, suffix)
            elif suffix:
                form.suffixes.insert(0, suffix)
        rule.forms[spec] = form


    def parse_form(self, lineno, line):
        tokens = line.split()
        if len(tokens) == 3:
            spec, prefix, suffix = tokens
            stem = None
        elif len(tokens) == 2:
            spec, stem = tokens
            prefix = suffix = ''
        else:
            raise GrammarSyntaxError(self, lineno,
                'invalid rule form "%s"' % line
            )

        self.add_form(lineno, line, self.rule, spec, (prefix,), (suffix,), 0, stem)

    def parse_include(self, lineno, line):
        tokens = line.split()
        if len(tokens) == 2:
            level, key = tokens
            spec = '*'
            prefix = ''
            suffix = ''
            fltr = '*'
        elif len(tokens) == 5:
            level, key, spec, prefix, suffix = tokens
            fltr = '*'
        elif len(tokens) == 6:
            level, key, spec, prefix, suffix, fltr = tokens
        else:
            raise GrammarSyntaxError(self, lineno, 'invalid include "%s"' % line)

        if self.rule is None:
            includes = self.includes
        else:
            includes = self.rule.includes

        level = 0 if level == '+' else level[1:]
        if level != '*':
            level = int(level)
            self.max_include_level = max(self.max_include_level, level)

        includes[level].append((
            lineno, line, key, spec, prefix, suffix, fltr
        ))

    def match_spec(self, fltr, spec):
        if fltr.startswith('!'):
            fltr = fltr[1:]
            match = False
        else:
            match = True
        if len(fltr) > len(spec):
            return not match
        for i, f in enumerate(fltr):
            if f == '*': continue
            if f != spec[i]:
                return not match
        return match

    def extend_spec(self, lineno, base, extension):
        if extension == '*':
            return base

        blen = len(base)
        elen = len(extension)

        if blen > elen:
            extension += '*' * (blen-elen)
        elif blen < elen:
            base += '*' * (elen-blen)

        return ''.join([
            b if extension[i] == '*' else extension[i]
            for i, b in enumerate(base)
        ])

    def get_include(self, lineno, key, rule, stack):
        if key not in self.rules:
            raise GrammarSyntaxError(self, lineno,
                'Specified include name "%s" is not defined.' % key
            )

        include = self.rules[key]

        if include.key in stack:
            raise GrammarSyntaxError(self, lineno,
                'Circular include detected, while processing %s' % rule
            )

        return include


    def process_rule_includes(self,
            rule, slevel, node=None, sspec='*', sprefixes=None, ssuffixes=None,
            sfltr='*', nstack=None
        ):
        node = node or rule
        sprefixes = sprefixes or tuple()
        ssuffixes = ssuffixes or tuple()
        nstack = nstack or tuple()
        if isinstance(slevel, tuple):
            slevel = slevel[0]
            includes = node.includes['*']
        elif slevel in node.includes:
            includes = node.includes[slevel]
        else:
            includes = []
        level = slevel + 1
        for lineno, line, key, spec, prefix, suffix, fltr in includes:
            prefixes = (prefix,) + sprefixes
            suffixes = ssuffixes + (suffix,)

            if key == '.':
                include = node
            elif key == '@':
                include = rule
            else:
                include = self.get_include(lineno, key, node, nstack)

            nspec = self.extend_spec(lineno, sspec, spec)
            nfltr = self.extend_spec(lineno, sfltr, fltr)
            for form in include.forms.values():
                if form.level < level and self.match_spec(nfltr, form.spec):
                    newspec = self.extend_spec(lineno, form.spec, nspec)
                    prefs = tuple(form.prefixes) + prefixes
                    suffs = suffixes + tuple(form.suffixes)
                    self.add_form(lineno, line, rule, newspec, prefs, suffs, level)

            if key not in ('.', '@'):
                stack = nstack + (include.key,)
                self.process_rule_includes(
                    rule, slevel, include, nspec, prefixes, suffixes, nfltr,
                    stack
                )
                self.process_rule_includes(
                    rule, (slevel, '*'), include, nspec, prefixes, suffixes,
                    nfltr, stack
                )

    def process_includes(self):
        rules = OrderedDict()
        for key, rule in self.rules.items():
            if not rule.macro:
                rules[key] = rule

        for level in range(self.max_include_level+1):
            for key, rule in rules.items():
                self.process_rule_includes(rule, level)
                self.process_rule_includes(rule, (level, '*'))
        return rules

    def parse(self, f, filename):
        self.filename = filename
        for lineno, line in enumerate(f, 1):
            line = line.decode('utf-8').strip()
            self.lines.append(line)
            line = self.strip_comments(line)
            if not line: continue

            if (
                line == '@rule' or line.startswith('@rule ') or
                line == '@macro' or line.startswith('@macro ')
            ):
                self.close_rule()
                self.open_rule(lineno, line)
            else:
                if line.startswith('+'):
                    self.parse_include(lineno, line)
                else:
                    self.parse_form(lineno, line)

        self.close_rule()
        return self.process_includes()


def get_grammar_rules(tree, filename):
    parser = Parser(tree)
    with open(filename) as f:
        try:
            return parser.parse(f, filename)
        except GrammarSyntaxError as e:
            raise UserSideError(e.format_error())
