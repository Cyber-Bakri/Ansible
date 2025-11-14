h1. Creating Terraform Cloud Workspaces for the Patrol Environment

h2. Overview

This document outlines the complete process for creating and configuring Terraform Cloud workspaces for the Patrol environment. The Patrol environment is a QA environment that requires dedicated infrastructure workspaces and corresponding application branches.

h2. High-Level Workflow

{code}
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
{code}

h2. Table of Contents

# [Prerequisites|#prerequisites]
# [Architecture Overview|#architecture-overview]
# [Step-by-Step Implementation|#step-by-step-implementation]
# [Infrastructure Configuration|#infrastructure-configuration]
# [Application Repository Setup|#application-repository-setup]
# [Validation and Deployment|#validation-and-deployment]
# [Azure AD Authentication Setup|#azure-ad-authentication-setup]
# [Troubleshooting|#troubleshooting]
# [References|#references]

----

h2. Prerequisites

{anchor:prerequisites}

h3. Access Requirements

* Admin privileges to the {{pge-tfc-workspaces}} repository
* Personal GitHub PAT (Personal Access Token) with appropriate permissions
* Access to Terraform Cloud with appropriate workspace creation permissions
* Read-only and apply AD group memberships configured

h3. Tools Required

* Git installed locally
* Python 3.x installed (for running orchestration script)
* Text editor or IDE

h3. Knowledge Required

* Basic understanding of Terraform Cloud workspaces
* Familiarity with Git branching and pull request workflows
* Understanding of YAML/JSON configuration files

----

h2. Architecture Overview

{anchor:architecture-overview}

h3. Workspace Configuration Process

{info}
*Important:* Workspaces are defined in YAML files ({{wsv2-*.yaml}}), which are then validated and converted to JSON by the {{orchestration.py}} script. Both YAML (source) and JSON (generated) files are committed to the repository.
{info}

h3. Workspaces Created

Three Terraform Cloud workspaces were created for the Patrol environment:

|| Workspace Name || Purpose || Working Directory ||
| {{patrolgraphinfra01}} | Graph service infrastructure | {{tf}} |
| {{patrolqueriesinfra01}} | Queries service infrastructure | {{tf}} |
| {{patrolwebappinfra01}} | Web application infrastructure | {{tf}} |

h3. Application Repositories

The following application repositories required {{patrol}} branches:

* *webcore-infra* (Infrastructure configuration)
* *Engage-Graph*
* *Engage-Queries-ECS*
* *Engage-Webapp*
* *Engage-Workorder-AtRisk-Sync*
* *Engage-Workorder-Status-GIS-Sync*
* *Engage-NLB-Manager*

----

h2. Step-by-Step Implementation

{anchor:step-by-step-implementation}

h3. Phase 1: Repository Setup

h4. 1. Clone the Workspace Repository

{code:bash}
git clone https://github.com/pgetech/pge-tfc-workspaces
cd pge-tfc-workspaces
{code}

h4. 2. Create a Feature Branch

Create a local branch following the naming convention: {{<your-lan-id>/<jira-user-story>}}

{code:bash}
git checkout -b <your-lan-id>/<jira-ticket-id>
{code}

*Example:*
{code:bash}
git checkout -b b1v6/CLOUDCOE-5414
{code}

h4. 3. Locate the Workspace Configuration File

Navigate to the workspace configuration files:
{code}
workspaces-aws/wsv2-08.yaml
{code}

{warning}
*Important:* You edit YAML files, not JSON. The orchestration script will generate JSON files from your YAML configuration.
{warning}

h3. Phase 2: Add Workspace Configurations

h4. 4. Add Workspace Blocks to YAML

Add a workspace block for each of the three workspaces to the {{wsv2-08.yaml}} file. 

*Workspace Configuration Template (YAML):*

{code:yaml}
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
{code}

*Create three workspace blocks using this template with these names:*
* {{patrolgraphinfra01}}
* {{patrolqueriesinfra01}}
* {{patrolwebappinfra01}}

{tip}
The configuration is identical for all three workspaces except for the workspace name. You can copy the template and change only the workspace name.
{tip}

*Key Parameters:*
* {{account}}: AWS account ID (471817339124 for QA)
* {{branch}}: Git branch to monitor (patrol)
* {{environment}}: Environment type (qa)
* {{apply_ad_groups}}: AD group with apply permissions
* {{terraform_version}}: Terraform version (1.9.8)

h3. Phase 3: Validation

h4. 5. Set GitHub PAT Environment Variable

*For PowerShell users:*
{code:powershell}
$Env:GH_TOKEN='ghp_XXX'
{code}

*For Bash/Linux users:*
{code:bash}
export GH_TOKEN='ghp_XXX'
{code}

