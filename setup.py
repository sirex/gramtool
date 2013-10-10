from setuptools import find_packages
from setuptools import setup


setup(
    name='gram',
    version='0.1',
    license='GPL',
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    install_requires=[
        'hunspell',
        'PyYAML',
    ],
    entry_points = {
        'console_scripts': [
            'gram=gram.main:gram',
        ],
    },
)
