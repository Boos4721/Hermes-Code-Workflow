# HCW Skill Authoring Notes

This repository defines HCW (Hermes-Code-Workflow), a Hermes-centered orchestration skill.

Current assumptions captured in the skill:
- Gemini CLI can participate through ACP-capable orchestration.
- Claude Code, Codex, and similar coding agents should be used through official vendor-supported CLI/SDK paths where possible.
- Hermes remains the top-level planner, router, verifier, and reporter.

The skill is intentionally workflow-focused rather than implementation-specific.
