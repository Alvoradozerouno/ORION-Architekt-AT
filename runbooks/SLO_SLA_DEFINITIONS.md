# ORION Architekt-AT - Service Level Objectives & Agreements

**Version:** 1.0.0
**Last Updated:** 2026-04-12
**Owner:** ORION Engineering Team
**Status:** PRODUCTION

---

## 📊 Service Level Objectives (SLOs)

SLOs are **internal targets** we commit to achieving. They are more stringent than SLAs to provide a buffer.

### 1. Availability

**Objective:** 99.95% uptime per month

**Measurement:**
- **Calculation:** `(Total minutes - Downtime minutes) / Total minutes × 100`
- **Monitoring:** Uptime checks via Blackbox Exporter every 30 seconds
- **Error Budget:** 21.6 minutes per month (0.05%)

**Exclusions:**
- Planned maintenance (announced 7 days in advance)
- Customer-side issues (network, DNS, etc.)
- Force majeure events

**Monthly Breakdown:**
```
99.95% = 43,200 minutes - 21.6 minutes downtime
         = 43,178.4 minutes uptime

Error Budget = 21.6 minutes/month = 0.72 minutes/day
```

**Thresholds:**
- ✅ **Target:** >99.95%
- ⚠️ **Warning:** <99.95% but >99.9%
- 🔴 **Critical:** <99.9%

---

### 2. Latency

**P50 (Median Response Time)**
- **Target:** <100ms
- **Warning:** >100ms
- **Critical:** >200ms

**P95 (95th Percentile)**
- **Target:** <300ms
- **Warning:** >300ms
- **Critical:** >500ms

**P99 (99th Percentile)**
- **Target:** <1000ms (1 second)
- **Warning:** >1000ms
- **Critical:** >3000ms

**Measurement:**
- **Tool:** Prometheus histogram metrics
- **Endpoint:** All API endpoints combined
- **Window:** Rolling 5-minute average

**Breakdown by Endpoint Type:**
| Endpoint Category | P50 Target | P95 Target | P99 Target |
|-------------------|------------|------------|------------|
| Health checks | <10ms | <20ms | <50ms |
| Simple calculations | <50ms | <150ms | <500ms |
| Complex calculations | <200ms | <500ms | <2000ms |
| File uploads | <1000ms | <3000ms | <10000ms |
| Compliance checks | <500ms | <1500ms | <5000ms |

---

### 3. Error Rate

**Objective:** <0.1% error rate

**Measurement:**
- **Calculation:** `(5xx errors / total requests) × 100`
- **Window:** Rolling 5-minute average
- **Exclusions:** 4xx client errors (not our fault)

**Thresholds:**
- ✅ **Target:** <0.1%
- ⚠️ **Warning:** >0.1% but <0.5%
- 🔴 **Critical:** >1%

**Error Rate Budget:**
```
0.1% = 1 error per 1,000 requests
At 100 req/sec = 360,000 req/hour
Error budget = 360 errors/hour
```

---

### 4. Throughput

**Objective:** Support 200 requests/second sustained load

**Measurement:**
- **Tool:** Prometheus rate metrics
- **Window:** 1-minute average

**Capacity Thresholds:**
- **Normal:** <100 req/sec
- **High:** 100-200 req/sec
- **Warning:** 200-300 req/sec (triggers auto-scaling)
- **Critical:** >300 req/sec (at capacity limit)

**Auto-scaling triggers:**
- CPU >70% for 2 minutes → Scale up
- CPU <30% for 10 minutes → Scale down

---

### 5. Data Durability

**Objective:** 99.999999999% (11 nines) data durability

**Implementation:**
- **Primary storage:** AWS S3 (11 nines durability)
- **Backup frequency:** Daily full + continuous WAL
- **Backup retention:** 30 days
- **Cross-region replication:** S3 → Azure Blob Storage

**Recovery Objectives:**
- **RTO (Recovery Time Objective):** <1 hour
- **RPO (Recovery Point Objective):** <15 minutes

---

### 6. Security

**Objective:** Zero unpatched high/critical vulnerabilities

**Measurement:**
- **Tool:** Dependabot, DAST scans, Trivy
- **Frequency:** Daily scans
- **SLA:** Patch within 7 days of disclosure

**Compliance:**
- **GDPR:** 100% compliant
- **eIDAS:** 100% compliant
- **OWASP Top 10:** All mitigations implemented

---

## 📜 Service Level Agreements (SLAs)

SLAs are **contractual commitments** to customers. They are less stringent than SLOs.

### Standard SLA (Free Tier)

**Availability:** 99.0% per month
- **Downtime allowance:** 43.2 minutes/month
- **Support:** Email only, 48-hour response time
- **Credits:** None

**Performance:**
- **P95 latency:** <1 second
- **Error rate:** <1%

---

### Professional SLA

**Availability:** 99.5% per month
- **Downtime allowance:** 21.6 minutes/month
- **Support:** Email + Chat, 8-hour response time
- **Credits:** 10% monthly fee for each 0.5% below SLA

**Performance:**
- **P95 latency:** <500ms
- **Error rate:** <0.5%

**Support Hours:**
- Monday-Friday, 09:00-17:00 CET
- Email response: 8 hours
- Chat response: 30 minutes

---

### Enterprise SLA

**Availability:** 99.9% per month
- **Downtime allowance:** 43.2 minutes/month
- **Support:** 24/7 Phone + Email + Chat, 1-hour response time
- **Credits:** 25% monthly fee for each 0.1% below SLA

**Performance:**
- **P95 latency:** <300ms
- **Error rate:** <0.1%
- **Throughput:** Guaranteed capacity reservation

**Premium Features:**
- Dedicated account manager
- Quarterly business reviews
- Custom integration support
- Priority feature requests

