import yaml


class GrammarSyntaxError(Exception):
    def __init__(self, parser, lineno, message):
        self.parser = parser
        self.lineno = lineno
        self.message = message
        message = 'Error in %s:%d: %s' % (parser.filename, lineno, message)
        super(GrammarSyntaxError, self).__init__(None, message)

    def format_error(self):
        return '\n'.join([
            'Error detected in this grammar file:',
            '',
            '  %s:%d' % (self.parser.filename, self.lineno),
            '',
            self.message,
        ])


def validate_rule(parser, rule, key):
    if key in parser.rules:
        duplicate = parser.rules[key]
        raise GrammarSyntaxError(parser, rule.lineno, (
            'rules with name "%s" already defined in %d line.'
        ) % (key, duplicate.lineno))


def validate_pos(parser, lineno, line, spec):
    pos = spec[0]
    if pos not in parser.tree['pos']:
        raise GrammarSyntaxError(parser, lineno, (
            'unknown part of speech "%s" in "%s", available options are: %s'
        ) % (pos, line, yaml.dump(parser.tree['pos'])))


def validate_props(parser, lineno, line, props, spec, pos_name):
    if len(props) < len(spec)-1:
        print(props)
        print(spec)
        print(len(props), len(spec)-1)
        raise GrammarSyntaxError(parser, lineno, (
            '%s has %d grammatical categories, but "%s" provides %d.\n\n'
            'You need to remove extra grammatical categories.'
        ) % (pos_name, len(props), line, len(spec)-1))


def validate_symbols(parser, lineno, line, props, spec, pos_name):
    special_symbols = set('-*?')
    for i, prop in enumerate(props, 1):
        if spec[i] in special_symbols:
            continue
        if spec[i] not in parser.tree[prop]:
            options = yaml.dump(parser.tree[prop], default_flow_style=False)
            raise GrammarSyntaxError(parser, lineno, (
                '"%s" in %s position is not valid value for %s %s, '
                'specified in "%s".\n\n'
                '%s %s possible options are these:\n\n%s'
            ) % (spec[i], i+1, pos_name, prop, line, pos_name, prop, options))


def validate_spec(parser, lineno, line, spec, name, props):
    line = ' '.join(line.split())
    validate_pos(parser, lineno, line, spec)
    validate_props(parser, lineno, line, props, spec, name)
    validate_symbols(parser, lineno, line, props, spec, name)
