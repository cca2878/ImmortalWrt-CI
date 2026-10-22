import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/security"
spec = importlib.util.spec_from_file_location("security_updates", ROOT / "Configs/security_updates.py")
security = importlib.util.module_from_spec(spec)
spec.loader.exec_module(security)


class BackportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.previous = Path.cwd()
        os.chdir(self.temp.name)
        self.addCleanup(os.chdir, self.previous)
        security.CA.parent.mkdir(parents=True)
        shutil.copyfile(FIXTURES / "ca.Makefile", security.CA)

    def feed(self, minor):
        target = security.GOLANG / f"golang{minor}/Makefile"
        target.parent.mkdir(parents=True)
        shutil.copyfile(FIXTURES / f"golang{minor}.Makefile", target)

    def test_x86_backports_are_idempotent_and_cloudflared_selects_go127(self):
        self.feed("1.26")
        security.CLOUD.parent.mkdir(parents=True)
        shutil.copyfile(FIXTURES / "cloudflared.Makefile", security.CLOUD)
        for _ in range(2):
            security.apply_source()
            security.apply_feeds("x86_jp_skylake")
            result = security.verify("x86_jp_skylake")
            self.assertEqual(len(result["packages"]), 4)
            self.assertIn("GO_MOD_ARGS+=-mod=readonly", security.CLOUD.read_text().splitlines())
        before = {p: p.read_bytes() for p in Path(".").rglob("Makefile")}
        security.apply_source()
        security.apply_feeds("x86_jp_skylake")
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_ap_keeps_feed_pins_and_does_not_add_cloudflared(self):
        self.feed("1.27")
        security.apply_source()
        security.apply_feeds("re_cs_02_ap")
        self.assertEqual(len(security.verify("re_cs_02_ap")["packages"]), 2)
        self.assertFalse(security.CLOUD.exists())
        self.assertFalse((security.GOLANG / "golang1.26").exists())
        config = yaml.safe_load((ROOT / "Configs/re_cs_02_ap.yml").read_text())
        self.assertIn("^8d50d4ea3f11eef6f8fcc889cd35ba6fcb530481", config["hooks"]["before_feeds_update"])

    def test_changed_upstream_is_rejected_without_overwriting(self):
        original = security.CA.read_text().replace("20260816", "20270101")
        security.CA.write_text(original)
        with self.assertRaises(ValueError):
            security.apply_source()
        self.assertEqual(security.CA.read_text(), original)

    def test_missing_backport_and_wrong_hash_are_rejected(self):
        self.feed("1.27")
        with self.assertRaises(ValueError):
            security.verify("re_cs_02_ap")
        security.apply_source()
        security.apply_feeds("re_cs_02_ap")
        security.CA.write_text(security.CA.read_text().replace(security.CA_HASH, "0" * 64))
        with self.assertRaises(ValueError):
            security.verify("re_cs_02_ap")

    def test_ca_source_version_is_separate_from_apk_package_version(self):
        security.apply_source()
        text = security.CA.read_text()
        self.assertEqual(security.value(text, "PKG_SOURCE"), "$(PKG_NAME)_20260816+nmu1.tar.xz")
        version = security.value(text, "PKG_VERSION") + "-r" + security.value(text, "PKG_RELEASE")
        self.assertRegex(version, r"^\d+(?:\.\d+)*-r\d+$")

    def test_profile_hooks_use_supported_workflow_order(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/WRT-CONTAINER.yml").read_text())
        steps = [s["name"] for s in workflow["jobs"]["core"]["steps"]]
        order = ["Hook - After Clone", "Update Feeds", "Hook - After Feeds Update", "Install Feeds", "Apply Config", "Hook - Before Compile", "Download Packages"]
        positions = [steps.index(name) for name in order]
        self.assertEqual(positions, sorted(positions))
        for profile in security.PROFILES:
            path = ROOT / f"Configs/{profile}.yml"
            hooks = yaml.safe_load(path.read_text())["hooks"]
            for name, stage in (("after_clone", "source"), ("after_feeds_update", "feeds"), ("before_compile", "verify")):
                script = subprocess.check_output(["python3", str(ROOT / "Configs/wrt_cfg.py"), "hook", str(path), name], text=True)
                self.assertEqual(script, hooks[name].strip())
                self.assertIn(f'security_updates.py" {stage} "$WRT_CONF"', script)
                subprocess.run(["bash", "-n"], input=script, text=True, check=True)

    def test_security_rebuild_cannot_restore_legacy_staging_cache(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/WRT-CONTAINER.yml").read_text())
        steps = workflow["jobs"]["core"]["steps"]
        generator = next(s["run"] for s in steps if s["name"] == "Generate Cache Key")
        cache = next(s["with"] for s in steps if s["name"] == "Check Caches")
        self.assertIn('CACHE_SCOPE="${CACHE_SCOPE}-security-${SECURITY_HASH}"', generator)
        for prefix in cache["restore-keys"].splitlines():
            self.assertIn("env.CACHE_SCOPE", prefix)
        # Execute the real key-generation shell with the workflow's paths.
        env = dict(os.environ, WRT_CONF="x86_jp_skylake", WRT_VER="upstream", WRT_HASH="source", PATH_WORKDIR=str(ROOT.parent), PATH_CI=ROOT.name)
        env["GITHUB_ENV"] = str(Path(self.temp.name) / "env")
        subprocess.run(["bash", "-e", "-o", "pipefail", "-c", generator], env=env, check=True, capture_output=True)
        values = Path(env["GITHUB_ENV"]).read_text()
        self.assertIn("CACHE_SCOPE=upstream-x86_jp_skylake-security-", values)
        self.assertIn("CACHE_KEY=upstream-x86_jp_skylake-security-", values)


if __name__ == "__main__":
    unittest.main()
