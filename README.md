Below is a **manager-ready, comprehensive documentation** you can present as an **authoritative FOSSA onboarding & operating guide**.
It is written in a **clear, executive-friendly but technically accurate tone**, suitable for **Confluence, SharePoint, or PDF**.

---

# FOSSA Platform Overview, Access Model, and CI/CD Integration

**(Single-Tenant vs Multi-Tenant Clarification & Operating Guidance)**

---

## 1. Executive Summary

The organization currently operates **two FOSSA SaaS environments** as part of a platform transition:

* A **Single-Tenant FOSSA instance** (new, authoritative, future state)
* A **Multi-Tenant FOSSA instance** (legacy, retained for historical data)

This document clarifies:

* Which platform teams must use going forward
* How access and entitlements work
* How team management and CI/CD scanning behavior has changed
* What actions application teams must take to avoid scan failures
* What historical data remains and why

This documentation resolves ongoing confusion around portals, entitlements, team creation, and pipeline behavior.

---

## 2. Official FOSSA Access Points

### 2.1 Single-Tenant FOSSA (Authoritative / Future State)

**Official Access Link**

```
https://go/fossa
```

**Purpose**

* Primary platform for:

  * New onboarding
  * CI/CD integration
  * Production security scanning
  * Controlled upgrades and validation

**Platform Characteristics**

* Dedicated AWS account
* Controlled release cadence
* SAML + Active Directory authentication
* Explicit team-based authorization
* No automatic creation of teams
* Establishes a **new SBOM baseline**

This is the **default and supported platform** moving forward.

---

### 2.2 Multi-Tenant FOSSA (Legacy / Historical)

**Official Access Link**

```
https://go/fossa-legacy
```

**Purpose**

* Retained for **historical reference only**

**Platform Characteristics**

* Shared SaaS environment
* Contains ~17,000 existing SBOMs
* Historical commits and scan data preserved
* More frequent platform changes
* Will be retired over time

This platform should **not** be used for new onboarding or pipelines.

---

## 3. Which Platform Should Teams Use?

| Use Case                   | Platform                         |
| -------------------------- | -------------------------------- |
| New onboarding             | Single-Tenant (`go/fossa`)       |
| CI/CD pipeline scans       | Single-Tenant (`go/fossa`)       |
| Production scanning        | Single-Tenant (`go/fossa`)       |
| Controlled upgrade testing | Single-Tenant (`go/fossa`)       |
| Historical SBOM review     | Multi-Tenant (`go/fossa-legacy`) |

**Guidance:**
If there is uncertainty, teams should **default to Single-Tenant FOSSA**.

---

## 4. Access & Authentication Model

### 4.1 Authentication

* Authentication is managed via **SAML and Active Directory (AD)**
* Users authenticate using corporate credentials
* AD group membership is evaluated at login

### 4.2 Authorization Behavior (Important)

* AD group names must match **existing FOSSA teams**
* If a matching team exists → user is added
* If no matching team exists → login succeeds, but user sees no data
* **Teams are not auto-created**

This behavior is intentional and enforces stricter governance.

---

## 5. Team Management Model (Critical Change)

### 5.1 Auto-Create Disabled

In the Single-Tenant FOSSA platform:

* Teams **must be created manually**
* FOSSA **will not auto-create teams**
* CI/CD scans referencing a non-existent team will **fail**

This is a significant change from earlier behavior and must be accounted for during onboarding.

---

### 5.2 Required Team Structure per Project

Each application or project must have **four predefined teams**:

| Team Name Pattern       | Role   |
| ----------------------- | ------ |
| `<project>_owner`       | Admin  |
| `<project>_maintainer`  | Editor |
| `<project>_contributor` | Editor |
| `<project>_viewer`      | Viewer |

**Scanning Behavior**

* Each scan is associated with all four teams
* Ensures visibility and access across roles
* Supports separation of duties

---

