PYTHON := python3
export PYTHONPATH := $(CURDIR):$(CURDIR)/scripts

.PHONY: test schemas mapping unit

test: schemas mapping unit

schemas:
	$(PYTHON) scripts/validate_schemas.py

mapping:
	$(PYTHON) scripts/mapping_report.py

unit:
	$(PYTHON) -m unittest discover -s tests -v
