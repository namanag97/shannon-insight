"""Author identity resolution and bot filtering.

Canonicalization ladder (cheap -> expensive):
  1. exact (name, email) pair
  2. email normalization (lowercase, gmail dot/+ stripping)
  3. .mailmap entries
  4. same local-part across domains (configurable, default on)
  5. name-token fuzzy match (difflib ratio >= threshold, default off)

Bot detection is rule-based (BoDeGHa-style): name/email substrings plus the
``[bot]`` suffix convention. Bots are excluded from bus-factor, silo and
Conway math upstream.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_BOT_PATTERNS = (
    r"\[bot\]$",
    r"^dependabot",
    r"^renovate",
    r"^greenkeeper",
    r"github-actions",
    r"semantic-release",
    r"^codecov",
    r"^coveralls",
    r"^circleci",
    r"^travis",
    r"^noreply@",
)

_BOT_RE = re.compile("|".join(_BOT_PATTERNS), re.IGNORECASE)


@dataclass(frozen=True)
class AuthorRecord:
    author_id: str
    names: tuple[str, ...]
    emails: tuple[str, ...]
    is_bot: bool


@dataclass
class AuthorResolver:
    """Accumulates raw (name, email) observations into canonical authors."""

    fuzzy_name_threshold: float = 0.0
    merge_same_localpart: bool = True

    _by_email: dict[str, str] = field(default_factory=dict, init=False)
    _by_localpart: dict[str, str] = field(default_factory=dict, init=False)
    _mailmap: dict[str, str] = field(default_factory=dict, init=False)
    _authors: dict[str, dict[str, set[str]]] = field(default_factory=dict, init=False)

    def load_mailmap(self, content: str) -> None:
        """Parse .mailmap format lines::

            Proper Name <proper@email> <commit@email>
            Proper Name <proper@email> Commit Name <commit@email>
        """
        for line in content.splitlines():
            emails = re.findall(r"<([^>]+)>", line)
            if len(emails) == 2:
                self._mailmap[self.normalize_email(emails[1])] = self.normalize_email(emails[0])


    @staticmethod
    def normalize_email(email: str) -> str:
        e = email.strip().lower()
        local, _, domain = e.partition("@")
        if domain in ("gmail.com", "googlemail.com") and local:
            base = local.split("+")[0].replace(".", "")
            return f"{base}@gmail.com"
        return e

    def _is_bot(self, name: str, email: str) -> bool:
        return bool(_BOT_RE.search(name)) or bool(_BOT_RE.search(email))

    def resolve(self, raw_name: str, raw_email: str) -> AuthorRecord:
        norm_raw = self.normalize_email(raw_email)
        email = self._mailmap.get(norm_raw, self._mailmap.get(raw_email.strip().lower(), norm_raw))
        canonical = self._canonical_id(raw_name, email)

        bucket = self._authors.setdefault(canonical, {"names": set(), "emails": set()})
        if raw_name.strip():
            bucket["names"].add(raw_name.strip())
        if email:
            bucket["emails"].add(email)

        return AuthorRecord(
            author_id=canonical,
            names=tuple(sorted(bucket["names"])),
            emails=tuple(sorted(bucket["emails"])),
            is_bot=self._is_bot(raw_name, email),
        )

    def _canonical_id(self, raw_name: str, email: str) -> str:
        if email and email in self._by_email:
            return self._by_email[email]
        local = email.partition("@")[0]
        if (
            self.merge_same_localpart
            and local
            and "@" in email
            and local in self._by_localpart
        ):
            canonical = self._by_localpart[local]
        elif email:
            canonical = email
        else:
            canonical = f"name:{raw_name.strip().lower()}"
        if self.fuzzy_name_threshold > 0 and raw_name.strip() and email:
            canonical = self._fuzzy_merge(raw_name, canonical)
        if email:
            self._by_email.setdefault(email, canonical)
            if local:
                self._by_localpart.setdefault(local, canonical)
        return canonical

    def _fuzzy_merge(self, raw_name: str, canonical: str) -> str:
        from difflib import SequenceMatcher

        target = raw_name.strip().lower()
        for aid, info in self._authors.items():
            for known in info["names"]:
                ratio = SequenceMatcher(None, target, known.lower()).ratio()
                if ratio >= self.fuzzy_name_threshold:
                    return aid
        return canonical

    def records(self) -> list[AuthorRecord]:
        out: list[AuthorRecord] = []
        for aid, info in self._authors.items():
            sample_name = next(iter(info["names"]), "")
            sample_email = next(iter(info["emails"]), "")
            out.append(
                AuthorRecord(
                    author_id=aid,
                    names=tuple(sorted(info["names"])),
                    emails=tuple(sorted(info["emails"])),
                    is_bot=self._is_bot(sample_name, sample_email),
                )
            )
        return sorted(out, key=lambda a: a.author_id)


def filter_human_authors(records: list[AuthorRecord]) -> list[AuthorRecord]:
    return [r for r in records if not r.is_bot]


__all__ = ["AuthorRecord", "AuthorResolver", "filter_human_authors"]