### 5.3 Team Administration

* Only **team admins** can add or remove users
* Organization-level admin access is not required for day-to-day team management
* This model decentralizes access while preserving governance

---

## 6. CI/CD Integration Requirements

### 6.1 Jenkins / Build Server Impact

**Mandatory prerequisites before enabling FOSSA scans:**

1. Project teams must exist in FOSSA
2. AD groups must map correctly to those teams
3. Service accounts must be assigned to required teams
4. Valid API token must be configured in Jenkins

**Failure Mode**

* If a scan references a missing team → scan fails immediately

This behavior is by design and must be documented for application teams.

---

### 6.2 API Tokens & Credential Management

* Existing API tokens from legacy environments will be **de-provisioned**
* New tokens must be generated after SSO setup
* Jenkins credentials must be updated accordingly

**Recommendation**

* Treat token rotation as mandatory during migration
* Avoid reusing legacy credentials

---

## 7. Desktop / Local CLI Usage

* Local scanning uses the `fossa-cli`
* CLI, plugins, and integrations must be:

  * Validated in **Staging**
  * Tested before Production use
* Once SSO is enabled, old tokens will no longer function

This primarily impacts developers running scans locally.

---

## 8. Upgrade & Release Management (Informational)

* Staging environment leads Production by **2–3 weeks**
* Validation window:

  * 2–3 weeks in Staging
* Sign-off required:

  * 5–10 business days for major upgrades
* Deferral policy:

  * Minor upgrades: up to 60 days
  * Major upgrades: up to 90 days
* If deferral expires, FOSSA performs an automatic upgrade to maintain security compliance

Pipeline owners do not manage upgrades directly; this is platform-controlled.

---

## 9. SBOM & Vulnerability Strategy

### 9.1 Data Continuity

* Live operational data is preserved during migration
* Historical commit data remains in the Multi-Tenant environment

### 9.2 Baseline Strategy

* Single-Tenant FOSSA establishes a **new SBOM baseline**
* Existing ~17,000 SBOMs remain in the legacy platform
* SBOM import is intentionally avoided to reduce complexity

This decision prevents data corruption and ensures clean baselining.

---

## 10. Common Failure Scenarios

| Issue                             | Cause                          | Resolution                    |
| --------------------------------- | ------------------------------ | ----------------------------- |
| User logs in but sees nothing     | No matching FOSSA team         | Create team + map AD group    |
| CI/CD scan fails immediately      | Referenced team does not exist | Create team before scan       |
| Pipeline worked before, now fails | Auto-create disabled           | Complete onboarding checklist |
| Token no longer works             | Legacy token de-provisioned    | Generate new token            |

---

## 11. Required Documentation Updates (Action Items)

To align with the Single-Tenant model, all FOSSA documentation must:

1. Reference **`https://go/fossa`** as the primary platform
2. Clearly label **`https://go/fossa-legacy`** as legacy
3. Explicitly state:

   * Teams must exist before scanning
   * Auto-create is disabled
   * Missing teams cause scan failures
4. Document the mandatory four-team project model
5. Clarify SBOM baseline and historical data strategy

---

## 12. Conclusion

The transition to **Single-Tenant FOSSA** introduces stronger governance, improved stability, and clearer ownership, but also requires **more deliberate onboarding**.

By documenting:

* Platform selection
* Team requirements
* AD mapping behavior
* CI/CD prerequisites

we eliminate ambiguity, reduce onboarding friction, and prevent avoidable pipeline failures.

---

### Optional Next Steps (If Approved)

* Publish a one-page **FOSSA onboarding checklist**
* Add Jenkins preflight validation guidance
* Create a visual flow diagram for access and scanning

---

If you want, I can:

* Convert this into a **Confluence-formatted page**
* Produce a **PDF for leadership**
* Create a **short executive summary slide**
* Tailor it to your org’s naming standards

Just tell me the format your manager prefers.
