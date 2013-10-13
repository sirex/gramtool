def print_grammar(grammar):
    for key, rule in grammar.rules.items():
        print ('@rule %s' % key).encode('utf-8')
        for form in rule.forms.values():
            word = '-'.join(form.prefixes + ['(stem)'] + form.suffixes)
            word = ''.join(form.prefixes + ['v'] + form.suffixes)
            print ' '.join([form.spec, word]).encode('utf-8')
        print


def print_forms(grammar, word):
    print word
    import pprint ; pprint.pprint(list(grammar.boo(word)))
