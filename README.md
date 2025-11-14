# Creating Terraform Cloud Workspaces for the Patrol Environment

## Overview

This document outlines the complete process for creating and configuring Terraform Cloud workspaces for the Patrol environment. The Patrol environment is a QA environment that requires dedicated infrastructure workspaces and corresponding application branches.

## High-Level Workflow

```
1. Clone pge-tfc-workspaces repo
   └─> Create feature branch
       └─> Add workspace blocks to wsv2-08.yaml
           └─> Run orchestration.py (validates YAML & generates JSON)
               └─> Create PR and merge
                   
2. Configure webcore-infra repo
   └─> Create patrol.tfvars
       └─> Update locals.tf with domains
           └─> Commit changes to patrol branch
           
3. Create patrol branches in all app repos
   └─> Engage-Graph
   └─> Engage-Queries-ECS
   └─> Engage-Webapp
   └─> Engage-Workorder-AtRisk-Sync
   └─> Engage-Workorder-Status-GIS-Sync
   └─> Engage-NLB-Manager
   
4. Verify workspace creation in Terraform Cloud
   └─> Check all 3 workspaces exist
       └─> Trigger initial Terraform runs
           └─> Monitor pipeline executions
           
5. Submit MyIT ticket for Azure AD
   └─> Wait for Azure AD configuration
       └─> Test authentication and access
           └─> ✅ Patrol environment ready!
```

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Infrastructure Configuration](#infrastructure-configuration)
5. [Application Repository Setup](#application-repository-setup)
6. [Validation and Deployment](#validation-and-deployment)
7. [Azure AD Authentication Setup](#phase-7-azure-ad-authentication-setup)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

---

## Prerequisites

Before beginning, ensure you have the following:

- **Access Requirements:**
  - Admin privileges to the `pge-tfc-workspaces` repository
  - Personal GitHub PAT (Personal Access Token) with appropriate permissions
  - Access to Terraform Cloud with appropriate workspace creation permissions
  - Read-only and apply AD group memberships configured

- **Tools:**
  - Git installed locally
  - Python 3.x installed (for running orchestration script)
  - Text editor or IDE

- **Knowledge:**
  - Basic understanding of Terraform Cloud workspaces
  - Familiarity with Git branching and pull request workflows
  - Understanding of YAML/JSON configuration files

---

## Architecture Overview

### Workspace Configuration Process

**Important:** Workspaces are defined in YAML files (`wsv2-*.yaml`), which are then validated and converted to JSON by the `orchestration.py` script. Both YAML (source) and JSON (generated) files are committed to the repository.

### Workspaces Created

Three Terraform Cloud workspaces were created for the Patrol environment:

| Workspace Name | Purpose | Working Directory |
|---|---|---|
| `patrolgraphinfra01` | Graph service infrastructure | `tf` |
| `patrolqueriesinfra01` | Queries service infrastructure | `tf` |
| `patrolwebappinfra01` | Web application infrastructure | `tf` |

### Application Repositories

The following application repositories required `patrol` branches:

- **webcore-infra** (Infrastructure configuration)
- **Engage-Graph**
- **Engage-Queries-ECS**
- **Engage-Webapp**
- **Engage-Workorder-AtRisk-Sync**
- **Engage-Workorder-Status-GIS-Sync**
- **Engage-NLB-Manager**

---

## Step-by-Step Implementation

### Phase 1: Repository Setup

#### 1. Clone the Workspace Repository

```bash
git clone https://github.com/pgetech/pge-tfc-workspaces
cd pge-tfc-workspaces
```

#### 2. Create a Feature Branch

Create a local branch following the naming convention: `<your-lan-id>/<jira-user-story>`

```bash
git checkout -b <your-lan-id>/<jira-ticket-id>
```

**Example:**
```bash
git checkout -b b1v6/CLOUDCOE-5414
```

#### 3. Locate the Workspace Configuration File

Navigate to the workspace configuration files:
```
workspaces-aws/wsv2-08.yaml
```

> **Important:** You edit YAML files, not JSON. The orchestration script will generate JSON files from your YAML configuration.

### Phase 2: Add Workspace Configurations

#### 4. Add Workspace Blocks to YAML

Add a workspace block for each of the three workspaces to the `wsv2-08.yaml` file. 

**Workspace Configuration Template (YAML):**

```yaml
<workspace-name>:
  account: "471817339124"
  apply_ad_groups: ["AWS-A2586-QA-Engage_Ops"]
  auto_apply: false
  branch: "patrol"
  csp: "aws"
  environment: "qa"
  file_triggers_enabled: true
  github_org: "PGEDigitalCatalyst"
  github_repo: "webcore-infra"
  project: "webcore"
  read_only_ad_groups: ["AWS-A3113-Dev-TF_Developers"]
  run_tasks: ["Wiz-QA"]
  terraform_version: "1.9.8"
  working_directory: "tf"
  tags: ["patrol", "infra"]
```

**Create three workspace blocks using this template with these names:**
- `patrolgraphinfra01`
- `patrolqueriesinfra01`
- `patrolwebappinfra01`

> **Note:** The configuration is identical for all three workspaces except for the workspace name. You can copy the template and change only the workspace name.

**Key Parameters:**
- `account`: AWS account ID (471817339124 for QA)
- `branch`: Git branch to monitor (patrol)
- `environment`: Environment type (qa)
- `apply_ad_groups`: AD group with apply permissions
- `terraform_version`: Terraform version (1.9.8)

### Phase 3: Validation

#### 5. Set GitHub PAT Environment Variable

**For PowerShell users:**
```powershell
$Env:GH_TOKEN='ghp_XXX'
```

**For Bash/Linux users:**
```bash
export GH_TOKEN='ghp_XXX'
```

#### 6. Run the Orchestration Script

The `orchestration.py` script validates your YAML configuration and generates the corresponding JSON files.

**Validate and generate JSON:**
```bash
python ./scripts/orchestration.py -w internal/aws/json/workspaces -f wsv2-08 -a
```

The script will:
- Validate that repository and branch exist
- Check all required fields are present
- Generate `wsv2-08.json` from `wsv2-08.yaml`

#### 7. Commit and Push Changes

```bash
git add workspaces-aws/wsv2-08.yaml workspaces-aws/wsv2-08.json
git commit -m "feat: add patrol workspaces for graph, queries, and webapp"
git push origin <your-branch-name>
```

> **Note:** Commit both the YAML source file and the generated JSON file.

#### 8. Create Pull Request

1. Navigate to the GitHub repository
2. Create a pull request from your branch to `main`
3. Add appropriate reviewers
4. Wait for approval and merge

---

## Infrastructure Configuration

### Phase 4: Configure webcore-infra Repository

Once the workspaces are created in Terraform Cloud, you need to configure the infrastructure repository.

#### 9. Create patrol.tfvars File

In the `webcore-infra` repository, create: `tf/vars/patrol.tfvars`

```hcl
app_id              = "2586"
data_classification = "Internal"
cris                = "Low"
notify              = ["engage-devops@pge.com"]
owner               = ["A1P2", "C1MP", "C3T1"]
compliance          = ["None"]
order               = "70039360"
```

> **Tip:** These values are specific to the Engage application. Adjust based on your application's requirements.

#### 10. Update locals.tf

Add patrol workspace FQDN (Fully Qualified Domain Name) mappings to `tf/locals.tf`.

**In the `workspace_webapp_fqdn` block, add:**

```hcl
"patrolgraphinfra01"    = "engage-patrol.digitalcatalyst.pge.com"
"patrolqueriesinfra01"  = "engage-patrol.digitalcatalyst.pge.com"
"patrolwebappinfra01"   = "engage-patrol.digitalcatalyst.pge.com"
```

**In the `workspace_viewer_fqdn` block, add:**

```hcl
"patrolinfra03" = "viewer-patrol.dc.pge.com"
```

> **Note:** Webapp patrol workspace use the same domain: `engage-patrol.digitalcatalyst.pge.com`

---

## Application Repository Setup

### Phase 5: Create Patrol Branches

**Critical:** The Terraform Cloud workspaces will trigger pipeline runs when changes are detected on the `patrol` branch. If the branches don't exist, the pipelines will fail.

#### 11. Create patrol Branch in Each Application Repository

For each of the following repositories, create a `patrol` branch:

1. **webcore-infra**
2. **Engage-Graph**
3. **Engage-Queries-ECS**
4. **Engage-Webapp**
5. **Engage-Workorder-AtRisk-Sync**
6. **Engage-Workorder-Status-GIS-Sync**
7. **Engage-NLB-Manager**

**Commands for each repository:**

```bash
# Clone the repository
git clone https://github.com/PGEDigitalCatalyst/<repository-name>
cd <repository-name>

# Create patrol branch from dev (or main)
git checkout dev
git pull origin dev
git checkout -b patrol
git push origin patrol
```

#### 12. Update Application Configuration (If Needed)

Some repositories may require additional configuration:

**Add patrol script to `package.json`:**
```json
"start:patrol": "dotenvx run -f .env -f .env.patrol --overload -- pm2-runtime start ecosystem.config.js"
```

**Create `.env.patrol` file (if using environment files):**
```bash
NODE_ENV=patrol
API_URL=https://engage-patrol.digitalcatalyst.pge.com
# ... other patrol-specific variables
```

> **Note:** Not all repositories require these changes. Check if your application uses environment-specific configurations.

---

## Validation and Deployment

### Phase 6: Verify Workspace Creation

#### 14. Verify Workspaces in Terraform Cloud

1. Log in to [Terraform Cloud](https://app.terraform.io)
2. Navigate to the `webcore` project
3. Confirm all three workspaces exist: patrolgraphinfra01, patrolqueriesinfra01, patrolwebappinfra01

#### 15. Check Pipeline Execution

Search for "patrol" in your CI/CD platform. Expected pipelines:
- engage-queries-patrol
- engage-graph-patrol
- engage-webapp-patrol
- Other lambda-related patrol pipelines

All should show "Succeeded" status.

#### 16. Run Initial Terraform Apply

For each workspace, trigger a run in Terraform Cloud and review/approve the plan.

---

## Phase 7: Azure AD Authentication Setup

### 17. Configure Azure AD Application Registration

After the infrastructure is deployed and the domain is accessible, you need to configure Azure AD authentication.

#### Symptom

When accessing the patrol domain (e.g., `https://engage-patrol.digitalcatalyst.pge.com`), you encounter an Azure AD authentication error:

```
AADSTS50011: The redirect URI 'https://engage-patrol.digitalcatalyst.pge.com/redirect' 
specified in the request does not match the redirect URIs configured for the application.
```

#### Solution

Submit a MyIT Services request to configure Azure AD authentication for the patrol environment.

#### Required Information for the Ticket

| Field | Value |
|---|---|
| **Request Type** | Azure AD Application Registration |
| **AppId** | 2586 |
| **Application Name** | Engage - MRAD |
| **Environment Type** | QA |
| **Application Internal URL** | `https://engage-patrol.digitalcatalyst.pge.com` |
| **Desired App Name** | `engage-patrol-pgedev.msappproxy.net` |
| **AWS Account Number** | 471817339124 |

**AD Groups Requiring Access:**
- AAD-Apr-A2586-Non-Prod-Engage-Supervisor-QA-AzureAD
- AAD-Apr-A2586-Non-Prod-PTT-Supervisor-QA-AzureAD
- AAD-Apr-A2586-Non-Prod-ET-Supervisor-QA-AzureAD
- AAD-Apr-A2586-Non-Prod-ET-RO-Supervisor-QA-AzureAD
- AAD-Apr-A2586-Non-Prod-Engage-Admin-QA-AzureAD

> **Tip:** Customize these values based on your application's specific requirements and AD groups.

#### Ticket Submission & Timeline

1. Navigate to [MyIT Services portal](https://iis101.cloud.pge.com/MyITServices/)
2. Search for "Azure AD Application Registration"
3. Submit ticket with the information above
4. **Expected resolution:** 2-5 business days

#### Verification After Resolution

Once the ticket is resolved:

1. Navigate to `https://engage-patrol.digitalcatalyst.pge.com`
2. Click "Sign In"
3. Authenticate with your PG&E credentials
4. Verify successful login and access to the application

**Note:** This step is critical and must be completed before users can access the patrol environment. Without proper Azure AD configuration, all authentication attempts will fail.

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Pipeline Fails - "Branch not found"
**Solution:** Create the `patrol` branch in all application repositories (see Phase 5, Step 11).

#### Issue 2: Orchestration Script Validation Fails
**Solution:** Check JSON syntax, ensure all mandatory fields are present, and verify repo/branch exist in GitHub.

#### Issue 3: Terraform Plan Fails
**Solution:** Verify `patrol.tfvars` exists and is properly formatted with all required variables.

#### Issue 4: Domain Name Resolution Issues
**Solution:** Verify domain mappings in `locals.tf` and check DNS/load balancer configurations.

#### Issue 5: Permission Denied Errors
**Solution:** Verify admin access to repository, check AD group memberships, and ensure GitHub PAT has proper permissions.

#### Issue 6: Azure AD Authentication Error (AADSTS50011)
**Solution:** This is expected before Azure AD configuration. Submit MyIT ticket as described in Phase 7. Resolution time: 2-5 business days.

---

## References

### Key Links
- **Workspace Repo:** https://github.com/pgetech/pge-tfc-workspaces
- **Infrastructure Repo:** https://github.com/PGEDigitalCatalyst/webcore-infra
- **Terraform Cloud:** https://app.terraform.io
- **MyIT Services:** https://iis101.cloud.pge.com/MyITServices/

### Key Files
- `workspaces-aws/wsv2-08.yaml` - Workspace definitions (source)
- `workspaces-aws/wsv2-08.json` - Generated workspace JSON
- `scripts/orchestration.py` - Validation and generation script
- `tf/vars/patrol.tfvars` - Environment variables
- `tf/locals.tf` - Domain mappings

---

## Summary

This document covered the complete process of creating Terraform Cloud workspaces for the Patrol environment, including:

1. ✅ Cloning and configuring the workspace repository
2. ✅ Adding workspace configurations to `wsv2-08.json`
3. ✅ Running validation with the orchestration script
4. ✅ Creating pull request and merging changes
5. ✅ Configuring infrastructure variables and domain mappings
6. ✅ Creating patrol branches in all application repositories
7. ✅ Verifying workspace creation and pipeline execution
8. ✅ Configuring Azure AD authentication for secure access

**Result:** Three fully functional Terraform Cloud workspaces for the Patrol environment with successful pipeline deployments and Azure AD authentication configured.

**Important:** The Azure AD authentication setup (Phase 7) is a critical post-deployment step. Without it, users will not be able to access the patrol environment through the web interface.

---

## Implementation Timeline

Typical timeline for creating patrol workspaces from start to finish:

| Phase | Task | Estimated Time |
|---|---|---|
| 1-3 | YAML configuration, validation, and JSON generation | 1-2 hours |
| 4 | Infrastructure configuration | 30 minutes |
| 5 | Creating application branches | 30-60 minutes |
| 6 | Workspace verification and Terraform runs | 30 minutes |
| 7 | Azure AD ticket submission | 15 minutes |
| 7 | Azure AD configuration (waiting) | 2-5 business days |
| **Total Active Work** | **~3-4 hours** | |
| **Total Calendar Time** | **3-6 business days** | |

**Note:** Most of the calendar time is spent waiting for Azure AD configuration. The actual hands-on work can be completed in a single day.

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2025-11-13 | Initial Author | Initial documentation creation |

---

## Quick Checklist

Use this checklist to track your progress when creating patrol workspaces:

### Pre-Implementation
- [ ] Verify you have admin access to pge-tfc-workspaces repository
- [ ] Create GitHub Personal Access Token (PAT)
- [ ] Set GH_TOKEN environment variable
- [ ] Identify all application repositories that need patrol branches

### Phase 1-3: Workspace Configuration
- [ ] Clone pge-tfc-workspaces repository
- [ ] Create feature branch: `<lan-id>/<jira-ticket>`
- [ ] Add patrolgraphinfra01 workspace block to wsv2-08.yaml
- [ ] Add patrolqueriesinfra01 workspace block to wsv2-08.yaml
- [ ] Add patrolwebappinfra01 workspace block to wsv2-08.yaml
- [ ] Run orchestration.py script (validates YAML and generates JSON)
- [ ] Fix any validation errors
- [ ] Commit both YAML and generated JSON files
- [ ] Create pull request
- [ ] Wait for approval and merge

### Phase 4: Infrastructure Configuration
- [ ] Clone/navigate to webcore-infra repository
- [ ] Checkout patrol branch (or create from dev)
- [ ] Create tf/vars/patrol.tfvars file
- [ ] Update tf/locals.tf with patrol workspace FQDNs
- [ ] Update workspace_viewer_fqdn in locals.tf
- [ ] Commit and push changes to patrol branch

### Phase 5: Application Repository Setup
- [ ] Create patrol branch in webcore-infra
- [ ] Create patrol branch in Engage-Graph
- [ ] Create patrol branch in Engage-Queries-ECS
- [ ] Create patrol branch in Engage-Webapp
- [ ] Create patrol branch in Engage-Workorder-AtRisk-Sync
- [ ] Create patrol branch in Engage-Workorder-Status-GIS-Sync
- [ ] Create patrol branch in Engage-NLB-Manager
- [ ] Add start:patrol scripts to package.json files (if needed)
- [ ] Create .env.patrol configuration files (if needed)

### Phase 6: Validation and Deployment
- [ ] Verify patrolgraphinfra01 exists in Terraform Cloud
- [ ] Verify patrolqueriesinfra01 exists in Terraform Cloud
- [ ] Verify patrolwebappinfra01 exists in Terraform Cloud
- [ ] Trigger initial Terraform run for patrolgraphinfra01
- [ ] Trigger initial Terraform run for patrolqueriesinfra01
- [ ] Trigger initial Terraform run for patrolwebappinfra01
- [ ] Verify engage-queries-patrol pipeline succeeds
- [ ] Verify engage-graph-patrol pipeline succeeds
- [ ] Verify engage-webapp-patrol pipeline succeeds
- [ ] Verify all other patrol pipelines succeed

### Phase 7: Azure AD Configuration
- [ ] Navigate to MyIT Services portal
- [ ] Submit Azure AD Application Registration ticket
- [ ] Include all required information (AppId, URL, AD Groups)
- [ ] Wait for ticket resolution (2-5 business days)
- [ ] Test access to https://engage-patrol.digitalcatalyst.pge.com
- [ ] Verify successful authentication
- [ ] Confirm application loads correctly

### Post-Implementation
- [ ] Document any issues encountered
- [ ] Share knowledge with team
- [ ] Update this documentation if needed

---

## Feedback

For questions, issues, or improvements to this documentation, please contact:
- **Team:** Engage DevOps
- **Email:** engage-devops@pge.com
- **Slack Channel:** #engage-devops

