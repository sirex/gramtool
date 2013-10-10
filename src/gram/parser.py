import collections
import hunspell
import re
import sys


class Parser(object):
    def __init__(self, hs, lexemes):
        self.hs = hs
        self.lexemes = lexemes
        self.encoding = hs.get_dic_encoding()
        self.irregulars_init(lexemes)

    def irregulars_init(self, lexemes):
        irregulars = collections.defaultdict(list)
        for lexeme in lexemes:
            words = set()
            affixes = lexeme.affixes or []
            for pos, affix, prefix, suffix, optional, irregular in affixes:
                if irregular and affix not in words:
                    irregulars[affix].append((pos, lexeme))
                    words.add(affix)
        self.irregulars = irregulars

    def find_suffixes(self, word):
        if word in self.irregulars:
            for pos, lexeme in self.irregulars[word]:
                yield lexeme, pos, [], word, []
        for lexeme in self.lexemes:
            if lexeme.regular:
                pos, prefixes, stem, suffixes = lexeme.split(word)
                yield lexeme, pos, prefixes, stem, suffixes

    def check_lexeme(self, lexeme, stem):
        for pos, word in lexeme.generate_words(stem):
            try:
                word = word.encode(self.encoding)
            except UnicodeEncodeError:
                return False
            if not (self.hs.spell(word) or
                    self.hs.spell(word[0].upper() + word[1:])):
                return False
        return True

    def analize(self, word):
        for lexeme, pos, prefixes, stem, suffixes in self.find_suffixes(word):
            if pos and self.check_lexeme(lexeme, stem):
                yield lexeme, pos, prefixes, stem, suffixes

    def get_lemma(self, word):
        for lexeme, pos, prefixes, stem, suffixes in self.find_suffixes(word):
            if pos and self.check_lexeme(lexeme, stem):
                for grammar, word in lexeme.generate_words(stem):
                    return word


class Lexeme(object):
    def __init__(self, key, name=''):
        self.key = key
        self.name = name
        self.affixes = []
        self.infixes = []
        self.regular = True

    def __repr__(self):
        if self.name:
            return '<Lexeme %s (%s)>' % (self.key, self.name)
        else:
            return '<Lexeme %s>' % self.key

    def get_key(self):
        return self.key

    def get_name(self):
        if self.name:
            return self.name
        else:
            return self.key

    def parse(self, spec, affix, options):
        prefix    = '^' in options
        infix     = '|' in options
        suffix    = '$' in options
        optional  = '?' in options
        irregular = '!' in options

        if '>' in options:
            infix = '>'
        elif '<' in options:
            infix = '<'
        elif '|' in options:
            infix = '|'
        else:
            infix = False

        if affix == '.':
            affix = ''

        if irregular:
            self.regular = False
        if suffix or prefix or irregular:
            self.affixes.append((spec, affix, prefix, suffix, optional, irregular))
        if infix:
            prefix = False
            suffix = False
            if infix == '<':
                prefix = True
            elif infix == '>':
                suffix = True
            elif infix == '|':
                prefix = True
                suffix = True
            self.infixes.append((spec, affix, prefix, suffix, optional))

    def feed(self, line):
        line = re.sub(r'\s+', ' ', line)
        items = line.split(' ')
        if len(items) == 2:
            spec, affix = items
            self.parse(spec, affix, '!')
        else:
            spec, affix, options = items
            self.parse(spec, affix, options)

    def merge(self, g1, g2):
        if (
            not isinstance(g1, (str, unicode)) or
            not isinstance(g2, (str, unicode))
        ):
            return g2

        pos = ''
        g1s = len(g1)
        g2s = len(g2)
        size = max(g1s, g2s)
        for i in range(size):
            if i < g2s and g2[i] != '*':
                pos += g2[i]
            elif i < g1s:
                pos += g1[i]
        return pos

    def split(self, word):
        stem = word
        suffixes = []
        prefixes = []
        pos = ''

        sort_by_len = lambda k: len(k[1])

        affixes = sorted(self.affixes, key=sort_by_len, reverse=True)
        found = False
        for spec, affix, prefix, suffix, optional, irregular in affixes:
            if prefix and stem.startswith(affix):
                if affix != '':
                    stem = stem[:-len(affix)]
                pos = self.merge(pos, spec)
                prefixes.append(affix)
                found = True

            if suffix and stem.endswith(affix):
                if affix != '':
                    stem = stem[:-len(affix)]
                pos = self.merge(pos, spec)
                suffixes.insert(0, affix)
                found = True

            if found:
                break

        infixes = sorted(self.infixes, key=sort_by_len, reverse=True)
        for spec, affix, prefix, suffix, optional in infixes:
            if prefix and stem.startswith(affix):
                if affix != '':
                    stem = stem[:-len(affix)]
                pos = self.merge(pos, spec)
                prefixes.append(affix)

            if suffix and stem.endswith(affix):
                if affix != '':
                    stem = stem[:-len(affix)]
                pos = self.merge(pos, spec)
                suffixes.insert(0, affix)

        return pos, prefixes, stem, suffixes

    def generate_infixed_words(self, stem, skip_optional=True):
        yield '', stem

        for spec, affix, prefix, suffix, optional in self.infixes:
            if optional and skip_optional: continue
            if prefix:
                yield spec, affix + stem

            if suffix:
                yield spec, stem + affix

    def generate_words(self, stem, skip_optional=True):
        for pos, stem in self.generate_infixed_words(stem, skip_optional):
            for spec, affix, prefix, suffix, optional, irregular in self.affixes:
                if optional and skip_optional: continue
                if irregular:
                    yield self.merge(spec, pos), affix
                    continue

                if prefix:
                    yield self.merge(spec, pos), affix + stem

                if suffix:
                    yield self.merge(spec, pos), stem + affix


