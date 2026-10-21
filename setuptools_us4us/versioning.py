"""
The rules implemented here are the ones used across the us4us Python
projects:

- a commit tagged with a release tag (``va.b.c``) or a release candidate
  tag (``va.b.c-rcN``) marks the stable version ``a.b.c``; release
  candidates of ``a.b.c`` are built with the final version number, so the
  tested package is the one that gets released,
- a commit on a **release branch** (``va.b.x`` or the legacy ``va.b.0-dev``)
  produces a development version of the next major.minor, i.e.
  ``a.b.(c+1).devYYYYMMDD``, where ``va.b.c`` is the latest release tag
  reachable from that branch; when there is no reachable release tag,
  ``a.b.0.devYYYYMMDD`` is used,
- a commit on a feature branch produces the dev version of its
  parent release branch, with the branch name local
  version label, e.g. ``0.7.0.dev20260823+ref.mvandv.194``.
"""
import datetime
import re
from typing import Optional, Sequence, Tuple

from setuptools_us4us.cmd import run_cmd

RELEASE_BRANCH_PATTERNS = (
    # Example: v0.7.x
    r"^v(?P<major>\d+)\.(?P<minor>\d+)\.x$",
    # Legacy example: v0.3.0-dev 
    r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)-dev$",
)

#: Tag names denoting a stable release, e.g. v0.7.1
RELEASE_TAG_PATTERN = r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$"

#: Tag names denoting a release candidate, e.g. v0.7.1-rc2
RELEASE_CANDIDATE_TAG_PATTERN = \
    r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)-rc(?P<rc>\d+)$"


class VersioningError(RuntimeError):
    """
    Raised when the version number cannot be determined from git.
    """
    pass


def get_today() -> str:
    """
    Returns the current date, formatted as ``YYYYMMDD``.
    """
    return datetime.datetime.now().strftime("%Y%m%d")


def match_release_branch(branch: str) -> Optional[Tuple[int, int]]:
    """
    Returns the ``(major, minor)`` pair for the given release branch name,
    or ``None`` when the name is not a release branch name.
    """
    for pattern in RELEASE_BRANCH_PATTERNS:
        match = re.match(pattern, branch.strip())
        if match is not None:
            return int(match.group("major")), int(match.group("minor"))
    return None


def match_release_tag(tag: str) -> Optional[Tuple[int, int, int]]:
    """
    Returns the ``(major, minor, patch)`` triple for the given release tag,
    or ``None`` when the name is not a release tag name.
    """
    match = re.match(RELEASE_TAG_PATTERN, tag.strip())
    if match is None:
        return None
    return (int(match.group("major")), int(match.group("minor")),
            int(match.group("patch")))


def match_release_candidate_tag(tag: str) -> Optional[Tuple[int, int, int]]:
    """
    Returns the ``(major, minor, patch)`` triple of the release the given
    release candidate tag is for, or ``None`` when the name is not a release
    candidate tag name.
    """
    match = re.match(RELEASE_CANDIDATE_TAG_PATTERN, tag.strip())
    if match is None:
        return None
    return (int(match.group("major")), int(match.group("minor")),
            int(match.group("patch")))


def normalize_local_label(branch: str) -> str:
    """
    Converts a branch name to a PEP 440 local version label
    e.g. ref-MVANDV-194 -> ref.mvandv.194.
    """
    label = re.sub(r"[^a-z0-9]+", ".", branch.strip().lower())
    return label.strip(".")


def _strip_v(version: str) -> str:
    return version[1:] if version.startswith("v") else version


