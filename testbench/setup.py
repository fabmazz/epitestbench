from setuptools import setup


setup(
    name="epitestlib",
    version="0.1",
    author="Fabio Mazza",
    packages=["epitestlib"],
    description="A package to generate synthetic epidemies on graphs",
    install_requires=[
        "numpy",
        "Sibyl-EpiGen",
        "pandas",
    ]
)