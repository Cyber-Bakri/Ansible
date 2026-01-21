Below is a **copy-and-paste–ready wiki version**, written in the **same style and structure as your initial document** (sectioned, concise, operational, no narrative fluff).
You can paste this directly into Confluence / internal wiki without edits.

---

= FOSSA Platform Overview, Access Model, and CI/CD Integration =

== Overview ==

The organization operates **two FOSSA SaaS environments** as part of a platform transition:

* **Single-Tenant FOSSA** – Authoritative / Future state
* **Multi-Tenant FOSSA** – Legacy / Historical reference

This document defines:

* Which FOSSA platform teams must use
* Access and entitlement behavior
* Team and CI/CD requirements
* Migration impacts and known failure modes

---

== Official FOSSA Access Links ==

=== Single-Tenant FOSSA (Authoritative) ===

**Access URL:**

```
https://go/fossa
```

**Description:**
Primary FOSSA platform used for:

* New onboarding
* CI/CD pipeline scanning
* Production usage
* Controlled upgrades and validation

**Key Characteristics:**

* Dedicated AWS account
* SAML + Active Directory authentication
* Explicit team-based authorization
* Auto-creation of teams is **disabled**
* New scans establish a **new SBOM baseline**

---

=== Multi-Tenant FOSSA (Legacy) ===

**Access URL:**

```
https://go/fossa-legacy
```

**Description:**
Legacy shared SaaS environment retained for **historical reference only**.

**Key Characteristics:**

* Contains ~17,000 historical SBOMs
* Historical commit and scan data preserved
* More frequent platform updates
* Will be retired over time
* Not used for new onboarding or pipelines

---

== Platform Usage Guidance ==

| Use Case               | Platform                       |
| ---------------------- | ------------------------------ |
| New onboarding         | Single-Tenant (go/fossa)       |
| CI/CD integration      | Single-Tenant (go/fossa)       |
| Production scanning    | Single-Tenant (go/fossa)       |
| Controlled upgrades    | Single-Tenant (go/fossa)       |
| Historical SBOM review | Multi-Tenant (go/fossa-legacy) |

**Rule:** If unsure, default to **Single-Tenant FOSSA**.

---

== Authentication & Authorization ==

=== Authentication ===

* Managed via **SAML and Active Directory (AD)**
* Users authenticate with corporate credentials

=== Authorization Behavior ===

* AD group names must match **existing FOSSA teams**
* Matching team → user added
* No matching team → login succeeds but no data is visible
* Teams are **not auto-created**

---

== Team Management Model ==

=== Auto-Create Disabled (Important) ===

* Teams must be created manually
* FOSSA will not auto-create missing teams
* CI/CD scans referencing a non-existent team will **fail**

---

=== Required Team Structure per Project ===

Each project must have the following four teams:

| Team Name Pattern       | Role   |
| ----------------------- | ------ |
| `<project>_owner`       | Admin  |
| `<project>_maintainer`  | Editor |
| `<project>_contributor` | Editor |
| `<project>_viewer`      | Viewer |

**Scanning Behavior:**

* Scans are associated with all four teams
* Ensures visibility across roles and separation of duties

---

=== Team Administration ===

* Only **team admins** can add/remove users
* Org-level admin access is not required for routine management

---

== CI/CD Integration Requirements ==

=== Pre-Scan Prerequisites ===
Before enabling FOSSA scans:

# Project teams must exist in FOSSA

# AD groups must map correctly to teams

# Service accounts must be added to required teams

# Valid FOSSA API token must be configured in CI/CD

**Failure Mode:**
If a scan references a missing team, the scan fails immediately.

---

=== API Tokens & Credentials ===

* Legacy API tokens will be **de-provisioned**
* New tokens must be generated after SSO setup
* CI/CD credentials must be updated accordingly

---

== Desktop / Local CLI Integration ==

* Local scans use the `fossa-cli`
* CLI and plugins must be validated in **Staging**
* Old tokens will stop working after SSO enablement

---

== Version / Upgrade Information (Early Testers) ==

**Upgrade Cycle:**
Single-Tenant Staging leads Production by ~2–3 weeks.

**Testing Window:**
US Bank has 2–3 weeks to validate releases in Staging.

**Validation Strategy:**

* Automated tests for plugins, CLI, and build containers
* API latency and ingestion verification
* Certificate validation

**Sign-Off:**
Required within 5–10 business days for major upgrades.

**Deferral Policy:**

* Minor upgrades: up to 60 days
* Major upgrades: up to 90 days

**Auto-Trigger:**
If deferral expires, FOSSA performs an automatic upgrade.

---

== Vulnerability & SBOM Strategy ==

**Data Continuity:**
Live data is preserved during migration. Historical commits remain in Multi-Tenant.

**Baseline:**
Single-Tenant scanning establishes a **new baseline**.

**SBOM Strategy:**
~17,000 existing SBOMs remain in Multi-Tenant for historical reference. SBOM import is intentionally avoided to reduce complexity.

---

== Common Failure Scenarios ==

| Issue                             | Cause                  | Resolution                 |
| --------------------------------- | ---------------------- | -------------------------- |
| User logs in but sees nothing     | No matching FOSSA team | Create team + map AD group |
| CI/CD scan fails                  | Team does not exist    | Create team before scan    |
| Previously working pipeline fails | Auto-create disabled   | Complete onboarding        |
| Token no longer works             | Legacy token revoked   | Generate new token         |

---

== Summary ==

The move to **Single-Tenant FOSSA** provides stronger governance, improved stability, and controlled upgrades.
However, it requires **explicit onboarding**, **manual team creation**, and **clear AD mapping**.

All new work must use **[https://go/fossa](https://go/fossa)**.
The legacy environment (**[https://go/fossa-legacy](https://go/fossa-legacy)**) remains read-only for historical reference.

---

{{Category:FOSSA}}
{{Category:Security Scanning}}
{{Category:CI/CD}}

---

If you want, I can also:

* Align this exactly to your existing wiki headings
* Add a short **“Before You Start” checklist**
* Convert this to **Confluence storage format (XML)**
