from setuptools import setup, find_packages
from typing import List

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Declaring variables for setup functions
PROJECT_NAME = "src"
VERSION = "0.0.1"
AUTHOR = "Hasanain"
USER_NAME = "hassi34"
AUTHOR_EMAIL = "hasanain@aicaliber.com"
REPO_NAME = "brain-tumor-classification"
DESRCIPTION = "This project contains the production ready Machine Learning(Deep Learning) solution for detecting and classifying the brain tumor in medical images"
REQUIREMENT_FILE_NAME = "requirements.txt"
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.7"

HYPHEN_E_DOT = "-e ."


def get_requirements_list() -> List[str]:
    """
    Description: This function is going to return list of requirement
    mention in requirements.txt file
    return This function is going to return a list which contain name
    of libraries mentioned in requirements.txt file
    """
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
        requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]
        if HYPHEN_E_DOT in requirement_list:
            requirement_list.remove(HYPHEN_E_DOT)
        return requirement_list


setup(
    name=PROJECT_NAME,
    version=VERSION,
    author=AUTHOR,
    description=DESRCIPTION,
    long_description=long_description,
    url=f"https://github.com/{USER_NAME}/{REPO_NAME}",
    packages=find_packages(),
    license=LICENSE,
    python_requires=PYTHON_REQUIRES,
    install_requires=get_requirements_list()
)