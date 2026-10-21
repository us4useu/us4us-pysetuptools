import os
import sys

import setuptools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from setuptools_us4us.setup_helpers import read_version_file  # noqa: E402

setuptools.setup(
    name="setuptools_us4us",
    # This package's own version is maintained manually in version.py
    # (bump it and tag va.b.c on release).
    version=read_version_file("setuptools_us4us/version.py"),
    author="us4us Ltd.",
    author_email="support@us4us.eu",
    description="Shared build-time (setuptools) helpers for the us4us "
                "Python packages.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://us4us.eu",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
    ],
    install_requires=[],
    python_requires=">=3.8",
)
