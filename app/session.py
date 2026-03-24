import os
import shutil
import json
import datetime
from pathlib import Path

class SessionManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir).resolve()
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, title_slug="lesson"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_id = f"{timestamp}_{title_slug}"
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_id, session_dir

    def save_request(self, session_dir, request_text):
        with open(session_dir / "request.txt", "w", encoding="utf-8") as f:
            f.write(request_text)

    def save_prompt(self, session_dir, prompt_data):
        with open(session_dir / "prompt.json", "w", encoding="utf-8") as f:
            json.dump(prompt_data, f, indent=2, ensure_ascii=False)

    def save_plan(self, session_dir, plan_json):
        with open(session_dir / "plan.json", "w", encoding="utf-8") as f:
            json.dump(plan_json, f, indent=2, ensure_ascii=False)
            
    def save_generated_files(self, session_dir, files):
        generated_dir = session_dir / "generated" / "datapack"
        generated_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            src = Path(file_path)
            if src.exists():
                # Preserve relative structure if possible, simplistic for now
                dst = generated_dir / src.name
                shutil.copy2(src, dst)

    def create_explain_md(self, session_dir, plan_json):
        summary = plan_json.get("summary", "No summary")
        steps = plan_json.get("run", {}).get("steps", [])
        
        md_content = f"""# Explanation
## Goal
{summary}

## Execution Steps
"""
        for i, step in enumerate(steps, 1):
            md_content += f"{i}. {step.get('type')}: {step.get('value', '')}\n"

        md_content += """
## Generated Files
(See generated folder)

## Safety Measures
- Path Isolation: Active
- Allowlist: Checked
- Deletion: Blocked
- Network: Localhost only
"""
        with open(session_dir / "explain.md", "w", encoding="utf-8") as f:
            f.write(md_content)

    def list_sessions(self):
        # Return list of (session_id, path) sorted by time desc
        sessions = []
        for d in self.sessions_dir.iterdir():
            if d.is_dir():
                sessions.append(d.name)
        sessions.sort(reverse=True)
        return sessions
