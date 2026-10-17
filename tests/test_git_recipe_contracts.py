from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

# Externally observable Git semantics that the smart-commit guidance depends
# on. These tests exercise the mechanisms in disposable repositories rather
# than asserting on Markdown prose.

GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


def run(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        env={**os.environ, **GIT_ENV},
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def git(repo: Path, *args: str) -> str:
    return run(repo, "git", *args)


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "-c", "init.defaultBranch=main", "init", "-q")
    return path


def write(path: Path, name: str, content: str) -> None:
    (path / name).write_text(content, encoding="utf-8")


def commit_names(repo: Path, revision: str = "HEAD") -> set[str]:
    output = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", revision)
    return {line for line in output.splitlines() if line}


class GitGroupedCommitRecipeTest(unittest.TestCase):
    def test_pathspec_commit_leaves_another_staged_group_out(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "alpha.txt", "alpha base\n")
            write(repo, "beta.txt", "beta base\n")
            git(repo, "add", "--", "alpha.txt", "beta.txt")
            git(repo, "commit", "-qm", "base")

            # Group B is already staged before the recipe runs.
            write(repo, "beta.txt", "beta base\nbeta staged-group-B\n")
            git(repo, "add", "--", "beta.txt")

            # Group A is changed, registered, and committed with a trailing pathspec.
            write(repo, "alpha.txt", "alpha base\nalpha group-A\n")
            git(repo, "add", "--", "alpha.txt")
            git(repo, "commit", "-qm", "group A: alpha", "--", "alpha.txt")

            status = git(repo, "status", "--porcelain")
            self.assertEqual(status, "M  beta.txt\n")
            self.assertEqual(commit_names(repo), {"alpha.txt"})
            self.assertEqual(git(repo, "show", "HEAD:beta.txt"), "beta base\n")
            self.assertEqual(
                git(repo, "show", ":beta.txt"), "beta base\nbeta staged-group-B\n"
            )
            self.assertEqual(
                git(repo, "show", ":alpha.txt"), "alpha base\nalpha group-A\n"
            )

    def test_pathspec_commit_includes_registered_new_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "alpha.txt", "alpha base\n")
            git(repo, "add", "--", "alpha.txt")
            git(repo, "commit", "-qm", "base")

            write(repo, "beta.txt", "beta base\nbeta staged-group-B\n")
            git(repo, "add", "--", "beta.txt")

            write(repo, "gamma.txt", "gamma group-A\n")
            git(repo, "add", "--", "gamma.txt")
            git(repo, "commit", "-qm", "group A: gamma", "--", "gamma.txt")

            self.assertEqual(commit_names(repo), {"gamma.txt"})
            self.assertEqual(git(repo, "show", "HEAD:gamma.txt"), "gamma group-A\n")
            self.assertEqual(git(repo, "status", "--porcelain"), "A  beta.txt\n")

    def test_pathspec_commit_commits_whole_working_tree_of_a_shared_file(self) -> None:
        # Honest limitation: a path-scoped commit cannot split one file at hunk level.
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "shared.txt", "l1\nl2\nl3\nl4\n")
            git(repo, "add", "--", "shared.txt")
            git(repo, "commit", "-qm", "base")

            write(repo, "shared.txt", "l1\nl2\nl3\nB4\n")
            git(repo, "add", "--", "shared.txt")
            write(repo, "shared.txt", "A1\nl2\nl3\nB4\n")

            self.assertEqual(git(repo, "status", "--porcelain"), "MM shared.txt\n")
            git(repo, "commit", "-qm", "group A: shared", "--", "shared.txt")

            self.assertEqual(git(repo, "show", "HEAD:shared.txt"), "A1\nl2\nl3\nB4\n")
            self.assertEqual(git(repo, "status", "--porcelain"), "")

    def test_pathspec_commit_includes_tracked_generated_deliverable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "source.txt", "source v1\n")
            write(repo, "generated-mirror.txt", "mirror v1\n")
            git(repo, "add", "--", "source.txt", "generated-mirror.txt")
            git(repo, "commit", "-qm", "base")

            write(repo, "source.txt", "source v2\n")
            write(repo, "generated-mirror.txt", "mirror v2\n")
            (repo / "build").mkdir()
            write(repo, "build/out.o", "foreign build output\n")

            git(repo, "add", "--", "source.txt", "generated-mirror.txt")
            git(
                repo,
                "commit",
                "-qm",
                "feature with regenerated mirror",
                "--",
                "source.txt",
                "generated-mirror.txt",
            )

            self.assertEqual(commit_names(repo), {"source.txt", "generated-mirror.txt"})
            self.assertEqual(
                git(repo, "show", "HEAD:generated-mirror.txt"), "mirror v2\n"
            )
            self.assertEqual(git(repo, "status", "--porcelain"), "?? build/\n")


