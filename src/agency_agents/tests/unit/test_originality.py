"""Originality check: 8-word shingle overlap against the existing roster.

The check is a merge gate, so the tests pin down the three outcomes that
matter: a find-replace re-skin FAILs, a genuinely new agent PASSes, and an
unreadable/mistyped input is reported as skipped instead of counted as a
duplicate. Thresholds are inclusive on the lower bound and the same pair must
flip sides when the threshold moves by a fraction of a point.
"""
import json
import sys
from pathlib import Path

import pytest

from agency_agents.core.originality import (
    _agent_dirs,
    build_corpus,
    is_agent,
    jaccard,
    main,
    rel,
    run_originality_check,
    shingles,
    strip_frontmatter,
    tokens,
)

# 30 distinct words -> 23 distinct 8-word shingles.
BODY_A = " ".join(f"alpha{i}" for i in range(30))
# Shares its first 15 words with BODY_A: 8 shingles in common out of 38.
BODY_OVERLAP = " ".join(f"alpha{i}" for i in range(15)) + " " + " ".join(
    f"beta{i}" for i in range(15)
)
BODY_DISTINCT = " ".join(f"gamma{i}" for i in range(30))


def write_agent(path: Path, name: str, body: str, description: str = "test agent") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n{body}\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "divisions.json").write_text(
        json.dumps({"divisions": {"eng": {"label": "Eng", "icon": "e", "color": "#000"}}}),
        encoding="utf-8",
    )
    return tmp_path


# --------------------------------------------------------------- primitives


def test_strip_frontmatter_removes_the_leading_block() -> None:
    assert strip_frontmatter("---\nname: X\n---\nBody") == "\nBody"


def test_strip_frontmatter_leaves_plain_text_untouched() -> None:
    assert strip_frontmatter("Just body text") == "Just body text"


def test_strip_frontmatter_keeps_unterminated_block() -> None:
    # Only two separators: the block is never closed, so nothing is stripped.
    text = "---\nname: X"
    assert strip_frontmatter(text) == text


def test_tokens_neutralise_entities_before_counting() -> None:
    assert tokens("---\nname: X\n---\nTikTok and Instagram growth") == [
        "and",
        "growth",
    ]


def test_tokens_lowercase_and_split_on_punctuation() -> None:
    assert tokens("AI-driven, 2024!") == ["ai", "driven", "2024"]


def test_shingles_are_overlapping_windows_of_eight_words() -> None:
    words = [f"w{i}" for i in range(10)]
    windows = shingles(words)
    assert len(windows) == 3
    assert " ".join(words[0:8]) in windows
    assert " ".join(words[2:10]) in windows


def test_shingles_of_short_text_is_empty() -> None:
    # A body shorter than k cannot match anything; it must never raise.
    assert shingles(["only", "three words"]) == set()


def test_jaccard_identical_sets_is_one() -> None:
    assert jaccard(shingles(tokens(BODY_A)), shingles(tokens(BODY_A))) == 1.0


def test_jaccard_disjoint_sets_is_zero() -> None:
    assert jaccard(shingles(tokens(BODY_A)), shingles(tokens(BODY_DISTINCT))) == 0.0


def test_jaccard_empty_side_is_zero_not_division_error() -> None:
    assert jaccard(set(), shingles(tokens(BODY_A))) == 0.0


def test_jaccard_partial_overlap_matches_window_count() -> None:
    a = shingles(tokens(BODY_A))
    b = shingles(tokens(BODY_OVERLAP))
    assert a & b and a != b
    assert jaccard(a, b) == pytest.approx(len(a & b) / len(a | b))


# --------------------------------------------------------------- file probes


def test_is_agent_true_for_frontmatter_file(tmp_path: Path) -> None:
    assert is_agent(write_agent(tmp_path / "a.md", "A", BODY_A)) is True


