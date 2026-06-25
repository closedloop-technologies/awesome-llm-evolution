# AGENTS.md - Awesome LLM Evolution Curation Guide

This file defines the standards, checks, and stylistic conventions for
maintaining this repository. All contributions, whether made manually or via an
agent, must follow these rules to preserve quality and taste.

---

## 1. Scope

- This repository is an Awesome List for curated resources at the intersection
  of large language models, evolutionary algorithms, search-based
  optimization, program synthesis, automated discovery, and prompt or policy
  optimization.
- It is **selective**, not exhaustive. Every item must be high-quality, actively maintained, and relevant to the scope.
- Off-topic or low-quality entries will be declined.

---

## 2. Content Best Practices

### ✅ Include
- **Curated entries only** — each link should have a proven track record (quality projects, authoritative articles, widely-used tools).
- **Short, descriptive annotations** explaining *why* the entry is worth including.
- Logical **category groupings** with clear section headings.
- **Table of Contents** at the top, linking to all major sections.
- Consistent link formatting:
```
- [Project Name](https://link) - short description ending with a period.
```

### 🚫 Avoid
- Random link dumps without context.
- Unmaintained or abandoned projects (no updates in 12+ months unless historically significant).
- Duplicate links (different anchors for the same resource).
- Overly long descriptions.

---

## 3. Formatting Rules

- Markdown must pass [`awesome-lint`](https://github.com/sindresorhus/awesome-lint) without errors.
- One blank line between list items and headings.
- Section titles in `Title Case`.
- No trailing spaces; no inconsistent indentation.
- Descriptions end with a period.
- Badges (if any) must be tasteful — limit to `Awesome` badge and relevant status badges.

---

## 4. Tooling & Linters

### Required Checks (run locally and in CI)
```bash
python3 scripts/check_readme.py
GITHUB_TOKEN="$(gh auth token)" npx --yes awesome-lint
```

Optional but recommended:

- **Markdown Link Checker** to detect broken links:

  ```bash
  npx markdown-link-check README.md
  ```
- **Prettier** for consistent Markdown formatting:

  ```bash
  npx prettier --check "**/*.md"
  ```

CI configuration:

- Configure GitHub Actions to run `awesome-lint` and link checks on every PR.
- Fail the build if there are formatting, linting, or broken link issues.

---

## 5. Contribution Guidelines

- **Read `contributing.md`** before opening a PR.
- One PR per addition or major change.
- Follow the established category structure; create new categories only if necessary.
- Additions **must** include:

  1. A link in `[Name](URL)` format.
  2. A concise description explaining why it’s awesome.
  3. Placement in the correct category.
- Do not reorder unrelated entries unless alphabetizing.

PR title format:

```
[Category] Add <Project Name>
```

---

## 6. Tagging & Metadata

- Keep repo description up to date.
- Add relevant topics in GitHub settings:

  ```
  awesome, awesome-list, llm, evolutionary-algorithms, program-synthesis
  ```
- Include the Awesome badge at the top of README:

  ```markdown
  [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
  ```

---

## 7. Quality & Maintenance

- Review and prune outdated entries quarterly.
- Check for broken links regularly (via CI or manual run).
- Encourage community contributions but enforce curation standards.
- Merge only after checks pass and content meets these guidelines.

---

## 8. Verification Steps for Agents

Before completing any PR:

1. **Run all linters**:

   ```bash
   python3 scripts/check_readme.py
   GITHUB_TOKEN="$(gh auth token)" npx --yes awesome-lint
   ```
2. Ensure no broken links.
3. Ensure descriptions are present, concise, and follow style rules.
4. Confirm correct alphabetical order within categories.
5. Pass all CI checks.

---

Maintaining an Awesome List is about taste, clarity, and discipline — keep it **curated, current, and clean**.
