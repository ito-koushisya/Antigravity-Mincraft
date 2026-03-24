import json
import time
import shutil
from pathlib import Path

class BridgeManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir).resolve()
        self.work_dir = self.base_dir / "mvb_work"
        self.bridge_in = self.work_dir / "bridge_in"
        self.bridge_out = self.work_dir / "bridge_out"
        
        self.bridge_in.mkdir(parents=True, exist_ok=True)
        self.bridge_out.mkdir(parents=True, exist_ok=True)

    def create_prompt(self, request_text):
        # Create a simple prompt structure for the AI
        prompt = {
            "role": "user",
            "content": request_text,
            "instruction": "Generate a MVB plan JSON based on this request."
        }
        
        # Clean output to ensure fresh start
        plan_file = self.bridge_out / "plan.json"
        if plan_file.exists():
            plan_file.unlink()
            
        # Write input
        with open(self.bridge_in / "prompt.json", "w", encoding="utf-8") as f:
            json.dump(prompt, f, indent=2, ensure_ascii=False)
            
        return prompt

    def check_for_plan(self):
        plan_file = self.bridge_out / "plan.json"
        if plan_file.exists():
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
        return None
