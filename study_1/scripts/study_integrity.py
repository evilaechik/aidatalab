"""Verify historical fingerprints across the explicitly recorded study cleanup."""
import hashlib
import json
import sqlite3
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
REPO = STUDY.parent
MANIFEST = STUDY / 'provenance/cleanup_manifest.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def historical_match(path, expected, *, allow_removed=False):
    """Require the original bytes or an exact, documented migration transition."""
    path = Path(path).resolve()
    if path.is_file() and sha(path) == expected:
        return True
    if not MANIFEST.is_file():
        return False
    record = json.loads(MANIFEST.read_text())['files'].get(str(path.relative_to(REPO)))
    if not record or record['before_sha256'] != expected:
        return False
    if record['action'] == 'removed':
        return allow_removed and not path.exists()
    if record['action'] == 'relocated':
        target = REPO / record['destination']
        return not path.exists() and target.is_file() and sha(target) == expected
    return path.is_file() and sha(path) == record['after_sha256']


def validate_cleanup():
    """Check every retirement, relocation, edited file and retained new input."""
    manifest = json.loads(MANIFEST.read_text())
    for name, record in manifest['files'].items():
        if record['action'] in {'removed', 'relocated'}:
            assert not (REPO / name).exists(), name
        assert historical_match(REPO / name, record['before_sha256'], allow_removed=True), name
    for name, fingerprint in manifest['added_files'].items():
        path = REPO / name
        assert path.is_file() and sha(path) == fingerprint, name
    return True


def sqlite_matches(path, tables):
    """Avoid rewriting a frozen database when rebuilding identical logical data."""
    import pandas as pd

    path = Path(path)
    if not path.is_file():
        return False
    try:
        with sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True) as existing, sqlite3.connect(':memory:') as expected:
            names = {r[0] for r in existing.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if names != set(tables) or existing.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                return False
            for name, frame in tables.items():
                frame.to_sql(name, expected, index=False, if_exists='replace')
                query = f'SELECT * FROM "{name}"'
                if not pd.read_sql_query(query, existing).equals(pd.read_sql_query(query, expected)):
                    return False
        return True
    except sqlite3.DatabaseError:
        return False
