from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

# Externally observable Git semantics that the smart-commit and smart-squash
# guidance depends on. These tests exercise the mechanisms in disposable
# repositories rather than asserting on Markdown prose.

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
            self.assertEqual(git(repo, "show", "HEAD:generated-mirror.txt"), "mirror v2\n")
            self.assertEqual(git(repo, "status", "--porcelain"), "?? build/\n")


class GitReachabilityPreflightTest(unittest.TestCase):
    def test_reachability_separates_shared_refs_from_upstream_difference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            bare = base / "remote.git"
            run(base, "git", "-c", "init.defaultBranch=main", "init", "-q", "--bare", str(bare))
            repo = base / "work"
            run(base, "git", "clone", "-q", str(bare), str(repo))

            write(repo, "base.txt", "base\n")
            git(repo, "add", "--", "base.txt")
            git(repo, "commit", "-qm", "base")
            git(repo, "push", "-q", "-u", "origin", "main")
            git(repo, "fetch", "--all", "--tags")

            # C1 is reachable from a second pushed branch and a pushed tag, but not
            # from the configured upstream. C2 is reachable from no remote ref.
            write(repo, "c1.txt", "c1\n")
            git(repo, "add", "--", "c1.txt")
            git(repo, "commit", "-qm", "C1 reached by topic and tag")
            c1 = git(repo, "rev-parse", "HEAD").strip()
            git(repo, "push", "-q", "origin", "HEAD:refs/heads/topic")
            git(repo, "tag", "shared-tag", c1)
            git(repo, "push", "-q", "origin", "refs/tags/shared-tag")
            git(repo, "tag", "-d", "shared-tag")
            git(repo, "fetch", "--all", "--tags")

            write(repo, "c2.txt", "c2\n")
            git(repo, "add", "--", "c2.txt")
            git(repo, "commit", "-qm", "C2 local only")
            c2 = git(repo, "rev-parse", "HEAD").strip()

            # The old upstream difference lists both commits as "unpublished".
            difference = git(repo, "rev-list", "@{u}..HEAD").split()
            self.assertIn(c1, difference)
            self.assertIn(c2, difference)

            # Reachability, not difference: C1 is published via a known shared ref.
            remote_contains = git(
                repo,
                "for-each-ref",
                "--contains",
                c1,
                "--format=%(refname:short)",
                "refs/remotes/",
            ).split()
            tag_contains = git(
                repo,
                "for-each-ref",
                "--contains",
                c1,
                "--format=%(refname:short)",
                "refs/tags/",
            ).split()
            self.assertIn("origin/topic", remote_contains)
            self.assertIn("shared-tag", tag_contains)

            # C2 is absent from every fetched remote-tracking ref and tag.
            for refspace in ("refs/remotes/", "refs/tags/"):
                contains = git(
                    repo,
                    "for-each-ref",
                    "--contains",
                    c2,
                    "--format=%(refname:short)",
                    refspace,
                ).strip()
                self.assertEqual(contains, "")

    def test_no_remote_leaves_remote_tracking_refs_empty(self) -> None:
        # A repository with no remote yields no remote-tracking refs to test
        # against, which the preflight must report as an unknown rather than as
        # evidence that the commits are unpushed.
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = init_repo(Path(temp_dir) / "repo")
            write(repo, "x.txt", "x\n")
            git(repo, "add", "--", "x.txt")
            git(repo, "commit", "-qm", "local commit")

            self.assertEqual(git(repo, "remote"), "")
            self.assertEqual(
                git(repo, "for-each-ref", "--format=%(refname)", "refs/remotes/"), ""
            )


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


