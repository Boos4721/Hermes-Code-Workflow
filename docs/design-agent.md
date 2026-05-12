### Design Agent

`scripts/hcw_design.py` adds a structured architecture/design phase to HCW.

```bash
# 1. Init — create design session
python3 scripts/hcw_design.py init \
  --goal "Add rate limiting to API gateway" \
  --context "Current gateway has no rate limiting" \
  --constraints "Must use Redis" "Must not add latency"

# 2. Explore — scan codebase for design context
python3 scripts/hcw_design.py explore \
  --dir . \
  --session .hcw/sessions/<session-id>

# 3. Propose — generate design proposal stubs (2-3 approaches)
python3 scripts/hcw_design.py propose \
  --goal "Add rate limiting" \
  --approaches 2 \
  --recommend 1 \
  --session .hcw/sessions/<session-id>

# 4. Finalize — produce design.md from artifacts
python3 scripts/hcw_design.py finalize \
  --session .hcw/sessions/<session-id> \
  --scope "gateway/middleware/ratelimit.py" "gateway/config.yaml" \
  --criteria "python3 -m pytest tests/test_ratelimit.py" "wrk -c 100 -d 10s http://localhost:8080"

# 5. Review — check design.md for completeness
python3 scripts/hcw_design.py review \
  --design .hcw/sessions/<session-id>/design.md
```

**Design session artifacts**:

```text
.hcw/sessions/<session-id>/
├── manifest.json           # Goal, context, status
├── events.jsonl            # Design event log
├── exploration/
│   └── codebase.json       # Codebase scan results
├── proposals.json          # Design proposals with trade-offs
├── review.json             # Review verdict and check results
└── design.md               # Final design document
```

**Integrates with**:
- `hcw_session.py` — design session can feed into implementation session
- `hcw_summarize.py` — design artifacts appear in final report
- `hcw_update.py` — syncs design script + template from GitHub

**When to run**: Before creating an implementation brief. The design phase produces the spec that the implementer brief references.
