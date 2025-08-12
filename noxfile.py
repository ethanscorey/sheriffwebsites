"""Test, format, lint, and type-check files."""

from pathlib import Path
import nox

LOCATIONS = ("sheriffwebsites", "tests", "noxfile.py")
VERSIONS = ["3.13"]
nox.options.default_venv_backend = "uv"
nox.options.sessions = (
    "tests",
    "format_files",
    "lint",
    "doc-lint",
    "mypy",
)


def install(session: nox.Session) -> None:
    """Install project dependencies.

    Arguments
    ---------
    session : nox.Session
        The nox session.
    """
    args = ["uv", "sync", "--python", str(session.python), "--group", "test"]
    session.run_install(
        *args,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session(python=VERSIONS, venv_backend="uv")
def tests(session: nox.Session) -> None:
    """Run test suit, skipping e2e tests by default.

    Arguments
    ---------
    session : nox.Session
        The nox session.
    """
    args = session.posargs or ["--cov", "-m", "not e2e"]
    install(session)
    session.run(
        "uv",
        "run",
        "pytest",
        "--typeguard-packages=sheriffwebsites",
        *args,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session(python=VERSIONS[0])
def format_files(session: nox.Session) -> None:
    """Format Python files with ruff.

    Arguments
    ---------
    session : nox.Session
        The nox session.
    """
    args = session.posargs or LOCATIONS
    session.run("uvx", "ruff", "format", *args, external=True)


@nox.session(python=VERSIONS[0])
def lint(session: nox.Session) -> None:
    """Lint Python files with ruff.

    Arguments
    ---------
    session : nox.Session
        The nox session.
    """
    args = session.posargs or LOCATIONS
    session.run("uvx", "ruff", "check", "--fix", *args, external=True)


@nox.session(name="doc-lint", python=VERSIONS[0])
def doc_lint(session: nox.Session) -> None:
    """Lint docstrings with pydoclint.

    Arguments
    ---------
    session : nox.Session
        The nox session.
    """
    args = session.posargs or LOCATIONS
    session.run("uvx", "pydoclint", *args, external=True)


@nox.session(python=VERSIONS)
def mypy(session: nox.Session) -> None:
    """Type-check Python files with mypy.

    Arguments
    ---------
    session : nox.Session
        The nox session.
    """
    args = session.posargs or ["sheriffwebsites", "tests"]
    install(session)
    package_dir = Path(
        session.run(
            "python",
            "-c",
            "import us, os; print(os.path.dirname(us.__file__))",
            silent=True,
        ).strip()
    )
    session.run(
        "touch",
        package_dir / "py.typed",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    session.run(
        "uv",
        "run",
        "mypy",
        *args,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session(python=VERSIONS, venv_backend="uv")
def test_e2e(session: nox.Session) -> None:
    """Run test suit, skipping e2e tests by default.

    Arguments
    ---------
    session : nox.Session
        The nox session.
    """
    args = session.posargs or ["tests/e2e/test_e2e_local.py"]
    install(session)
    session.run(
        "uv",
        "run",
        "pytest",
        *args,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
