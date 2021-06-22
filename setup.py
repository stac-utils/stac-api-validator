"""Setup stac-api-validator."""

from setuptools import find_namespace_packages, setup

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "pystac-client>=0.1.1,<0.2",
    "requests",
    "pystac",
    "pystac[validation]"
]

extra_reqs = {
    "test": ["pytest", "pytest-cov", "pytest-asyncio", "requests"],
}


setup(
    name="stac-api-validator",
    version="0.1.0",
    description=u"A validation client for STAC API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="STAC",
    author=u"Phil Varner",
    author_email="phil@philvarner.com",
    url="https://github.com/stac-utils/stac-api-validator",
    license="Apache 2.0",
    packages=find_namespace_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
