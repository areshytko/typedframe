import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()


setup(
    name="typedframe",
    version='0.10.0',
    description="Typed Wrappers over Pandas and Polars DataFrames with schema validation",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/areshytko/typedframe",
    author="Alexander Reshytko",
    author_email="alexander@reshytko.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["typedframe"],
    install_requires=[
    ],
    extras_require={
        "pandas": ["pandas", "numpy"],
        "polars": ["polars", "pyarrow"],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)