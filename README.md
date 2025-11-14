# User Request Data Flow - Quick Reference

## Overview
This document provides a concise overview of how user requests flow from the browser through AWS infrastructure to your web application.

---

## Architecture Stack

```
Browser → Route53 → CloudFront → WAF → CloudFront Cache → S3
```

**Components:**
- **Route53**: DNS resolution
- **CloudFront**: Global CDN with edge caching
- **WAF**: Web Application Firewall (IP whitelist + AWS managed rules)
- **S3**: Static web content hosting
- **Origin Access Control (OAC)**: Secure CloudFront-to-S3 communication

---

## Request Flow (8 Steps)

### 1️⃣ DNS Resolution
```
User enters: https://webapp.pge.com
Route53 returns: d1234abcd.cloudfront.net
```

### 2️⃣ TLS/SSL Handshake
```
CloudFront Edge Location (nearest to user)
↓
ACM Certificate validation
↓
Secure HTTPS connection established (TLS 1.2+)
```

### 3️⃣ WAF Security Check
```
Request → AWS WAF (us-east-1)
↓
Rule Priority 0: AWS Managed Rules (Known Bad Inputs)
Rule Priority 1: IP Whitelist (PGE Corporate IPs) → ALLOW
Default Action: BLOCK
↓
✅ Allowed OR ❌ Blocked (403 Forbidden)
```

**⚠️ Critical:** WAF MUST be in us-east-1 for CloudFront (AWS requirement)

### 4️⃣ CloudFront Cache Check
```
Cache HIT → Return cached content immediately
Cache MISS → Continue to origin (S3)
```

### 5️⃣ CloudFront Function (SPAs only)
```
For Angular/React apps:
Request: /dashboard → Rewritten to: /index.html
(Enables client-side routing)
```

### 6️⃣ Origin Request via OAC
```
CloudFront signs request with AWS SigV4
↓
S3 Bucket Policy validates CloudFront identity
↓
Access granted (only CloudFront can access S3)
```

### 7️⃣ S3 Content Retrieval
```
S3 Bucket retrieves: index.html, assets, etc.
Returns to CloudFront
```

### 8️⃣ Response to Browser
```
CloudFront caches response at edge
Compresses content
Adds security headers
↓
HTTPS response to browser
↓
Browser renders application
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER BROWSER                           │
│                https://webapp.pge.com                       │
└────────────────────┬────────────────────────────────────────┘
                     │ 1. DNS Query
                     ↓
┌────────────────────────────────────────────────────────────┐
│                    ROUTE 53                                │
│         Returns CloudFront domain name                     │
└────────────────────┬───────────────────────────────────────┘
                     │ 2. HTTPS Request
                     ↓
┌────────────────────────────────────────────────────────────┐
│              CLOUDFRONT EDGE LOCATION                      │
│                                                            │
│  Step 3: ACM Certificate (TLS Handshake)                  │
│          ↓                                                 │
│  Step 4: AWS WAF Security Filter                          │
│          ├─ AWS Managed Rules                             │
│          ├─ IP Whitelist → ALLOW/BLOCK                    │
│          ↓                                                 │
│  Step 5: Cache Check (HIT or MISS)                        │
│          ↓                                                 │
│  Step 6: CloudFront Function (SPA routing)                │
│          ↓                                                 │
└────────────────────┬───────────────────────────────────────┘
                     │ Origin Request (if cache miss)
                     ↓
┌────────────────────────────────────────────────────────────┐
│         CLOUDFRONT ORIGIN ACCESS CONTROL                   │
│           Signs request with AWS SigV4                     │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────────┐
│                  S3 BUCKET POLICY                          │
│       Validates CloudFront identity & SourceArn            │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────────┐
│                    S3 BUCKET                               │
│         /index.html, /assets/, /static/                    │
│    Block all public access - CloudFront only               │
└────────────────────┬───────────────────────────────────────┘
                     │ Content retrieved
                     ↓
         ┌───────────────────────┐
         │  CloudFront caches &  │
         │  returns to browser   │
         └───────────┬───────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────────┐
│                   USER BROWSER                             │
│              Renders web application                       │
└────────────────────────────────────────────────────────────┘
```

---

## Security Layers

| Layer | Component | Protection |
|-------|-----------|------------|
| 1 | Route53 | DNS resolution, geo-restriction (US/CA) |
| 2 | CloudFront | TLS 1.2+, HTTPS redirect, DDoS (Shield Standard) |
| 3 | WAF | IP whitelist, AWS managed rules, default BLOCK |
| 4 | OAC | Signed requests, prevents direct S3 access |
| 5 | S3 | Block public access, bucket policy, optional KMS encryption |

