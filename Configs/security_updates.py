#!/usr/bin/env python3
"""Apply reviewed security backports before feed indexing/config generation.

Run from the OpenWrt source directory. Unexpected upstream versions fail closed:
review/remove the overlay when upstream incorporates equivalent or newer fixes.
"""
import argparse
import json
from pathlib import Path
import re

PROFILES = ("re_cs_02_ap",)
CA_VERSION = "20261020"  # APK versions cannot contain Debian's +nmu suffix.
CA_SOURCE = "$(PKG_NAME)_20260816+nmu1.tar.xz"
CA_HASH = "914416a1e44a25733aff51092fe4e27fdec1c9f6e8d1db0b8364922486153134"
GO = {
    "1.27": ("2", "3", "6e7749035cf360f06b2575d162ea79df9fda8ef671889e5c375f8e50777f26bb"),
}
CA = Path("package/system/ca-certificates/Makefile")
GOLANG = Path("feeds/packages/lang/golang")
# Source metadata from immortalwrt/immortalwrt master. Keep ubus and rpcd
# together: rpcd's non-root session checks require libubus's pre_invoke API.
SOURCE_UPDATES = {
    Path("package/network/services/uhttpd/Makefile"): (
        "373145f72c884c36a2b16f7f47e74ffae06bd754",
        "ca796d7dec5697a2d1a7a42be79677f239b64282", "2026-10-19",
        "6a2fbcc0dbd3f6c9d076037f23b8544356487aea6b00d2a82a3591b09ba4a8e4"),
    Path("package/system/ubus/Makefile"): (
        "414c60a2e29e72c2c4f573bc50ad54aef076d169",
        "db20eff5535fe3126c05dc0edc029caf0e82fe10", "2026-10-28",
        "6c877039f5e57429c964848332636439ed1b34b2e9445e51c5ec8e290dab8d0a"),
    Path("package/system/rpcd/Makefile"): (
        "d99f703e4035d03fbcfbada3cb697db346c2b984",
        "469d7852316ef692805396d8af744ec43604b842", "2026-10-28",
        "dec618e00ee5550b360498997fc5c4725526243e22e866aab3d584e919e0603d"),
}


def value(text, name):
    matches = re.findall(r"^" + re.escape(name) + r":=(.*)$", text, re.M)
    if len(matches) != 1:
        raise ValueError(f"Expected one {name} assignment")
    return matches[0].strip()


def replace(text, name, new):
    value(text, name)  # Refuse changed/ambiguous Makefile layouts.
    return re.sub(r"^" + re.escape(name) + r":=.*$", lambda _: f"{name}:={new}", text, flags=re.M)


def update(path, version_key, old, new, checksum, hash_key="PKG_HASH"):
    text = path.read_text()
    current = value(text, version_key)
    if current not in (old, new):
        raise ValueError(f"{path}: unexpected {version_key}={current}; review the backport")
    if current == new:
        if value(text, hash_key) != checksum:
            raise ValueError(f"{path}: patched version has an unexpected source hash")
        return
    text = replace(text, version_key, new)
    text = replace(text, hash_key, checksum)
    text = replace(text, "PKG_RELEASE", "1")
    path.write_text(text)


def apply_source():
    source = value(CA.read_text(), "PKG_SOURCE")
    if source not in ("$(PKG_NAME)_$(PKG_VERSION).tar.xz", CA_SOURCE):
        raise ValueError("Unexpected CA source archive")
    update(CA, "PKG_VERSION", "20260816", CA_VERSION, CA_HASH)
    CA.write_text(replace(CA.read_text(), "PKG_SOURCE", CA_SOURCE))
    for path, (old, new, date, checksum) in SOURCE_UPDATES.items():
        update(path, "PKG_SOURCE_VERSION", old, new, checksum, "PKG_MIRROR_HASH")
        path.write_text(replace(path.read_text(), "PKG_SOURCE_DATE", date))


def apply_feeds(profile):
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


def verify(profile):
    result = {"profile": profile, "packages": {}}
    def check(path, expected):
        text = path.read_text()
        actual = {key: value(text, key) for key in expected}
        if actual != expected:
            raise ValueError(f"{path}: security backport missing: {actual}")
        result["packages"][str(path)] = actual
    check(CA, {"PKG_VERSION": CA_VERSION, "PKG_SOURCE": CA_SOURCE, "PKG_HASH": CA_HASH})
    for path, (_, new, date, checksum) in SOURCE_UPDATES.items():
        check(path, {"PKG_SOURCE_VERSION": new, "PKG_SOURCE_DATE": date, "PKG_MIRROR_HASH": checksum})
    for minor, (_, patch, checksum) in GO.items():
        path = GOLANG / f"golang{minor}/Makefile"
        if path.exists():
            check(path, {"GO_VERSION_MAJOR_MINOR": minor, "GO_VERSION_PATCH": patch, "PKG_HASH": checksum})
    if not (GOLANG / "golang1.27/Makefile").exists():
        raise ValueError("Profile's Go compiler is missing")
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
