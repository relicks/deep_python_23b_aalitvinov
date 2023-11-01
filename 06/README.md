# Домашнее задание #06 (потоки, процессы)

<!-- * Решение первого пункта ДЗ#05 содержится в `./lru_cache.py`
* Решение второго пункта ДЗ#05 (тесты LRUCache) содержится в `./test_lru_cache.py` -->

## Report

100% of tests are passing.

### Coverage report

```text
Name           Stmts   Miss Branch BrPart  Cover
------------------------------------------------
lru_cache.py      42      0     12      0   100%
------------------------------------------------
TOTAL             42      0     12      0   100%
```

## Testing

To run tests and generate coverage report you will need:

* Python `>=3.10,<3.13`
* Poetry `^1.6`

Then follow these instructions:

1. clone this repository:

   ```bash
   git clone https://github.com/relicks/deep_python_23b_aalitvinov.git
   ```

1. _cd_ into this dir:

   ```bash
   cd deep_python_23b_aalitvinov/05
   ```

   and run all commands from this working directory.

1. [Download and install Poetry](https://python-poetry.org/docs/#installation) following the instructions for your OS.
1. Set up the virtual environment, don't forget to specify the path to python3.11:

   ```bash
   poetry env use path/to/your/python3.10
   poetry install --with dev-opts
   ```

1. Activate the virtual environment (alternatively, ensure any python or git-related command is preceded by `poetry run`):

   ```bash
   poetry shell
   ```

1. _[OPTIONAL]_ Install the git hooks, if you need them:

   ```bash
   pre-commit install
   ```

1. run tests and linters:

   ```bash
   inv test --cov
   inv lint --pylint
   ```
