"""
setuptools-us4us: shared build-time helpers for the us4us Python packages.
"""
from setuptools_us4us.setup_helpers import (
    is_dev_version,
    read_version_file,
    setup_version,
    write_version_file,
)
from setuptools_us4us.version import __version__
from setuptools_us4us.versioning import (
    VersioningError,
    find_parent_release_branch,
    get_version,
    get_version_for_release_branch,
)

__all__ = [
    "VersioningError",
    "__version__",
    "find_parent_release_branch",
    "get_version",
    "get_version_for_release_branch",
    "is_dev_version",
    "read_version_file",
    "setup_version",
    "write_version_file",
]
