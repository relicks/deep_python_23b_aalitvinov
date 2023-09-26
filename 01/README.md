# Poetry Template

To use this repository as a template for your own application:
1. [Download and install Poetry](https://python-poetry.org/docs/#installation) following the instructions for your OS.
1. Click the green "*Use this template*" button above
1. Name and create your repository
1. Clone your new repository and make it your working directory
1. Replace instances of `poetry_template` with your own application name.
1. Set up the virtual environment, don't forget to use the path to python3.11:

   ```bash
   poetry env use <path/to/your/python3.11>
   poetry install
   ```

1. Activate the virtual environment (alternatively, ensure any python-related command is preceded by `poetry run`):

   ```bash
   poetry shell
   ```

1. Install the git hooks:

   ```bash
   pre-commit install
   ```
1. **Run `git` commands only from `poetry shell`**!