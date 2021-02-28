from setuptools import setup, find_packages
setup(
    name='twitter_api',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'httpx',
        'httpx_oauth @ git+ssh://git@github.com/vphpersson/httpx_oauth.git#egg=httpx_oauth',
        'pyutils @ git+ssh://git@github.com/vphpersson/pyutils.git#egg=pyutils'
    ]
)
