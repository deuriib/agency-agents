import pytest
from pathlib import Path
from agency_agents.infrastructure.catalog import CatalogManager
from agency_agents.core.validator import LintEngine

def test_divisions_consistency(tmp_path):
    # Create a dummy divisions.json
    import json
    divs = {"divisions": {"engineering": {"label": "Eng", "icon": "Code", "color": "blue"}}}
    with open(tmp_path / "divisions.json", "w") as f:
        json.dump(divs, f)
    
    # Create the corresponding directory
    (tmp_path / "engineering").mkdir()
    
    engine = LintEngine(tmp_path)
    errors = engine.check_divisions_consistency()
    assert len(errors) == 0

def test_divisions_mismatch(tmp_path):
    import json
    divs = {"divisions": {"missing": {"label": "M", "icon": "I", "color": "C"}}}
    with open(tmp_path / "divisions.json", "w") as f:
        json.dump(divs, f)
    
    engine = LintEngine(tmp_path)
    errors = engine.check_divisions_consistency()
    assert any("missing" in e for e in errors)
