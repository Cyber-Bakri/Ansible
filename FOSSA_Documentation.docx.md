# FOSSA Integration Guide
**Version 2.0 | January 2026**

---

## Table of Contents
1. [Overview](#overview)
2. [FOSSA Environments](#fossa-environments)
3. [Access Management](#access-management)
4. [Team Structure](#team-structure)
5. [Onboarding](#onboarding)
6. [Jenkins Integration](#jenkins-integration)
7. [CLI Integration](#cli-integration)
8. [Troubleshooting](#troubleshooting)
9. [Resources](#resources)

---

## 1. Overview

FOSSA is a Software Composition Analysis (SCA) tool that generates Software Bill of Materials (SBOM) for dependency analysis and license compliance.

**Key Points:**
- **Use PROD environment** (`https://go/fossa`) for all production scans
- Request **"Fossa SSO Access PROD"** entitlement via IAM Portal
- Create 4 teams per project with AD mapping
- Auto-create is disabled - teams must be created manually

---

## 2. FOSSA Environments

### Environment URLs

| Environment | URL | Purpose |
|-------------|-----|---------|
| **Legacy** | `https://go/fossa-legacy` | Historical BlackDuck imports - reference only |
| **DEV** | Contact FOSSA admin | Infrastructure testing |
| **UAT** | `https://app.staging-us-bank.fossa.com` | Pipeline testing |
| **PROD** | `https://go/fossa` | **Production - use this** |

**Important:** PROD is the only environment product teams should use for scans.

### Migration Overview

US Bank migrated from Multi-Tenant (Legacy) to Single-Tenant (PROD) infrastructure:
- Legacy server maintains ~17,000 historical SBOMs for reference
- All new scans run on PROD Single-Tenant environment
- Entitlement-based access control (Legacy used manual management)

---

## 3. Access Management

### Entitlement Types

**1. Fossa SSO Access <ENVIRONMENT>**
- Grants UI access to FOSSA portal
- **Most product teams need**: `Fossa SSO Access PROD`

**2. Fossa Role <ROLE> <ENVIRONMENT>**
- Grants global privileges to ALL projects (bypasses team membership)
- Roles: Read, Write, Admin
- **Service accounts need**: `Fossa Role Write PROD` for Jenkins scans
- Use with caution - global privileges

### Requesting Access

1. Navigate to IAM Portal: `https://iamportal.us.bank-dns.com/entitlement_management/modify`
2. Search for "fossa"
3. Request appropriate entitlement:
   - Product team members: `Fossa SSO Access PROD`
   - Jenkins service accounts: `Fossa Role Write PROD`
4. Submit with business justification
5. Wait 1-3 business days for approval
6. Visit `https://go/fossa` to verify access

---

## 4. Team Structure

### Required Teams Per Project

For each project, create **four teams** with AD mapping:

| Team Name | Permission | AD Role | Purpose |
|-----------|------------|---------|---------|
| `{ProjectName}_owner` | Admin | Owner AD Group | Full control |
| `{ProjectName}_maintainer` | Editor | Maintainer AD Group | Modify/update |
| `{ProjectName}_contributor` | Editor | Contributor AD Group | Contribute |
| `{ProjectName}_viewer` | Viewer | Viewer AD Group | Read-only |

**Critical:** Teams must be created BEFORE running scans. Auto-create is disabled - scans will fail if teams don't exist.

### Admin Account Types

- **Human Admins**: Muted permissions (Editor) for day-to-day management
- **Non-Human Admin**: Service Account via CyberArk with Full Access for emergency tasks

---

## 5. Onboarding

### Quick Checklist

- [ ] Request `Fossa SSO Access PROD` entitlement
- [ ] Request `Fossa Role Write PROD` for service account (if using Jenkins)
- [ ] Wait for approval (1-3 days)
- [ ] Visit `https://go/fossa` to establish account
- [ ] Create 4 teams with AD mapping
- [ ] Generate API token (admin)
- [ ] Store token in Jenkins as `fossa-api-token`
- [ ] Add `fossaScan()` to Jenkinsfile
- [ ] Test and validate

---

## 6. Jenkins Integration

### Authorization Process

When running scans, FOSSA validates:
1. FOSSA_TEAM exists
2. Service account is team member
3. User has `Fossa SSO Access`
4. Scan fails if entitlements missing

### Naming Convention

Projects use this format:
```
METTA_APPLICATION.METTA_COMPONENT.VERSION
Example: BANKCARD-CLOUD.tmlite.001.00.00
```

- **METTA_APPLICATION**: CAR ID application name
- **METTA_COMPONENT**: Component name
- **VERSION**: Use TEST for testing, ALL for production

### Supported Languages

Golang, Java (Maven/Gradle), Python, JavaScript, PHP, .NET, C#

### Token Setup

1. Go to CloudBees → Credentials
2. Add Credentials → Secret Text
3. **Secret**: Paste FOSSA API token
4. **ID**: `fossa-api-token`
5. Save

**Migration Note:** Legacy tokens won't work on PROD. Generate new tokens from `https://go/fossa`.

### Basic Pipeline Example

```groovy
stage('Security Scans') {
    agent {
        kubernetes {
            yaml easyAgents()
        }
    }
    
    stages {
        stage('Fossa Scan') {
            steps {
                container('fossa') {
                    fossaScan(
                        releaseGroups: ['MyApp-Component.001.00.00'],
                        releaseGroupVer: "${env.BUILD_NUMBER}",
                        team: "ProjectName_owner"
                    )
                }
            }
        }
    }
}
```

### Configuration Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `releaseGroups` | Yes | Release group name | `['MyApp-Component.001.00.00']` |
| `releaseGroupVer` | Yes | Build version | `"${env.BUILD_NUMBER}"` |
| `team` | Yes | Team name (case-sensitive) | `"ProjectName_owner"` |
| `dependencies` | No | Link to other artifacts | `['MyLib.001.00.00':'123']` |

### Maven Configuration

If using Maven, provide `settings.xml`:

```groovy
stage('Fossa') {
    steps {
        container('fossa') {
            configFileProvider([configFile(fileId: 'YOUR-PROJECT', variable: 'MAVEN_SETTINGS')]) {
                sh 'cat $MAVEN_SETTINGS > settings.xml'
                fossaScan(
                    releaseGroups: ['MyApp.001.00.00'],
                    team: 'ProjectName_owner',
                    releaseGroupVer: "${BUILD_NUMBER}"
                )
            }
        }
    }
}
```

---

## 7. CLI Integration

### Installation

```bash
# Linux/Mac
curl -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/fossas/fossa-cli/master/install-latest.sh | bash

# Verify
fossa --version
```

### Configuration

```bash
export FOSSA_API_KEY="your-token"
export FOSSA_ENDPOINT="https://app.us-bank.fossa.com"
```

### Running Scans

```bash
fossa init
fossa analyze --team "ProjectName_owner"
fossa test
```

**Token Migration:** Legacy tokens won't work. Generate new tokens from PROD portal.

---

## 8. Troubleshooting

### Common Issues

**"Authentication Failed"**
- Verify `fossa-api-token` credential exists in Jenkins
- Check token hasn't expired
- Confirm you have Write or Admin role (Read is insufficient)
- If migrating, generate new token from PROD portal

**"Team Not Found"**
- Remember: Auto-create is disabled
- Manually create all 4 teams: `_owner`, `_maintainer`, `_contributor`, `_viewer`
- Verify team name matches exactly (case-sensitive)
- Ensure teams exist in PROD environment

**"Old API Token Not Working"**
- Legacy tokens won't work on Single-Tenant servers
- Generate new token from `https://go/fossa`
- Update Jenkins credential and CLI configuration
- Test in UAT before updating production

**"Maven Dependencies Not Found"**
- Verify `settings.xml` exists: `sh 'ls -la settings.xml'`
- Check configFileProvider fileId is correct
- Test Maven resolution: `mvn dependency:tree`

---

## 9. Resources

### Quick Reference

**Most Common Setup:**
1. Request `Fossa SSO Access PROD`
2. Visit `https://go/fossa`
3. Create 4 teams: `ProjectName_owner`, `_maintainer`, `_contributor`, `_viewer`
4. Generate token → Store as `fossa-api-token` in Jenkins
5. Use `fossaScan()` in pipeline

**Project Naming:**
```
METTA_APPLICATION.METTA_COMPONENT.VERSION
```

### Portal Links

| Resource | URL |
|----------|-----|
| **FOSSA PROD** | https://go/fossa |
| **IAM Portal** | https://iamportal.us.bank-dns.com/entitlement_management/modify |
| **EDSE Pipeline Docs** | Contact EDSE team |

### Support

| Issue Type | Contact |
|------------|---------|
| **Entitlements** | IAM Help Desk via Service Now |
| **Jenkins/Pipeline** | EDSE CDAAS Team (Slack: #edse-support) |
| **FOSSA Config** | Team FOSSA Admin |

---

## Appendix: Best Practices

**Naming:** Match Aegis/Fortify conventions  
**Versioning:** Always use `${env.BUILD_NUMBER}` for historical tracking  
**Security:** Never commit tokens to source control  
**Testing:** Test in UAT before promoting to PROD  
**Upgrades:** Staging is 2-3 weeks ahead of PROD; validate before production rollout

---

*Document Version: 2.0 | January 2026 | Migration to Single-Tenant Infrastructure*
