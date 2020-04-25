from setuptools import setup, find_packages
setup(
    name='twitter_api',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'httpx',
        'httpx-oauth @ https://github.com/vphpersson/httpx_oauth/tarball/master',
        'pyutils @ https://github.com/vphpersson/pyutils/tarball/master'
    ]
)
