import os
import re
import json
from pathlib import Path

class SecurityManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir).resolve()
        self.allowed_commands = [
            r'^say .*',
            r'^title @p .*',
            r'^tellraw @p .*',
            r'^give @p [a-z0-9_:]+( \d+)?',
            r'^effect give @p [a-z0-9_:]+ \d+ \d+( true|false)?',
            r'^summon [a-z0-9_:]+ ~?[-.\d]* ~?[-.\d]* ~?[-.\d]*( \{.*\})?',
            r'^particle [a-z0-9_:]+ .*',
            r'^playsound [a-z0-9_.]+ .*',
            r'^time set (day|night|noon|midnight|\d+)',
            r'^weather (clear|rain|thunder)( \d+)?',
            r'^gamerule [a-zA-Z]+ (true|false|\d+)'
        ]
        # Compiled regex for performance
        self.allowed_patterns = [re.compile(p) for p in self.allowed_commands]

    def is_safe_path(self, path_str):
        """
        Validates if the path is within the BASE_DIR.
        """
        try:
            # resolve() handles symlinks and '..'
            target_path = (self.base_dir / path_str).resolve()
            return str(target_path).startswith(str(self.base_dir))
        except Exception:
            return False

    def validate_plan_json(self, plan_json):
        """
        Validates the structure of the execution plan JSON.
        """
        if plan_json.get("schema_version") != "mvb.plan.v0.1":
            raise ValueError("Invalid schema version")
        
        # Check basic keys
        required_keys = ["title", "datapack", "run"]
        for key in required_keys:
            if key not in plan_json:
                raise ValueError(f"Missing required key: {key}")

        # Check Datapack structure
        datapack = plan_json["datapack"]
        if not re.match(r'^[a-z0-9_]+$', datapack.get("pack_id", "")):
             raise ValueError("Invalid pack_id format")
        if not re.match(r'^[a-z0-9_]+$', datapack.get("namespace", "")):
             raise ValueError("Invalid namespace format")
             
        # Validate commands in functions
        for func in datapack.get("functions", []):
            if not re.match(r'^[a-z0-9_]+$', func.get("name", "")):
                raise ValueError(f"Invalid function name: {func.get('name')}")
            
            for line in func.get("lines", []):
                if not self.check_allowlist(line):
                    raise ValueError(f"Command not allowed: {line}")

        # Validate Run steps
        for step in plan_json["run"].get("steps", []):
            step_type = step.get("type")
            if step_type not in ["reload", "function"]:
                 raise ValueError(f"Invalid step type: {step_type}")
            if step_type == "function":
                 if not re.match(r'^[a-z0-9_:]+$', step.get("value", "")):
                      raise ValueError(f"Invalid function call: {step.get('value')}")

        return True

    def check_allowlist(self, command):
        """
        Checks if the command matches any of the allowed patterns.
        """
        # Comments are allowed
        if command.strip().startswith("#") or command.strip() == "":
            return True
            
        for pattern in self.allowed_patterns:
            if pattern.match(command):
                return True
        return False
