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
    filename = f"{safe_title}.md"
    file_path = os.path.join(base_folder, filename)
    
    tags = analysis_result.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    
    tags_str = "\n  - ".join([f'"{t}"' for t in tags])
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

    core_issues = analysis_result.get("core_issues", {})
    if isinstance(core_issues, str):
        core_issues = {"direct_issue": core_issues}
        
    markdown_content += f"""# {title}

## 기본 정보

- 사건번호: {analysis_result.get("case_no", "")}
- 법원: {analysis_result.get("court", "")}
- 선고일/판결일: {analysis_result.get("date", "")}
- 사건유형: {analysis_result.get("case_type", "")}
- **소비자 유불리**: {analysis_result.get("favorability", "판단 불가")} ({analysis_result.get("favorability_reason", "")})
{analysis_result.get("basic_info", "")}

## 핵심 쟁점

- **사건 직접 쟁점**: {core_issues.get("direct_issue", "")}
- **약관/법리 쟁점**: {core_issues.get("legal_issue", "")}
- **실무 확장 쟁점**: {core_issues.get("practical_issue", "")}

## 인정 요건

{to_bullet_list(analysis_result.get("acceptance_criteria", []))}

## 배척 요건 또는 한계

{to_bullet_list(analysis_result.get("rejection_criteria", []))}

## 사실관계 타임라인

{to_bullet_list(analysis_result.get("fact_timeline", []))}

## 원문상 인정 사실

{to_bullet_list(analysis_result.get("recognized_facts", []))}

## 법원의 판단

{to_bullet_list(analysis_result.get("court_decision", []))}

## 진단확정일/책임개시일 판단

{analysis_result.get("diagnosis_and_liability_date", "- 내용 없음")}

## 실무 적용 포인트

{to_bullet_list(analysis_result.get("practical_points", []))}

## 보험사 실제 주장

{to_bullet_list(analysis_result.get("insurer_actual_claim", []))}

## 보험사 예상 반론

{to_bullet_list(analysis_result.get("expected_rebuttals", []))}

## 반박 논리

{to_bullet_list(analysis_result.get("counter_logic", []))}

## 주의할 점

{to_bullet_list(analysis_result.get("cautions", []))}

## 관련 노트

- (필요시 작성)

---

## 인포그래픽 텍스트

{analysis_result.get("infographic_text", "- 내용 없음")}
"""

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return f"Successfully saved to Obsidian: {file_path}"
    except Exception as e:
        return f"Error saving to Obsidian: {e}"
