import sys
import json
import os
from dotenv import load_dotenv

import obsidian_exporter
from image_generator import generate_infographic
from obsidian_browser import find_duplicate
import export_to_github

def main():
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: python cli_post_process.py <result_json_path> [raw_text_path]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    raw_text = ""
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except Exception as e:
            print(f"Could not read raw text file: {e}")
            
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)
        
    print(f"▶ Loaded analysis result for case: {result.get('case_no', 'Unknown')}")
    
    # 1. Obsidian Export
    vault_path = os.environ.get("OBSIDIAN_VAULT_PATH")
    if vault_path:
        dup = find_duplicate(result.get("case_no", ""), vault_path)
        if dup:
            print(f"⚠️ Duplicate found in Vault: {dup['filename']}")
            print("Skipping further export operations.")
            sys.exit(0)
            
        print("▶ Exporting to Obsidian...")
        obs_res = obsidian_exporter.save_to_obsidian(vault_path, result, raw_text)
        print(f"  Result: {obs_res}")
    else:
        print("⚠️ OBSIDIAN_VAULT_PATH not set in .env. Skipping Obsidian export.")
            
    # 2. Image Generation
    print("▶ Generating Infographic...")
    try:
        img_path = generate_infographic(result)
        print(f"  Result: {img_path}")
    except Exception as e:
        print(f"  Error generating image: {e}")
    
    # 3. Github Export
    print("▶ Pushing to Github Pages...")
    try:
        github_res = export_to_github.update_github_pages_data("court", result)
        print(f"  Result: {github_res}")
    except Exception as e:
        print(f"  Error exporting to Github: {e}")
        
    print("✅ All post-processing complete!")

if __name__ == "__main__":
    main()
