import pathlib
import argparse
import pkg_resources as pres

from gramtool.views import print_forms, print_all_forms
from gramtool.exceptions import UserSideError

import gramtool


def main():
    data_dir = pres.resource_filename('gramtool', 'data')

    parser = argparse.ArgumentParser()
    parser.add_argument('word', type=str, help="A lexeme from morphology database.")
    parser.add_argument('-d', '--data-dir', type=str, default=data_dir, help="Data directory.")
    parser.add_argument('-l', '--lang', type=str, default='lt', help="Two letter language code [default: lt].")
    parser.add_argument('-f', '--forms', action='store_true', default=False, help="Print all <word> forms.")

    parser.add_argument('--case', type=str, default=None, help="Change case of given <word>.")

    args = parser.parse_args()

    gs = gramtool.GramTool(pathlib.Path(args.data_dir), args.lang)

    try:
        gt = gramtool.GramTool(pathlib.Path(args.data_dir), args.lang)
    except UserSideError as e:
        print(e)
        return 1

    change_form_kwargs = {
        'case': args.case,
    }
    change_form_kwargs = {k: v for k, v in change_form_kwargs.items() if v}

    if change_form_kwargs:
        print(gramtool.change_form(args.word, **change_form_kwargs))
    else:
        print_forms(gt.grammar, args.word)
        if args.forms:
            print_all_forms(gt.grammar, args.word)
