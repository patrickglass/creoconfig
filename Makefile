
default: test

test:
	# Run the test suite with coverage enabled
	nosetests --with-coverage --cover-package creoconfig --cover-inclusive --cover-branches

interactive:
	python -Wall interactive_prompt.py

chmod:
	# Set the correct permissions for all files
	find . -type d -exec chmod 755 {} \;
	find . -type f -exec chmod 644 {} \;


clean: chmod
	# Delete any generated files
	@find . -name "*.py?" | xargs rm -f

.PHONY: chmod test clean
