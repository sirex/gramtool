from setuptools import find_packages
from setuptools import setup


setup(
    name='gramtool',
    version='0.2',
    license='LGPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hunspell',
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'gramtool=gramtool.main:main',
        ],
    },
)
