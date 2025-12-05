#!/usr/bin/env python3
"""
FOSSA to Datadog Integration Script

This script processes FOSSA scan results and sends metrics and events to Datadog.
It captures:
- Scan completion status
- Number of issues found
- License compliance violations
- Security vulnerabilities
- Custom events for tracking
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any
import requests


class DatadogReporter:
    """Handles sending metrics and events to Datadog"""
    
    def __init__(self, api_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.api_url = f"https://api.{site}"
        self.headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": api_key
        }
    
    def send_metric(self, metric_name: str, value: float, tags: List[str], metric_type: str = "gauge"):
        """Send a metric to Datadog"""
        current_time = int(time.time())
        
        payload = {
            "series": [
                {
                    "metric": metric_name,
                    "points": [[current_time, value]],
                    "type": metric_type,
                    "tags": tags
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v2/series",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"✓ Sent metric: {metric_name} = {value}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Error sending metric {metric_name}: {e}")
            return False
    
    def send_event(self, title: str, text: str, alert_type: str, tags: List[str], **kwargs):
        """Send an event to Datadog"""
        payload = {
            "title": title,
            "text": text,
            "alert_type": alert_type,  # info, warning, error, success
            "tags": tags,
            "source_type_name": "fossa",
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/events",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"✓ Sent event: {title}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Error sending event {title}: {e}")
            return False
    
    def send_service_check(self, check_name: str, status: int, tags: List[str], message: str = ""):
        """Send a service check to Datadog
        status: 0 (OK), 1 (WARNING), 2 (CRITICAL), 3 (UNKNOWN)
        """
        payload = {
            "check": check_name,
            "status": status,
            "tags": tags,
            "message": message,
            "timestamp": int(time.time())
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/check_run",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"✓ Sent service check: {check_name} = {status}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Error sending service check {check_name}: {e}")
            return False


def parse_fossa_results(results_file: str) -> Dict[str, Any]:
    """Parse FOSSA JSON results file"""
    try:
        with open(results_file, 'r') as f:
            content = f.read()
            
            # Handle empty file
            if not content.strip():
                return {
                    "issues": [],
                    "total_issues": 0,
                    "has_violations": False
                }
            
            data = json.loads(content)
            
            # FOSSA test output structure
            issues = data.get("issues", [])
            
            return {
                "issues": issues,
                "total_issues": len(issues),
                "has_violations": len(issues) > 0,
                "raw_data": data
            }
    except FileNotFoundError:
        print(f"Warning: FOSSA results file not found: {results_file}")
        return {
            "issues": [],
            "total_issues": 0,
            "has_violations": False
        }
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse FOSSA results as JSON: {e}")
        return {
            "issues": [],
            "total_issues": 0,
            "has_violations": False,
            "parse_error": str(e)
        }


def categorize_issues(issues: List[Dict]) -> Dict[str, int]:
    """Categorize FOSSA issues by type"""
    categories = {
        "license_violations": 0,
        "security_vulnerabilities": 0,
        "policy_violations": 0,
        "other": 0
    }
    
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "unknown": 0
    }
    
    for issue in issues:
        issue_type = issue.get("type", "").lower()
        severity = issue.get("severity", "unknown").lower()
        
        # Categorize by type
        if "license" in issue_type:
            categories["license_violations"] += 1
        elif "security" in issue_type or "vulnerability" in issue_type:
            categories["security_vulnerabilities"] += 1
        elif "policy" in issue_type:
            categories["policy_violations"] += 1
        else:
            categories["other"] += 1
        
        # Count by severity
        if severity in severity_counts:
            severity_counts[severity] += 1
        else:
            severity_counts["unknown"] += 1
    
    return {**categories, **severity_counts}


def main():
    parser = argparse.ArgumentParser(description="Send FOSSA scan results to Datadog")
    parser.add_argument("--fossa-results", required=True, help="Path to FOSSA JSON results file")
    parser.add_argument("--exit-code", type=int, required=True, help="FOSSA scan exit code")
    parser.add_argument("--dd-api-key", required=True, help="Datadog API key")
    parser.add_argument("--dd-site", default="datadoghq.com", help="Datadog site (e.g., datadoghq.com, datadoghq.eu)")
    parser.add_argument("--project-name", required=True, help="Project name")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--pipeline-id", required=True, help="Pipeline ID")
    parser.add_argument("--branch", default="unknown", help="Git branch name")
    parser.add_argument("--commit-sha", default="unknown", help="Git commit SHA")
    
    args = parser.parse_args()
    
    # Initialize Datadog reporter
    dd = DatadogReporter(args.dd_api_key, args.dd_site)
    
    # Parse FOSSA results
    print("\n" + "="*60)
    print("FOSSA to Datadog Integration")
    print("="*60 + "\n")
    
    results = parse_fossa_results(args.fossa_results)
    categories = categorize_issues(results["issues"])
    
    # Prepare common tags
    tags = [
        f"project:{args.project_name}",
        f"project_id:{args.project_id}",
        f"pipeline_id:{args.pipeline_id}",
        f"branch:{args.branch}",
        f"commit:{args.commit_sha[:8]}",
        "source:fossa",
        "service:security-scan"
    ]
    
    # Determine scan status
    scan_success = args.exit_code == 0
    status_text = "PASSED" if scan_success else "FAILED"
    alert_type = "success" if scan_success else "error"
    service_check_status = 0 if scan_success else 2  # OK or CRITICAL
    
    print(f"FOSSA Scan Status: {status_text}")
    print(f"Exit Code: {args.exit_code}")
    print(f"Total Issues: {results['total_issues']}")
    print(f"  - License Violations: {categories['license_violations']}")
    print(f"  - Security Vulnerabilities: {categories['security_vulnerabilities']}")
    print(f"  - Policy Violations: {categories['policy_violations']}")
    print(f"  - Other: {categories['other']}")
    print(f"\nSeverity Breakdown:")
    print(f"  - Critical: {categories['critical']}")
    print(f"  - High: {categories['high']}")
    print(f"  - Medium: {categories['medium']}")
    print(f"  - Low: {categories['low']}")
    
    print("\n" + "-"*60)
    print("Sending data to Datadog...")
    print("-"*60 + "\n")
    
    # Send metrics to Datadog
    metrics_sent = 0
    
    # 1. Scan status (0 = failed, 1 = passed)
    if dd.send_metric("fossa.scan.status", 1 if scan_success else 0, tags):
        metrics_sent += 1
    
    # 2. Total issues
    if dd.send_metric("fossa.issues.total", results["total_issues"], tags):
        metrics_sent += 1
    
    # 3. Issues by category
    if dd.send_metric("fossa.issues.license_violations", categories["license_violations"], tags):
        metrics_sent += 1
    
    if dd.send_metric("fossa.issues.security_vulnerabilities", categories["security_vulnerabilities"], tags):
        metrics_sent += 1
    
    if dd.send_metric("fossa.issues.policy_violations", categories["policy_violations"], tags):
        metrics_sent += 1
    
    # 4. Issues by severity
    if dd.send_metric("fossa.issues.critical", categories["critical"], tags):
        metrics_sent += 1
    
    if dd.send_metric("fossa.issues.high", categories["high"], tags):
        metrics_sent += 1
    
    if dd.send_metric("fossa.issues.medium", categories["medium"], tags):
        metrics_sent += 1
    
    if dd.send_metric("fossa.issues.low", categories["low"], tags):
        metrics_sent += 1
    
    # 5. Exit code
    if dd.send_metric("fossa.scan.exit_code", args.exit_code, tags):
        metrics_sent += 1
    
    # Send event to Datadog
    event_title = f"FOSSA Scan {status_text}: {args.project_name}"
    event_text = f"""
