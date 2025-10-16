.PHONY: test coverage badge clean

# Run tests with coverage
test:
	uv run pytest

# Generate coverage report and update badge
coverage: test
	uv run pytest --cov=dpn_pyutils --cov-report=html --cov-report=xml --cov-report=term-missing
	uv run generate-coverage-badge

# Update coverage badge only (requires existing coverage.xml)
badge:
	uv run generate-coverage-badge

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -f coverage.xml
	rm -f .coverage
	rm -f pytest.log
