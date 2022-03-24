from setuptools import setup, find_packages

setup(
    name="levenshteinaugment",
    version="0.0.1",
    description="SLURM distributed Levenshtein augmentation of datasets",
    author="Molecular AI group",
    author_email="esben.bjerrum@astrazeneca.com",
    license="proprietary",
    packages=find_packages(exclude=("tests",)),
)