def get_version_for_release_branch(branch: str, cwd: str = None,
                                   today: str = None) -> str:
    """
    Returns the development version for the given release branch.

    :param branch: release branch name e.g. v0.7.x
    :param cwd: repository directory
    :param today: date timestamp to use, YYYYMMDD; default: current date
    :return: version string (e.g. v0.7.1)
    """
    today = today if today is not None else get_today()
    major_minor = match_release_branch(branch)
    if major_minor is None:
        raise VersioningError(f"Not a release branch name: '{branch}'")
    major, minor = major_minor
    base = f"v{major}.{minor}"
    tag, _, ret = run_cmd(
        # "Release candidate" tags (va.b.c-rcN) are not releases.
        cmd=f"git describe --tags --match {base}.* --exclude *-rc* "
            f"--abbrev=0",
        return_code=True, cwd=cwd,
    )
    if ret == 0 and tag:
        release = match_release_tag(tag)
        if release is not None:
            # There already is a stable release on this branch: the next
            # thing we are going to release is the next patch version.
            tag_major, tag_minor, tag_patch = release
            return f"v{tag_major}.{tag_minor}.{tag_patch + 1}.dev{today}"
        # Non-conformant tag (e.g. v0.7.0-rc1): ignore it.
    return f"{base}.0.dev{today}"


def _list_branches(cwd: str = None) -> Sequence[str]:
    """Returns the names of all local and remote-tracking branches."""
    stdout, _, ret = run_cmd(
        cmd="git branch --all --format=%(refname:short)",
        return_code=True, cwd=cwd,
    )
    if ret != 0:
        return ()
    branches = []
    for line in stdout.split("\n"):
        name = line.strip()
        if not name or "->" in name:
            continue
        # Drop the remote prefix, e.g. origin/v0.7.x -> v0.7.x
        if "/" in name:
            name = name.split("/", 1)[1]
        branches.append(name)
    return branches


def find_parent_release_branch(cwd: str = None) -> str:
    """
    Returns the release branch the current ``HEAD`` was most likely branched
    off from: out of all the release branches sharing a common ancestor with
    ``HEAD``, the one with the highest ``major.minor``.

    :raises VersioningError: when no such branch exists
    """
    candidates = []
    for branch in set(_list_branches(cwd=cwd)):
        major_minor = match_release_branch(branch)
        if major_minor is None:
            continue
        _, _, ret = run_cmd(cmd=f"git merge-base {branch} HEAD",
                            return_code=True, cwd=cwd)
        if ret == 0:
            candidates.append((major_minor, branch))
    if len(candidates) == 0:
        raise VersioningError(
            "Could not determine the version number: the current HEAD has no "
            "parent release branch (expected a branch named e.g. 'v0.7.x'). "
            "Make sure the release branches are fetched "
            "(e.g. 'git fetch --unshallow' in a CI checkout).")
    candidates = sorted(candidates)
    return candidates[-1][1]


def get_commit(cwd: str = None) -> str:
    """
    Returns the full hash of the current ``HEAD`` commit.
    """
    return run_cmd(cmd="git rev-parse HEAD", cwd=cwd)


def get_version(cwd: str = None, today: str = None) -> str:
    """
    Determines the package version from the state of the git repository.

    :param cwd: repository directory, the current working directory by default
    :param today: date stamp to use, ``YYYYMMDD``; the current date by default
    :return: PEP 440 version string, e.g. ``0.7.1.dev20260823``
    :raises VersioningError: when the version number cannot be determined
    """
    today = today if today is not None else get_today()
    current_branch = run_cmd(cmd="git rev-parse --abbrev-ref HEAD", cwd=cwd)
    current_tags = run_cmd(cmd="git tag --points-at HEAD", cwd=cwd)

    # 1. A tagged commit (release or release candidate) is a stable release.
    for tag in current_tags.split("\n"):
        release = match_release_tag(tag) or match_release_candidate_tag(tag)
        if release is not None:
            return "{}.{}.{}".format(*release)

    # 2. A release branch: the development version of the next patch release.
    if match_release_branch(current_branch) is not None:
        return _strip_v(get_version_for_release_branch(
            current_branch, cwd=cwd, today=today))

    # 3. A feature branch: the parent release branch version + local label.
    parent = find_parent_release_branch(cwd=cwd)
    version = get_version_for_release_branch(parent, cwd=cwd, today=today)
    return _strip_v(f"{version}+{normalize_local_label(current_branch)}")