class GitHunkSplitRecipeTest(unittest.TestCase):
    def test_index_commit_separates_hunks_of_a_shared_file(self) -> None:
        # The documented hunk path: stage exactly one group's hunks (the
        # scriptable equivalent of `git add -p` is `git apply --cached`),
        # confirm nothing else is staged, then commit the index.
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "shared.txt", "l1\nl2\nl3\nl4\n")
            git(repo, "add", "--", "shared.txt")
            git(repo, "commit", "-qm", "base")

            # Group A and group B hunks are both present in the working tree.
            write(repo, "shared.txt", "A1\nl2\nl3\nB4\n")
            status = git(repo, "status", "--porcelain")
            self.assertEqual(status, " M shared.txt\n")

            patch = "diff --git a/shared.txt b/shared.txt\n--- a/shared.txt\n+++ b/shared.txt\n@@ -1,4 +1,4 @@\n-l1\n+A1\n l2\n l3\n l4\n"
            (repo / "a.patch").write_text(patch, encoding="utf-8")
            git(repo, "apply", "--cached", "a.patch")
            (repo / "a.patch").unlink()
            self.assertEqual(git(repo, "status", "--porcelain"), "MM shared.txt\n")

            git(repo, "commit", "-qm", "group A: hunks only")

            self.assertEqual(git(repo, "show", "HEAD:shared.txt"), "A1\nl2\nl3\nl4\n")
            self.assertEqual(git(repo, "status", "--porcelain"), " M shared.txt\n")

    def test_partial_staging_then_pathspec_commit_records_working_tree(self) -> None:
        # Documents why the recipe forbids combining `git add -p` with a
        # pathspec commit: the pathspec records the whole working tree of the
        # named path, silently absorbing the other group's unstaged hunks.
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "shared.txt", "l1\nl2\nl3\nl4\n")
            git(repo, "add", "--", "shared.txt")
            git(repo, "commit", "-qm", "base")

            write(repo, "shared.txt", "A1\nl2\nl3\nB4\n")
            patch = "diff --git a/shared.txt b/shared.txt\n--- a/shared.txt\n+++ b/shared.txt\n@@ -1,4 +1,4 @@\n-l1\n+A1\n l2\n l3\n l4\n"
            (repo / "a.patch").write_text(patch, encoding="utf-8")
            git(repo, "apply", "--cached", "a.patch")
            (repo / "a.patch").unlink()

            git(repo, "commit", "-qm", "accidental absorption", "--", "shared.txt")

            self.assertEqual(git(repo, "show", "HEAD:shared.txt"), "A1\nl2\nl3\nB4\n")


class GitPendingMergeRecipeTest(unittest.TestCase):
    def test_pending_merge_rejects_pathspec_commit_and_commits_whole(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "base.txt", "base\n")
            git(repo, "add", "--", "base.txt")
            git(repo, "commit", "-qm", "base")

            git(repo, "switch", "-qc", "topic")
            write(repo, "topic.txt", "topic\n")
            git(repo, "add", "--", "topic.txt")
            git(repo, "commit", "-qm", "topic")
            git(repo, "switch", "-q", "main")
            write(repo, "main.txt", "main\n")
            git(repo, "add", "--", "main.txt")
            git(repo, "commit", "-qm", "main")

            git(repo, "merge", "--no-commit", "--no-ff", "-q", "topic")
            git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD")

            # The grouped pathspec recipe cannot record part of a pending merge.
            with self.assertRaises(subprocess.CalledProcessError) as raised:
                git(repo, "commit", "-qm", "group: topic only", "--", "topic.txt")
            self.assertIn("partial commit during a merge", raised.exception.stderr)

            # Committing the whole index preserves the merge topology.
            git(repo, "commit", "-qm", "merge topic")
            parents = git(repo, "rev-list", "--parents", "-n", "1", "HEAD").split()
            self.assertEqual(len(parents), 3)
            self.assertEqual(git(repo, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
