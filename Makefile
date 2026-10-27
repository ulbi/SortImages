.PHONY: test clean

test:
	python3 test_sortinfolder.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
