
docs: go_extension
	sphinx-apidoc -f -o ./docs_src go_extension
	sphinx-build docs_src docs

test: mypy unittest

mypy: 
	mypy .

unittest:
	coverage run -m unittest
	go mod tidy
	coverage html
	coverage report
