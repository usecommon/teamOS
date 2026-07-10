PYTHON := python3
export PYTHONPATH := $(CURDIR):$(CURDIR)/scripts

.PHONY: test schemas mapping unit

test: schemas mapping hookbudget unit chains

schemas:
	$(PYTHON) scripts/validate_schemas.py

mapping:
	$(PYTHON) scripts/mapping_report.py

hookbudget:
	@lines=$$(grep -c '' hooks/gate.py); \
	if [ $$lines -gt 300 ]; then echo "gate.py $$lines lines > 300 budget (X-1)"; exit 1; \
	else echo "gate.py $$lines lines (<= 300 budget, X-1)"; fi

unit:
	$(PYTHON) -m unittest discover -s tests -v

chains:
	$(PYTHON) scripts/verify_chains.py
