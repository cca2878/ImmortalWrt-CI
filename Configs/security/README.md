# Security backports for the pinned RE-CS-02 AP source

Only `re_cs_02_ap` calls `Configs/security_updates.py`. Its source and feed pins
remain unchanged. Hooks apply source updates after cloning, Go updates before
feed indexing, and verify all five recipes before compilation.

* CA source: Debian `20260816+nmu1`, SHA-256 from its `.dsc`:
  https://deb.debian.org/debian/pool/main/c/ca-certificates/ca-certificates_20260816+nmu1.dsc
  This blacklists `emSign ECC Root CA - G3` and `Comodo AAA Services root`.
  The APK package version remains `20261020-r1`; the source archive is explicit
  because APK does not accept Debian's `+nmu1` version suffix.
* Go 1.27.3: source SHA-256 from https://go.dev/dl/?mode=json. The pinned feed
  still contains 1.27.2. No additional compiler recipe is needed.
* uhttpd: source `ca796d7dec5697a2d1a7a42be79677f239b64282` includes the
  unauthenticated out-of-bounds-read fix for non-string ubus list parameters:
  https://github.com/openwrt/uhttpd/commit/64dcf47aa7f84ae60db9a3950e5c4b8fbe5ed6f1
* rpcd: source `469d7852316ef692805396d8af744ec43604b842` enforces session ACLs
  for non-root ubus callers:
  https://github.com/openwrt/rpcd/commit/469d7852316ef692805396d8af744ec43604b842
* ubus: source `db20eff5535fe3126c05dc0edc029caf0e82fe10` supplies the
  `pre_invoke` API required by that rpcd fix. Update these recipes together.

The three git source dates and mirror hashes are copied from
`immortalwrt/immortalwrt` master at
`89f1ef18c888f841633f19f92655ee4b7f7716a4`. Package layout, options and install
rules stay as defined by the AP source. Unknown revisions and incorrect
patched hashes fail closed.

`x86_jp_skylake` now uses unmodified openwrt-25.12 recipes: CA blacklist
patches, Go 1.26.10/1.27.3 and cloudflared 2026.10.6 are upstream. The old CA
overlay would duplicate the blacklist patch, and the old cloudflared version
guard would reject the newer release. The bundled Go recipe and cloudflared
vendor workaround have been removed; cloudflared 2026.10.6 has no vendor tree.

Both profiles use a new `profile-v2` cache namespace. It hashes profile YAML
(including pins and hooks), plus the helper for AP only. Legacy staging outputs
cannot match its exact or restore keys. Start the first full rebuild with
`WRT_CACHE=false` and `WRT_TEST=false`, without source overrides.

The AP audit also checked OpenSSL 3.5.9 and its corrected AES-SIV patch,
hostapd, dropbear, cgi-io and the selected package set. curl and libssh2 recipes
are available through feeds but are not selected in the AP image. The pinned
NSS kernel remains 6.18.55; kernel.org has newer stable releases, but updating
the NSS kernel/patch stack requires a separate compatibility validation.

Diagnostics record verified recipe metadata in `security-updates.json`.
Recipe tests do not replace a complete firmware build or hardware validation.
Flash and restart to replace deployed certificates and binaries.
