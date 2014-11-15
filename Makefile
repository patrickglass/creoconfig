
default: test

test: chmod_quick
	# Run the test suite with coverage enabled
	nosetests -v --with-coverage --cover-package creoconfig --cover-inclusive --cover-branches

test_quick: chmod_quick
	# Run the test suite with coverage enabled
	nosetests -v --with-coverage --cover-package creoconfig --cover-inclusive --cover-branches --stop

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
	@rm -rf tmp_*

.PHONY: chmod chmod_quick test test_quick clean