def test_is_agent_false_for_prose_file(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text("# Notes\n\nNo frontmatter here.\n", encoding="utf-8")
    assert is_agent(path) is False


def test_is_agent_false_for_unreadable_path(tmp_path: Path) -> None:
    # A directory cannot be opened as text: OSError must be swallowed.
    assert is_agent(tmp_path) is False


def test_rel_returns_repo_relative_path(repo: Path) -> None:
    assert rel(repo / "eng" / "a.md", repo) == "eng/a.md"


def test_rel_falls_back_to_absolute_for_outside_paths(repo: Path, tmp_path: Path) -> None:
    outside = Path("/definitely/not/in/repo/agent.md")
    assert rel(outside, repo) == str(outside)


# --------------------------------------------------------------- corpus build


def test_agent_dirs_returns_empty_without_divisions_json(tmp_path: Path) -> None:
    assert _agent_dirs(tmp_path) == []


def test_agent_dirs_returns_empty_for_malformed_json(tmp_path: Path) -> None:
    (tmp_path / "divisions.json").write_text("{not json", encoding="utf-8")
    assert _agent_dirs(tmp_path) == []


def test_agent_dirs_are_sorted_division_keys(repo: Path) -> None:
    (repo / "divisions.json").write_text(
        json.dumps({"divisions": {"zeta": {}, "alpha": {}}}), encoding="utf-8"
    )
    assert _agent_dirs(repo) == ["alpha", "zeta"]


def test_build_corpus_indexes_only_frontmatter_files(repo: Path) -> None:
    write_agent(repo / "eng" / "agent.md", "Agent", BODY_A)
    (repo / "eng" / "README.md").write_text("# Read me\n", encoding="utf-8")

    corpus = build_corpus(repo)
    assert [p.name for p in corpus] == ["agent.md"]
    assert corpus[next(iter(corpus))] == shingles(tokens(BODY_A))


def test_build_corpus_includes_nested_directories(repo: Path) -> None:
    write_agent(repo / "eng" / "nested" / "deep.md", "Deep", BODY_A)
    assert [p.name for p in build_corpus(repo)] == ["deep.md"]


# --------------------------------------------------------------- run outcomes


def test_no_agents_anywhere_reports_and_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = run_originality_check(repo_root=tmp_path)
    assert code == 0
    assert "No agent files to check." in capsys.readouterr().out


def test_single_distinct_agent_passes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_agent(repo / "eng" / "agent.md", "Agent", BODY_A)

    assert run_originality_check(repo_root=repo) == 0
    out = capsys.readouterr().out
    assert "[OK   ]" in out
    assert "PASSED" in out
    assert "Thresholds: WARN >= 20%, FAIL >= 40%" in out


def test_audit_flags_two_identical_agents(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_agent(repo / "eng" / "one.md", "One", BODY_A)
    write_agent(repo / "eng" / "two.md", "Two", BODY_A)

    assert run_originality_check(repo_root=repo) == 1
    out = capsys.readouterr().out
    assert "[FAIL ]" in out
    assert "100.0%" in out
    assert "FAILED: 2 agent(s) substantially duplicate existing content" in out
    assert "one.md  ~100% like  eng/two.md" in out


def test_overlapping_pair_warns_but_does_not_fail(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_agent(repo / "eng" / "one.md", "One", BODY_A)
    write_agent(repo / "eng" / "two.md", "Two", BODY_OVERLAP)

    assert run_originality_check(repo_root=repo) == 0
    out = capsys.readouterr().out
    expected = jaccard(shingles(tokens(BODY_A)), shingles(tokens(BODY_OVERLAP))) * 100
    assert "[WARN ]" in out
    assert f"{expected:5.1f}%" in out
    # Both sides of the pair are reported, so the warning count is two.
    assert "2 warning(s) - review for overlap, but not blocking." in out
    assert "PASSED" in out


def test_fail_threshold_is_inclusive(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_agent(repo / "eng" / "one.md", "One", BODY_A)
    write_agent(repo / "eng" / "two.md", "Two", BODY_A)

    # 100% is exactly at the threshold, so the pair is flagged.
    assert run_originality_check(repo_root=repo, fail_threshold=100.0) == 1
    assert "FAILED: 2 agent(s)" in capsys.readouterr().out


def test_pair_just_below_fail_threshold_only_warns(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_agent(repo / "eng" / "one.md", "One", BODY_A)
    write_agent(repo / "eng" / "two.md", "Two", BODY_A)

    # One tenth of a point above 100% moves the same pair out of FAIL.
    assert run_originality_check(repo_root=repo, fail_threshold=100.1, warn_threshold=10.0) == 0
    out = capsys.readouterr().out
    assert "[WARN ]" in out
    assert "FAILED" not in out


def test_explicit_file_outside_repo_is_compared_against_the_corpus(repo: Path, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    write_agent(repo / "eng" / "existing.md", "Existing", BODY_A)
    candidate = write_agent(tmp_path / "candidate.md", "Candidate", BODY_A)

    assert run_originality_check([candidate], repo_root=repo) == 1
    out = capsys.readouterr().out
    assert "FAILED: 1 agent(s)" in out
    assert "eng/existing.md" in out


def test_two_new_candidates_are_compared_as_the_same_change_set(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    first = write_agent(repo / "incoming" / "one.md", "One", BODY_A)
    second = write_agent(repo / "incoming" / "two.md", "Two", BODY_A)

    assert run_originality_check([first, second], repo_root=repo) == 1
    out = capsys.readouterr().out
    assert "(same change set)" in out
    assert "incoming/two.md (same change set)" in out


def test_missing_candidate_is_skipped_not_flagged(repo: Path, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    write_agent(repo / "eng" / "existing.md", "Existing", BODY_A)

    code = run_originality_check([tmp_path / "ghost.md"], repo_root=repo)

    assert code == 0
    out = capsys.readouterr().out
    assert "skip (not found)" in out
    assert "No agent files to check." in out


def test_non_agent_candidate_is_skipped(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_agent(repo / "eng" / "existing.md", "Existing", BODY_A)
    prose = repo / "eng" / "notes.md"
    prose.write_text("# Notes\n\nprose only\n", encoding="utf-8")

    assert run_originality_check([prose], repo_root=repo) == 0
    out = capsys.readouterr().out
    assert "skip (no frontmatter, not an agent)" in out
    assert "eng/notes.md" in out


def test_relative_candidate_paths_resolve_from_cwd(repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    write_agent(repo / "eng" / "existing.md", "Existing", BODY_A)
    write_agent(repo / "eng" / "new.md", "New", BODY_DISTINCT)
    monkeypatch.chdir(repo)

    assert run_originality_check([Path("eng/new.md")], repo_root=repo) == 0
    out = capsys.readouterr().out
    assert "eng/new.md" in out
    # Nothing overlaps, so no closest-match line is printed.
    assert "closest:" not in out
    assert "[OK   ]" in out


def test_thresholds_come_from_environment_when_not_passed(repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    write_agent(repo / "eng" / "one.md", "One", BODY_A)
    write_agent(repo / "eng" / "two.md", "Two", BODY_OVERLAP)
    monkeypatch.setenv("ORIGINALITY_FAIL", "99")
    monkeypatch.setenv("ORIGINALITY_WARN", "95")

    assert run_originality_check(repo_root=repo) == 0
    out = capsys.readouterr().out
    assert "Thresholds: WARN >= 95%, FAIL >= 99%" in out
    assert "0 warning(s)" not in out  # the pair is below both, so it is OK
    assert "[OK   ]" in out


def test_repo_root_comes_from_environment(repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    write_agent(repo / "eng" / "agent.md", "Agent", BODY_A)
    monkeypatch.setenv("REPO_ROOT", str(repo))
    monkeypatch.chdir(repo.parent)

    assert run_originality_check() == 0
    assert "PASSED" in capsys.readouterr().out


def test_main_uses_argv_when_given(repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    write_agent(repo / "eng" / "existing.md", "Existing", BODY_A)
    candidate = write_agent(repo / "eng" / "candidate.md", "Candidate", BODY_A)
    monkeypatch.setenv("REPO_ROOT", str(repo))

    assert main([str(candidate)]) == 1
    assert "FAILED" in capsys.readouterr().out


def test_main_falls_back_to_sys_argv(repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    write_agent(repo / "eng" / "existing.md", "Existing", BODY_A)
    candidate = write_agent(repo / "eng" / "distinct.md", "Distinct", BODY_DISTINCT)
    monkeypatch.setenv("REPO_ROOT", str(repo))
    monkeypatch.setattr(sys, "argv", ["originality", str(candidate)])

    assert main() == 0
    assert "PASSED" in capsys.readouterr().out
