import glob
import setuptools
from pathlib import Path



def get_package_description():
    """Returns a description of this package from the markdown files."""
    _readme = Path("README.md")
    _history = Path("HISTORY.md")
    if _readme.exists() and _history.exists():
        with open(_readme.resolve(), "r", encoding="utf-8", errors="ignore") as f:
            readme = f.read()
    else:
        readme = "README"
    if _history.exists():
        with open(_history.resolve(), "r", encoding="utf-8", errors="ignore") as f:
            history = f.read()
    else:
        history = "No history yet."
    return f"{readme}\n\n{history}"

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError as e:
    print(f"could not read README.md: {e}")
    long_description = get_package_description()


def get_scripts_from_bin():
    """Get all local scripts from bin so they are included in the package."""
    return glob.glob("bin/*")



def get_requirements():
    """Returns all requirements for this package."""
    with open("requirements.txt") as f:
        requirements = f.readlines()
    return requirements


setuptools.setup(
    name="confectionary",
    author="Peter Szemraj, Jonathan Lehner",
    author_email="szemraj.dev@gmail.com",
    description="A tool to quickly create sweet PDF files from text files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pszemraj/confectionary",
    # packages=setuptools.find_packages(),
    package_dir={"": "confectionary"},
    packages=setuptools.find_packages(where="confectionary"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Text Processing",
    ],
    scripts=get_scripts_from_bin(),
    python_requires=">=3.7",
    setuptools_git_versioning={
        "enabled": True,
    },
    setup_requires=["setuptools-git-versioning"],
)
