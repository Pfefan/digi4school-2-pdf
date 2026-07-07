from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="digi4school-2-pdf",
    version="0.1.0",
    packages=find_packages(),
    author='Pfefan',
    author_email='pfefan04@gmail.com',
    description='Converts Digi4School books to PDFs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pfefan/digi4school-2-pdf",
    install_requires=[
        'beautifulsoup4',
        'CairoSVG',
        'pypdf',
        'pytest',
        'python-dotenv',
        'python-slugify',
        'Requests',
        'selenium',
        'tqdm',
    ],
)