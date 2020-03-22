import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 7):
    raise Exception("Python 3.7 or higher is required. Your version is %s." % sys.version)

long_description = open('README.md', encoding="utf-8").read()

setup(
    name='lazy-async',
    packages=find_packages(include=['lazy_async', 'lazy_async.*']),
    version=0.6,
    description='Lazy evaluation for function/method/property getter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Curtis Jiang',
    url='https://github.com/jqqqqqqqqqq/',
    license='MIT',
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
    keywords=['Lazy Evaluation', 'Decorator'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ]
)
