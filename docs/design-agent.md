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

---

## Visual Design (via huashu-design)

`hcw_design.py visual` bridges HCW with the built-in **huashu-design** skill for
UI/UX, animation, slide, and infographic design.

```bash
# List available capabilities
python3 scripts/hcw_design.py visual --list-capabilities --goal x

# List available design philosophy styles (5 schools × 20 philosophies)
python3 scripts/hcw_design.py visual --list-styles --goal x

# Create a visual design session with a structured brief
python3 scripts/hcw_design.py visual \
  --goal "做一个跑步记录 App 原型, 5 屏, iOS" \
  --capability prototype \
  --style "Kenya Hara 空的设计" \
  --print-brief

# Generate slides
python3 scripts/hcw_design.py visual \
  --goal "10页产品 pitch deck" \
  --capability slides

# Animation / motion design
python3 scripts/hcw_design.py visual \
  --goal "30秒神经网络的 HTML 动画" \
  --capability animation
```

**Supported capabilities**:

| Capability | Deliverable | Time |
|------------|-------------|------|
| `prototype` | Interactive HTML prototype | 10-15 min |
| `slides` | HTML deck + editable PPTX | 15-25 min |
| `animation` | MP4 + GIF + BGM | 8-12 min |
| `variations` | Side-by-side with Tweaks | 10 min |
| `infographic` | Print-quality PDF/PNG/SVG | 10 min |
| `direction` | 3 parallel design directions | 5 min |
| `critique` | 5-dimension radar chart | 3 min |

**Design philosophy schools** (from huashu-design):

| School | Example philosophies |
|--------|-------------------|
| 信息建筑派 | Pentagram, Stamen, iA, Fathom |
| 运动诗学派 | Locomotive, Active Theory, Field.io, Resn |
| 极简主义派 | Experimental Jetset, Müller-Brockmann, Build, Sagmeister |
| 实验先锋派 | Zach Lieberman, Raven Kwok, Ash Thorp, Territory |
| 东方哲学派 | Takram, Kenya Hara, Irma Boom, Neo Shen |

**Skill location**: `skills/huashu-design/SKILL.md` — clone with:
```bash
git submodule update --init skills/huashu-design
```
