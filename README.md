# User Request Flow: Browser → CloudFront → F5 → NGINX → Engage Webapp

## Overview
This document outlines the data flow path for user requests from the browser through our enterprise infrastructure to the Engage Web Application.

---

## Architecture Flow

```
Browser → CloudFront → F5 → NGINX (ECS/Fargate) → ALB → Engage Services → Datastores
```

---

## Component Breakdown

### 1. **Browser**
- User accesses: `https://engage.<company>.com`
- Initiates HTTPS request over public internet

### 2. **CloudFront (CDN + Edge Layer)**
**Responsibilities:**
- Global CDN edge caching
- TLS termination and AWS WAF security
- Serves static assets (HTML, JS, CSS) directly from S3 Webapp bucket
- Forwards dynamic/API requests to backend layers

**Traffic Split:**
- **Static content** → Served from S3 via CloudFront
- **Dynamic requests** → Forwarded to F5/ALB

### 3. **F5 (Network Gateway)**
**Responsibilities:**
- External-to-internal network bridging
- Enterprise security policy enforcement
- Load balancing and SSL offloading (if configured)
- Routes traffic to internal services

### 4. **NGINX (Reverse Proxy & Auth Layer)**
**Deployment:** ECS Fargate within Engage Web stack

**Responsibilities:**
- Entry-point routing for `/engage/*` endpoints
- Request forwarding to backend services (Queries, Proxy, Poller)
- Header injection and caching bypass logic
- Keepalive and connection management
- Entra Auth integration for authentication validation

**Example Configuration:**
```nginx
# Set the engage production server
location ~ ^/engage/?(.*)\$ {
    set $fqdn d34jzp2avuov5.cloudfront.net;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host engage.digitalcatalyst.pge.com;
    proxy_cache_bypass $http_upgrade;
    proxy_ssl_server_name on;
    
    keepalive_requests 1000;
    keepalive_timeout 360s;
    proxy_read_timeout 360s;
    
    proxy_pass https://$fqdn:443/engage/$1$is_args$args;
}
```

### 5. **Application Load Balancer (ALB)**
- Routes requests from NGINX to appropriate microservices
- Health checks and service distribution

### 6. **Engage Microservices**
**Services:**
- **Queries Service** - Read operations
- **Proxy Service** - Write/workflow operations
- **Poller Service** - Background polling tasks; syncs data from Couchbase to Neptune via SQS

**Backend Integrations:**
- Neptune (graph database)
- GIS (Geographic Information System)
- Couchbase Sync Gateway
- SAP
- SQS (Simple Queue Service) - Message queue for data synchronization
- Lambda functions

---

## Request Type Routing

| Request Type | Flow Path |
|-------------|-----------|
| **Static Assets** | Browser → CloudFront → S3 Webapp Bucket |
| **Dynamic API** | Browser → CloudFront → F5 → NGINX → ALB → Services → Datastores |

---

## Backend Data Synchronization

**Couchbase → Neptune Sync Flow:**
```
Couchbase Sync Gateway → Poller Service → SQS → Lambda → Neptune
```

The Poller Service monitors changes in Couchbase and publishes messages to SQS queues for asynchronous processing, ensuring data consistency between Couchbase and the Neptune graph database.

---

## Important Notes

### CloudFront Distribution Update
- **Current CF Distribution:** `d34jzp2avuov5.cloudfront.net`
- If the CloudFront distribution changes, update configuration in: [nginx-ecs-fargate](https://github.com/PGEDigitalCatalyst/nginx-ecs-fargate)
- Reference PRs: [#516](https://github.com/PGEDigitalCatalyst/nginx-ecs-fargate/pull/516), [#517](https://github.com/PGEDigitalCatalyst/nginx-ecs-fargate/pull/517)

### Environment Branching Strategy
- **DEV changes** → Merge to `development` branch
- **QA changes** → Merge to `main` branch
- **Prod changes** → Merge to `production` branch

---

## Acceptance Criteria
✓ Document complete request flow from browser to web layer  
✓ Include all infrastructure components (CloudFront, F5, NGINX)  
✓ Detail each layer's responsibilities  
✓ Provide configuration examples where applicable  

