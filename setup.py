import os
import re
from setuptools import setup, find_packages


RE_PY_VERSION = re.compile(
    r'__version__\s*=\s*["\']'
    r'(?P<version>\d+(\.\d+(\.\d+)?)?)'
    r'["\']'
)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_version():
    content = read('src/jwtlib/__init__.py')
    m = RE_PY_VERSION.search(content)
    if not m:
        return '0.0'
    else:
        return m.group('version')


setup(
    name="jwtlib",
    version=read_version(),
    author="Mateusz Klos",
    author_email="novopl@gmail.com",
    license="Apache 2.0",
    keywords="library",
    url="https://github.com/novopl/jwtlib",
    description="library",
    long_description=read('README.rst'),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        "pyjwt~=1.7.1",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
)
