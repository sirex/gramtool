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
            self.hs.spell(word.decode(self.encoding).title().encode(self.encoding))
        )

    def stem(self, word: str):
        assert isinstance(word, str)
        try:
            word = word.encode(self.encoding)
        except UnicodeEncodeError:
            return []
        else:
            return [w.decode(self.encoding) for w in self.hs.stem(word)]

    def suggest(self, word: str):
        assert isinstance(word, str)
        try:
            word = word.encode(self.encoding)
        except UnicodeEncodeError:
            return []
        else:
            return [w.decode(self.encoding) for w in self.hs.suggest(word)]


def get_hunspell_dict(aff, dic):
    hs = hunspell.HunSpell(dic, aff)
    return HunSpell(hs)
