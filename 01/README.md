# Домашнее задание #01 (введение, тестирование). Решение

## Report

100% of tests are passing.

### Coverage report

```text
Name                          Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------
src/__init__.py                   0      0      0      0   100%
src/predict_message_mood.py      10      0      4      0   100%
src/read_generator.py            18      0     10      0   100%
---------------------------------------------------------------
TOTAL                            28      0     14      0   100%
```

## Testing

To run tests and generate coverage report you will need:

- Python ^3.11
- Poetry ^1.6

Then follow these instructions:

1. clone this repository:

   ```bash
   git clone https://github.com/relicks/deep_python_23b_aalitvinov.git
   ```

1. _cd_ into this dir:

   ```bash
   cd deep_python_23b_aalitvinov/01
   ```

   and run all commands from this working directory.

1. [Download and install Poetry](https://python-poetry.org/docs/#installation) following the instructions for your OS.
1. Set up the virtual environment, don't forget to specify the path to python3.11:

   ```bash
   poetry env use path/to/your/python3.11
   poetry install
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