h4. 6. Run the Orchestration Script

The {{orchestration.py}} script validates your YAML configuration and generates the corresponding JSON files.

*Validate and generate JSON:*
{code:bash}
python ./scripts/orchestration.py -w internal/aws/json/workspaces -f wsv2-08 -a
{code}

The script will:
* Validate that repository and branch exist
* Check all required fields are present
* Generate {{wsv2-08.json}} from {{wsv2-08.yaml}}

h4. 7. Commit and Push Changes

{code:bash}
git add workspaces-aws/wsv2-08.yaml workspaces-aws/wsv2-08.json
git commit -m "feat: add patrol workspaces for graph, queries, and webapp"
git push origin <your-branch-name>
{code}

{tip}
Commit both the YAML source file and the generated JSON file.
{tip}

h4. 8. Create Pull Request

# Navigate to the GitHub repository
# Create a pull request from your branch to {{main}}
# Add appropriate reviewers
# Wait for approval and merge

----

h2. Infrastructure Configuration

{anchor:infrastructure-configuration}

h3. Phase 4: Configure webcore-infra Repository

Once the workspaces are created in Terraform Cloud, you need to configure the infrastructure repository.

h4. 9. Create patrol.tfvars File

In the {{webcore-infra}} repository, create: {{tf/vars/patrol.tfvars}}

{code:hcl}
app_id              = "2586"
data_classification = "Internal"
cris                = "Low"
notify              = ["engage-devops@pge.com"]
owner               = ["A1P2", "C1MP", "C3T1"]
compliance          = ["None"]
order               = "70039360"
{code}

{tip}
These values are specific to the Engage application. Adjust based on your application's requirements.
{tip}

h4. 10. Update locals.tf

Add patrol workspace FQDN (Fully Qualified Domain Name) mappings to {{tf/locals.tf}}.

*In the {{workspace_webapp_fqdn}} block, add:*

{code:hcl}
"patrolgraphinfra01"    = "engage-patrol.digitalcatalyst.pge.com"
"patrolqueriesinfra01"  = "engage-patrol.digitalcatalyst.pge.com"
"patrolwebappinfra01"   = "engage-patrol.digitalcatalyst.pge.com"
{code}

*In the {{workspace_viewer_fqdn}} block, add:*

{code:hcl}
"patrolinfra03" = "viewer-patrol.dc.pge.com"
{code}

{tip}
Webapp patrol workspace use the same domain: {{engage-patrol.digitalcatalyst.pge.com}}
{tip}

----

h2. Application Repository Setup

{anchor:application-repository-setup}

h3. Phase 5: Create Patrol Branches

{warning}
*Critical:* The Terraform Cloud workspaces will trigger pipeline runs when changes are detected on the {{patrol}} branch. If the branches don't exist, the pipelines will fail.
{warning}

h4. 11. Create patrol Branch in Each Application Repository

For each of the following repositories, create a {{patrol}} branch:

# *webcore-infra*
# *Engage-Graph*
# *Engage-Queries-ECS*
# *Engage-Webapp*
# *Engage-Workorder-AtRisk-Sync*
# *Engage-Workorder-Status-GIS-Sync*
# *Engage-NLB-Manager*

*Commands for each repository:*

{code:bash}
# Clone the repository
git clone https://github.com/PGEDigitalCatalyst/<repository-name>
cd <repository-name>

# Create patrol branch from dev (or main)
git checkout dev
git pull origin dev
git checkout -b patrol
git push origin patrol
{code}

h4. 12. Update Application Configuration (If Needed)

Some repositories may require additional configuration:

*Add patrol script to {{package.json}}:*
{code:json}
"start:patrol": "dotenvx run -f .env -f .env.patrol --overload -- pm2-runtime start ecosystem.config.js"
{code}

*Create {{.env.patrol}} file (if using environment files):*
{code:bash}
NODE_ENV=patrol
API_URL=https://engage-patrol.digitalcatalyst.pge.com
# ... other patrol-specific variables
{code}

{info}
Not all repositories require these changes. Check if your application uses environment-specific configurations.
{info}

----

h2. Validation and Deployment

{anchor:validation-and-deployment}

h3. Phase 6: Verify Workspace Creation

h4. 14. Verify Workspaces in Terraform Cloud

# Log in to [Terraform Cloud|https://app.terraform.io]
# Navigate to the {{webcore}} project
# Confirm all three workspaces exist: patrolgraphinfra01, patrolqueriesinfra01, patrolwebappinfra01

h4. 15. Check Pipeline Execution

Search for "patrol" in your CI/CD platform. Expected pipelines:
* engage-queries-patrol
* engage-graph-patrol
* engage-webapp-patrol
* Other lambda-related patrol pipelines

