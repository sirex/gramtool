import unittest

import gramtool


class LemmaTests(unittest.TestCase):

    def assertLemma(self, word, lemma):
        self.assertEqual(gramtool.get_lemma(word), lemma)

    def test_lemma(self):
        self.assertLemma('Vilnius', 'Vilnius')
        self.assertLemma('Vilnių', 'Vilnius')
        self.assertLemma('Vilniaus', 'Vilnius')
        self.assertLemma('Vilniui', 'Vilnius')
        self.assertLemma('Vilniuje', 'Vilnius')
        self.assertLemma('Vilniau', 'Vilnius')

    def test_suo(self):
        self.assertLemma('šunį', 'šuo')

    def test_phrase(self):
        self.assertLemma('Šiaulių banko', 'Šiaulių bankas')


class ChangeFormTests(unittest.TestCase):

    def test_change_form(self):
        self.assertEqual(gramtool.change_form('Vilnius', case='genitive'), 'Vilniaus')
        self.assertEqual(gramtool.change_form('žmogus', case='locative'), 'žmoguje')
        self.assertEqual(gramtool.change_form('medis', case='accusative', number='plural'), 'medžius')
        self.assertEqual(gramtool.change_form('kairėje', case='nominative'), 'kairė')
        self.assertEqual(gramtool.change_form('šuo', case='accusative'), 'šunį')
        self.assertEqual(gramtool.change_form('pelėse', case='accusative'), 'peles')
        self.assertEqual(gramtool.change_form('krūmai', case='locative'), 'krūmuose')
