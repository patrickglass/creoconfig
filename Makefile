
default: test

test: chmod_quick
	# Run the test suite with coverage enabled
	nosetests -v --with-coverage --cover-package creoconfig --cover-inclusive --cover-branches

interactive:
	python -Wall tests/test_interactive_prompt.py

chmod:
	# Set the correct permissions for all files
	find . -type d -exec chmod 755 {} \;
	find . -type f -exec chmod 644 {} \;

chmod_quick:
	chmod 644 tests/*

clean: chmod
	# Delete any generated files
	@find . -name "*.py?" | xargs rm -f

.PHONY: chmod chmod_quick test clean
