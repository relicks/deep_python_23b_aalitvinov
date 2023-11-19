"""This is Invoke tasks file. Not meant to be executed directly."""
import os
import platform
import shutil
from pathlib import Path

try:
    from invoke import Collection, task  # type: ignore
    from invoke.context import Context  # type: ignore
except (ModuleNotFoundError, ImportError):
    pass
else:

    def get_python_bin_path() -> str | None:
        match platform.system():
            case "Linux" | "Darwin":
                return "./.venv/bin/"
            case "Windows":
                return "./.venv/Scripts/"
            case _:
                return None

    @task
    def clean(_: Context, venv=False):
        paths = [
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".coverage",
            "__pycache__",
        ]
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

    @task
    def mypy(c: Context, strict=False):
        args = list(c.lint_paths)
        args.extend(["--check-untyped-defs"])

        if strict:
            args.append("--strict")

        c.run(f"{c.python_bin_path}mypy {' '.join(args)}", echo=True, pty=True)

    @task(iterable=["lint_paths"])
    def lint(
        c: Context,
        pylint: bool = False,
        static_check: bool = True,
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
        if static_check:
            mypy(c)

    @task
    def test(c: Context, cov=False, missing=True):
        args = []
        if cov:
            args.extend(["-q", "--cov-branch", "--cov=."])
            if missing:
                args.append("--cov-report=term-missing")

        c.run(
            f"{c.python_bin_path}pytest {' '.join(args)}",
            pty=True,
        )

    namespace = Collection(
        clean,
        lint,
        test,
        mypy,
    )
    namespace.configure(
        {
            "python_bin_path": get_python_bin_path(),
            "lint_paths": ["client.py", "server.py"],
        }
    )
