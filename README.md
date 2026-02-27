# Three Pillars AI Agent Demo 🤖

This repository demonstrates the **Three Pillars** of AI agent management in GitHub using the **Agentic HQ** methodology.

## The Three Pillars

| Pillar | Description | Location |
|--------|-------------|----------|
| 🔓 **Agent Freedom** | Custom agents as versioned repo assets | [`.github/agents/`](.github/agents/) |
| 🎯 **Agent Orchestration** | Agentic automation via GitHub Actions | [`.github/workflows/`](.github/workflows/) |
| 🛡️ **Agent Controls** | Guardrails, evaluation, and CI gates | [`.github/workflows/`](.github/workflows/) |

## Quick Links

- [🔓 Agent Freedom](#-agent-freedom)
- [🎯 Agent Orchestration](#-agent-orchestration)
- [🛡️ Agent Controls](#%EF%B8%8F-agent-controls)
- [🚀 Foundry Agent](#-foundry-agent)
- [🎬 5-Minute Demo Script](#-5-minute-demo-script)
- [⚙️ Setup Guide](#%EF%B8%8F-setup-guide)
- [🔑 Required Secrets](#-required-secrets)
- [🐛 Troubleshooting](#-troubleshooting)

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
- Intent: [`.github/workflows/continuous-triage.md`](.github/workflows/continuous-triage.md)
- Workflow: [`.github/workflows/continuous-triage.lock.yml`](.github/workflows/continuous-triage.lock.yml)

---

## 🛡️ Agent Controls

Agent Controls ensure **quality, safety, and auditability** through automated gates.

### Deploy Gate

**Workflow**: [`.github/workflows/foundry-agent-deploy.yml`](.github/workflows/foundry-agent-deploy.yml)

| Feature | Description |
|---------|-------------|
| **Trigger** | Push to main modifying `foundry-agent/` |
| **Action** | Deploy/update agent via Azure AI Foundry |
| **Audit** | Full logs in GitHub Actions |

> **Note**: Evaluation workflows can be added to enforce quality gates before deployment. See the [Setup Guide](#%EF%B8%8F-setup-guide) for more information.

---

## 🚀 Foundry Agent

The repository includes a deployable Azure AI Foundry agent:

| File | Purpose |
|------|----------|
| [`foundry-agent/agent.yaml`](foundry-agent/agent.yaml) | Declarative agent configuration |
| [`foundry-agent/instructions.md`](foundry-agent/instructions.md) | Agent system instructions |

The agent demonstrates the **Agentic HQ** methodology, where agents are managed as versioned files in your repository.

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

1. Navigate to [`.github/workflows/`](https://github.com/AndressaSiqueira/coding/tree/main/.github/workflows)
2. Show the `foundry-agent-deploy.yml` workflow
3. Explain how deployment happens automatically when changes are pushed to main
4. **Key point**: "Automated deployment with audit trails"

### Slide 4: Live Demo (0.5 min)

1. Make a change to `foundry-agent/instructions.md`
2. Push to main branch
3. Show **Foundry Agent Deploy** workflow trigger
4. Show deployment summary in workflow logs
5. **Key point**: "Automated deployment to Azure AI Foundry"

---

## ⚙️ Setup Guide

### Prerequisites

- GitHub repository with Actions enabled
- Azure subscription with AI Foundry access
- (Optional) Azure Developer CLI (`azd`) installed locally for testing

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

### Deploy failing

**Issue**: Foundry Agent Deploy fails with auth errors

**Solution**:
1. Verify OIDC is configured correctly
2. Check all AZURE_* secrets are set
3. Ensure service principal has Cognitive Services Contributor role

### Deploy not running

**Issue**: Deploy workflow doesn't trigger after push

**Solution**:
1. Ensure changes were in `foundry-agent/` directory
2. Verify the push was to `main` branch
3. Check workflow permissions in repository settings

---

## 📝 Extending This Demo

### Adding Evaluation Workflows

To add quality gates before deployment:

1. Create an evaluation dataset in `eval/dataset.json` with test cases
2. Add an evaluation workflow in `.github/workflows/foundry-agent-evaluate.yml`
3. Configure it to run on PRs that modify `foundry-agent/`
4. Set quality thresholds (coherence, groundedness, relevance, fluency ≥ 3.5)

### Adding More Agentic Workflows

To create additional automated workflows:

1. Define the workflow intent in `.github/workflows/<workflow-name>.md`
2. Implement the automation logic
3. Set up appropriate triggers and permissions
4. Test with real repository events

### Agentic Workflow Considerations

GitHub Copilot agentic workflows enable intelligent automation. If not available:
- Workflows run as standard GitHub Actions
- Classification uses rule-based logic instead of AI
- Manual steps may be required for some features

---

## 📄 License

This project is open source. See the repository for license details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a PR - the agents will help review!

## 🌐 Language / Idioma

This documentation is available in English. Para documentação em português, sinta-se à vontade para abrir uma issue solicitando tradução.

---

**Built to demonstrate AI agent best practices with GitHub and Azure AI Foundry using the Agentic HQ methodology**
