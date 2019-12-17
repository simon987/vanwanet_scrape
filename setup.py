from setuptools import setup

setup(
    name="vanwanet_scrape",
    version="1.0",
    description="VanwaTech DDoS protection bypass",
    author="simon987",
    author_email="me@simon987.net",
    packages=["vanwanet_scrape"],
    install_requires=[
        "requests", "bs4", "git+git://github.com/simon987/hexlib.git",
    ]
)
