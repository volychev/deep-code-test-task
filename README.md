# python-template
![Static Badge](https://img.shields.io/badge/Python-0?style=flat-square&logo=python&color=010409)
![Static Badge](https://img.shields.io/badge/Poetry-0?style=flat-square&logo=Poetry&color=010409)
![Static Badge](https://img.shields.io/badge/Docker-0?style=flat-square&logo=Docker&color=010409)
![Static Badge](https://img.shields.io/badge/Flake8-0?style=flat-square&logo=Flake8&color=010409)
![Static Badge](https://img.shields.io/badge/Black-0?style=flat-square&logo=Black&color=010409)

Template for the [Python 3.13.11](https://www.python.org/downloads/release/python-3110/) projects based on [Poetry](https://python-poetry.org/docs/) using [Flake8](https://flake8.pycqa.org/en/latest/), [Black](https://black.readthedocs.io/en/stable/), [pre-commit](https://pre-commit.com/), [Docker](https://docs.docker.com/) and more

## Quick Start:
1. Create a repository using this template
2. Clone the created repository with `git clone`
3. Rename the created folder
4. Go to the created folder
5. Create a local environment using the command `poetry env use PYTHON_PATH` and add it to your IDE
6. Rename the `python_template` folder to the project name and mark it in the IDE as `Source Root`
7. Configure the `pyproject.toml` file for the project
8. Configure the Flake8 linter and other required tools in the `setup.cfg` file
9. Configure the `Dockerfile` for the project
10. Configure and install pre-commits with the command `pre-commit install`
11. Add the required dependencies with the command `poetry add PACKAGE_NAME` and install them with the command `poetry install`
