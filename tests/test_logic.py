import unittest
import shutil
from pathlib import Path
from app.security import SecurityManager
from app.datapack import DatapackGenerator

class TestMVBLogic(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("./test_env").resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        (self.base_dir / "server" / "world" / "datapacks").mkdir(parents=True, exist_ok=True)
        self.security = SecurityManager(self.base_dir)
        self.generator = DatapackGenerator(self.base_dir, self.security)

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_security_path(self):
        self.assertTrue(self.security.is_safe_path("server/world"))
        self.assertFalse(self.security.is_safe_path("../outside"))
        self.assertFalse(self.security.is_safe_path("/etc/passwd"))

    def test_security_allowlist(self):
        self.assertTrue(self.security.check_allowlist("say Hello"))
        self.assertTrue(self.security.check_allowlist("give @p minecraft:diamond 1"))
        self.assertFalse(self.security.check_allowlist("op player"))
        self.assertFalse(self.security.check_allowlist("execute as @a run say hi"))

    def test_datapack_generation(self):
        plan = {
            "title": "Test Pack",
            "datapack": {
                "pack_id": "test_pack",
                "namespace": "test_ns",
                "functions": [
                    {
                        "name": "helloworld",
                        "lines": ["say Hello World"]
                    }
                ]
            },
            "schema_version": "mvb.plan.v0.1",
            "run": {"steps": []} # Minimal
        }
        
        generated = self.generator.generate(plan)
        pack_dir = self.base_dir / "server" / "world" / "datapacks" / "test_pack"
        
        self.assertTrue(pack_dir.exists())
        self.assertTrue((pack_dir / "pack.mcmeta").exists())
        self.assertTrue((pack_dir / "data" / "test_ns" / "functions" / "helloworld.mcfunction").exists())
        
        with open(pack_dir / "data" / "test_ns" / "functions" / "helloworld.mcfunction", "r") as f:
            content = f.read()
            self.assertIn("say Hello World", content)

if __name__ == '__main__':
    unittest.main()
