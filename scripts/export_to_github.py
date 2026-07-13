import os
import json
import subprocess
import datetime

# Path to the cloned Laika repo
LAIKA_REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "laika"))

def update_github_pages_data(precedent_type: str, analysis_result: dict) -> str:
    """
    Updates the precedent data JS file in the Laika repo and pushes to GitHub.
    precedent_type must be either 'court' or 'fss'.
    """
    if precedent_type not in ["court", "fss"]:
        return "Error: Invalid precedent type. Must be 'court' or 'fss'."
        
    js_filename = f"precedent_{precedent_type}_data.js"
    js_filepath = os.path.join(LAIKA_REPO_PATH, js_filename)
    
    if not os.path.exists(js_filepath):
        return f"Error: Laika repo or {js_filename} not found at {js_filepath}. Make sure it is cloned."
        
    # Read existing content
    with open(js_filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Content format is: const court_precedents = [...];
    # We need to parse the JSON array, append the new item, and write back.
    var_name = f"{precedent_type}_precedents"
    prefix = f"const {var_name} = "
    
    if prefix in content:
        json_str = content.split(prefix)[1].rsplit(";", 1)[0].strip()
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            data = []
    else:
        data = []
        
    # Append new data
    new_item = {
        "title": analysis_result.get("title", "Untitled"),
        "case_no": analysis_result.get("case_no", ""),
        "court": analysis_result.get("court", ""),
        "year": analysis_result.get("year", ""),
        "date": analysis_result.get("date", ""),
        "case_type": analysis_result.get("case_type", ""),
        "tags": analysis_result.get("tags", []),
        "favorability": analysis_result.get("favorability", ""),
        "favorability_reason": analysis_result.get("favorability_reason", ""),
        "basic_info": analysis_result.get("basic_info", ""),
        "core_issues": analysis_result.get("core_issues", {}),
        "fact_timeline": analysis_result.get("fact_timeline", []),
        "recognized_facts": analysis_result.get("recognized_facts", []),
        "court_decision": analysis_result.get("court_decision", []),
        "diagnosis_and_liability_date": analysis_result.get("diagnosis_and_liability_date", ""),
        "acceptance_criteria": analysis_result.get("acceptance_criteria", []),
        "rejection_criteria": analysis_result.get("rejection_criteria", []),
        "practical_points": analysis_result.get("practical_points", []),
        "insurer_actual_claim": analysis_result.get("insurer_actual_claim", []),
        "expected_rebuttals": analysis_result.get("expected_rebuttals", []),
        "counter_logic": analysis_result.get("counter_logic", []),
        "cautions": analysis_result.get("cautions", [])
    }
    
    # Avoid exact duplicates by title
    data = [item for item in data if item["title"] != new_item["title"]]
    
    # Prepend new item (newest first)
    data.insert(0, new_item)
    
    # Write back
    new_content = f"{prefix}{json.dumps(data, ensure_ascii=False, indent=4)};\n"
    with open(js_filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    # Push to GitHub
    try:
        # Commit local changes first
        subprocess.run(["git", "add", js_filename], cwd=LAIKA_REPO_PATH, check=True, capture_output=True)
        commit_msg = f"Add new {precedent_type} precedent: {new_item['title']}"
        # Using run without check=True for commit, because it fails if there are no changes to commit
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=LAIKA_REPO_PATH, capture_output=True)
        
        # Pull remote changes using rebase to avoid merge commits and conflicts
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=LAIKA_REPO_PATH, check=True, capture_output=True)
        
        # Push to remote
        subprocess.run(["git", "push", "origin", "main"], cwd=LAIKA_REPO_PATH, check=True, capture_output=True)
        return f"Successfully updated and pushed {js_filename} to GitHub Pages!"
    except subprocess.CalledProcessError as e:
        return f"Data saved locally but Git push failed: {e.stderr.decode('utf-8', errors='ignore')}"
    except FileNotFoundError:
        return "Git command not found. Data saved locally."
