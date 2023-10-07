import os
import platform
import shutil
from pathlib import Path

from invoke import Collection, task  # type: ignore
from invoke.context import Context  # type: ignore


def get_python_bin_path() -> str | None:
    match platform.system():
        case "Linux" | "Darwin":
            return "./.venv/bin/"
        case "Windows":
            return "./.venv/Scripts/"
        case _:
            return None


@task
def clean(c: Context, venv=False):
    paths = [".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage"]
    if venv:
        paths.append(".venv")
    paths = (Path(p).resolve() for p in paths)
    for path in paths:
        try:
            shutil.rmtree(path)
            print(f"Removed directory: \t{path!s}")
        except NotADirectoryError:
            os.remove(path)
            print(f"Removed file: \t{path!s}")
        except FileNotFoundError:
            print(f"Path not found: \t{path!s}")


@task(iterable=["lint_paths"])
def lint(
    c: Context,
    pylint: bool = False,
    mypy: bool = True,
    paths: list[str] | None = None,
):
    if not paths:
        to_lint: str = " ".join(c.lint_paths)
    else:
        to_lint: str = " ".join(paths)

    c.run(f"{c.python_bin_path}black {to_lint}", echo=True)
    c.run(f"{c.python_bin_path}isort {to_lint}", echo=True)
    c.run(f"{c.python_bin_path}flake8 {to_lint}", echo=True)
    c.run(f"{c.python_bin_path}ruff {to_lint}", echo=True)
    if pylint:
        c.run(f"{c.python_bin_path}pylint {to_lint}", echo=True)
    if mypy:
        c.run(
            f"{c.python_bin_path}mypy -p src -p tests --check-untyped-defs", echo=True
        )


@task
def test(c: Context, cov=False):
    if cov:
        c.run(f"{c.python_bin_path}pytest -q --cov-branch --cov=src", pty=True)
    else:
        c.run(f"{c.python_bin_path}pytest", pty=True)


namespace = Collection(
    clean,
    lint,
    test,
)
namespace.configure(
    {"python_bin_path": get_python_bin_path(), "lint_paths": ["tests", "src"]}
)