All should show "Succeeded" status.

h4. 16. Run Initial Terraform Apply

For each workspace, trigger a run in Terraform Cloud and review/approve the plan.

----

h2. Phase 7: Azure AD Authentication Setup

{anchor:azure-ad-authentication-setup}

h3. 17. Configure Azure AD Application Registration

After the infrastructure is deployed and the domain is accessible, you need to configure Azure AD authentication.

h4. Symptom

When accessing the patrol domain (e.g., {{https://engage-patrol.digitalcatalyst.pge.com}}), you encounter an Azure AD authentication error:

{code}
AADSTS50011: The redirect URI 'https://engage-patrol.digitalcatalyst.pge.com/redirect' 
specified in the request does not match the redirect URIs configured for the application.
{code}

h4. Solution

Submit a MyIT Services request to configure Azure AD authentication for the patrol environment.

h4. Required Information for the Ticket

|| Field || Value ||
| *Request Type* | Azure AD Application Registration |
| *AppId* | 2586 |
| *Application Name* | Engage - MRAD |
| *Environment Type* | QA |
| *Application Internal URL* | {{https://engage-patrol.digitalcatalyst.pge.com}} |
| *Desired App Name* | {{engage-patrol-pgedev.msappproxy.net}} |
| *AWS Account Number* | 471817339124 |

*AD Groups Requiring Access:*
* AAD-Apr-A2586-Non-Prod-Engage-Supervisor-QA-AzureAD
* AAD-Apr-A2586-Non-Prod-PTT-Supervisor-QA-AzureAD
* AAD-Apr-A2586-Non-Prod-ET-Supervisor-QA-AzureAD
* AAD-Apr-A2586-Non-Prod-ET-RO-Supervisor-QA-AzureAD
* AAD-Apr-A2586-Non-Prod-Engage-Admin-QA-AzureAD

{tip}
Customize these values based on your application's specific requirements and AD groups.
{tip}

h4. Ticket Submission & Timeline

# Navigate to [MyIT Services portal|https://iis101.cloud.pge.com/MyITServices/]
# Search for "Azure AD Application Registration"
# Submit ticket with the information above
# *Expected resolution:* 2-5 business days

h4. Verification After Resolution

Once the ticket is resolved:

# Navigate to {{https://engage-patrol.digitalcatalyst.pge.com}}
# Click "Sign In"
# Authenticate with your PG&E credentials
# Verify successful login and access to the application

{warning}
This step is critical and must be completed before users can access the patrol environment. Without proper Azure AD configuration, all authentication attempts will fail.
{warning}

----

h2. Troubleshooting

{anchor:troubleshooting}

h3. Common Issues and Solutions

h4. Issue 1: Pipeline Fails - "Branch not found"
*Solution:* Create the {{patrol}} branch in all application repositories (see Phase 5, Step 11).

h4. Issue 2: Orchestration Script Validation Fails
*Solution:* Check JSON syntax, ensure all mandatory fields are present, and verify repo/branch exist in GitHub.

h4. Issue 3: Terraform Plan Fails
*Solution:* Verify {{patrol.tfvars}} exists and is properly formatted with all required variables.

h4. Issue 4: Domain Name Resolution Issues
*Solution:* Verify domain mappings in {{locals.tf}} and check DNS/load balancer configurations.

h4. Issue 5: Permission Denied Errors
*Solution:* Verify admin access to repository, check AD group memberships, and ensure GitHub PAT has proper permissions.

h4. Issue 6: Azure AD Authentication Error (AADSTS50011)
*Solution:* This is expected before Azure AD configuration. Submit MyIT ticket as described in Phase 7. Resolution time: 2-5 business days.

----

h2. References

{anchor:references}

h3. Key Links
* [Workspace Repo|https://github.com/pgetech/pge-tfc-workspaces]
* [Infrastructure Repo|https://github.com/PGEDigitalCatalyst/webcore-infra]
* [Terraform Cloud|https://app.terraform.io]
* [MyIT Services|https://iis101.cloud.pge.com/MyITServices/]

h3. Key Files
* {{workspaces-aws/wsv2-08.yaml}} - Workspace definitions (source)
* {{workspaces-aws/wsv2-08.json}} - Generated workspace JSON
* {{scripts/orchestration.py}} - Validation and generation script
* {{tf/vars/patrol.tfvars}} - Environment variables
* {{tf/locals.tf}} - Domain mappings

----

h2. Summary

This document covered the complete process of creating Terraform Cloud workspaces for the Patrol environment, including:

# (/) Cloning and configuring the workspace repository
# (/) Adding workspace configurations to {{wsv2-08.yaml}}
# (/) Running validation with the orchestration script
# (/) Creating pull request and merging changes
# (/) Configuring infrastructure variables and domain mappings
# (/) Creating patrol branches in all application repositories
# (/) Verifying workspace creation and pipeline execution
# (/) Configuring Azure AD authentication for secure access

*Result:* Three fully functional Terraform Cloud workspaces for the Patrol environment with successful pipeline deployments and Azure AD authentication configured.

{warning}
The Azure AD authentication setup (Phase 7) is a critical post-deployment step. Without it, users will not be able to access the patrol environment through the web interface.
{warning}

----

h2. Implementation Timeline

Typical timeline for creating patrol workspaces from start to finish:

|| Phase || Task || Estimated Time ||
| 1-3 | YAML configuration, validation, and JSON generation | 1-2 hours |
| 4 | Infrastructure configuration | 30 minutes |
| 5 | Creating application branches | 30-60 minutes |
| 6 | Workspace verification and Terraform runs | 30 minutes |
| 7 | Azure AD ticket submission | 15 minutes |
| 7 | Azure AD configuration (waiting) | 2-5 business days |
| *Total Active Work* | *~3-4 hours* | |
| *Total Calendar Time* | *3-6 business days* | |

{info}
Most of the calendar time is spent waiting for Azure AD configuration. The actual hands-on work can be completed in a single day.
{info}

----

h2. Quick Checklist

Use this checklist to track your progress when creating patrol workspaces:

h3. Pre-Implementation
* {_} Verify you have admin access to pge-tfc-workspaces repository
* {_} Create GitHub Personal Access Token (PAT)
* {_} Set GH_TOKEN environment variable
* {_} Identify all application repositories that need patrol branches

h3. Phase 1-3: Workspace Configuration
* {_} Clone pge-tfc-workspaces repository
* {_} Create feature branch: {{<lan-id>/<jira-ticket>}}
* {_} Add patrolgraphinfra01 workspace block to wsv2-08.yaml
* {_} Add patrolqueriesinfra01 workspace block to wsv2-08.yaml
* {_} Add patrolwebappinfra01 workspace block to wsv2-08.yaml
* {_} Run orchestration.py script (validates YAML and generates JSON)
* {_} Fix any validation errors
* {_} Commit both YAML and generated JSON files
* {_} Create pull request
* {_} Wait for approval and merge

h3. Phase 4: Infrastructure Configuration
* {_} Clone/navigate to webcore-infra repository
* {_} Checkout patrol branch (or create from dev)
* {_} Create tf/vars/patrol.tfvars file
* {_} Update tf/locals.tf with patrol workspace FQDNs
* {_} Update workspace_viewer_fqdn in locals.tf
* {_} Commit and push changes to patrol branch

h3. Phase 5: Application Repository Setup
* {_} Create patrol branch in webcore-infra
* {_} Create patrol branch in Engage-Graph
* {_} Create patrol branch in Engage-Queries-ECS
* {_} Create patrol branch in Engage-Webapp
* {_} Create patrol branch in Engage-Workorder-AtRisk-Sync
* {_} Create patrol branch in Engage-Workorder-Status-GIS-Sync
* {_} Create patrol branch in Engage-NLB-Manager
* {_} Add start:patrol scripts to package.json files (if needed)
* {_} Create .env.patrol configuration files (if needed)

h3. Phase 6: Validation and Deployment
* {_} Verify patrolgraphinfra01 exists in Terraform Cloud
* {_} Verify patrolqueriesinfra01 exists in Terraform Cloud
* {_} Verify patrolwebappinfra01 exists in Terraform Cloud
* {_} Trigger initial Terraform run for patrolgraphinfra01
* {_} Trigger initial Terraform run for patrolqueriesinfra01
* {_} Trigger initial Terraform run for patrolwebappinfra01
* {_} Verify engage-queries-patrol pipeline succeeds
* {_} Verify engage-graph-patrol pipeline succeeds
* {_} Verify engage-webapp-patrol pipeline succeeds
* {_} Verify all other patrol pipelines succeed

h3. Phase 7: Azure AD Configuration
* {_} Navigate to MyIT Services portal
* {_} Submit Azure AD Application Registration ticket
* {_} Include all required information (AppId, URL, AD Groups)
* {_} Wait for ticket resolution (2-5 business days)
* {_} Test access to https://engage-patrol.digitalcatalyst.pge.com
* {_} Verify successful authentication
* {_} Confirm application loads correctly

h3. Post-Implementation
* {_} Document any issues encountered
* {_} Share knowledge with team
* {_} Update this documentation if needed

----

h2. Feedback

For questions, issues, or improvements to this documentation, please contact:
* *Team:* Engage DevOps
* *Email:* engage-devops@pge.com
* *Slack Channel:* #engage-devops

