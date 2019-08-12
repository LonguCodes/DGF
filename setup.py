import setuptools

with open("VERSION", "r") as fh:
    version = fh.read()


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-graphene-framework",
    version=version,
    author="Maciej Łyskawiński",
    author_email="lyskawinski.maciej@gmail.com",
    description="Framework to streamline working with django and graphene",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LonguCodes/DGF/",
    packages=setuptools.find_packages(),
    install_requires=[
	'django',
	'graphene'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)