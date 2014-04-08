#!/usr/bin/env python

import re
import sys

SPACES_RE = re.compile(r'(^ *)(.*?)( *$)')


def parse_comments(line):
    ending = ''
    if line.endswith('\n'):
        ending = '\n'
        line = line[:-1]

    comments = ''
    if '#' in line:
        pos = line.find('#')
        line, comments = line[:pos], line[pos:]

    (pfx, line, sfx), = SPACES_RE.findall(line)
    return pfx, line, sfx + comments + ending


def parse_rule(line, rule_id):
    if line == '@rule':
        return '@rule rule-%d' % rule_id
    else:
        return line


def parse_form(line):
    spl = line.split()
    if len(spl) == 3:
        spec, affix, ending = spl
        if ending == '$':
            return spec, '.', affix
        elif ending == '>?':
            return spec, '.', affix + '>'
    elif len(spl) == 2:
        spec, stem = spl
        return spec, stem
    raise Exception('Unknown line format: %s' % line)


def format_line(pfx, line, sfx):
    if isinstance(line, tuple):
        line = ' '.join(line)
    if sfx:
        line += '  ' + sfx
    return line.strip()


def convert_line(line):
    pfx, line, sfx = parse_comments(line)
    rule_id = 0
    if line.startswith('@'):
        rule_id += 1
        line = parse_rule(line, rule_id)
    elif line:
        line = parse_form(line)
    return format_line(pfx, line, sfx)


def main():
    input_file = sys.argv[1]
    with open(input_file) as f:
        for line in  f:
            print convert_line(line)


if __name__ == '__main__':
    main()
