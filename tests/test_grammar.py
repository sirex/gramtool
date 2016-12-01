import pytest

from gramtool import gt
from gramtool.grammar import check_spec
from gramtool.grammar import change_spec
from gramtool.grammar import get_properties


def test_check_spec():
    symbols = gt.symbols

    assert check_spec(symbols, 'nmsg', pos='noun', case='genitive') is True
    assert check_spec(symbols, 'nmsg', pos='verb', case='genitive') is False

    assert check_spec(symbols, 'nmsg', number='singular') is True
    assert check_spec(symbols, 'nmSg', number='singular') is True
    assert check_spec(symbols, 'nmsg', number='singular-only') is False
    assert check_spec(symbols, 'nmSg', number='singular-only') is True

    assert check_spec(symbols, 'nmsg', gender='masculine') is True
    assert check_spec(symbols, 'nMsg', gender='masculine') is True
    assert check_spec(symbols, 'nmsg', gender='masculine-only') is False
    assert check_spec(symbols, 'nMsg', gender='masculine-only') is True


def test_key_error():
    with pytest.raises(ValueError):
        check_spec(gt.symbols, 'nmsn', incorrect='nominative')


def test_value_error():
    with pytest.raises(ValueError):
        check_spec(gt.symbols, 'nmsn', case='incorrect')


def test_change_spec():
    change_spec(gt.symbols, 'nmsn', case='genitive') == 'nmsg'


def test_get_properties():
    assert list(get_properties(gt.symbols, 'nmsg').items()) == [
        ('pos', 'noun'),
        ('gender', 'masculine'),
        ('number', 'singular'),
        ('case', 'genitive'),
    ]


def test_get_properties_error():
    with pytest.raises(ValueError):
        get_properties(gt.symbols, '')

    with pytest.raises(ValueError):
        get_properties(gt.symbols, '?msg')

    with pytest.raises(ValueError):
        get_properties(gt.symbols, 'n')

    with pytest.raises(ValueError):
        get_properties(gt.symbols, 'n?sg')
