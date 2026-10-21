# setuptools-us4us

Common setuptools extensions used by the us4us Python packages, e.g.
determining the package version from the state of the git repository
(release tags and branches).

## Installation

```
pip install setuptools_us4us
```

Usually it is needed only at build time, e.g. in the project's `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61", "wheel", "setuptools_us4us"]
build-backend = "setuptools.build_meta"
```

and `setup.py`:

```python
import setuptools
from setuptools_us4us import setup_version

setuptools.setup(
    name="my_package",
    version=setup_version("my_package"),  # also writes my_package/version.py
    ...
)
```

## Repository structure

- `setuptools_us4us/versioning.py`: git-based version numbers
  (`get_version`, `get_version_for_release_branch`,
  `find_parent_release_branch`):
  - tagged commit `va.b.c` -> `a.b.c`,
  - release branch `va.b.x` -> `a.b.(c+1).devYYYYMMDD`,
  - feature branch -> parent release branch version + branch name as local
    label, e.g. `0.7.0.dev20260823+ref.mvandv.194`.
- `setuptools_us4us/setup_helpers.py`: helpers for `setup.py`
  (`setup_version`, `write_version_file`, `read_version_file`,
  `is_dev_version`).
- `setuptools_us4us/cmd.py`: running shell commands (`run_cmd`).
