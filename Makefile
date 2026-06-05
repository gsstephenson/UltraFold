# UltraFold developer tasks. The reference implementation is Python 2.7;
# set PYTHON to your py2.7 interpreter (e.g. a py2-MaP conda env) if `python`
# is not 2.7. Example: make test PYTHON=~/anaconda3/envs/py2-MaP/bin/python
PYTHON ?= python

.PHONY: help compile test test-e2e test-all update-goldens

help:
	@echo "make compile        - byte-compile src/ultrafold (py2.7 syntax check)"
	@echo "make test           - run pure-Python unit tests (no external tools)"
	@echo "make test-e2e       - run end-to-end golden tests (needs contrafold/dot2ct + DATAPATH)"
	@echo "make test-all       - unit + e2e (RNAstructure e2e via UF_TEST_RNASTRUCTURE=1)"
	@echo "make update-goldens - regenerate golden outputs (deliberate; needs tools)"

compile:
	$(PYTHON) -m py_compile src/ultrafold/*.py

test:
	cd tests && $(PYTHON) -m unittest -v test_unit

test-e2e:
	cd tests && $(PYTHON) -m unittest -v test_e2e_golden

test-all: compile
	cd tests && $(PYTHON) -m unittest discover -p 'test_*.py' -v

update-goldens:
	cd tests && $(PYTHON) update_goldens.py --engines eternafold
