from setuptools import setup

setup(
    name='porkhollow',
    version='0.1',
    packages=['porkhollow'],
    entry_points={
        'console_scripts': ['rebalance = porkhollow.rebalance:rebalance']
    }
)
