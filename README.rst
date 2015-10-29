gramtool - a Python library for morphological analysis.

Main purpose of this library is to identify given phrase and provide all
information about that phrase, its grammatical category, part of speech, used
affixes and etc.


Installing
==========

On Ubuntu 12.04::

    $ sudo apt-get install python-dev libhunspell-dev
    $ pip install gramtool


Using command line
==================

::

    $ gramtool žodžiuose
    žodžiuose [nmpl] -> žodis
    žodžiuose [nmsl] -> žodžiai

    Masculine dis (medis)
      [nmsn] žodis
      [nmsg] žodžio
      [nmsd] žodžiui
      [nmsa] žodį
      [nmsi] žodžiu
      [nmsl] žodyje
      [nmpn] žodžiai
      [nmpg] žodžių
      [nmpd] žodžiams
      [nmpa] žodžius
      [nmpi] žodžiais
      [nmpl] žodžiuose

    AI Miltai only plural
      [nmsn] žodžiai
      [nmsg] žodžių
      [nmsd] žodžiams
      [nmsa] žodžius
      [nmsi] žodžiais
      [nmsl] žodžiuose

    $ gramtool žmogus --case=locative
    žmoguje


Using library
=============

Find word lemma
---------------

.. code-block:: python

    assert gramtool.get_lemma('žodžiai') == 'žodis'


Get different grammatical form
------------------------------

.. code-block:: python

    assert gramtool.change_form('dėžė', case='locative') == 'dėžėje'


How it works?
=============

gramtool uses Hunspell dictionaries and grammar files to define grammars for
each language.

For a language these files are used:

``grammar.yaml``
    Defines grammatical category.

``grammar``
    Defines morphological structure, using ``grammar.yaml``.

``hunspell.aff``, ``hunspell.dic``
    Dictionaries, that defines all possible correct word forms.


gramtool takes a word, then tries to find best match from ``grammar`` file,
identifying all possible word form variants. Then using Hunspell spell checker,
for each matching grammar rule, all forms are generated. Only those rules, that
passes spell checking for all generated forms are considered as correct rules
for that given word.


Defining new grammars
=====================

To define new grammar for a language, first you need to define all grammar
parts in ``grammar.yaml`` file. All defined symbols must be compatible with
general, language independed ``grammar.yaml`` file. General ``grammar.yaml`` is
used to connect all defined rules between all languages, for example, Noun,
should be known as Noun in all languages.

Second thing, you need to do is describing morphological structure. This you
need to put in ``grammar`` file.

Here is a simples ``grammar`` file example::

    @rule nouns
    ns . .
    np . s

This file defines english noun. ``@rule nouns`` opens new rule, all lines
below, untile next rule or macro definition belongs to this rule.

Second line from example above::

    ns . .

Tells, that ``n`` - noun, ``s`` - singulare, ``.`` - does not have any prefixes
and ``.`` - does not have any suffixes.

Third line::

    np . s

Tells that plural form of a noun must be appended with ``s`` suffix.

So in as you probably understood, each rule line consists of:

* grammatical form specification, using symbols taken from ``grammar.yaml``
  file, I will call in gram-spec

* prefix part

* suffix part.

Lets take a look at an example with english verbs::

    @macro verb
    xs1   .      .    # I
    xs2   .      .    # you
    xs3   .      .    # he
    xp1   .      .    # we
    xp2   .      .    # you
    xp3   .      .    # they

    @macro verb-s
    xs1   .      .    # I
    xs2   .      .    # you
    xs3   .      s    # he
    xp1   .      .    # we
    xp2   .      .    # you
    xp3   .      .    # they

    @macro verb-am
    xs1   am+    .    # I
    xs2   are+   .    # you
    xs3   is+    .    # he
    xp1   are+   .    # we
    xp2   are+   .    # you
    xp3   are+   .    # they

    @macro verb-was
    xs1   was+   .    # I
    xs2   where+ .    # you
    xs3   was+   .    # he
    xp1   where+ .    # we
    xp2   where+ .    # you
    xp3   where+ .    # they

    @macro verb-have
    xs1   have+  .    # I
    xs2   have+  .    # you
    xs3   has+   .    # he
    xp1   have+  .    # we
    xp2   have+  .    # you
    xp3   have+  .    # they

    @rule regular-verbs
    + verb-s     ***p    .           .
    + verb-am    ***pc   .           ing
    + verb       ***ss   .           ed
    + verb-was   ***sc   .           ing
    + verb-have  ***pp   .           ed
    + verb-have  ***ppc  been+       .
    + verb       ***sp   had+        ed
    + verb       ***spc  had+been+   ed
    + verb       ***f    will+       .
    + verb       ***fc   will+be+    ing
    + verb       ***fp   will+have+  ed
    + verb       ***p-C  would+      .

Here we have many new things. First of all we see five macros: ``verb``,
``verb-s``, ``verb-am``, ``verb-was``, ``verb-have``. Macros are used to be
included into other rules. Also it is possible to include macro into macro,
rule into rule.

Here is example, how a macro is included::

    + verb-s     ***p    .           .

In this example, macro ``verb-s`` will be included into rule ``regular-verbs``.
It means, that all lines, defined in ``verb-s``, will be included into
``regular-verbs`` rule. Also, ``***p`` parameter specifies, that during
inclusion, all gram-specs from ``verb-s`` will be replaced with forth letter to
become ``p``.

Also, when including, specified prefixes and suffixes will be prepended with
specified affixes in inclusion parameters.

You can include not only specified macro or rule, by name, but it is also
possible to include same rule again or parent rule from a macro. Also it is
possible to specify a filter, that tells what lines will be included.


Grammar file reference
======================

Starting a rule or macro:

``@rule <name>``
    Start new rule.

``@macro <name>``
    Start new macro. Macros will net be used when generating word forms, macros
    can only be included into other rules.

Both, rules and macros can contain same lines, specifying possible word forms.
Word form line can be defined in these forms:

``<spec> <stem>``
    This form is used to define irregular word forms, when stem is not same for
    all other forms, for example, words go and went have different stems.

``<spec> <prefix> <suffix>``
    This form is used to define regular word forms.

Both, rules and macros can contain includes:

``+[<level>] <name>``
    Simple include form. Just includes all lines from rule or macro named with
    ``<name>``.

    ``<name>`` has several special symbols:

    ``.`` - include self lines.

    ``@`` - include top most rule lines.

    Optional level is a number that restricts included lines to only those with
    lower inclusion level. Inclusion level is assigned to each line when
    inclusio is performed. Each line after inclusion has level as specified in
    ``+[<level>]``.

``+[<level>] <name> <spec> <prefix> <suffix>``
    Same as above, but all included lines will be extended with ``<spec>`` and
    specified ``<prefix>`` and ``<suffix>`` will be prepended to prefixes and
    suffixes of included line.

``+[<level>] <name> <spec> <prefix> <suffix> <filter>``
    Same as above, but will be included only lines, whose ``<spec>`` will match
    specified ``<filter>``.
