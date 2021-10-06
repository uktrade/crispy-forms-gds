"""Nox sessions."""
import tempfile
import shutil
from typing import Any

import nox
from nox.sessions import Session


package = "crispy_forms_gds"
nox.options.sessions = ["tests"]


locations = "src", "tests", "noxfile.py", "docs/conf.py"


def install_with_constraints(session, *args, **kwargs):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=["3.8", "3.9"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python="3.8")
def build(session):
    session.install("setuptools", "wheel", "twine")
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)
    session.run("python", "setup.py", "--quiet", "sdist", "bdist_wheel")
    session.run("twine", "check", "dist/*")


@nox.session(python="3.8")
def upload(session):
    build(session)
    print("REMINDER: Has the changelog been updated?")
    session.run(
        "python", "-m", "twine", "upload", "dist/*", "--skip-existing", "--sign"
    )
    publish_docs(session)


@nox.session(python=["3.8"])
def check(session):
    # ufmt combines Black and isort
    args = session.posargs
    # install_with_constraints(session, "ufmt")
    session.install("ufmt")
    session.run("ufmt", "check", "src", *args)


@nox.session(python=["3.8"])
def ufmt(session):
    # ufmt combines Black and isort
    args = session.posargs
    install_with_constraints(session, "ufmt")
    session.run("ufmt", *args)
