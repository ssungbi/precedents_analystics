# 손사봇 판례 분석 스킬 (SonsaBot Legal Precedent Analyzer)

오픈클로(OpenCLO)나 안티그래비티(Antigravity) 같은 에이전트 시스템에서 사용할 수 있는 판례 분석 전용 **스킬(Skill)** 입니다.

이 스킬을 설치하면, 채팅창에 판례 PDF나 웹페이지 URL을 던져주는 것만으로 에이전트가 알아서 14개 항목에 걸쳐 초정밀 분석을 수행하고, 옵시디언 마크다운 저장, 인포그래픽 이미지 생성, 깃허브 웹페이지 연동까지 완벽하게 백그라운드에서 처리해 줍니다.

## 📦 설치 방법

1. **저장소 복제 (Clone)**
   본 저장소의 폴더명을 `sonsabot` 등의 적당한 이름으로 변경하여 에이전트의 전역 또는 워크스페이스 스킬 폴더 안에 넣습니다.
   - 전역(Global): `C:\Users\SB\.gemini\config\skills\sonsabot\`
   - 지역(Workspace): `[프로젝트 경로]\.agents\skills\sonsabot\`

2. **의존성 패키지 설치**
   스킬이 사용하는 파이썬 패키지를 설치해야 합니다.
   ```bash
   pip install -r requirements.txt
   ```

3. **환경 변수 세팅 (`.env`)**
   에이전트가 구동되는 워크스페이스 경로에 `.env` 파일을 생성하고 다음 값을 입력합니다.
   ```ini
   # 필수
   OBSIDIAN_VAULT_PATH="C:/Users/SB/Documents/손사봇볼트"
   
   # 선택 (블로그 등 연동 시)
   NAVER_BLOG_ID="bsbo321"
   ```

## 🚀 사용법

에이전트에게 자연어로 지시만 하면 됩니다.
> "바탕화면에 있는 판례.pdf 분석해서 옵시디언에 넣어줘."
> "이번에 올라온 대법원 2023다12345 판결문 URL 분석해줘."

에이전트가 `SKILL.md`를 읽고 알아서 `scripts/cli_post_process.py`를 가동하여 후처리를 완수합니다.

## 📂 구성 요소
- `SKILL.md`: 에이전트가 이 스킬을 언제 어떻게 구동해야 하는지에 대한 프롬프트
- `scripts/cli_post_process.py`: 에이전트가 도출한 JSON 분석 결과를 받아 옵시디언/이미지/깃허브 저장을 오케스트레이션하는 메인 처리기
- `scripts/obsidian_exporter.py`: 옵시디언 마크다운 노트 포매터 및 저장기
- `scripts/obsidian_browser.py`: 옵시디언 볼트 내 중복 판례 탐색기
- `scripts/image_generator.py`: 판례 내용을 바탕으로 인포그래픽 이미지 생성 (Pillow)
- `scripts/export_to_github.py`: 라이카(laika) 깃허브 웹페이지용 JSON 데이터 업데이트 및 Git Push 자동화 (GitPython)
