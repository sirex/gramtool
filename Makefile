CONFIGS = \
  buildout.cfg \
  setup.py


.PHONY: all
all: bin/gram


bin/gram: bin/buildout $(CONFIGS)
	bin/buildout
	touch -c $@


bin/buildout: bin/python
	bin/python bootstrap.py --version=2.2.1 --distribute


bin/python:
	virtualenv --distribute --no-site-packages .
	bin/pip install distribute --upgrade


.PHONY: clean
clean:
	rm -r bin include lib local develop-eggs parts


.PHONY: tags
tags: all
	bin/ctags -v