---

## Request Scenarios

### ✅ Scenario 1: First-Time User
```
DNS → TLS → WAF (ALLOW) → Cache MISS → Origin Request → S3 → Cache → Browser
Time: ~500ms-2s (depending on location)
```

### ⚡ Scenario 2: Returning User (Cached)
```
DNS (cached) → TLS → WAF (ALLOW) → Cache HIT → Browser
Time: ~50-200ms (served from edge)
```

### ❌ Scenario 3: Blocked Request
```
DNS → TLS → WAF (BLOCK - IP not whitelisted) → 403 Forbidden
Time: ~100ms (never reaches S3)
```

### 🔄 Scenario 4: SPA Client Route
```
User navigates to: /dashboard
CloudFront Function rewrites to: /index.html
Browser receives index.html → React/Angular router handles /dashboard
```

---

## CI/CD Deployment Flow

```
Developer pushes to GitHub
    ↓
GitHub Webhook triggers CodePipeline
    ↓
┌───────────────────────────────┐
│ Source   → GitHub checkout    │
│ Build    → npm install & build│
│ Sonarqube → Code quality scan │
│ Deploy   → Sync S3 + Invalidate CloudFront
└───────────────────────────────┘
    ↓
Users get new content in ~5-15 minutes
```

---

## Key Configuration

### Application Types
- `html` - Static HTML sites (no CloudFront Function)
- `angular` - Angular SPAs (with CloudFront Function for routing)
- `react` - React SPAs (with CloudFront Function for routing)
- `custom` - Custom configuration

### WAF Options
- `internal` - Module creates WAF in us-east-1 (recommended)
- `external` - Use existing WAF Web ACL via SSM parameter

### Logging Locations
- **CloudFront**: `s3://pge-{ACCOUNT}-cloudfront/`
- **WAF**: `s3://aws-waf-logs-{ACCOUNT}-us-east-1/`
- **S3 Access**: `s3://ccoe-s3-accesslogs-spoke-{REGION}-{ACCOUNT}/`

---

## Troubleshooting Quick Guide

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| 403 Forbidden | IP not in WAF whitelist | Check WAF IP Set |
| 404 on SPA routes | CloudFront Function missing | Verify `s3web_type` is "angular" or "react" |
| Stale content | Cache not invalidated | CodePipeline should auto-invalidate; check deploy logs |
| Slow load | Large bundle size | Implement code splitting, optimize images |
| SSL error | Certificate issue | Verify ACM cert in us-east-1, check domain validation |

---

## Important Notes

1. **WAF Region**: WAF for CloudFront MUST be in us-east-1 (AWS requirement)
2. **S3 Access**: No direct S3 access - only via CloudFront OAC
3. **Cache Invalidation**: Automatic during deployment via CodePipeline
4. **HTTPS Only**: HTTP requests automatically redirected to HTTPS
5. **Geo-Restriction**: Only US and Canada allowed by default

---

## Quick Reference - Terraform Modules

```hcl
# S3 Web Module - Main infrastructure
module "webapp" {
  source  = "app.terraform.io/pgetech/s3web/aws"
  version = "0.0.33"
  
  s3web_type         = "custom"  # or "html", "angular", "react"
  s3web_pge_waf      = "external" # or "internal"
  custom_domain_name = "webapp.pge.com"
  github_repo_url    = "https://github.com/ORG/REPO.git"
  github_branch      = "main"
}

# Pipeline Module - CI/CD
module "pl_webapp" {
  source  = "app.terraform.io/pgetech/mrad-webcore-plweb/aws"
  version = "0.2.1"
  
  repo_name                  = "Webapp"
  git_branch                 = "main"
  s3_bucket_id               = module.webapp[0].s3_bucket_id
  cloudfront_distribution_id = module.webapp[0].cloudfront_distribution_id
}
```

---

## Performance Tips

✅ Enable code splitting for SPAs  
✅ Optimize images (use WebP format)  
✅ Set proper cache headers in S3 metadata  
✅ Use CloudFront compression (automatic)  
✅ Minimize bundle size (tree-shaking, lazy loading)  

---

## Support

- **Module Owner**: PGE Cloud Center of Excellence (CCoE)
- **Documentation**: https://wiki.comp.pge.com/display/CCE/Terraform-S3Web
- **Terraform Registry**: https://app.terraform.io/app/pgetech/registry/modules

---

**For detailed information, see `REQUEST_DATA_FLOW.md`**

**Last Updated**: November 14, 2024

