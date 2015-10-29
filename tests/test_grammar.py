import unittest

from gramtool import gt
from gramtool.grammar import check_spec


class CheckSpecTests(unittest.TestCase):

    def assertCheckSpecTrue(self, spec, **kwargs):
        self.assertTrue(check_spec(gt.symbols(), spec, **kwargs))

    def assertCheckSpecFalse(self, spec, **kwargs):
        self.assertFalse(check_spec(gt.symbols(), spec, **kwargs))

    def test_check_spec(self):
        self.assertCheckSpecTrue('nmsg', case='genitive')
        self.assertCheckSpecTrue('nmsg', pos='noun', case='genitive')
        self.assertCheckSpecFalse('nmsg', pos='verb', case='genitive')

        self.assertCheckSpecTrue('nmsg', number='singular')
        self.assertCheckSpecTrue('nmSg', number='singular')
        self.assertCheckSpecFalse('nmsg', number='singular-only')
        self.assertCheckSpecTrue('nmSg', number='singular-only')

        self.assertCheckSpecTrue('nmsg', gender='masculine')
        self.assertCheckSpecTrue('nMsg', gender='masculine')
        self.assertCheckSpecFalse('nmsg', gender='masculine-only')
        self.assertCheckSpecTrue('nMsg', gender='masculine-only')

    def test_key_error(self):
        self.assertRaises(ValueError, check_spec, gt.symbols(), 'nmsn', incorrect='nominative')

    def test_value_error(self):
        self.assertRaises(ValueError, check_spec, gt.symbols(), 'nmsn', case='incorrect')
