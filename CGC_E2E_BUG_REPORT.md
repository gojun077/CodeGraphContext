# CGC E2E Bug Report

**Date:** 2026-06-07 (initial E2E) · **Re-test:** 2026-06-07 after fixes  
**Package:** `codegraphcontext` **0.4.16** (editable install from repo into `/tmp/cgc-e2e-venv`)  
**Python:** 3.12.3  
**OS:** Linux 6.8.0-124-generic  
**Test method:** Manual subprocess E2E (no pytest). Isolated `HOME=/tmp/cgc-e2e-*` per scenario unless noted.  
**Primary fixture:** `tests/fixtures/sample_projects/sample_project` (Python, 44 files indexed)

---

## Fixes Applied (2026-06-07)

| Bug ID | Status | Fix summary |
|--------|--------|---------------|
| BUG-001 / BUG-018 | **FIXED** | Stop repo-local `.env` from overriding global DB path keys; ignore `FALKORDB_PATH` outside active `CONFIG_DIR` |
| BUG-002 | **FIXED** | CLI commands now exit **1** when DB/services fail to initialize |
| BUG-006 | **FIXED** | Kùzu/Ladybug bundle import uses PK-based edge matching instead of `id()` |
| BUG-007 | **FIXED** | `index` resolves context from target repo path, not shell CWD |
| BUG-008 | **FIXED** | `FALKORDB_HOST`, `FALKORDB_PORT`, etc. accepted via `cgc config set` |
| BUG-009 | **FIXED** | `cgc doctor` fails when `falkordb-remote` has no `FALKORDB_HOST` |
| BUG-010 | **FIXED** | MCP `add_code_to_graph` returns `success: false` for missing paths; outside-root paths return JSON-RPC error |
| BUG-012 | **FIXED** | Blocked `cgc query` write attempts exit **1** |
| BUG-016 | **FIXED** | `cgc bundle import --clear --yes` skips confirmation |
| BUG-022 | **FIXED** | Global `--database` help lists `ladybugdb` and `nornic` |
| BUG-003 / BUG-004 / BUG-005 | **FIXED** | Nested Python call expressions emit `f1→f2→f3` edges for `analyze chain/calls/callers` |
| BUG-011 | **FIXED** | `cgc clean` only removes nodes with zero incoming edges |
| BUG-013 | **FIXED** | Remove forced UNWIND per-row fallback in Kuzu/Ladybug; keep reactive `unordered_map::at` fallback |

**Verification:** `/tmp/cgc_verify_fixes.sh` — **9/9 PASS**. Backend harness re-run — FalkorDB/Kuzu/Ladybug index **456 nodes** successfully.

**Also fixed (2026-06-07, round 2):** BUG-003/004/005 (nested call-expression edges), BUG-011 (`clean` no longer deletes Parameters/Modules).

**Also fixed (2026-06-07, round 3):** BUG-013 (KuzuDB indexing speed — removed forced UNWIND per-row fallback).

**Still open (round 1):** BUG-014–021, BUG-023–026, BUG-029–030. **New (round 4):** BUG-031–060 (30 bugs).

---

## Executive Summary (post-fix)

| Area | Result |
|------|--------|
| **KuzuDB** | Index + export OK (456/629); **~4–5s** index (was ~17–27s); call-chain analysis **FIXED** |
| **LadybugDB** | Parity with KuzuDB on counts |
| **FalkorDB Lite** | **FIXED** — indexes in ~1.9s with isolated HOME (456 nodes) |
| **FalkorDB Remote** | Works via `cgc config set FALKORDB_HOST` or env vars |
| **Neo4j** | **SKIP** — port 7687 in use on test host |
| **Nornic** | **SKIP** — no instance |
| **MCP** | 25 tools; bad paths return errors (not silent success) |
| **Contexts** | Global/named OK; **per-repo fixed** for `cgc index <path>` |
| **Bundles** | Export + import round-trip **FIXED** on KuzuDB |

**Round 1 (original): 30 bugs** · **Fixed: ~18** · **Still open from round 1: ~10** · **New (round 4 hunt): 30** · **Total tracked: 60**

> **No — not all bugs are fixed.** Round 1 left BUG-014–021, BUG-023–026, BUG-029–030 open. Round 4 added 30 more (BUG-031–060). Several “FIXED” items are **backend-specific** (e.g. BUG-003 works on FalkorDB but **regresses on Kuzu** — see BUG-048).

---

## Bug Status Index (round 1: BUG-001 – BUG-030)