class GitRootRangeRecipeTest(unittest.TestCase):
    SKILL = Path(__file__).resolve().parents[1] / "src/skills/git/smart-squash/SKILL.md"

    @classmethod
    def published_option3_line(cls) -> str:
        text = cls.SKILL.read_text(encoding="utf-8")
        return next(
            line for line in text.splitlines() if line.startswith("    3) RANGE_LABEL=")
        )

    @staticmethod
    def eval_option3(repo: Path, line: str) -> dict[str, object]:
        # Evaluates the option-3 selection assignments (source text by
        # default, a doctored line for the sensitivity check) and returns the
        # selected RANGE_LABEL and RANGE_ARGS.
        assignments = line.split(") ", 1)[1].rsplit(" ;;", 1)[0].strip()
        script = (
            "set -e\n"
            f"TARGET_REPO={str(repo)!r}\n"
            f"{assignments}\n"
            'printf \'%s\\n---\\n%s\\n\' "$RANGE_LABEL" "${RANGE_ARGS[*]}"\n'
        )
        output = run(repo, "bash", "-c", script)
        label, remainder = output.split("\n---\n", 1)
        args = remainder.split()
        return {"label": label, "args": args}

    @classmethod
    def published_rebase_dispatch(cls, repo: Path, label: str) -> str:
        # Executes the published rebase-command dispatch with the
        # source-selected RANGE_LABEL. The condition and both rebase commands
        # are extracted verbatim from the Skill; only the shared
        # GIT_SEQUENCE_EDITOR line-continuation prefix (identical in both
        # branches) is mechanically stripped so the sequence editor can be
        # injected through the environment.
        lines = cls.SKILL.read_text(encoding="utf-8").splitlines()
        start = next(
            i
            for i, line in enumerate(lines)
            if line.startswith('if [ "$RANGE_LABEL" = "--root" ]; then')
        )
        commands = [
            line.strip()
            for line in lines[start:]
            if "git -C \"$TARGET_REPO\" rebase -i" in line
        ]
        assert len(commands) == 2, "published rebase dispatch not found"
        return (
            "set -e\n"
            f"TARGET_REPO={str(repo)!r}\n"
            f"RANGE_LABEL={label!r}\n"
            'BASE_COMMIT="$(git -C "$TARGET_REPO" rev-list --max-parents=0 HEAD)"\n'
            'if [ "$RANGE_LABEL" = "--root" ]; then\n'
            f"  {commands[0]}\n"
            "else\n"
            f"  {commands[1]}\n"
            "fi\n"
        )

    def run_dispatch_capture_todo(self, repo: Path, base: Path, label: str) -> str:
        todo = base / f"todo-{label.replace(' ', '_')}.txt"
        env = {
            **os.environ,
            **GIT_ENV,
            "GIT_SEQUENCE_EDITOR": f"cat > {todo}",
            "GIT_EDITOR": "true",
        }
        subprocess.run(
            ["bash", "-c", self.published_rebase_dispatch(repo, label)],
            cwd=repo,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        return todo.read_text(encoding="utf-8")

    def make_two_commit_repo(self, temp_dir: str) -> tuple[Path, Path, str]:
        base = Path(temp_dir)
        bare = base / "remote.git"
        run(base, "git", "-c", "init.defaultBranch=main", "init", "-q", "--bare", str(bare))
        repo = base / "work"
        run(base, "git", "clone", "-q", str(bare), str(repo))
        write(repo, "one.txt", "one\n")
        git(repo, "add", "--", "one.txt")
        git(repo, "commit", "-qm", "one")
        root = git(repo, "rev-parse", "HEAD").strip()
        write(repo, "two.txt", "two\n")
        git(repo, "add", "--", "two.txt")
        git(repo, "commit", "-qm", "two")
        return base, repo, root

    @staticmethod
    def pick_lines(todo: str) -> list[str]:
        return [line for line in todo.splitlines() if line.startswith("pick ")]

    def test_root_range_rebase_selection_includes_the_root_commit(self) -> None:
        # The source-selected label must drive the published dispatch so the
        # all-history range rewrites from the root; a label the dispatch does
        # not recognize would silently exclude the root commit.
        with tempfile.TemporaryDirectory() as temp_dir:
            base, repo, root = self.make_two_commit_repo(temp_dir)
            selected = self.eval_option3(repo, self.published_option3_line())
            self.assertEqual(selected["label"], "--root")

            todo = self.run_dispatch_capture_todo(repo, base, str(selected["label"]))
            root_short = git(repo, "rev-parse", "--short", root).strip()
            self.assertTrue(
                any(line.split()[1] == root_short for line in self.pick_lines(todo)),
                "the published --root rebase selection must include the root "
                "commit in the rebase plan",
            )
            self.assertEqual(
                len(git(repo, "rev-list", "HEAD").split()), 2,
                "no-op rebase must preserve the commit count",
            )

    def test_root_range_regression_detects_a_broken_label(self) -> None:
        # Sensitivity check: the previously broken label must change the
        # observable dispatch outcome, otherwise the regression above guards
        # nothing.
        with tempfile.TemporaryDirectory() as temp_dir:
            base, repo, root = self.make_two_commit_repo(temp_dir)
            broken = self.published_option3_line().replace(
                'RANGE_LABEL="--root"', 'RANGE_LABEL="--root HEAD"'
            )
            selected = self.eval_option3(repo, broken)

            todo = self.run_dispatch_capture_todo(repo, base, str(selected["label"]))
            root_short = git(repo, "rev-parse", "--short", root).strip()
            self.assertFalse(
                any(line.split()[1] == root_short for line in self.pick_lines(todo)),
                "a label the published dispatch does not recognize must "
                "exclude the root commit from the rebase plan, so the "
                "regression above fails",
            )

    def test_root_range_recipe_classifies_pushed_commits(self) -> None:
        # Executes the published no-upstream "all commits" recipe from range
        # selection through guarded enumeration to classification; the range
        # must name an explicit revision, and enumeration failure must not be
        # silently swallowed by the loop.
        with tempfile.TemporaryDirectory() as temp_dir:
            base, repo, root = self.make_two_commit_repo(temp_dir)
            # Only the first commit is published; the second stays local so the
            # two reachability classes are both observable.
            git(repo, "push", "-q", "origin", f"{root}:refs/heads/main")
            git(repo, "fetch", "--all", "--tags")

            # The old root form without an explicit revision is a usage error
            # that a bare `for ... in $(...)` loop would silently swallow.
            with self.assertRaises(subprocess.CalledProcessError):
                git(repo, "rev-list", "--root", "--reverse")

            # Selection assignments exactly as published, then guarded
            # enumeration with the selected arguments.
            selected = self.eval_option3(repo, self.published_option3_line())
            self.assertIn("HEAD", selected["args"])
            candidates = git(repo, "rev-list", *selected["args"], "--reverse").split()
            self.assertEqual(len(candidates), 2)

            classifications: dict[str, str] = {}
            for commit in candidates:
                shared_refs = git(
                    repo,
                    "for-each-ref",
                    "--contains",
                    commit,
                    "--format=%(refname:short)",
                    "refs/remotes/",
                    "refs/tags/",
                ).split()
                if shared_refs:
                    classifications[commit] = "PUBLISHED"
                else:
                    classifications[commit] = "UNPUSHED-ON-KNOWN-REFS"

            self.assertEqual(
                sorted(classifications.values()), ["PUBLISHED", "UNPUSHED-ON-KNOWN-REFS"]
            )


if __name__ == "__main__":
    unittest.main()
