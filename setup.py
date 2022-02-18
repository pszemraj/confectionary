import glob
import setuptools

import confectionary


def get_scripts_from_bin():
    """Get all local scripts from bin so they are included in the package."""
    return glob.glob("bin/*")


def get_package_description():
    """Returns a description of this package from the markdown files."""
    with open("README.md", "r") as stream:
        readme: str = stream.read()
    with open("HISTORY.md", "r") as stream:
        history: str = stream.read()
    return f"{readme}\n\n{history}"


def get_requirements():
    """Returns all requirements for this package."""
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
    return requirements


setuptools.setup(
    name="confectionary",
    author="Peter Szemraj, Jonathan Lehner",
    author_email="szemraj.dev@gmail.com",
    description="A tool to quickly create sweet PDF files from text files.",
    long_description=get_package_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/pszemraj/confectionary",
    packages=setuptools.find_packages(),
    install_requires=get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    scripts=get_scripts_from_bin(),
    python_requires=">=3.7",
    setuptools_git_versioning={
        "enabled": True,
    },
    setup_requires=["setuptools-git-versioning"],
)
