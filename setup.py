from setuptools import setup, find_packages

VERSION = "0.0.2"
PACKAGE_NAME = "fdamage"
AUTHOR = "Valerio Luzzi"
EMAIL = "valerio.luzzi@gecosistema.com"
GITHUB = f"https://github.com/valluzzi/{PACKAGE_NAME}.git"
DESCRIPTION = "A fdamage utility for reading damage functions"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    license='MIT',
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    url=GITHUB,
    packages=find_packages("src"),
    package_dir={'': 'src'},
    package_data={
        "": ["data/*.json"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[ "boto3" ]
)










