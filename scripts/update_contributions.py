#!/usr/bin/env python3
"""Rewrite the contributions table in README.md from the public GitHub API.

Needs the `gh` CLI (preinstalled on GitHub Actions; set GH_TOKEN there).
To track another repo, add a line to REPOS.
"""
import re
import subprocess
from pathlib import Path

USER = "mnurisso"
REPOS = [  # (owner/repo, role, what it is)
    ("DestinE-Climate-DT/AQUA", "Main developer",
     "Core framework for evaluating high-resolution climate models"),
    ("DestinE-Climate-DT/AQUA-diagnostics", "Main contributor",
     "Diagnostic suite for online monitoring of ClimateDT simulations"),
    ("DestinE-Climate-DT/Climate-DT-catalog", "Main contributor",
     "Catalog describing the ClimateDT simulations for AQUA"),
    ("jhardenberg/smmregrid", "Contributor",
     "Compact regridder using sparse matrix multiplication, used by AQUA"),
]
README = Path(__file__).resolve().parent.parent / "README.md"


def gh(path, jq, paginate=False):
    cmd = ["gh", "api", path, "--jq", jq] + (["--paginate"] if paginate else [])
    out = subprocess.run(
        cmd,
        check=True, capture_output=True, text=True,
    ).stdout.split()
    return sum(int(x) for x in out)


rows = ["| Repo | What it is | Role | My commits | My merged PRs |", "|---|---|---|---:|---:|"]
for repo, role, what in REPOS:
    commits = gh(f"repos/{repo}/contributors?per_page=100",
                 f'.[] | select(.login=="{USER}") | .contributions', paginate=True)
    prs = gh(f"search/issues?q=repo:{repo}+author:{USER}+type:pr+is:merged&per_page=1",
             ".total_count")
    rows.append(f"| [{repo.split('/')[1]}](https://github.com/{repo}) | {what} | {role} | {commits:,} | {prs:,} |")

table = "\n".join(rows)
text = README.read_text()
new = re.sub(
    r"(<!-- CONTRIBUTIONS:START -->).*?(<!-- CONTRIBUTIONS:END -->)",
    lambda m: m.group(1) + "\n" + table + "\n" + m.group(2),
    text, flags=re.S,
)
if new != text:
    README.write_text(new)
    print("README updated")
else:
    print("No change")
