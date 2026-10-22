# October 2026 security backports

Only `x86_jp_skylake` and `re_cs_02_ap` call `Configs/security_updates.py`.
The existing WRT-CONTAINER workflow executes source changes in `after_clone`,
feed changes in `after_feeds_update` (before indexing/install/defconfig), and
checks the result in `before_compile`. AP source/feed pins remain unchanged.

* CA source: Debian `20260816+nmu1`, SHA-256 from its `.dsc`:
  https://deb.debian.org/debian/pool/main/c/ca-certificates/ca-certificates_20260816+nmu1.dsc
  Debian blacklists `emSign ECC Root CA - G3` and `Comodo AAA Services root`.
  Both ca-certificates and ca-bundle use the corrected generated certificates.
  The OpenWrt package version is normalized to `20261020-r1`, with an explicit
  `PKG_SOURCE` naming the Debian archive: APK rejects Debian's `+nmu1` suffix.
* Go sources: 1.26.10 and 1.27.3, SHA-256 from https://go.dev/dl/?mode=json
  The fixes block compromised intermediate keys, including alternate chains.
* x86 cloudflared: 2026.10.2, source archive from
  https://codeload.github.com/cloudflare/cloudflared/tar.gz/2026.10.2
  This release requires Go 1.27, so its build dependency explicitly selects
  `golang1.27/host`. Other x86 Go applications retain the patched 1.26 series.
  The archive's vendor metadata is inconsistent with go.mod; append
  `-mod=readonly` to the Go helper's module arguments to use go.mod/go.sum
  without silently changing dependency versions during the build.

The Go 1.27 recipe is copied from immortalwrt/packages master (reviewed against
commit 8d50d4ea3f11eef6f8fcc889cd35ba6fcb530481). Its compiler, bootstrap and
package helpers are identical to openwrt-25.12; only golang-values.mk's default
compiler series differs. The recipe is patched to 1.27.3 before feed indexing.

Package hashes remain mandatory. The script rejects unexpected upstream versions
or source hashes rather than silently overwriting a later upstream update.
Review/remove this overlay when upstream supplies equivalent or newer fixes.
The pinned bootstrap compiler is a build-only tool, not an installed firmware
package. WRT-CONTAINER caches staging directories, so both exact keys and restore
prefixes for these profiles are isolated using a hash of the profile and backport
inputs. Old toolchain/staging caches cannot cross into the security rebuild.
For the first security rebuild use WRT_CACHE=false to start without old outputs.

Build each profile using WRT-CONTAINER on the updated CI branch, with WRT_CONF
set to its profile name, WRT_CACHE=false and WRT_TEST=false. Repository/branch
overrides and WRT_COMMIT should remain empty. WRT_TEST=true checks configuration
and backport application only; it does not compile a firmware image.
Diagnostics include hook logs and `security-updates.json` with checked versions
and hashes. The lightweight security-updates CI tests are not a full firmware
build. Flash/restart is necessary to replace deployed CA stores and Go binaries.

Fixtures in tests/fixtures/security are the original upstream recipes used to
exercise both branches and fail-closed behavior; their upstream license headers
are preserved.