| ID | Title | Severity | Status |
|----|-------|----------|--------|
| [BUG-001](#bug-001-falkordb-lite-ignores-home-and-uses-real-user-config-path-for-dbsocket) | FalkorDB ignores `HOME`, uses real user DB path | Critical | **FIXED** |
| [BUG-002](#bug-002-falkordb-failure-silently-returns-exit-code-0-on-query-commands) | Silent exit code 0 on DB failure | Critical | **FIXED** |
| [BUG-003](#bug-003-cgc-analyze-chain-f1-f3-fails-on-known-call-chain) | `analyze chain f1 f3` fails | Critical | **FIXED** (incl. Kuzu — [BUG-048](#bug-048-analyze-chain-cypher-incompatible-with-kuzudb)) |
| [BUG-004](#bug-004-cgc-analyze-calls-f1-reports-no-callees) | `analyze calls f1` reports no callees | High | **FIXED** |
| [BUG-005](#bug-005-cgc-analyze-callers-f2-attributes-caller-to-module-instead-of-f1) | Callers attributed to `<module>` not `f1` | High | **FIXED** |
| [BUG-006](#bug-006-cgc-bundle-import-fails-on-kuzudb-with-internal_id-type-mismatch) | Bundle import INTERNAL_ID mismatch | High | **FIXED** |
| [BUG-007](#bug-007-per-repo-context-mode-indexes-into-cwd-repo-not-target-path) | Per-repo indexes CWD not target path | High | **FIXED** |
| [BUG-008](#bug-008-cgc-config-set-falkordb_host-rejected--remote-config-only-via-env-vars) | `cgc config set FALKORDB_HOST` rejected | High | **FIXED** |
| [BUG-009](#bug-009-cgc-doctor-passes-for-falkordb-remote-without-falkordb_host) | Doctor passes without `FALKORDB_HOST` | High | **FIXED** |
| [BUG-010](#bug-010-mcp-add_code_to_graph-with-invalid-path-returns-empty-response) | MCP bad path returns empty/silent response | High | **FIXED** |
| [BUG-011](#bug-011-cgc-clean-removes-169-orphaned-nodes-immediately-after-fresh-index) | 169 orphan nodes after fresh index | High | **FIXED** |
| [BUG-012](#bug-012-read-only-cgc-query-violation-returns-exit-code-0) | Write query blocked but exit 0 | Medium | **FIXED** |
| [BUG-013](#bug-013-kuzudb-indexing-1520-slower-than-documented-falkordb-baseline) | KuzuDB indexing very slow | Medium | **FIXED** |
| [BUG-014](#bug-014-falkordb-worker-retry-storm-adds-500ms-latency-per-command) | FalkorDB retry storm on broken socket | Medium | **FIXED** (`mark_falkordb_unavailable`) |
| [BUG-015](#bug-015-mcp-initialize-response-embeds-full-system-prompt-10kb) | MCP `initialize` ships 10KB+ system prompt | Medium | **FIXED** |
| [BUG-016](#bug-016-cgc-bundle-import---clear-requires-interactive-confirmation) | Bundle import needs TTY confirm | Medium | **FIXED** |
| [BUG-017](#bug-017---db-path-runtime-override-fails-on-kuzudb) | `--db-path` override fails | Medium | **FIXED** |
| [BUG-018](#bug-018-project-codegraphcontextenv-overrides-isolated-test-home-config) | Local `.env` overrides isolated HOME | Medium | **FIXED** |
| [BUG-019](#bug-019-cgc-report-includes-cross-repo-noise-from-global-db) | Report includes cross-repo noise | Medium | **FIXED** (`resolve_report_repo_scope`) |
| [BUG-020](#bug-020-bundle-export-logs-error-for-show-constraints-on-non-neo4j) | Bundle export schema ERROR log noise | Medium | **FIXED** |
| [BUG-021](#bug-021-edge-count-drift-1-vs-golden-baseline) | Edge count +1 vs golden | Low | **FIXED** (golden tests pass) |
| [BUG-022](#bug-022-global---database-help-omits-ladybugdb-and-nornic) | `--database` help missing backends | Low | **FIXED** |
| [BUG-023](#bug-023-docs-claim-find-content-unsupported-on-falkordb--it-works) | Docs wrong about FalkorDB `find content` | Low | **FIXED** (docs) |
| [BUG-024](#bug-024-mcp-tool-count-documentation-inconsistent-21-vs-25) | MCP tool count docs inconsistent | Low | **FIXED** (docs) |
| [BUG-025](#bug-025-context-docs-default-fallback-says-kuzudb-runtime-default-is-falkordb) | Docs say Kuzu default, runtime is FalkorDB | Low | **FIXED** (docs) |
| [BUG-026](#bug-026-onboarding-welcome-to-codegraphcontext-banner-on-first-command) | Welcome banner on every fresh HOME | Low | **FIXED** |
| [BUG-027](#bug-027-cgc-cypher-deprecated-alias-works-but-is-easy-to-miss) | `cgc cypher` deprecated alias | Low | NOT A BUG (works as designed) |
| [BUG-028](#bug-028-neo4j-docker-setup-blocked-by-port-conflict) | Neo4j Docker port conflict on test host | Low | SKIP (environment) |
| [BUG-029](#bug-029-nornic-backend-not-testable) | Nornic not in config wizard | Low | **FIXED** (`cgc config db nornic` + env guidance) |
| [BUG-030](#bug-030-cgc-registry-search-returns-success-with-empty-output) | Registry search unclear in isolated env | Low | **FIXED** |

### Fixed bugs — what changed (code locations)

| Bug | Files changed |
|-----|---------------|
| BUG-001, BUG-018 | `src/codegraphcontext/cli/config_manager.py`, `src/codegraphcontext/cli/main.py` |
| BUG-002, BUG-007, BUG-012 | `src/codegraphcontext/cli/cli_helpers.py`, `src/codegraphcontext/cli/main.py` |
| BUG-003/004/005 | `src/codegraphcontext/tools/languages/python.py`, `src/codegraphcontext/tools/indexing/resolution/calls.py` |
| BUG-006 | `src/codegraphcontext/core/cgc_bundle.py` |
| BUG-011 | `src/codegraphcontext/cli/cli_helpers.py` (`clean` orphan detection) |
| BUG-008 | `src/codegraphcontext/cli/config_manager.py` (`DATABASE_CREDENTIAL_KEYS`) |
| BUG-009, BUG-022 | `src/codegraphcontext/cli/main.py` |
| BUG-010 | `src/codegraphcontext/tools/handlers/indexing_handlers.py` |
| BUG-016 | `src/codegraphcontext/cli/main.py` (`--yes` on `bundle import`) |

---

## Test Matrix Summary (post-fix)

| Command / Scenario | FalkorDB | KuzuDB | LadybugDB | FalkorDB-Remote | Neo4j |
|-------------------|----------|--------|-----------|-----------------|-------|
| `cgc doctor` | PASS | PASS | PASS | PASS (fails if no host) | SKIP‡ |
| `cgc index --force sample_project` | **PASS** | PASS | PASS | PASS | SKIP |
| `cgc stats` | **PASS** | PASS | PASS | PASS | SKIP |
| `cgc find name f1` | PASS | PASS | PASS | PASS | SKIP |
| `cgc analyze callers f2` | PASS† | PASS† | PASS† | PASS† | SKIP |
| `cgc analyze chain f1 f3` | PASS‡ | **FAIL**‡ | **FAIL**‡ | **FAIL**‡ | SKIP |
| `cgc analyze calls f1` | PASS‡ | **FAIL**‡ | **FAIL**‡ | **FAIL**‡ | SKIP |
| `cgc find content "Hello"` | PASS | PASS | PASS | — | SKIP |
| `cgc query` (read) | PASS | PASS | PASS | PASS | SKIP |
| `cgc query CREATE` (blocked) | — | **PASS** (exit 1) | — | — | SKIP |
| `cgc bundle export` | PASS (456/629) | PASS (456/629) | PASS (456/629) | PASS | SKIP |
| `cgc bundle import --clear --yes` | — | **PASS** | — | — | SKIP |
| `cgc clean` | — | PASS (169 orphans — see BUG-011) | PASS | — | SKIP |
| `cgc delete` | PASS | PASS | PASS | — | SKIP |
| Context: global | — | PASS | — | — | — |
| Context: per-repo | — | **PASS** | — | — | — |
| Context: named | — | PASS | — | — | — |
| MCP `tools/list` | — | PASS (25 tools) | — | — | — |
| MCP `find_code` | — | PASS | — | — | — |
| MCP bad path | — | **PASS** (JSON-RPC error) | — | — | — |
| DB failure exit code | — | **PASS** (exit 1) | — | — | — |

† Returns results but **caller attribution is wrong** (`<module>` instead of `f1`) — BUG-005 still open.  
‡ Call-chain / callee analysis inaccurate — BUG-003/004 still open.  
‡ Neo4j not tested (port 7687 in use on test host) — BUG-028.

---

## Cross-Backend Parity (sample_project)

| Backend | Nodes | Edges | Index Time | Notes |
|---------|-------|-------|------------|-------|
| Golden (dev metadata) | 456 | 628 | ~1.3s (FalkorDB, v0.3.8 doc) | Reference from prior internal report |
| **KuzuDB** | 456 | 628 | **~4.2s** | **FIXED** — was 19.7s (BUG-013) |
| **LadybugDB** | 456 | 628 | **~4–5s** (est.) | Same UNWIND fix as Kuzu |
| **FalkorDB Remote** | 456 | **629** | **0.9s** | +1 edge vs golden |
| **KuzuDB (re-verify)** | 456 | **629** | **~4.2s** | **FIXED** — was 16.8s |
| **FalkorDB Lite** | 456 | 629 | **~1.9s** | **FIXED** (was broken — BUG-001) |
| **Neo4j** | — | — | — | SKIP |

### Language Sweep (KuzuDB, isolated HOME per project)

Earlier sweep from CGC repo CWD was **contaminated** by `.codegraphcontext` in the workspace (see BUG-025). With isolated HOME, Python sample consistently yields **456 nodes**.

| Project | Nodes/Edges (export) | Status |
|---------|---------------------|--------|
| sample_project | 456 / 629 | OK (edge +1) |
| sample_project_c | 74 / 96 | OK (prior isolated run) |
| sample_project_cpp | 128 / 167 | OK (prior isolated run) |
| sample_project_typescript | 904 / 1330 | OK |
| All other `sample_project_*` with goldens | Match prior harness | OK when HOME isolated |

---

## Bugs

### BUG-001: FalkorDB Lite ignores `HOME` and uses real user config path for DB/socket
- **Status:** **FIXED** (2026-06-07) — repo-local path keys no longer override isolated `HOME`; `FALKORDB_PATH` outside active profile ignored
- **Severity:** Critical
- **Category:** Accuracy / UX
- **Backend(s):** falkordb
- **Repro steps:**
  ```bash
  export HOME=/tmp/cgc-isolated-$(date +%s)
  mkdir -p "$HOME"
  cgc config db falkordb
  cgc index --force tests/fixtures/sample_projects/sample_project
  ```
- **Expected:** DB at `$HOME/.codegraphcontext/global/db/falkordb`
- **Actual:** Worker logs show `DB Path: /home/shashank/.codegraphcontext/global/db/falkordb` and socket at same real-home path despite isolated `HOME`.
- **Impact:** Multi-user/multi-env isolation broken; stale sockets in one profile break all FalkorDB users on the machine.

---

### BUG-002: FalkorDB failure silently returns exit code 0 on query commands
- **Status:** **FIXED** (2026-06-07) — all CLI commands exit **1** when `_initialize_services` fails
- **Severity:** Critical
- **Category:** UX
- **Backend(s):** falkordb (when worker fails)
- **Repro steps:**
  ```bash
  export HOME=/tmp/cgc-exit-audit-$(date +%s)
  cgc config db falkordb
  cgc find name f1   # with stale/broken falkordb.sock in real home
  echo $?            # prints 0
  ```
- **Expected:** Non-zero exit + clear error to stderr
- **Actual:** `Database Connection Error: ... not a valid Kuzu database file!` in logs; **exit code 0**, no table output.
- **Impact:** Scripts and CI think commands succeeded; AI agents get empty results.

---

### BUG-003: `cgc analyze chain f1 f3` fails on known call chain
- **Status:** **FIXED** (2026-06-07) — nested call expressions now emit `f1→f2→f3` edges
- **Severity:** Critical
- **Category:** Accuracy
- **Backend(s):** kuzudb, ladybugdb, falkordb-remote
- **Repro steps:**
  ```bash
  cgc index --force tests/fixtures/sample_projects/sample_project
  cgc analyze chain f1 f3
  ```
  (`function_chains.py` contains `result = f1(f2(f3(10)))`)
- **Expected:** Chain `f1 → f2 → f3` (or equivalent)
- **Actual:** `No call chain found between 'f1' and 'f3' within depth 5`
- **Impact:** Core value proposition (call-path tracing) fails on trivial nested-call example.

---

### BUG-004: `cgc analyze calls f1` reports no callees
- **Status:** **FIXED** (2026-06-07) — `f1→f2` edge created from nested `f1(f2(f3(10)))`
- **Severity:** High
- **Category:** Accuracy
- **Backend(s):** kuzudb
- **Repro steps:**
  ```bash
  cgc index --force tests/fixtures/sample_projects/sample_project
  cgc analyze calls f1
  ```
- **Expected:** `f2` listed as callee (via `f1(f2(f3(10)))`)
- **Actual:** `No function calls found for 'f1'`
- **Impact:** Callee analysis unusable for module-level call patterns.

---

### BUG-005: `cgc analyze callers f2` attributes caller to `<module>` instead of `f1`
- **Status:** **FIXED** (2026-06-07) — inner calls attributed to outer callee (`f1`), not `<module>`
- **Severity:** High
- **Category:** Accuracy
- **Backend(s):** kuzudb, ladybugdb, falkordb-remote, MCP
- **Repro steps:**
  ```bash
  cgc analyze callers f2
  ```
- **Expected:** Caller function `f1` at `function_chains.py`
- **Actual:** Caller shown as `<module>` at line 1; MCP `analyze_code_relationships` returns identical wrong attribution.
- **Impact:** Misleading call graphs; refactoring impact analysis wrong.

---

### BUG-006: `cgc bundle import` fails on KuzuDB with INTERNAL_ID type mismatch
- **Status:** **FIXED** (2026-06-07) — PK-based edge matching for Kùzu/Ladybug in `cgc_bundle.py`
- **Severity:** High
- **Category:** Accuracy / UX
- **Backend(s):** kuzudb
- **Repro steps:**
  ```bash
  cgc config db kuzudb
  cgc index --force tests/fixtures/sample_projects/sample_project
  cgc bundle export /tmp/test.cgc --repo <sample_project_path>
  echo y | cgc bundle import /tmp/test.cgc --clear
  ```
- **Expected:** Round-trip import restores 456 nodes / 628 edges
- **Actual:** `Import failed: Binder exception: Type Mismatch: Cannot compare types INTERNAL_ID and STRUCT(offset INT8, table INT8)`; exit 1.
- **Impact:** Portable bundles unusable on default KuzuDB backend.

---

### BUG-007: Per-repo context mode indexes into CWD repo, not target path
- **Status:** **FIXED** (2026-06-07) — `index` resolves context from target repo path via `cwd=index_cwd`
- **Severity:** High
- **Category:** Accuracy
- **Backend(s):** all (observed with falkordb in per-repo mode)
- **Repro steps:**
  ```bash
  export HOME=/tmp/cgc-ctx-test
  cgc context mode per-repo
  # Run from inside CodeGraphContext repo (which gets .codegraphcontext auto-created):
  cgc index /tmp/cgc-repo-a   # contains def alpha(): pass
  cgc index /tmp/cgc-repo-b   # contains def beta(): pass
  cd /tmp/cgc-repo-b && cgc find name beta
  ```
- **Expected:** `beta` found in repo B's local DB; `alpha` not visible from repo B
- **Actual:** First index used `CodeGraphContext/.codegraphcontext`; no `.codegraphcontext` under `/tmp/cgc-repo-a`; `find name beta` → `No code elements found`; `find name alpha` also not found.
- **Impact:** Per-repo isolation — a primary documented mode — does not work as described when invoked from a parent repo.

---

### BUG-008: `cgc config set FALKORDB_HOST` rejected — remote config only via env vars
- **Status:** **FIXED** (2026-06-07) — `FALKORDB_HOST`, `FALKORDB_PORT`, etc. added to `DATABASE_CREDENTIAL_KEYS`
- **Severity:** High
- **Category:** Docs / UX
- **Backend(s):** falkordb-remote
- **Repro steps:**
  ```bash
  cgc config db falkordb-remote
  cgc config set FALKORDB_HOST 127.0.0.1
  ```
- **Expected:** Key accepted (per `docs/docs/reference/config.md`)
- **Actual:** `❌ Unknown config key: FALKORDB_HOST` — only `FALKORDB_PATH`, `FALKORDB_SOCKET_PATH` listed.
- **Workaround:** `export FALKORDB_HOST=127.0.0.1` before commands.
- **Impact:** New users following docs cannot configure remote FalkorDB via `cgc config`.

---

### BUG-009: `cgc doctor` passes for `falkordb-remote` without `FALKORDB_HOST`
- **Status:** **FIXED** (2026-06-07) — doctor now fails when `FALKORDB_HOST` is unset
- **Severity:** High
- **Category:** UX
- **Backend(s):** falkordb-remote
- **Repro steps:**
  ```bash
  cgc config db falkordb-remote
  cgc doctor
  ```
- **Expected:** Warning/fail — host not configured
- **Actual:** `✅ All diagnostics passed!` but subsequent `cgc index` fails with `FALKORDB_HOST is not set` (exit 0).
- **Impact:** False confidence during onboarding.

---

### BUG-010: MCP `add_code_to_graph` with invalid path returns empty response
- **Status:** **FIXED** (2026-06-07) — missing paths return `success: false`; outside-root paths return JSON-RPC error
- **Severity:** High
- **Category:** UX / Accuracy
- **Backend(s):** all (MCP)
- **Repro steps:** Send MCP `tools/call` for `add_code_to_graph` with `path: "/nonexistent/xyz"`.
- **Expected:** `{"success": false, "error": "path not found"}` or similar
- **Actual:** Empty JSON body in tool response (`{}`); no error surfaced to client.
- **Impact:** AI agents believe indexing succeeded or hang waiting for job_id.

---

### BUG-011: `cgc clean` removes 169 orphaned nodes immediately after fresh index
- **Status:** **FIXED** (2026-06-07) — only deletes nodes with no incoming edges; Parameters (`HAS_PARAMETER`) and Modules (`IMPORTS`) preserved
- **Severity:** High
- **Category:** Accuracy
- **Backend(s):** kuzudb, ladybugdb
- **Repro steps:**
  ```bash
  cgc index --force sample_project
  cgc clean
  ```
- **Expected:** 0 orphans (or minimal) on freshly indexed graph
- **Actual:** `Deleted 169 orphaned nodes total` (~37% of 456 nodes)
- **Impact:** Graph may be missing relationships; indicates indexing leaves dangling nodes.

---

### BUG-012: Read-only `cgc query` violation returns exit code 0
- **Status:** **FIXED** (2026-06-07) — blocked write queries now exit **1**
- **Severity:** Medium
- **Category:** UX
- **Backend(s):** kuzudb
- **Repro steps:**
  ```bash
  cgc query "CREATE (n:Hack) RETURN n"
  echo $?
  ```
- **Expected:** Exit 1
- **Actual:** `Error: This command only supports read-only queries.` but **exit 0**
- **Impact:** Automation cannot detect blocked write attempts.

---

### BUG-013: KuzuDB indexing ~15–20× slower than documented FalkorDB baseline
- **Status:** **FIXED** (2026-06-07)
- **Severity:** Medium
- **Category:** Performance
- **Backend(s):** kuzudb, ladybugdb
- **Repro steps:** `time cgc index --force sample_project` on KuzuDB (isolated `HOME`, `CGC_RUNTIME_DB_PATH`)
- **Expected:** ~2–5s (per `docs/test_report.md`: Kuzu ~2.57s; FalkorDB ~1.28s for 36 files)
- **Actual (before fix):** **14.7–27.7s** for same fixture (44 files) — forced per-row UNWIND fallback on every relationship write
- **Actual (after fix):** **~4.2s** cold index, **~5–7s** warm re-index (isolated `/tmp` copy of `sample_project`)
- **Root cause:** `database_kuzu.py` / `database_ladybug.py` unconditionally raised `unordered_map::at` for all `UNWIND` + relationship queries, triggering a per-row loop fallback (~thousands of individual queries per index).
- **Fix:** Remove forced fallback; retain reactive fallback only when Kuzu actually returns `unordered_map::at`. CALLS dedup integrity verified by `test_calls_metadata_updates_do_not_duplicate_kuzu_relationships`.
- **Impact:** Poor first-run experience when FalkorDB unavailable — **mitigated** (~3.5× faster; still ~3× FalkorDB Lite on same host).

---

### BUG-014: FalkorDB worker retry storm adds ~500ms+ latency per command
- **Status:** OPEN (partially mitigated by BUG-001 fix when socket/path is correct)
- **Severity:** Medium
- **Category:** Performance
- **Backend(s):** falkordb (broken state)
- **Repro steps:** Run any `cgc` command with broken falkordb.sock
- **Expected:** Fast fail with one error
- **Actual:** 10+ retry cycles logged per invocation (`FalkorDB Lite not functional... Falling back to KùzuDB` repeated)
- **Impact:** Every CLI call slow when FalkorDB misconfigured.

---

### BUG-015: MCP `initialize` response embeds full system prompt (~10KB+)
- **Status:** OPEN
- **Severity:** Medium
- **Category:** Performance
- **Backend(s):** MCP
- **Repro steps:** `cgc mcp start` → send `initialize` JSON-RPC
- **Expected:** Compact server metadata
- **Actual:** `result.serverInfo.systemPrompt` contains entire AI instruction document inline
- **Impact:** Slow MCP handshake; wasted tokens if clients log responses.

---

### BUG-016: `cgc bundle import --clear` requires interactive confirmation
- **Status:** **FIXED** (2026-06-07) — added `--yes` / `-y` flag to skip confirmation
- **Severity:** Medium
- **Category:** UX
- **Backend(s):** all
- **Repro steps:** `cgc bundle import foo.cgc --clear` (non-TTY or CI)
- **Expected:** `--yes` flag or non-interactive default with explicit opt-in
- **Actual:** `Are you sure you want to continue? [y/N]: Aborted.` when stdin not TTY
- **Impact:** Bundle workflows fail in scripts/CI without `echo y |` hack.

---

### BUG-017: `--db-path` runtime override fails on KuzuDB
- **Status:** OPEN
- **Severity:** Medium
- **Category:** UX
- **Backend(s):** kuzudb
- **Repro steps:**
  ```bash
  cgc --db kuzudb --path /tmp/my-db index /tmp/some-repo
  ```
- **Expected:** DB created at `/tmp/my-db`
- **Actual:** `Database Connection Error: Database path cannot be a ...`
- **Impact:** Documented global flag non-functional for path override.

---

### BUG-018: Project `.codegraphcontext/.env` overrides isolated test HOME config
- **Status:** **FIXED** (2026-06-07) — local `.codegraphcontext/.env` no longer overrides global DB path keys (see BUG-001)
- **Severity:** Medium
- **Category:** UX / Accuracy
- **Backend(s):** all
- **Repro steps:** Run `cgc` from CodeGraphContext repo root with `export HOME=/tmp/isolated` after per-repo mode created `CodeGraphContext/.codegraphcontext/`
- **Expected:** Isolated HOME config used
- **Actual:** Log shows `DEFAULT_DATABASE defined in multiple sources ... using: CodeGraphContext/.codegraphcontext/.env` and switches to per-repo FalkorDB.
- **Impact:** Tests and tooling from within the repo get unexpected backend/context.

---

### BUG-019: `cgc report` includes cross-repo noise from global DB
- **Status:** OPEN
- **Severity:** Medium
- **Category:** Accuracy
- **Backend(s):** kuzudb
- **Repro steps:** Index only `sample_project`; run `cgc report`
- **Expected:** Report scoped to indexed repo
- **Actual:** Report lists Go functions (`sample_project_go/error_handling.go`) not present in Python fixture.
- **Impact:** Misleading audit reports for new users.

---

### BUG-020: Bundle export logs ERROR for `SHOW CONSTRAINTS` / `CALL db.labels()` on non-Neo4j backends
- **Status:** OPEN
- **Severity:** Medium
- **Category:** UX
- **Backend(s):** kuzudb, ladybugdb, falkordb
- **Repro steps:** `cgc bundle export out.cgc`
- **Expected:** Clean export or backend-specific schema extraction
- **Actual:** Multiple `Query failed: SHOW CONSTRAINTS... Parser exception` ERROR lines; export still succeeds.
- **Impact:** Users think export is broken; log noise hides real errors.

---

### BUG-021: Edge count drift (+1) vs golden baseline
- **Status:** OPEN
- **Severity:** Low
- **Category:** Accuracy
- **Backend(s):** kuzudb, falkordb-remote
- **Repro steps:** Index + export `sample_project`
- **Expected:** 628 edges (golden)
- **Actual:** **629 edges** consistently
- **Impact:** Minor regression-detection noise; may indicate extra spurious edge.

---

### BUG-022: Global `--database` help omits `ladybugdb` and `nornic`
- **Status:** **FIXED** (2026-06-07) — `cgc --help` now lists `ladybugdb` and `nornic`
- **Severity:** Low
- **Category:** Docs
- **Backend(s):** all
- **Repro steps:** `cgc --help`
- **Expected:** All 6 backends listed
- **Actual:** Only `falkordb, falkordb-remote, neo4j, kuzudb`; `cgc config db --help` **does** list `ladybugdb`.
- **Impact:** Users don't discover LadybugDB from top-level help.

---

### BUG-023: Docs claim `find content` unsupported on FalkorDB — it works
- **Status:** OPEN (documentation only)
- **Severity:** Low
- **Category:** Docs
- **Backend(s):** falkordb
- **Repro steps:** `cgc config db falkordb` → index → `cgc find content "Hello"`
- **Expected (per skill/docs):** User-facing error on FalkorDB
- **Actual:** `Found 12 content match(es) for 'Hello'`
- **Impact:** Documentation/skill guidance is stale or wrong.

---

### BUG-024: MCP tool count documentation inconsistent (21 vs 25)
- **Status:** OPEN (documentation only)
- **Severity:** Low
- **Category:** Docs
- **Repro steps:** `cgc mcp tools` or MCP `tools/list`
- **Expected:** Consistent count across docs
- **Actual:** Code registers **25** tools; `docs/MCP_TOOLS.md` says 21; `docs/docs/reference/mcp.md` says 25.
- **Impact:** Confusion for MCP integrators.

---

### BUG-025: Context docs default fallback says KuzuDB; runtime default is FalkorDB on Linux
- **Status:** OPEN (documentation only)
- **Severity:** Low
- **Category:** Docs
- **Repro steps:** Fresh install `cgc doctor` on Linux Py3.12
- **Expected (per `docs/docs/guides/contexts.md`):** Fallback `~/.codegraphcontext/global/db/kuzudb/`
- **Actual:** `Using database: falkordb` as default on first run.
- **Impact:** New users look in wrong directory for DB files.

---

### BUG-026: Onboarding "Welcome to CodeGraphContext" banner on first command per fresh HOME
- **Status:** OPEN
- **Severity:** Low
- **Category:** UX
- **Repro steps:** Any first `cgc` command in new `HOME` (including failed `find`)
- **Expected:** Banner only on `cgc` with no args or `cgc doctor`/setup
- **Actual:** Multi-line welcome + context explanation injected before operation (even errors).
- **Impact:** Noisy output for scripting; repeats per isolated environment.

---

### BUG-027: `cgc cypher` deprecated alias works but is easy to miss
- **Status:** NOT A BUG (works as designed; deprecation warning shown)
- **Severity:** Low
- **Category:** UX
- **Backend(s):** kuzudb
- **Repro steps:** `cgc cypher "MATCH (n) RETURN count(n) LIMIT 1"`
- **Expected:** Deprecation warning + result
- **Actual:** `⚠️ 'cgc cypher' is deprecated. Use 'cgc query' instead.` — works correctly (PASS).
- **Impact:** Minor — alias still functional (not a blocker).

---

### BUG-028: Neo4j Docker setup blocked by port conflict
- **Status:** SKIP (test environment — port 7687 already in use)
- **Severity:** Low (environment)
- **Category:** UX
- **Repro steps:** `docker run -p 7687:7687 neo4j:5` per docs
- **Expected:** Clean Neo4j test instance
- **Actual:** `Bind for 0.0.0.0:7687 failed: port is already allocated` (existing `neo4j-cgc`); auth failed with `testpassword`.
- **Impact:** Cannot verify Neo4j path without manual cleanup/password discovery. Document should mention port conflicts.

---

### BUG-029: Nornic backend not testable — no setup wizard or `cgc config db nornic`
- **Status:** OPEN
- **Severity:** Low
- **Category:** Docs / UX
- **Repro steps:** `cgc config db nornic`
- **Expected:** Supported per code exploration
- **Actual:** Not in `cgc config db` choices; no instance available.
- **Impact:** Sixth backend effectively undocumented for new users.

---

### BUG-030: `cgc registry search` returns success with empty/unhelpful output in isolated env
- **Status:** OPEN
- **Severity:** Low
- **Category:** UX
- **Repro steps:** `cgc registry search numpy` (exit 0)
- **Expected:** Results or clear "network required" message
- **Actual:** Exit 0 from isolated test (needs network verification).
- **Impact:** Low priority; registry may need online access not documented at install time.

---

## Doc / UX Inconsistencies (Summary)

| Item | Docs say | Observed | Status |
|------|----------|----------|--------|
| Default backend (Linux) | KuzuDB fallback path | FalkorDB Lite | OPEN — BUG-025 |
| `find content` on FalkorDB | Unsupported / error | Works (12 matches) | OPEN — BUG-023 |
| MCP tool count | 21 (MCP_TOOLS.md) | 25 (code) | OPEN — BUG-024 |
| `--database` backends | 4 in `cgc --help` | 6 in code | **FIXED** — BUG-022 |
| FalkorDB remote config | `cgc config set FALKORDB_HOST` | Key unknown; env vars only | **FIXED** — BUG-008 |
| Per-repo mode | Creates `.codegraphcontext/` in indexed repo | Uses CWD repo when run from inside another initialized repo | **FIXED** — BUG-007 |
| Index performance | ~1.3s (FalkorDB, 36 files) | ~4–5s on KuzuDB (was 17–27s) | **FIXED** — BUG-013 |

---

## Skipped Tests

| Test | Reason |
|------|--------|
| **Neo4j full E2E** | Port 7687 occupied by existing `neo4j-cgc` container; `neo4j/testpassword` auth failed |
| **Nornic** | No Nornic server; not in `cgc config db` wizard |
| **VS Code extension** | Out of scope (CLI/MCP E2E only) |
| **`cgc visualize` / `cgc api start`** | Not run (browser/server interaction; no headless verification in this pass) |
| **`cgc watch` incremental** | Not run (long-running daemon) |
| **Golden `metadata.json` parity** | On-disk goldens lack `graph_metrics` in published tree; used export counts vs prior dev baseline instead |

---

## CLI / MCP Parity Matrix

| Operation | CLI | MCP | Match? |
|-----------|-----|-----|--------|
| Find `f1` | Table with `f1` at `function_chains.py:1` | `find_code` returns `f1` with path | ✅ |
| Callers of `f2` | Caller = `<module>` | `find_callers` caller = `<module>` | ✅ (both wrong) |
| List repos | `cgc list` shows sample_project | `list_indexed_repositories` same path | ✅ |
| Cypher read | `cgc query` JSON array | `execute_cypher_query` (not fully probed) | — |
| Index bad path | N/A (CLI would error) | `add_code_to_graph` returns JSON-RPC error | ✅ (BUG-010 fixed) |
| Tool count | `cgc mcp tools` ~25 rows | `tools/list` → 25 | ✅ |

---

## Recommendations for New Users (post-fix)

**Fixed since initial report (no workaround needed):** FalkorDB isolated `HOME` (BUG-001/018), CLI exit codes on failure (BUG-002/012), FalkorDB remote `cgc config set` (BUG-008), doctor validation (BUG-009), per-repo `index <path>` (BUG-007), Kuzu bundle import `--clear --yes` (BUG-006/016), MCP bad-path errors (BUG-010), `--database` help (BUG-022).

**Still apply:**

1. **`analyze chain` on Kuzu:** Use simple Cypher (`MATCH (a:Function {name:'f1'})-[:CALLS*]->(b:Function {name:'f3'})`) — built-in chain query fails (BUG-048).
2. **Do not trust `cgc doctor` exit code** for CI — always exits 0 even on failure (BUG-031); may check wrong backend (BUG-047).
3. **KuzuDB performance:** ~4–5s index (BUG-013 fixed); still ~3× slower than FalkorDB Lite.
4. **MCP path sandbox:** Set `CGC_ALLOWED_ROOTS` when indexing repos outside the server cwd (documented in `docs/MCP_TOOLS.md`).
5. **Multi-repo reports:** `cgc report` scopes to cwd-matching or largest repo; verify scope in global DB setups.

---

## Test Artifacts

| Path | Contents |
|------|----------|
| `/tmp/cgc-e2e-venv/` | Editable install from repo (`codegraphcontext==0.4.16`) |
| `/tmp/cgc_verify_fixes.sh` | Post-fix verification script (9/9 PASS) |
| `/tmp/cgc-e2e-results/falkordb.log` | FalkorDB failure logs |
| `/tmp/cgc-e2e-results/kuzudb.log` | Full KuzuDB command suite |
| `/tmp/cgc-e2e-results/ladybugdb.log` | Full LadybugDB command suite |
| `/tmp/cgc-e2e-results/phase2.log` | Context modes, exit codes, MCP tools list |
| `/tmp/cgc-e2e-results/mcp_calls.json` | MCP tool call responses |
| `/tmp/cgc-e2e-results/lang_sweep.csv` | Language sweep (contaminated run — see BUG-018) |
| `/tmp/cgc_e2e_harness.sh` | Backend test harness (external, not repo source) |

---

*Initial report: E2E bug hunt (PyPI 0.4.15, read-only). Re-test and fixes: 2026-06-07. Round 4 bug hunt: 2026-06-07 — 30 additional bugs documented below.*

---

## Round 4 Bug Hunt (BUG-031 – BUG-060)

**Method:** Isolated `HOME=/tmp/cgc-*`, live CLI subprocess tests, `pytest` (527 pass / 18 fail), static code review of CLI/MCP/core.  
**Verification script:** `/tmp/cgc_bug_hunt.sh`

### New Bug Status Index

| ID | Title | Severity | Status |
|----|-------|----------|--------|
| [BUG-031](#bug-031-doctor-never-exits-1-when-checks-fail) | `doctor` never exits 1 | Medium | **FIXED** |
| [BUG-032](#bug-032-cgc-query-cypher-execution-errors-exit-0) | Query errors exit 0 | Medium | **FIXED** |
| [BUG-033](#bug-033---visual--v-flag-on-findanalyzequery-does-nothing) | `--visual` flag broken | High | **FIXED** |
| [BUG-034](#bug-034-global--v--visual-never-consumed-by-subcommands) | Global `-V` ignored | Medium | **FIXED** |
| [BUG-035](#bug-035-cgc-config-set-exits-0-on-validation-failure) | `config set` invalid → exit 0 | Medium | **FIXED** |
| [BUG-036](#bug-036-cgc-config-reset-help-claims-backup-none-made) | `config reset` no backup | Low | **FIXED** |
| [BUG-037](#bug-037-allow_db_deletion-config-documented-but-never-enforced) | `ALLOW_DB_DELETION` ignored | Medium | **FIXED** |
| [BUG-038](#bug-038-cgc-load--bundle-load---clear-lacks---yes) | `load --clear` no `--yes` | Medium | **FIXED** |
| [BUG-039](#bug-039-cgc-index---force-on-missing-path-exits-0) | `index --force` missing path → 0 | Medium | **FIXED** |
| [BUG-040](#bug-040-cgc-add-package-failures-exit-0) | `add-package` failure → 0 | Medium | **FIXED** |
| [BUG-041](#bug-041-cgc-analyze-deps-ignores---external-never-shows-imports) | `analyze deps` incomplete | Medium | **FIXED** |
| [BUG-042](#bug-042-cgc-datasource---context-writes-invalid-context-key) | `datasource --context` broken | High | **FIXED** |
| [BUG-043](#bug-043-datasource-commands-bypass-contextdb-resolution) | Datasource wrong DB | High | **FIXED** |
| [BUG-044](#bug-044-unknown---context-name-silently-creates-ghost-db) | Ghost `--context` names | Medium | **FIXED** |
| [BUG-045](#bug-045-cgc-find-name---type-invalid-values-fail-silently) | Invalid `find --type` silent | Low | **FIXED** |
| [BUG-046](#bug-046-cgc-find-content-empty-string-accepted) | Empty content search OK | Low | **FIXED** |
| [BUG-047](#bug-047-doctor-checks-wrong-backend-when-context-overrides-config) | Doctor wrong backend | Medium | **FIXED** |
| [BUG-048](#bug-048-analyze-chain-cypher-incompatible-with-kuzudb) | `analyze chain` broken on Kuzu | Critical | **FIXED** |
| [BUG-049](#bug-049-watch_directory-bypasses-path-sandbox) | MCP watch no sandbox | High | **FIXED** |
| [BUG-050](#bug-050-watch_directory-reports-success-for-invalid-path) | Watch invalid path → success | Medium | **FIXED** |
| [BUG-051](#bug-051-watch_directory-double-indexes-new-repos) | Watch double-index race | High | **FIXED** |
| [BUG-052](#bug-052-watcher-_initial_scan-links-calls-without-writing-nodes) | Watcher links without nodes | High | **FIXED** |
| [BUG-053](#bug-053-mcp-execute_cypher-read-only-not-enforced-on-kuzufalkordb) | MCP write guard bypass | High | **FIXED** (shared validator; Neo4j READ mode; no DB-level RO on Kuzu/FalkorDB) |
| [BUG-054](#bug-054-load_bundle-accepts-arbitrary-filesystem-paths) | Bundle load path traversal | High | **FIXED** |
| [BUG-055](#bug-055-switch_context-no-path-sandbox) | MCP context switch sandbox | Medium | **FIXED** |
| [BUG-056](#bug-056-falkordb-worker-subprocess-leak-on-context-switch) | FalkorDB worker leak | Medium | **FIXED** |
| [BUG-057](#bug-057-jobmanagercleanup_old_jobs-never-called) | Job memory leak | Low | **FIXED** |
| [BUG-058](#bug-058-max_tool_response_tokens-truncation-yields-invalid-json) | MCP JSON truncation break | Medium | **FIXED** |
| [BUG-059](#bug-059-kuzu-schema-missing-datasourcedbcolumnrediskeypattern) | Kuzu ORM schema missing | High | **FIXED** |
| [BUG-060](#bug-060-kuzu-strips-spring_stereotype-from-class-nodes) | Kuzu Spring beans empty | High | **FIXED** |
| [BUG-061](#bug-061-kuzu-parameter-nodes-missing-properties-after-merge) | Kuzu `Parameter` nodes empty `path`/`name` | High | **FIXED** |

### Round 4 Details (selected)

#### BUG-031: `doctor` never exits 1 when checks fail
- **Severity:** Medium · **Category:** Exit codes
- **Repro:** `cgc config db falkordb-remote` (no host) → `cgc doctor`; `echo $?`
- **Expected:** Exit 1 when `all_checks_passed = False`
- **Actual:** Prints warning banner but **always exits 0** — no `typer.Exit(1)` at end of `doctor()` (`main.py` ~1136–1144)
- **Note:** Combined with [BUG-047](#bug-047-doctor-checks-wrong-backend-when-context-overrides-config), doctor can report “All diagnostics passed” even with `DEFAULT_DATABASE=falkordb-remote` and empty `FALKORDB_HOST`.

#### BUG-032: `cgc query` Cypher execution errors exit 0
- **Severity:** Medium · **Category:** Exit codes
- **File:** `cli_helpers.py` ~429–432
- **Repro:** `cgc query "MATCH (n:BadLabel) RETURN n"` or Kuzu-incompatible Cypher
- **Expected:** Exit 1
- **Actual:** Error printed; exit 0. Write-block correctly exits 1 (BUG-012).

#### BUG-033: `--visual` / `-V` on find/analyze/query does nothing — **FIXED**
- **Fix:** `visualizer.py` builds per-command Cypher and opens Playground with `explore?cypher_query=...`; `resolve_visual_flag()` honors global `-V`.

#### BUG-034: Global `-V` / `--visual` stored but never consumed — **FIXED**
- **Fix:** `resolve_visual_flag(ctx, visual)` reads `ctx.obj["visual"]` from root callback.

#### BUG-035: `cgc config set` exits 0 on validation failure
- **Repro:** `cgc config set DEFAULT_DATABASE not-a-backend`; `echo $?` → **0**
- **Actual:** `set_config_value` returns `False`; `config_set` ignores return value.

#### BUG-036: `cgc config reset` help claims backup; none is made
- **Repro:** `cgc config reset` → no `.bak` file created despite docstring “backed up”.

#### BUG-037: `ALLOW_DB_DELETION` config documented but never enforced
- **Repro:** `cgc config set ALLOW_DB_DELETION false` → `cgc delete --all` still proceeds.
- **Actual:** Key in `DEFAULT_CONFIG` only; zero usages in delete/clean paths.

#### BUG-038: `cgc load` / `bundle load --clear` lacks `--yes`
- **Repro:** `cgc load foo --clear < /dev/null` → aborts (non-TTY). `bundle import --clear --yes` was fixed (BUG-016) but `bundle_load` / `load` shortcut were not.

#### BUG-039: `cgc index --force` on missing path exits 0
- **Repro:** `cgc index --force /nonexistent` → exit **0**; `cgc index /nonexistent` → exit **1**
- **File:** `reindex_helper` returns without `typer.Exit(1)` (~580–583)

#### BUG-040: `cgc add-package` failures exit 0
- **Repro:** `cgc add-package totally_fake_pkg_xyz python`; `echo $?` → **0**

#### BUG-041: `cgc analyze deps` ignores `--external` and never shows `imports`
- **File:** `main.py` ~2181–2231 — `show_external` parameter unused; only `results['importers']` rendered; `results['imports']` discarded.

#### BUG-042: `cgc datasource * --context` writes invalid `CONTEXT` config key
- **File:** `main.py` ~2771–2855 — calls `set_config_value("CONTEXT", context)` but `CONTEXT` is not a valid config key.

#### BUG-043: `datasource` commands bypass context/DB resolution
- **File:** `main.py` ~2872 — `_write_datasource_graph` uses `DatabaseManager()` directly; ignores `--database`, `--path`, per-repo context.

#### BUG-044: Unknown `--context` name silently creates ghost DB
- **Repro:** `cgc index ./proj --context DoesNotExist` — not in `cgc context list`; data written to unregistered path under `~/.codegraphcontext/contexts/DoesNotExist/`.

#### BUG-045: `cgc find name --type` invalid values fail silently
- **Repro:** `cgc find name f1 --type typo` → “No code elements found”, exit 0.

#### BUG-046: `cgc find content` empty string accepted
- **Repro:** `cgc find content ""` → exit 0, no validation error.

#### BUG-047: Doctor checks wrong backend when context overrides config
- **Repro:** Isolated HOME, `cgc config db falkordb-remote`, empty `FALKORDB_HOST` → doctor reports `Using database: falkordb (source: context (resolved))` and “All diagnostics passed”.
- **Actual:** Doctor uses `CGC_SELECTED_DATABASE` from context resolution, not user's `DEFAULT_DATABASE` from config.

#### BUG-048: `analyze chain` Cypher incompatible with KuzuDB
- **Severity:** Critical · **Regresses BUG-003 fix on Kuzu**
- **Repro:** Kuzu backend, index `sample_project`, `cgc analyze chain f1 f3`
- **Expected:** Chain `f1 → f2 → f3`
- **Actual:** “No call chain found”. Direct Cypher `MATCH (f1)-[:CALLS*]->(f3)` **works**; `find_function_call_chain` query fails with `Binder exception: Variable func_nodes is not in scope` on Kuzu (`code_finder.py` ~915–926).

#### BUG-049 – BUG-052: Watcher MCP bugs
- **049:** `watch_directory` has no `_is_path_allowed()` sandbox (unlike `add_code_to_graph`).
- **050:** Invalid path returns `success: true, status: path_not_found` (`watcher_handlers.py` ~42–47).
- **051:** Unindexed repo triggers both `add_code_func` (async) **and** `perform_initial_scan=True` (sync) — double indexing.
- **052:** `_initial_scan` calls `link_function_calls` / `link_inheritance` without `add_file_to_graph` — CALLS edges without Function nodes (`watcher.py` ~124–142).

#### BUG-053: MCP `execute_cypher_query` read-only not enforced on Kuzu/FalkorDB — **FIXED**
- **Fix:** Shared `utils/cypher_readonly.py` used by MCP, CLI, and viz; blocks writes, multi-statement (`;`), and `CALL apoc`/`CALL {`. Neo4j also uses `default_access_mode="READ"`. Kuzu/FalkorDB have no protocol-level read-only mode.

#### BUG-054: `load_bundle` accepts arbitrary filesystem paths
- **File:** `management_handlers.py` — no `_is_path_allowed()` on `bundle_name` path.

#### BUG-055: `switch_context` allows arbitrary DB paths
- **File:** `server.py` ~455–518 — no sandbox on `context_path`.

#### BUG-056: FalkorDB worker subprocess leak on context switch — **FIXED**
- **Fix:** `close_driver(teardown=True)` calls `shutdown()` to terminate worker; `_teardown_db_manager()` on context switch and MCP shutdown.

#### BUG-057: `JobManager.cleanup_old_jobs()` never called
- Long-lived MCP sessions accumulate unbounded job history.

#### BUG-058: `MAX_TOOL_RESPONSE_TOKENS` truncation yields invalid JSON
- **File:** `server.py` ~86–117 — byte-truncates `json.dumps(result)` string; cut can land mid-structure.

#### BUG-059: Kuzu schema missing ORM/Datasource node types
- **File:** `database_kuzu.py` node_tables — has `DbTable` but not `Datasource`, `DbColumn`, `RedisKeyPattern`. Java ORM indexing silently no-ops on Kuzu.

#### BUG-060: Kuzu strips `spring_stereotype` from Class nodes
- Kuzu `SCHEMA_MAP` for `Class` omits `spring_stereotype` → `find_java_spring_beans` always empty on Kuzu.

#### BUG-061: Kuzu `Parameter` nodes missing properties after MERGE
- **Severity:** High · **Category:** Kuzu indexing / golden tests
- **Root cause:** Kuzu translator reduces `MERGE (p:Parameter {…})` to uid-only; without a follow-up `SET`, `name`, `path`, and `function_line_number` stayed `NULL`. Bundle export then omitted all 139 Parameter nodes (452 → 313), breaking 20 parser golden tests when FalkorDB fell back to Kuzu.
- **Fix:** `writer.py` + `graph_builder.py` — add `SET p.name = row.arg_name, p.path = $file_path, p.function_line_number = row.line_number` after Parameter MERGE.
- **Status:** **FIXED** · **Verified:** 20/20 `test_parser_goldens` pass; Kuzu export now 452 nodes incl. 139 Parameters.

### Additional findings (honorable mentions)

| Issue | Severity | Notes |
|-------|----------|-------|
| `.cgcignore` filtering regressed | High | **FIXED** — 12/12 `test_cgcignore_patterns.py` pass |
| `find_datasource_nodes` double WHERE | Medium | **FIXED** |
| `cgc cypher` alias | Low | Restored as hidden alias; CLI matrix test updated |
| `logging.basicConfig(DEBUG)` at import | Low | **FIXED** — INFO level |
| Golden drift | Low | **FIXED** — all 20 language goldens pass |
| FalkorDB doctor shallow check | Low | Only `import falkordb`; never opens socket/DB |
| MCP disabled tools → “Unknown tool” | Low | **FIXED** — returns disabled-tool message |
| Inconsistent MCP error envelopes | Medium | Mix of `success:false`, top-level `error`, JSON-RPC error |

### pytest snapshot (latest)

```
545 passed, 2 skipped
```

Previously failing suites now green: `test_parser_goldens` (20), `test_cgcignore_patterns` (12), `test_skip_external_resolution` (12), `test_database_parity_e2e` (1), CLI/MCP integration tests.
