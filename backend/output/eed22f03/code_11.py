from setuptools import setup, find_packages

setup(
    name="your_project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pytest-cov",
        "black",
        "flake8",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "your-command=src.your_module:main",
        ],
    },
)