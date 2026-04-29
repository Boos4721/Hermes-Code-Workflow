# Hermes Code Workflow Skill Authoring Notes

This repository defines Hermes Code Workflow, a Hermes-centered orchestration skill.

Current assumptions captured in the skill:

- Gemini command-line interface can participate through Agent Client Protocol capable orchestration.
- Claude Code, Codex, and similar coding agents should be used through official vendor-supported command-line interface or software development kit paths where possible.
- Hermes remains the top-level planner, router, verifier, and reporter.

The skill is intentionally workflow-focused rather than implementation-specific.
