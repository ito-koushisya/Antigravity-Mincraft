import json
import os
from pathlib import Path

class DatapackGenerator:
    def __init__(self, base_dir, security_manager=None):
        self.base_dir = Path(base_dir).resolve()
        self.security_manager = security_manager
        # Fixed path for datapacks as per spec
        self.datapacks_dir = self.base_dir / "server" / "world" / "datapacks"

    def generate(self, plan_json, pack_format=48):
        """
        Generates the datapack files from the plan_json.
        """
        datapack_config = plan_json["datapack"]
        pack_id = datapack_config["pack_id"]
        namespace = datapack_config["namespace"]
        
        # Define pack root
        pack_root = self.datapacks_dir / pack_id
        
        # Security check (Double check)
        if self.security_manager and not self.security_manager.is_safe_path(pack_root.relative_to(self.base_dir)):
            raise ValueError(f"Unsafe datapack path: {pack_root}")
            
        # Clean/Create directory
        # Note: Spec says "Deletion prohibited", but for identifying collision we might need to know if it exists.
        # However, we are supposed to overwrite/create new.
        # If folder exists, we just overwrite files.
        
        data_dir = pack_root / "data" / namespace / "functions"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Create pack.mcmeta
        mcmeta_content = {
            "pack": {
                "pack_format": pack_format,
                "description": "MVB Safe Pack"
            }
        }
        
        with open(pack_root / "pack.mcmeta", "w", encoding="utf-8") as f:
            json.dump(mcmeta_content, f, indent=2)
            
        # 2. Create functions
        generated_files = [str(pack_root / "pack.mcmeta")]
        
        for func in datapack_config["functions"]:
            func_name = func["name"]
            func_path = data_dir / f"{func_name}.mcfunction"
            
            # Write lines
            with open(func_path, "w", encoding="utf-8") as f:
                for line in func["lines"]:
                    f.write(line + "\n")
            
            generated_files.append(str(func_path))
            
        return generated_files