def strip_comments(line):
    if line.startswith('#'):
        return None

    if '#' in line:
        line, comment = line.split('#', 1)
        line = line.strip()

    return line


def read_grammar(f):
    lexeme = None
    key = 0
    for line in f:
        line = line.decode('utf-8').strip()
        line = strip_comments(line)
        if not line: continue

        if line == '@rule' or line.startswith('@rule '):
            if lexeme is not None:
                yield lexeme
            name = line[5:].strip()
            lexeme = Lexeme(key, name)
            key += 1
            continue

        if lexeme is None: continue

        lexeme.feed(line)

    if lexeme is not None:
        yield lexeme


def read_hunspell_words(f, encoding):
    for i, line in enumerate(f):
        line = line.decode(encoding).strip()

        # Ignore comment
        if line.startswith('/'): continue

        # First line is number of words in dictionary
        if i == 0:
            #noflines = int(line.strip())
            continue

        word = line
        if '/' in word:
            word = word.split('/', 1)[0]

        yield word


def analize_word(grammar, word, skip_optional=True):
    for lexeme, pos, prefixes, stem, suffixes in grammar.analize(word):
        print
        for grammar, word in lexeme.generate_words(stem, skip_optional):
            print ('%s %s' % (
                grammar,
                word,
            )).encode('utf-8')


def analize_all_words(grammar, dic):
    total_words = 0
    covered_words = 0
    words_by_pos = collections.defaultdict(int)
    with open(dic) as f:
        for i, line in enumerate(f):
            line = line.decode(grammar.encoding).strip()

            # Ignore comment
            if line.startswith('/'): continue

            # First line is number of words in dictionary
            if i == 0:
                #noflines = int(line.strip())
                continue

            total_words += 1
            word = line
            if '/' in word:
                word = word.split('/', 1)[0]

            lexemes = list(grammar.analize(word))
            if len(lexemes) == 0:
                pass
                #print line.encode('utf-8')
            else:
                covered_words += 1
                lexeme, grammar, prefixes, stem, suffixes = lexemes[0]
                morphemes = '-'.join(prefixes + [stem] + suffixes)
                print ('{:8} {:24} {}'.format(grammar, morphemes, word)).encode('utf-8')
                words_by_pos[grammar[0]] += 1

            #if i > 10: break

    print
    print
    for pos, n in words_by_pos.items():
        print 'Number of {}: {:8>}'.format(pos, n)
    print 'Total coverted: ', covered_words
    print 'Total uncovered: ', total_words - covered_words
    print 'All words: ', total_words



def main():
    dic = sys.argv[1]
    aff = dic[:-3] + 'aff'
    hs = hunspell.HunSpell(dic, aff)

    with open('spec-lt') as f:
        lexemes = list(read_grammar(f))
    morph = Parser(hs, lexemes)

    if len(sys.argv) > 2:
        word = sys.argv[2].decode('utf-8')
        analize_word(morph, word, skip_optional=False)
    else:
        analize_all_words(morph, dic)


if __name__ == '__main__':
    main()
