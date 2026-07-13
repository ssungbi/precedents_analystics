"""
obsidian_browser.py
옵시디언 vault 폴더(20_Precedents)를 읽어
 - 파일 목록 반환
 - 특정 사건번호의 중복 여부 검사
"""
import os
import re


PRECEDENT_SUBFOLDER = "20_Precedents"


def get_vault_path() -> str:
    """Return the configured vault path from env."""
    return os.environ.get("OBSIDIAN_VAULT_PATH", "")


def get_precedent_folder(vault_path: str = "") -> str:
    vp = vault_path or get_vault_path()
    return os.path.join(vp, PRECEDENT_SUBFOLDER)


# ─── File list ────────────────────────────────────────────────────────────────

def list_precedent_files(vault_path: str = "") -> list[dict]:
    """
    Returns a list of dicts for every .md file in 20_Precedents.
    Each dict: { "filename": str, "filepath": str, "case_no": str|None, "title": str|None }
    """
    folder = get_precedent_folder(vault_path)
    if not os.path.isdir(folder):
        return []

    results = []
    for fname in sorted(os.listdir(folder), reverse=True):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(folder, fname)
        case_no, title = _parse_frontmatter(fpath)
        results.append({
            "filename": fname,
            "filepath": fpath,
            "case_no":  case_no,
            "title":    title or fname.replace(".md", ""),
        })
    return results


def _parse_frontmatter(filepath: str):
    """
    Read YAML frontmatter from a markdown file and extract case_no and title.
    Returns (case_no, title) — both may be None.
    """
    case_no = None
    title   = None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(2000)          # only need the top
    except Exception:
        return case_no, title

    # Look for YAML frontmatter block ---...---
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        for line in fm.splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
    
    # Look for "사건번호: XXXX" in the body (first 500 chars after frontmatter)
    cn_match = re.search(r"사건번호[:\s*]+([0-9가-힣]+나[0-9가-힣]+|[0-9가-힣]+)", content)
    if cn_match:
        case_no = cn_match.group(1).strip()

    return case_no, title


# ─── Duplicate check ─────────────────────────────────────────────────────────

def find_duplicate(case_no: str, vault_path: str = "") -> dict | None:
    """
    Given a case_no string, scan the vault for an existing file with the same
    case number. Returns the matching file dict, or None.
    """
    if not case_no:
        return None

    # Normalise for comparison
    norm = _normalise_case_no(case_no)

    for entry in list_precedent_files(vault_path):
        if entry["case_no"] and _normalise_case_no(entry["case_no"]) == norm:
            return entry

        # Also try matching against filename
        if norm in _normalise_case_no(entry["filename"]):
            return entry

    return None


def _normalise_case_no(s: str) -> str:
    """Strip spaces, dashes, dots for loose comparison."""
    return re.sub(r"[\s\-\.년도]", "", s).lower()
