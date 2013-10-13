from __future__ import absolute_import

import hunspell


class HunSpell(hunspell.HunSpell):
    def __init__(self, hs):
        self.hs = hs
        self.encoding = hs.get_dic_encoding()

    def spell(self, word):
        try:
            word = word.encode(self.encoding)
        except UnicodeEncodeError:
            return False
        return (
            self.hs.spell(word) or
            self.hs.spell(word[0].upper() + word[1:])
        )

def get_hunspell_dict(aff, dic):
    hs =  hunspell.HunSpell(dic, aff)
    return HunSpell(hs)
