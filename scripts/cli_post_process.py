import sys
import json
import os
import re
import time
from dotenv import load_dotenv

import obsidian_exporter
from image_generator import generate_infographic
from obsidian_browser import find_duplicate
import export_to_github


def compare_and_supplement_cli(old_markdown: str, new_result: dict):
    """
    Uses Gemini to compare old markdown with new analysis result.
    Returns the supplemented markdown if there's new content, or None if no update is needed.
    """
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        print("langchain_google_genai not installed. Skipping comparison.")
        return None

    MODEL_CASCADE = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ]

    prompt = (
        "당신은 최고의 손해사정사 및 법률 분석가입니다.\n"
        "아래의 기존에 작성된 [기존 마크다운 판례 분석글]과 [새로 추출된 판례 JSON 데이터]를 꼼꼼하게 비교해 주세요.\n\n"
        "## [비교 원칙]\n"
        "1. 단순한 문맥이나 표현의 차이는 무시하세요.\n"
        "2. 새 데이터에 유의미한 보충 내용이 있는지 확인하세요.\n"
        "3. 유의미한 보충 내용이 있다면, 기존 마크다운 글에 추가하여 최종 완성된 마크다운 전체 텍스트만 출력하세요.\n"
        "4. 동일한 경우 NO_UPDATE_NEEDED 만 출력하세요.\n\n"
        "[기존 마크다운 판례 분석글]\n"
        + old_markdown
        + "\n\n[새로 추출된 판례 JSON 데이터]\n"
        + json.dumps(new_result, ensure_ascii=False, indent=2)
    )

    for model_name in MODEL_CASCADE:
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.1)
            response = llm.invoke(prompt)
            content = response.content.strip()

            if "NO_UPDATE_NEEDED" in content:
                return None

            content = re.sub(r"^```markdown\n", "", content)
            content = re.sub(r"^```\n", "", content)
            content = re.sub(r"\n```$", "", content)

            return content
        except Exception as e:
            print(f"  Model {model_name} failed: {e}")
            time.sleep(2)
            continue

    return None


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

    print(f"Loading analysis result for case: {result.get('case_no', 'Unknown')}")

    # 1. Duplicate Check
    vault_path = os.environ.get("OBSIDIAN_VAULT_PATH")
    if vault_path:
        dup = find_duplicate(result.get("case_no", ""), vault_path)
        if dup:
            dup_filepath = dup if isinstance(dup, str) else dup.get("filepath", "")
            print(f"\n[WARNING] Duplicate found: {dup_filepath}")

            # Compare and supplement
            print("Comparing old file with new analysis using AI...")
            try:
                with open(dup_filepath, "r", encoding="utf-8") as f:
                    old_markdown = f.read()

                updated_markdown = compare_and_supplement_cli(old_markdown, result)

                if updated_markdown:
                    print("\n[NEW CONTENT FOUND] Supplementable content detected.")
                    print("=" * 60)
                    print(updated_markdown[:1000] + ("..." if len(updated_markdown) > 1000 else ""))
                    print("=" * 60)

                    confirm = input("\n위 내용으로 기존 파일을 업데이트하시겠습니까? [y/N]: ").strip().lower()
                    if confirm == "y":
                        with open(dup_filepath, "w", encoding="utf-8") as f:
                            f.write(updated_markdown)
                        print(f"[OK] Obsidian file updated: {dup_filepath}")

                        print("Regenerating infographic...")
                        try:
                            img_path = generate_infographic(result)
                            print(f"  Result: {img_path}")
                        except Exception as e:
                            print(f"  Error: {e}")

                        print("Pushing to GitHub Pages...")
                        try:
                            github_res = export_to_github.update_github_pages_data("court", result)
                            print(f"  Result: {github_res}")
                        except Exception as e:
                            print(f"  Error: {e}")

                        print("[DONE] Duplicate supplemented successfully!")
                    else:
                        print("Skipped by user.")
                else:
                    print("[OK] Content is identical. No update needed.")

            except Exception as e:
                print(f"  Error during comparison: {e}")

            sys.exit(0)

        # Not a duplicate - proceed normally
        print("Exporting to Obsidian...")
        obs_res = obsidian_exporter.save_to_obsidian(vault_path, result, raw_text)
        print(f"  Result: {obs_res}")
    else:
        print("[WARNING] OBSIDIAN_VAULT_PATH not set in .env. Skipping Obsidian export.")

    # 2. Image Generation
    print("Generating Infographic...")
    try:
        img_path = generate_infographic(result)
        print(f"  Result: {img_path}")
    except Exception as e:
        print(f"  Error generating image: {e}")

    # 3. Github Export
    print("Pushing to Github Pages...")
    try:
        github_res = export_to_github.update_github_pages_data("court", result)
        print(f"  Result: {github_res}")
    except Exception as e:
        print(f"  Error exporting to Github: {e}")

    print("All post-processing complete!")


if __name__ == "__main__":
    main()
