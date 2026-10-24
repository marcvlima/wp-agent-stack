import unittest
import os
import json

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestContract(unittest.TestCase):
    def test_files_exist(self):
        for path in [
            "SKILL.md",
            "skill.json",
            "references/gateway.md",
            "references/products.md",
            "scripts/seed_trae_cache.py",
        ]:
            full = os.path.join(SKILL_DIR, path)
            self.assertTrue(os.path.isfile(full), f"missing {path}")

    def test_skill_md_phrases(self):
        with open(os.path.join(SKILL_DIR, "SKILL.md")) as f:
            text = f.read()
        for phrase in [
            "https://nex-global.risegen.ai/v1",
            "custom_openai_compatible",
            "Full URL",
            "ANTHROPIC_BASE_URL",
            "nemotron-3.5-lightning-30b-a3b-1gpu",
            "gemma-4-26b-a4b-1gpu",
            "billing lane",
            "local-inference-policy",
        ]:
            self.assertIn(phrase, text, f"SKILL.md missing phrase: {phrase}")

    def test_no_gateway_key_leak(self):
        creds_path = os.path.expanduser("~/.risegen/credentials.json")
        if not os.path.isfile(creds_path):
            self.skipTest("credentials.json not found")
            return
        with open(creds_path) as f:
            creds = json.load(f)
        key = creds.get("gateway_api_key", "")
        if not key or len(key) < 20:
            self.skipTest("gateway_api_key missing or too short")
            return
        for root, _dirs, files in os.walk(SKILL_DIR):
            for name in files:
                if name.endswith(".py") and "test" in name.lower():
                    continue
                fpath = os.path.join(root, name)
                try:
                    with open(fpath) as f:
                        content = f.read()
                except Exception:
                    continue
                self.assertNotIn(
                    key,
                    content,
                    f"{os.path.relpath(fpath, SKILL_DIR)} contains gateway_api_key",
                )


if __name__ == "__main__":
    unittest.main()