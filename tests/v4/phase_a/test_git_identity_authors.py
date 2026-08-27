"""Gates G4+G5: git extraction, identity chains, author canonicalization."""

import sqlite3

from shannon_insight.facts.git_extractor import canonicalize_authors, classify_intent, extract_git_facts
from shannon_insight.facts.identity import FileChange, FileIdentityResolver
from shannon_insight.facts.models import ChangeType


class TestGitExtractor:
    def test_commit_stream_and_intents(self, git_repo):
        commits, changes = extract_git_facts(git_repo)
        assert len(commits) >= 4  # add, fix, rename, bot-empty
        assert commits == sorted(commits, key=lambda c: c.timestamp), "oldest-first"
        subjects = [c.message_subject for c in commits]
        assert any(s.startswith("fix:") for s in subjects)
        assert classify_intent("fix: correct one() result") == "fix"
        assert classify_intent("refactor: tidy") == "refactor"
        assert classify_intent("initial add") == "other"

    def test_rename_detected(self, git_repo):
        _, changes = extract_git_facts(git_repo)
        renames = [c for c in changes if c.change_type is ChangeType.RENAMED]
        assert len(renames) == 1
        assert renames[0].old_path == "b.py"
        assert renames[0].new_path == "c.py"

    def test_additions_deletions_attached(self, git_repo):
        _, changes = extract_git_facts(git_repo)
        modified = [c for c in changes if c.change_type is ChangeType.MODIFIED and c.new_path == "a.py"]
        assert modified and modified[0].additions is not None

    def test_bot_author_present(self, git_repo):
        commits, _ = extract_git_facts(git_repo)
        assert any("bot" in c.author_email_raw for c in commits)


class TestIdentityChain:
    def _resolve_all(self, git_repo):
        commits, changes = extract_git_facts(git_repo)
        conn = sqlite3.connect(":memory:")
        resolver = FileIdentityResolver(conn)
        for commit in commits:
            for chg in (x for x in changes if x.commit_hash == commit.commit_hash):
                resolver.process_change(
                    commit.commit_hash,
                    commit.timestamp,
                    FileChange(commit.commit_hash, chg.new_path or chg.old_path or "",
                               chg.change_type, old_path=chg.old_path),
                )
        resolver.commit()
        return resolver

    def test_rename_chain_shares_identity(self, git_repo):
        r = self._resolve_all(git_repo)
        b_id = r.resolve("c.py")  # b.py renamed to c.py
        assert b_id is not None
        history = r.get_path_history(b_id)
        paths = [h[0] for h in history]
        assert "b.py" in paths and "c.py" in paths[-1]

    def test_stable_id_across_modify(self, git_repo):
        r = self._resolve_all(git_repo)
        assert r.resolve("a.py") is not None

    def test_readd_gets_new_identity(self, tmp_path):
        import subprocess
        root = tmp_path / "readd"
        root.mkdir()
        env = {"GIT_AUTHOR_NAME": "A", "GIT_AUTHOR_EMAIL": "a@x.com",
               "GIT_COMMITTER_NAME": "A", "GIT_COMMITTER_EMAIL": "a@x.com", "HOME": str(tmp_path)}
        def g(*a):
            subprocess.run(["git", "-C", str(root), *a], capture_output=True, env=env, check=True)
        g("init", "-q")
        (root / "f.txt").write_text("v1")
        g("add", "."); g("commit", "-qm", "add")
        (root / "f.txt").unlink(); g("add", "-A"); g("commit", "-qm", "del")
        (root / "f.txt").write_text("v2")
        g("add", "."); g("commit", "-qm", "re-add")

        commits, changes = extract_git_facts(root)
        conn = sqlite3.connect(":memory:")
        r = FileIdentityResolver(conn)
        for c in commits:
            for chg in (x for x in changes if x.commit_hash == c.commit_hash):
                r.process_change(c.commit_hash, c.timestamp,
                                 FileChange(c.commit_hash, chg.new_path or "", chg.change_type, old_path=chg.old_path))
        stats = r.stats()
        assert stats["total_identities"] == 2  # original + re-add


class TestAuthors:
    def test_gmail_normalization_merges(self):
        from shannon_insight.facts.authors import AuthorResolver
        r = AuthorResolver()
        a = r.resolve("Alice", "a.b+x@gmail.com")
        b = r.resolve("Alice B", "ab@gmail.com")
        assert a.author_id == b.author_id

    def test_mailmap(self):
        from shannon_insight.facts.authors import AuthorResolver
        r = AuthorResolver()
        r.load_mailmap("Alice <alice@real.com> Ali <old@legacy.com>")
        a = r.resolve("Ali", "old@legacy.com")
        assert a.author_id == "alice@real.com"

    def test_localpart_merge_across_domains(self):
        from shannon_insight.facts.authors import AuthorResolver
        r = AuthorResolver()
        a = r.resolve("Bob", "bob@corp.com")
        b = r.resolve("Bob", "bob@personal.io")
        assert a.author_id == b.author_id

    def test_bots_flagged_and_isolated(self):
        from shannon_insight.facts.authors import AuthorResolver, filter_human_authors
        r = AuthorResolver()
        records = [
            r.resolve("dependabot[bot]", "bot@github.com"),
            r.resolve("Renovate Bot", "renovate@whitesource.io"),
            r.resolve("Alice", "alice@example.com"),
        ]
        bots = [x for x in records if x.is_bot]
        humans = filter_human_authors(records)
        assert len(bots) == 2 and len(humans) == 1

    def test_canonicalize_rewrites_commits(self, git_repo):
        commits, _ = extract_git_facts(git_repo)
        out, records = canonicalize_authors(commits)
        ids = {c.author_id for c in out}
        known = {r.author_id for r in records}
        assert ids <= known
        assert any(r.is_bot for r in records)
