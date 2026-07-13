import os
import datetime
from dotenv import load_dotenv

load_dotenv()

def save_to_obsidian(vault_path: str, analysis_result: dict, raw_text: str) -> str:
    """
    Saves the analysis result and raw text as a markdown file in the Obsidian vault.
    Path: <OBSIDIAN_VAULT_PATH>/20_Precedents/
    """
    if not vault_path:
        return "Warning: Obsidian vault path is not properly configured in .env. Saved locally."
        
    base_folder = os.path.join(vault_path, "20_Precedents")
    os.makedirs(base_folder, exist_ok=True)
    
    # Generate filename based on title and date
    title = analysis_result.get("title", "Untitled")
    # Clean title for filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}_{safe_title}.md"
    file_path = os.path.join(base_folder, filename)
    
    keywords = analysis_result.get("keywords", [])
    tags = [f'"{k}"' for k in keywords]
    tags_str = "\n  - ".join(tags)
    if tags:
        tags_str = "\n  - " + tags_str
    
    markdown_content = f"""---
title: "{title}"
date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
tags:{tags_str}
aliases: []
---
"""
    def to_bullet_list(items):
        if not items:
            return "- 내용 없음"
        if isinstance(items, str):
            return f"- {items}"
        return "\n".join([f"- {item}" for item in items])

    markdown_content += f"""# {title}

## 기본 정보

- 사건번호: {analysis_result.get("case_no", "")}
- 법원: {analysis_result.get("court", "")}
- 선고연도: {analysis_result.get("year", "")}
- 선고일: {analysis_result.get("date", "")}
- 사건유형: {analysis_result.get("case_type", "")}

## 핵심 쟁점

- {analysis_result.get("core_issue", "")}

## 인정 요건

{to_bullet_list(analysis_result.get("acceptance_criteria", []))}

## 배척 요건 또는 한계

{to_bullet_list(analysis_result.get("rejection_criteria", []))}

## 사실관계 요약

{to_bullet_list(analysis_result.get("fact_summary", []))}

## 법원의 판단

{to_bullet_list(analysis_result.get("court_decision", []))}

## 실무 적용 포인트

{to_bullet_list(analysis_result.get("practical_points", []))}

## 보험사 예상 반론

{to_bullet_list(analysis_result.get("expected_rebuttals", []))}

## 반박 논리

{to_bullet_list(analysis_result.get("counter_logic", []))}

---
## 인포그래픽 텍스트
{analysis_result.get("infographic_text", "")}
"""

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return f"Successfully saved to Obsidian: {file_path}"
    except Exception as e:
        return f"Error saving to Obsidian: {e}"
