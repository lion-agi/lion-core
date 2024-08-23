import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the code version
version = {}
with open(os.path.join(here, "lion_core/version.py")) as fp:
    exec(fp.read(), version)
__version__ = version["__version__"]

# Read the contents of the README file
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the contents of the requirements file
with open("requirements.txt", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="lion_core",
    version=__version__,
    author="HaiyangLi",
    author_email="quantocean.li@gmail.com",
    description="A core package for the Lion framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lion-agi/lion-core",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["LICENSE", "README.md"],
    },
)
