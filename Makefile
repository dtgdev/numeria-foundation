.PHONY: validate install-dev

install-dev:
	python3 -m pip install -r requirements-dev.txt

validate:
	python3 scripts/validate_all.py
