from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the contents of the requirements file
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="lion_core",
    version="0.1.0",
    author="HaiyangLi",
    author_email="",
    description="A core package for the Lion framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ohdearquant/lion-core",
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
