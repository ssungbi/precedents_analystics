import os
import datetime
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

def generate_infographic(analysis_result: dict, output_dir: str = "assets") -> str:
    """
    Generates a PNG infographic from the analysis result using Playwright.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Prepare data
    title = analysis_result.get("title", "Untitled")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    info_text = analysis_result.get("infographic_text", "내용이 없습니다.")
    
    # 2. Render HTML template
    env = Environment(loader=FileSystemLoader("assets"))
    template = env.get_template("infographic_template.html")
    rendered_html = template.render(title=title, date=date_str, infographic_text=info_text)
    
    temp_html_path = os.path.abspath(os.path.join(output_dir, "temp.html"))
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)
        
    # 3. Use Playwright to capture screenshot
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"infographic_{datetime.datetime.now().strftime('%Y%m%d')}_{safe_title}.png"
    output_path = os.path.abspath(os.path.join(output_dir, filename))
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1080})
            page.goto(f"file:///{temp_html_path}")
            # Wait for any fonts/renders
            page.wait_for_timeout(500)
            page.screenshot(path=output_path)
            browser.close()
            
        # Clean up temp html
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
            
        return output_path
    except Exception as e:
        return f"Error generating image: {e}"
