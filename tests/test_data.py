import gramtool


def test_lemma():
    gramtool.get_lemma('Vilnius') == 'Vilnius'
    gramtool.get_lemma('Vilnių') == 'Vilnius'
    gramtool.get_lemma('Vilniaus') == 'Vilnius'
    gramtool.get_lemma('Vilniui') == 'Vilnius'
    gramtool.get_lemma('Vilniuje') == 'Vilnius'
    gramtool.get_lemma('Vilniau') == 'Vilnius'


def test_suo():
    gramtool.get_lemma('šunį') == 'šuo'


def test_phrase():
    gramtool.get_lemma('Šiaulių banko') == 'Šiaulių bankas'


def test_change_form():
    gramtool.change_form('Vilnius', case='genitive') == 'Vilniaus'
    gramtool.change_form('žmogus', case='locative') == 'žmoguje'
    gramtool.change_form('medis', case='accusative', number='plural') == 'medžius'
    gramtool.change_form('kairėje', case='nominative') == 'kairė'
    gramtool.change_form('šuo', case='accusative') == 'šunį'
    gramtool.change_form('pelėse', case='accusative') == 'peles'
    gramtool.change_form('krūmai', case='locative') == 'krūmuose'
