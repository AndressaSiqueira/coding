# Three Pillars AI Agent Demo 🤖

This repository demonstrates the **Three Pillars** of AI agent management in GitHub:

| Pillar | Description | Location |
|--------|-------------|----------|
| 🔓 **Agent Freedom** | Custom agents as versioned repo assets | [`.github/agents/`](.github/agents/) |
| 🎯 **Agent Orchestration** | Agentic automation via GitHub Actions | [`.github/copilot/agentic-workflows/`](.github/copilot/agentic-workflows/) |
| 🛡️ **Agent Controls** | Guardrails, evaluation, and CI gates | [`.github/workflows/`](.github/workflows/) |

## Quick Links

- [🎬 5-Minute Demo Script](#5-minute-demo-script)
- [📚 How It Works](#how-it-works)
- [⚙️ Setup Guide](#setup-guide)
- [🔑 Required Secrets](#required-secrets)
- [🐛 Troubleshooting](#troubleshooting)

---

## 🔓 Agent Freedom

Agent Freedom means defining custom AI agents as **versioned repository assets**. Instead of configuring agents in external tools, agent definitions live alongside your code.

### Repository Agents

| Agent | Purpose | File |
|-------|---------|------|
| **docs-agent** | Documentation maintenance specialist | [`.github/agents/docs-agent.agent.md`](.github/agents/docs-agent.agent.md) |
| **devops-agent** | CI/CD and workflow specialist | [`.github/agents/devops-agent.agent.md`](.github/agents/devops-agent.agent.md) |

### Why This Matters

- ✅ **Versioned**: Track agent changes over time with git
- ✅ **Reviewable**: Use pull requests to approve agent behavior changes
- ✅ **Portable**: Clone the repo, get the agents
- ✅ **Discoverable**: Anyone can see how agents behave

---

## 🎯 Agent Orchestration

Agent Orchestration uses **agentic workflows** to automate intelligent tasks via GitHub Actions.

### Implemented Workflows

#### 1. Continuous Triage
**Trigger**: When an issue is opened

**Actions**:
- Classifies issue as `bug`, `feature`, `docs`, or `question`
- Adds appropriate label
- Posts a helpful summary comment
- If `docs`: proposes documentation updates

**Files**:
- Intent: [`.github/copilot/agentic-workflows/continuous-triage.md`](.github/copilot/agentic-workflows/continuous-triage.md)
- Execution: [`.github/workflows/continuous-triage.yml`](.github/workflows/continuous-triage.yml)

#### 2. CI Failure Investigator
**Trigger**: When a workflow fails OR manual dispatch

**Actions**:
- Fetches failure logs
- Analyzes root cause
- Creates an issue with analysis and recommended fixes

**Files**:
- Intent: [`.github/copilot/agentic-workflows/ci-failure-investigator.md`](.github/copilot/agentic-workflows/ci-failure-investigator.md)
- Execution: [`.github/workflows/ci-failure-investigator.yml`](.github/workflows/ci-failure-investigator.yml)

---

## 🛡️ Agent Controls

Agent Controls ensure **quality, safety, and auditability** through automated gates.

### Evaluation Gate

**Workflow**: [`.github/workflows/foundry-agent-evaluate.yml`](.github/workflows/foundry-agent-evaluate.yml)

| Feature | Description |
|---------|-------------|
| **Trigger** | PRs modifying `foundry-agent/` |
| **Evaluation** | Azure AI Agent Evaluation action |
| **Metrics** | Coherence, Groundedness, Relevance, Fluency |
| **Gate** | PR blocked if thresholds not met |

### Deploy Gate

**Workflow**: [`.github/workflows/foundry-agent-deploy.yml`](.github/workflows/foundry-agent-deploy.yml)

| Feature | Description |
|---------|-------------|
| **Trigger** | Push to main modifying `foundry-agent/` |
| **Prerequisite** | Evaluation must pass |
| **Action** | Deploy/update agent via `azd ai agent` |
| **Audit** | Full logs in GitHub Actions |

---

## 🚀 Foundry Agent

The repository includes a deployable Azure AI Foundry agent:

| File | Purpose |
|------|----------|
| [`foundry-agent/agent.yaml`](foundry-agent/agent.yaml) | Declarative agent configuration |
| [`foundry-agent/instructions.md`](foundry-agent/instructions.md) | Agent system instructions |
| [`eval/dataset.json`](eval/dataset.json) | Evaluation test cases |

---

## 🎬 5-Minute Demo Script

Use this script to demonstrate all three pillars live:

### Slide 1: Agent Freedom (1 min)

1. Navigate to [`.github/agents/`](https://github.com/AndressaSiqueira/coding/tree/main/.github/agents)
2. Open `docs-agent.agent.md` - show YAML frontmatter + rules
3. Open `devops-agent.agent.md` - show specialization difference
4. **Key point**: "Agents are versioned files, reviewable via PRs"

### Slide 2: Agent Orchestration (2 min)

1. Go to **Issues** tab
2. Create new issue: "Add documentation for the eval dataset format"
3. Watch the **Continuous Triage** workflow run
4. Show the automatic label (`docs`) and comment
5. **Key point**: "Intelligent automation, triggered by events"

### Slide 3: Agent Controls (1.5 min)

1. Create a branch and modify `foundry-agent/instructions.md`
2. Open a Pull Request
3. Show the **Foundry Agent Evaluation** check running
4. Show evaluation results in PR comment
5. **Key point**: "Quality gates block bad changes"

### Slide 4: Deploy (0.5 min)

1. Merge the PR (if evaluation passed)
2. Show **Foundry Agent Deploy** workflow trigger
3. Show deployment summary in workflow logs
4. **Key point**: "Automated deployment to Azure AI Foundry"

---

## ⚙️ Setup Guide

### Prerequisites

- GitHub repository with Actions enabled
- Azure subscription with AI Foundry access
- Azure Developer CLI (`azd`) installed locally (for testing)

### Step 1: Fork/Clone Repository

```bash
git clone https://github.com/AndressaSiqueira/coding.git
cd coding
```

### Step 2: Configure Azure OIDC

Set up federated credentials for GitHub Actions:

```bash
# Create service principal
az ad sp create-for-rbac --name "github-three-pillars" --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth

# Configure federated identity
az ad app federated-credential create --id {app-id} --parameters @- <<EOF
{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:AndressaSiqueira/coding:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}
EOF
```

### Step 3: Add Repository Secrets

Go to **Settings > Secrets and variables > Actions** and add the secrets listed below.

### Step 4: Create Azure AI Project

```bash
# Using Azure CLI
az cognitiveservices account create \
  --name three-pillars-ai \
  --resource-group {resource-group} \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Deploy a model
az cognitiveservices account deployment create \
  --name three-pillars-ai \
  --resource-group {resource-group} \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-05-13" \
  --model-format OpenAI
```

---

## 🔑 Required Secrets

Configure these secrets in your repository settings:

| Secret | Description | Example |
|--------|-------------|----------|
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_TENANT_ID` | Azure AD tenant ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_CLIENT_ID` | Service principal app ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_RESOURCE_GROUP` | Resource group name | `rg-three-pillars` |
| `AZURE_AI_PROJECT_ENDPOINT` | AI Foundry project endpoint | `https://xxx.openai.azure.com/` |
| `AZURE_AI_PROJECT_NAME` | AI Foundry project name | `three-pillars-ai` |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Model deployment name | `gpt-4o` |

### Optional Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_AI_SEARCH_ENDPOINT` | For file_search tool |
| `AZURE_FUNCTION_ENDPOINT` | For custom tool integrations |

---

## 🐛 Troubleshooting

### Workflow not triggering

**Issue**: Continuous Triage doesn't run when issue is opened

**Solution**: 
1. Check Actions is enabled in repository settings
2. Verify workflow file is on the default branch
3. Check workflow permissions include `issues: write`

### Evaluation failing

**Issue**: Foundry Agent Evaluation fails with auth errors

**Solution**:
1. Verify OIDC is configured correctly
2. Check all AZURE_* secrets are set
3. Ensure service principal has Cognitive Services Contributor role

### Deploy not running

**Issue**: Deploy workflow doesn't trigger after merge

**Solution**:
1. Ensure changes were in `foundry-agent/` directory
2. Check the evaluation workflow passed on the PR
3. Verify the push was to `main` branch

### azd commands not found

**Issue**: `azd ai agent` commands fail

**Solution**:
1. The `azd ai` extension is in preview
2. Check [Azure Developer CLI docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/) for updates
3. Use fallback script in workflow (TODO section)

---

## 📝 TODO / Known Limitations

### azd AI Extension
The `azd ai agent` commands are in preview. If unavailable:
- Use Azure AI Foundry REST API directly
- Use Azure Python SDK
- Deploy via Azure portal

### Agentic Workflow Fallbacks
If GitHub Copilot agentic workflows are not available:
- The workflows still run as standard GitHub Actions
- Classification uses rule-based logic instead of AI
- PR creation requires manual steps

### Evaluation Action
The Azure AI Agent Evaluation action may have limited availability:
- Fallback static validation is included
- Manual evaluation can be triggered via Azure portal

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a PR - the agents will help review!

---

*Built to demonstrate AI agent best practices with GitHub and Azure AI Foundry*