**Support Levels:**
- **P1 (Critical):** 15-minute response, 1-hour resolution target
- **P2 (High):** 1-hour response, 4-hour resolution target
- **P3 (Medium):** 4-hour response, 1-day resolution target
- **P4 (Low):** 1-day response, best effort

---

## 📈 SLA Credits

### Credit Calculation

**Formula:**
```
Credit % = (Target Uptime % - Actual Uptime %) × Multiplier

Professional: Multiplier = 20x
Enterprise: Multiplier = 250x
```

**Examples:**

**Professional SLA (99.5% target):**
- Actual uptime: 99.0% → Credit: (99.5 - 99.0) × 20 = 10%
- Actual uptime: 98.5% → Credit: (99.5 - 98.5) × 20 = 20%

**Enterprise SLA (99.9% target):**
- Actual uptime: 99.8% → Credit: (99.9 - 99.8) × 250 = 25%
- Actual uptime: 99.5% → Credit: (99.9 - 99.5) × 250 = 100% (max)

**Maximum credit:** 100% of monthly subscription fee

---

## 🎯 Monitoring & Reporting

### Real-time Dashboards

**Public Status Page:** https://status.orion-architekt.at
- Current system status
- Incident history
- Planned maintenance

**Internal Monitoring:**
- Grafana: Real-time metrics
- Prometheus: Alerting
- PagerDuty: Incident management

### Monthly SLA Reports

**Delivered:** 5th business day of following month

**Contents:**
1. **Uptime Summary**
   - Monthly uptime percentage
   - Total downtime minutes
   - Incident breakdown

2. **Performance Metrics**
   - P50, P95, P99 latency
   - Error rate
   - Request volume

3. **Incident Summary**
   - Number of incidents by severity
   - Mean time to detect (MTTD)
   - Mean time to resolve (MTTR)

4. **SLA Compliance**
   - SLA target vs. actual
   - Credit calculation (if applicable)
   - Root cause analysis for major incidents

---

## 🚨 Incident Classification

### P1 - Critical (SLA Impact: Severe)
- Complete service outage
- Data loss or corruption
- Security breach
- **Response:** 15 minutes
- **Resolution Target:** 1 hour
- **SLA Penalty:** High

### P2 - High (SLA Impact: Moderate)
- Partial service degradation
- High error rates (>5%)
- Slow performance (P95 >1s)
- **Response:** 1 hour
- **Resolution Target:** 4 hours
- **SLA Penalty:** Medium

### P3 - Medium (SLA Impact: Low)
- Minor feature issues
- Performance degradation (P95 >500ms)
- **Response:** 4 hours
- **Resolution Target:** 1 day
- **SLA Penalty:** Low

### P4 - Low (SLA Impact: None)
- Cosmetic issues
- Documentation errors
- **Response:** 1 day
- **Resolution Target:** Best effort
- **SLA Penalty:** None

---

## 📊 SLO/SLA Dashboard Metrics

### Key Metrics to Track

**Availability Metrics:**
```promql
# Uptime percentage (last 30 days)
(1 - (sum(increase(probe_http_duration_seconds_count{status=~"5.."}[30d]))
/ sum(increase(probe_http_duration_seconds_count[30d])))) * 100

# Error budget remaining
slo_error_budget_remaining{slo="availability"}
```

**Latency Metrics:**
```promql
# P95 latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# P99 latency
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

**Error Rate:**
```promql
# 5xx error rate
(sum(rate(http_requests_total{status=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m]))) * 100
```

---

## 🎓 Best Practices

### 1. Error Budget Management

**Philosophy:** Error budget allows for innovation and rapid deployment

**Process:**
1. **Monitor burn rate:** How fast are we using error budget?
2. **Fast burn (>10x):** Stop deployments, focus on reliability
3. **Slow burn (<1x):** Increase deployment frequency, take risks
4. **No budget left:** Freeze non-critical changes until next month

### 2. SLO Review Cadence

**Weekly:**
- Check current SLO status
- Review incidents
- Adjust alerts if needed

**Monthly:**
- Full SLO review
- Adjust targets if consistently missed or exceeded
- Update error budget policy

**Quarterly:**
- SLA review with customers
- Capacity planning
- SLO/SLA alignment

### 3. Communication

**Transparency:**
- Publish all incidents on status page
- Monthly SLA reports sent automatically
- Quarterly business reviews (Enterprise)

**Incident Communication:**
- Initial notification: <15 minutes
- Updates every: 30 minutes
- Postmortem: Within 72 hours

---

## 📞 Escalation for SLA Breaches

**Notification Chain:**
1. **Automated:** Alert triggers when SLO at risk
2. **On-call Engineer:** Immediately investigates
3. **Team Lead:** Notified if >30 min to resolution
4. **Engineering Manager:** Notified if P1 or SLA breach imminent
5. **Customer Success:** Notified for Enterprise customers
6. **CTO:** Notified for repeated SLA breaches

---

## 📝 Definitions

**Uptime:** Service is accessible and functional
**Downtime:** 5xx errors, timeouts, or service unavailable
**Planned Maintenance:** Announced 7+ days in advance
**Emergency Maintenance:** Critical security or stability fixes
**Service Credits:** Monetary compensation for SLA breaches

---

## 🔗 Related Documentation

- [Production Preflight Checklist](../PRODUCTION_PREFLIGHT_CHECKLIST.md)
- [Monitoring Configuration](../monitoring/prometheus.yml)
- [Incident Response Runbook](INCIDENT_RESPONSE.md)
- [Disaster Recovery Runbook](DISASTER_RECOVERY.md)

---

**Status:** ACTIVE
**Next Review:** 2026-07-12 (Quarterly)
**Approved By:** CTO, Head of Engineering
**Version:** 1.0.0
