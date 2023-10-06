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
def clean(c: Context):
    paths = [".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage"]
    paths = (Path(p).resolve() for p in paths)
    for path in paths:
        try:
            shutil.rmtree(path)
            print(f"Removed directory: \t{path!s}")
        except NotADirectoryError:
            os.remove(path)
            print(f"Removed file: \t{path!s}")
        except FileNotFoundError:
            print(f"Directory not found: \t{path!s}")


@task
def get_os(c: Context):
    bin_path = c.python_bin_path
    if bin_path is not None:
        print(Path(bin_path).resolve())
        assert Path(bin_path).exists()


@task(iterable=["lint_paths"])
def lint(
    c: Context,
    pylint: bool = False,
    mypy: bool = True,
    lint_paths: list[str] | None = None,
):
    if not lint_paths:
        to_lint: str = " ".join(["tests", "src"])
    else:
        to_lint: str = " ".join(lint_paths)

    c.run(f"{c.python_bin_path}black {to_lint}", echo=True)
    c.run(f"{c.python_bin_path}isort {to_lint}", echo=True)
    c.run(f"{c.python_bin_path}flake8 {to_lint}", echo=True)
    c.run(f"{c.python_bin_path}ruff {to_lint}", echo=True)
    if pylint:
        c.run(f"{c.python_bin_path}pylint {lint_paths}", echo=True)
    if mypy:
        c.run(f"{c.python_bin_path}mypy -p src -p tests", echo=True)


@task
def test(c: Context, cov=False):
    if cov:
        c.run(f"{c.python_bin_path}pytest -q --cov-branch --cov=src")
    else:
        c.run(f"{c.python_bin_path}pytest")


@task
def getinp(c: Context, inp=None):
    print(inp)


namespace = Collection(clean, lint, test, get_os, getinp)
namespace.configure({"python_bin_path": get_python_bin_path()})
