#!/usr/bin/env python3
"""Apply reviewed security backports before feed indexing/config generation.

Run from the OpenWrt source directory. Unexpected upstream versions fail closed:
review/remove the overlay when upstream incorporates equivalent or newer fixes.
"""
import argparse
import json
from pathlib import Path
import re
import shutil

PROFILES = ("x86_jp_skylake", "re_cs_02_ap")
CA_VERSION = "20261020"  # APK versions cannot contain Debian's +nmu suffix.
CA_SOURCE = "$(PKG_NAME)_20260816+nmu1.tar.xz"
CA_HASH = "914416a1e44a25733aff51092fe4e27fdec1c9f6e8d1db0b8364922486153134"
GO = {
    "1.26": ("9", "10", "fd63e883ba2f2bfca93c1646b31ebef63e2b1e4d2b317c9789d976a68d81f36f"),
    "1.27": ("2", "3", "6e7749035cf360f06b2575d162ea79df9fda8ef671889e5c375f8e50777f26bb"),
}
CLOUD_VERSION = "2026.10.2"
CLOUD_HASH = "8dde1e9e4b0ad5ae09abd7b5790dabc9195ba48a5c7f0af7e54e787eef54a3cb"
CA = Path("package/system/ca-certificates/Makefile")
GOLANG = Path("feeds/packages/lang/golang")
CLOUD = Path("feeds/packages/net/cloudflared/Makefile")


def value(text, name):
    matches = re.findall(r"^" + re.escape(name) + r":=(.*)$", text, re.M)
    if len(matches) != 1:
        raise ValueError(f"Expected one {name} assignment")
    return matches[0].strip()


def replace(text, name, new):
    value(text, name)  # Refuse changed/ambiguous Makefile layouts.
    return re.sub(r"^" + re.escape(name) + r":=.*$", lambda _: f"{name}:={new}", text, flags=re.M)


def update(path, version_key, old, new, checksum):
    text = path.read_text()
    current = value(text, version_key)
    if current not in (old, new):
        raise ValueError(f"{path}: unexpected {version_key}={current}; review the backport")
    if current == new:
        if value(text, "PKG_HASH") != checksum:
            raise ValueError(f"{path}: patched version has an unexpected source hash")
        return
    text = replace(text, version_key, new)
    text = replace(text, "PKG_HASH", checksum)
    text = replace(text, "PKG_RELEASE", "1")
    path.write_text(text)


def apply_source():
    source = value(CA.read_text(), "PKG_SOURCE")
    if source not in ("$(PKG_NAME)_$(PKG_VERSION).tar.xz", CA_SOURCE):
        raise ValueError("Unexpected CA source archive")
    update(CA, "PKG_VERSION", "20260816", CA_VERSION, CA_HASH)
    CA.write_text(replace(CA.read_text(), "PKG_SOURCE", CA_SOURCE))


def apply_feeds(profile):
    # 25.12 has Go 1.26 only. The 1.27 recipe uses the same shared compiler,
    # bootstrap and package helpers, verified identical in the two feeds.
    if profile == "x86_jp_skylake" and not (GOLANG / "golang1.27/Makefile").exists():
        target = GOLANG / "golang1.27/Makefile"
        shutil.copytree(Path(__file__).parent / "security/golang1.27", target.parent)
    found = False
    for minor, (old, new, checksum) in GO.items():
        path = GOLANG / f"golang{minor}/Makefile"
        if path.exists():
            if value(path.read_text(), "GO_VERSION_MAJOR_MINOR") != minor:
                raise ValueError(f"{path}: mismatched Go compiler series")
            update(path, "GO_VERSION_PATCH", old, new, checksum)
            found = True
    if not found:
        raise ValueError("No supported Go compiler in packages feed")
    if profile == "x86_jp_skylake":
        update(CLOUD, "PKG_VERSION", "2026.8.3", CLOUD_VERSION, CLOUD_HASH)
        text = CLOUD.read_text()
        if value(text, "PKG_BUILD_DEPENDS") not in ("golang/host", "golang1.27/host"):
            raise ValueError("Unexpected cloudflared build dependencies")
        text = replace(text, "PKG_BUILD_DEPENDS", "golang1.27/host")
        # The release archive's vendor metadata is stale. Use the checked-in
        # go.mod/go.sum without allowing dependency resolution to rewrite them.
        flag = "GO_MOD_ARGS+=-mod=readonly"
        if flag not in text.splitlines():
            include = "include ../../lang/golang/golang-package.mk\n"
            if text.count(include) != 1:
                raise ValueError("Unexpected cloudflared Go helper include")
            text = text.replace(include, include + "\n" + flag + "\n")
        CLOUD.write_text(text)


def verify(profile):
    result = {"profile": profile, "packages": {}}
    def check(path, expected):
        text = path.read_text()
        actual = {key: value(text, key) for key in expected}
        if actual != expected:
            raise ValueError(f"{path}: security backport missing: {actual}")
        result["packages"][str(path)] = actual
    check(CA, {"PKG_VERSION": CA_VERSION, "PKG_SOURCE": CA_SOURCE, "PKG_HASH": CA_HASH})
    for minor, (_, patch, checksum) in GO.items():
        path = GOLANG / f"golang{minor}/Makefile"
        if path.exists():
            check(path, {"GO_VERSION_MAJOR_MINOR": minor, "GO_VERSION_PATCH": patch, "PKG_HASH": checksum})
    required_minor = "1.26" if profile == "x86_jp_skylake" else "1.27"
    if not (GOLANG / f"golang{required_minor}/Makefile").exists():
        raise ValueError("Profile's Go compiler is missing")
    if profile == "x86_jp_skylake":
        if not (GOLANG / "golang1.27/Makefile").exists():
            raise ValueError("cloudflared requires Go 1.27")
        check(CLOUD, {"PKG_VERSION": CLOUD_VERSION, "PKG_HASH": CLOUD_HASH, "PKG_BUILD_DEPENDS": "golang1.27/host"})
        if "GO_MOD_ARGS+=-mod=readonly" not in CLOUD.read_text().splitlines():
            raise ValueError("cloudflared must use its authoritative go.mod/go.sum")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("source", "feeds", "verify"))
    parser.add_argument("profile", choices=PROFILES)
    args = parser.parse_args()
    if args.stage == "source":
        apply_source()
    elif args.stage == "feeds":
        apply_feeds(args.profile)
    else:
        print(json.dumps(verify(args.profile), indent=2))


if __name__ == "__main__":
    main()
