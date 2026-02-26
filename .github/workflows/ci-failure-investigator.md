---
on:
  workflow_run:
    workflows: ["*"]
    types: [completed]
  workflow_dispatch:
    inputs:
      run_id:
        description: 'Workflow run ID to investigate'
        required: true

permissions:
  contents: read
  issues: read
  pull-requests: read
  actions: read

network: defaults

tools:
  github:
    toolsets: [default]

safe-outputs:
  create-issue:
    max: 1
  create-pull-request:
  add-comment:
    max: 2
  add-labels:
---

# CI Failure Investigator

Analyze CI/CD workflow failures and provide actionable fixes.

## Trigger Conditions

Only investigate when:
- A workflow has completed with `failure` conclusion
- The failing workflow is NOT this investigator (skip self-investigation)
- Manual dispatch with a specific run_id

## Analysis Process

1. **Retrieve Failure Logs**
   - Download workflow run logs from the failed run
   - Extract error messages and stack traces
   - Identify the specific failing step(s)
   - Truncate logs if too large (keep last 200 lines)

2. **Classify the Failure Type**
   - 🧪 **Test Failure**: Unit/integration tests failing, assertion errors
   - 🛠️ **Build Failure**: Compilation errors, missing dependencies, syntax errors
   - ☁️ **Infrastructure Failure**: Network timeouts, service unavailable, rate limiting
   - ⚙️ **Config Failure**: Missing secrets, invalid YAML, incorrect paths

3. **Determine Severity**
   - 🔴 Critical: Blocks all deployments
   - 🟠 High: Major feature broken
   - 🟡 Medium: Non-critical functionality affected
   - 🟢 Low: Minor issue, workaround available

4. **Generate Response**
   
   If the failure is deterministic AND fix is straightforward:
   → Create a draft PR with minimal fix
   → Include verification steps
   
   Otherwise:
   → Create an issue with detailed analysis
   → Include root cause, suggested fix, and prevention tips

## Issue Template

When creating an issue, include:
- Workflow name and link to failed run
- Branch name
- Severity level with emoji indicator
- Root cause analysis
- Suggested fix with specific steps
- Code snippet if applicable
- List of related files
- Prevention recommendations

## PR Template (Auto-Fix)

When creating a fix PR, include:
- Brief description of the failure
- Link to the failed workflow run
- Root cause explanation
- Description of the fix applied
- Verification checklist

## Safety Guardrails

- PRs are always created as draft
- Fixes must be minimal and focused
- Never modify security-sensitive files automatically
- Never modify .github/workflows/*.yml without human review
- Maximum auto-fix attempts: 1 per failure
- Skip investigating self (workflows containing "Investigator")