### FOSSA Security Scan Results

**Project:** {args.project_name}  
**Branch:** {args.branch}  
**Commit:** {args.commit_sha[:8]}  
**Pipeline:** {args.pipeline_id}  
**Status:** {status_text}  
**Exit Code:** {args.exit_code}

---

**Issues Found:** {results['total_issues']}

- **License Violations:** {categories['license_violations']}
- **Security Vulnerabilities:** {categories['security_vulnerabilities']}
- **Policy Violations:** {categories['policy_violations']}

**Severity Breakdown:**
- Critical: {categories['critical']}
- High: {categories['high']}
- Medium: {categories['medium']}
- Low: {categories['low']}

---

View detailed report in FOSSA dashboard.
"""
    
    if dd.send_event(event_title, event_text, alert_type, tags, priority="normal"):
        print("✓ Event sent successfully")
    
    # Send service check
    check_message = f"FOSSA scan {status_text} with {results['total_issues']} issues"
    if dd.send_service_check("fossa.scan", service_check_status, tags, check_message):
        print("✓ Service check sent successfully")
    
    print("\n" + "="*60)
    print(f"Summary: Sent {metrics_sent} metrics to Datadog")
    print("="*60 + "\n")
    
    # Print issues if any
    if results["total_issues"] > 0:
        print("Issues found:")
        for i, issue in enumerate(results["issues"][:10], 1):  # Show first 10
            print(f"  {i}. {issue.get('title', 'Unknown issue')} [{issue.get('severity', 'unknown')}]")
        
        if results["total_issues"] > 10:
            print(f"  ... and {results['total_issues'] - 10} more")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





