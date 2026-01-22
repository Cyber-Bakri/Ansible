# FOSSA Integration Guide

## Quick Start

**For Product Teams:**
1. Request `Fossa SSO Access PROD` via IAM Portal
2. Visit `https://go/fossa` 
3. Create 4 teams: `ProjectName_owner`, `_maintainer`, `_contributor`, `_viewer`
4. Generate API token → Store in Jenkins as `fossa-api-token`
5. Add `fossaScan()` to Jenkinsfile

---

## Environments

| Environment | URL | Use |
|-------------|-----|-----|
| **PROD** | `https://go/fossa` | **Production - use this** |
| UAT | `https://app.staging-us-bank.fossa.com` | Pipeline testing |
| DEV | Contact admin | Infrastructure testing |
| Legacy | `https://go/fossa-legacy` | Historical reference only |

---

## Access Management

### Entitlements

**Fossa SSO Access PROD** - UI access (most product teams need this)  
**Fossa Role Write PROD** - Global scan privileges (service accounts need this)

### Request Access

1. IAM Portal: `https://iamportal.us.bank-dns.com/entitlement_management/modify`
2. Search "fossa"
3. Request appropriate entitlement
4. Wait 1-3 days for approval

---

## Team Structure

Create 4 teams per project with AD mapping:

| Team | Permission | Purpose |
|------|------------|---------|
| `{ProjectName}_owner` | Admin | Full control |
| `{ProjectName}_maintainer` | Editor | Modify/update |
| `{ProjectName}_contributor` | Editor | Contribute |
| `{ProjectName}_viewer` | Viewer | Read-only |

**Important:** Teams must exist before running scans (auto-create disabled).

---

## Jenkins Integration

### Authorization

FOSSA validates: team exists → user is member → has SSO Access → entitlements present

### Naming Convention

```
METTA_APPLICATION.METTA_COMPONENT.VERSION
Example: BANKCARD-CLOUD.tmlite.001.00.00
```

### Supported Languages

Golang, Java, Python, JavaScript, PHP, .NET, C#

### Basic Pipeline

```groovy
stage('Fossa Scan') {
    agent {
        kubernetes {
            yaml easyAgents()
        }
    }
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
```

### Parameters

- `releaseGroups` - Array of release group names
- `releaseGroupVer` - Use `${env.BUILD_NUMBER}`
- `team` - Team name (case-sensitive)
- `dependencies` - Optional, link to other artifacts

### Token Setup

CloudBees → Credentials → Add → Secret Text
- **ID**: `fossa-api-token`
- **Secret**: Your FOSSA token from `https://go/fossa`

**Migration:** Legacy tokens won't work. Generate new from PROD.

---

## CLI Integration

```bash
# Install
curl -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/fossas/fossa-cli/master/install-latest.sh | bash

# Configure
export FOSSA_API_KEY="your-token"
export FOSSA_ENDPOINT="https://app.us-bank.fossa.com"

# Run
fossa analyze --team "ProjectName_owner"
```

---

## Troubleshooting

**"Authentication Failed"**
→ Check token exists, hasn't expired, have Write/Admin role

**"Team Not Found"**
→ Create 4 teams manually (auto-create disabled)

**"Old Token Not Working"**
→ Legacy tokens won't work on PROD, generate new token

**"Maven Dependencies Not Found"**
→ Ensure `settings.xml` in root directory

---

## Resources

**FOSSA PROD:** https://go/fossa  
**IAM Portal:** https://iamportal.us.bank-dns.com/entitlement_management/modify  
**Support:** EDSE CDAAS Team (Slack: #edse-support)

---

*Version 2.0 | January 2026*
