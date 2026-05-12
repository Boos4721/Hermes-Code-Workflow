### Design Agent

`scripts/hcw_design.py` adds a structured architecture/design phase to HCW,
inspired by [huashu-design](https://github.com/alchaincyf/huashu-design) methodology:

1. **Deep context gathering** — scan codebase for architecture patterns, config values, dependencies
2. **Variations by dimension** — each approach explores a distinct architectural axis (modularity, data flow, state, resilience, etc.)
3. **Junior Designer mode** — surface assumptions and open questions before finalizing
4. **5-dimension critique** — score design on coherence, modularity, scalability, maintainability, testability
5. **Quick Wins** — review output includes a prioritized fix list

```bash
# 1. Init — create design session (use --ask-questions to surface context questions)
python3 scripts/hcw_design.py init \
  --goal "Add rate limiting to API gateway" \
  --context "Current gateway has no rate limiting; peak traffic 5000 req/s" \
  --constraints "Must use Redis" "Must not add >5ms latency" \
  --ask-questions

# 2. Explore — deep codebase scan (extracts exact config values, architecture markers)
python3 scripts/hcw_design.py explore \
  --dir . \
  --session .hcw/sessions/<session-id>

# 3. Propose — generate 2-3 approaches by distinct architectural dimensions
python3 scripts/hcw_design.py propose \
  --goal "Add rate limiting to API gateway" \
  --approaches 3 \
  --recommend 1 \
  --session .hcw/sessions/<session-id>
# Proposals span dimensions like: modularity, data flow style, state management

# 4. Assumptions — surface design assumptions (Junior Designer pattern)
python3 scripts/hcw_design.py assumptions \
  --session .hcw/sessions/<session-id> \
  --items "scope_impact:only touches gateway/middleware" "performance:target <5ms overhead per request" \
  --open-questions "How to handle rate limit exceeded errors?" "What window size?"

# 5. Finalize — produce design.md from all artifacts
python3 scripts/hcw_design.py finalize \
  --session .hcw/sessions/<session-id> \
  --scope "gateway/middleware/ratelimit.py" "gateway/config.yaml" \
  --criteria "python3 -m pytest tests/test_ratelimit.py" "load-test --rps 6000 < latency-5ms"

# 6. Review — 5-dimension critique with score + quick wins
python3 scripts/hcw_design.py review \
  --design .hcw/sessions/<session-id>/design.md \
  --scores "architectural_coherence:7" "modularity:8" "scalability:6" "maintainability:7" "testability:8" \
  --fixes "high|missing error handling|add error middleware" "medium|no config defaults|add fallback values" \
  --session .hcw/sessions/<session-id>
```

**Design session artifacts**:

```text
.hcw/sessions/<session-id>/
├── manifest.json           # Goal, context, assumptions, status
├── events.jsonl            # Design event log
├── exploration/
│   └── codebase.json       # Deep codebase scan (arch markers, config values)
├── proposals.json          # Approaches by architectural dimension
├── assumptions.json        # Documented assumptions + open questions
├── review.json             # 5-dimension score + quick wins
└── design.md               # Final design document (includes all of the above)
```

**Architecture scan marks** patterns found in codebase:
- `routes` — HTTP/API route definitions
- `models` — data models and entities
- `services` — service layer classes and functions
- `middleware` — middleware/interceptor pipelines
- `handlers` — request handlers
- `config` — configuration variables
- `errors` — error classes and exception hierarchies
- `tests` — test functions and classes

**5 review dimensions**:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Architectural coherence | 25% | Unified architecture style, clear component boundaries |
| Modularity | 20% | Coupling, cohesion, interface clarity |
| Scalability | 20% | Ease of adding features, impact of changes |
| Maintainability | 20% | Error handling, logging, debuggability |
| Testability | 15% | Mockability, dependency isolation |

**Integrates with**:
- `hcw_session.py` — design session feeds into implementation session
- `hcw_summarize.py` — design artifacts appear in final report
- `hcw_update.py` — syncs design script + template from GitHub
