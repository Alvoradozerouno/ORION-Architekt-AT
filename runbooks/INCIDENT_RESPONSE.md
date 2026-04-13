# ORION Architekt-AT - Incident Response Runbook

**Version:** 1.0.0
**Last Updated:** 2026-04-12
**Owner:** ORION Engineering Team

## 🚨 Incident Severity Levels

### P1 - CRITICAL (Response Time: <15 minutes)
- Complete API outage
- Database down
- Data breach or security incident
- Payment system failure
- Loss of user data

### P2 - HIGH (Response Time: <1 hour)
- Partial service degradation
- High error rates (>5%)
- Slow performance (P95 >1s)
- Authentication issues
- Critical feature broken

### P3 - MEDIUM (Response Time: <4 hours)
- Minor feature issues
- Performance degradation (P95 >500ms)
- Non-critical bug affecting some users

### P4 - LOW (Response Time: <24 hours)
- Cosmetic issues
- Documentation errors
- Minor enhancements

---

## 📋 Incident Response Process

### 1. DETECT (0-5 minutes)
**Alert received via:**
- PagerDuty notification
- Prometheus AlertManager
- User reports
- Monitoring dashboard

**Initial Actions:**
1. Acknowledge the alert
2. Assess severity (P1/P2/P3/P4)
3. Check monitoring dashboards:
   - Grafana: http://monitoring.orion-architekt.at
   - Prometheus: http://prometheus.orion-architekt.at

### 2. RESPOND (5-15 minutes)
**P1/P2 Incidents:**
1. **Page on-call engineer** (if not already alerted)
2. **Create incident channel:**
   ```
   #incident-YYYY-MM-DD-description
   ```
3. **Start incident doc:**
   - Copy template: `/templates/incident-template.md`
   - Fill in: Time, Severity, Impact, Commander

4. **Assemble response team:**
   - Incident Commander (IC)
   - Technical Lead (TL)
   - Communications Lead (CL)

**P3/P4 Incidents:**
1. Create GitHub issue with template
2. Assign to appropriate team member
3. No need for dedicated channel

### 3. DIAGNOSE (Concurrent with Response)
**Quick Checks:**

#### Is API responding?
```bash
curl https://api.orion-architekt.at/health
```

#### Check service status:
```bash
kubectl get pods -n orion-production
kubectl get svc -n orion-production
kubectl logs -f deployment/orion-api -n orion-production --tail=100
```

#### Check database:
```bash
kubectl exec -it deployment/orion-api -n orion-production -- \
  psql $DATABASE_URL -c "SELECT 1"
```

#### Check Redis:
```bash
kubectl exec -it deployment/orion-api -n orion-production -- \
  redis-cli -u $REDIS_URL ping
```

**Review Metrics:**
- Error rate: `sum(rate(http_requests_total{status=~"5.."}[5m]))`
- Latency: P95, P99
- Resource usage: CPU, Memory, Disk
- Database connections
- Redis memory

### 4. MITIGATE (Immediate Relief)
**Goal:** Restore service ASAP, even if not fully fixed

#### Quick Mitigations:

**High Load:**
```bash
# Scale up pods
kubectl scale deployment orion-api --replicas=10 -n orion-production
```

**Bad Deployment:**
```bash
# Rollback to previous version
kubectl rollout undo deployment/orion-api -n orion-production
kubectl rollout status deployment/orion-api -n orion-production
```

**Database Issues:**
```bash
# Restart database (last resort)
kubectl rollout restart statefulset/postgres -n orion-production

# Increase connection pool (if exhausted)
kubectl set env deployment/orion-api DATABASE_POOL_SIZE=40 -n orion-production
```

**Redis Issues:**
```bash
# Flush cache if corrupted
kubectl exec -it deployment/orion-api -- redis-cli -u $REDIS_URL FLUSHDB

# Restart Redis
kubectl rollout restart deployment/redis -n orion-production
```

**Rate Limiting Issues:**
```bash
# Temporarily increase rate limits (emergency only)
kubectl set env deployment/orion-api RATE_LIMIT_ANONYMOUS=500 -n orion-production
```

### 5. RESOLVE (Root Cause Fix)
**After service is restored:**

1. **Identify root cause:**
   - Review logs thoroughly
   - Analyze metrics patterns
   - Reproduce if possible

2. **Implement proper fix:**
   - Create PR with fix
   - Get review
   - Deploy to staging
   - Test thoroughly
   - Deploy to production with monitoring

3. **Verify resolution:**
   - Monitor for 30 minutes
   - Check error rates return to normal
   - Verify performance metrics

### 6. DOCUMENT (Post-Incident)
**Within 24 hours of resolution:**

1. **Complete incident report:**
   - Timeline of events
   - Root cause analysis
   - Impact assessment (users affected, duration)
   - Mitigation steps taken

2. **Schedule postmortem meeting:**
   - Within 48 hours
   - Invite all involved parties
   - Focus on learning, not blame

3. **Create action items:**
   - Preventive measures
   - Monitoring improvements
   - Documentation updates
   - Assign owners and deadlines

---

## 🔍 Common Incidents & Solutions

### API Service Down

**Symptoms:**
- `up{job="orion-api"} == 0`
- Health check failing
- All requests timing out

**Quick Diagnosis:**
```bash
# Check pod status
kubectl get pods -n orion-production -l app=orion-api

# Check recent events
kubectl get events -n orion-production --sort-by='.lastTimestamp' | tail -20

# Check logs
kubectl logs -f deployment/orion-api -n orion-production --tail=100
```

**Common Causes & Fixes:**

1. **OOM (Out of Memory):**
   ```bash
   # Check memory usage
   kubectl top pods -n orion-production

   # Increase memory limit
   kubectl set resources deployment/orion-api --limits=memory=4Gi -n orion-production
   ```

2. **Crash Loop:**
   ```bash
   # View crash reason
   kubectl describe pod <pod-name> -n orion-production

   # Check for config errors
   kubectl get configmap orion-config -n orion-production -o yaml
   kubectl get secret orion-secrets -n orion-production -o yaml
   ```

3. **Database Connection Failure:**
   ```bash
   # Test database connectivity
   kubectl exec -it deployment/orion-api -n orion-production -- \
     psql $DATABASE_URL -c "SELECT version()"

   # Check database is running
   kubectl get pods -n orion-production -l app=postgres
   ```

**Escalation:** If not resolved in 30 minutes, escalate to infrastructure team

---

### High Error Rate (>5%)

**Symptoms:**
- `http_requests_total{status=~"5.."} >5%`
- Users reporting errors
- Error logs flooding

**Quick Diagnosis:**
```bash
# Get error breakdown
kubectl logs deployment/orion-api -n orion-production | \
  grep -i error | tail -50

# Check which endpoints are failing
# (Requires Prometheus)
```

**Common Causes & Fixes:**

1. **Database Connection Pool Exhausted:**
   ```bash
   # Check pool usage in logs
   kubectl logs deployment/orion-api -n orion-production | grep "pool"

   # Increase pool size
   kubectl set env deployment/orion-api DATABASE_POOL_SIZE=40 -n orion-production
   ```

2. **External API Timeout:**
   ```bash
   # Check if external APIs are down
   curl -I https://ris.bka.gv.at

   # Temporarily disable external features if critical
   kubectl set env deployment/orion-api DISABLE_RIS_INTEGRATION=true
   ```

3. **Memory Leak:**
   ```bash
   # Monitor memory growth
   kubectl top pods -n orion-production --watch

   # Restart pods in rolling fashion
   kubectl rollout restart deployment/orion-api -n orion-production
   ```

---

### Slow Performance (P95 >1s)

**Symptoms:**
- High latency metrics
- User complaints about slowness
- Timeouts

**Quick Diagnosis:**
```bash
# Check response times in Grafana
# Check database slow queries
kubectl logs deployment/orion-api -n orion-production | grep "slow query"

# Check CPU usage
kubectl top pods -n orion-production
```

**Common Causes & Fixes:**

1. **Database Slow Queries:**
   ```sql
   -- Connect to database
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query
   FROM pg_stat_activity
   WHERE state = 'active'
   ORDER BY duration DESC;
   ```

   Fix: Add missing indexes, optimize queries

2. **High CPU Usage:**
   ```bash
   # Scale horizontally
   kubectl scale deployment orion-api --replicas=8 -n orion-production
   ```

3. **Redis Cache Miss Rate High:**
   ```bash
   # Check cache stats
   kubectl exec deployment/orion-api -- redis-cli -u $REDIS_URL INFO stats

   # Increase Redis memory
   kubectl set env deployment/redis REDIS_MAXMEMORY=1gb
   ```

---

### Database Down

**Symptoms:**
- `up{job="postgres"} == 0`
- Database connection errors
- Complete service failure

**CRITICAL - Follow these steps exactly:**

1. **Assess situation:**
   ```bash
   kubectl get pods -n orion-production -l app=postgres
   kubectl describe pod <postgres-pod> -n orion-production
   ```

2. **Check if data volume is intact:**
   ```bash
   kubectl get pvc -n orion-production
   ```

3. **Attempt restart (if pod crashed):**
   ```bash
   kubectl delete pod <postgres-pod> -n orion-production
   # Wait for StatefulSet to recreate
   ```

4. **If restart fails, restore from backup:**
   ```bash
   # See DR_RUNBOOK.md for detailed restore procedures
   # DO NOT PROCEED without backup verification
   ```

5. **After recovery:**
   - Verify data integrity
   - Check all connections
   - Monitor for 1 hour

**Escalation:** Immediately escalate to database team and infrastructure lead

---

### Security Incident

**Symptoms:**
- Unauthorized access detected
- Suspicious activity in logs
- Security scanner alerts
- Data breach notification

**IMMEDIATE ACTIONS:**

1. **DO NOT PANIC - Follow protocol:**
   ```bash
   # Document everything you see
   # Take screenshots
   # Save logs
   ```

2. **Isolate affected systems:**
   ```bash
   # If compromised, scale to zero immediately
   kubectl scale deployment orion-api --replicas=0 -n orion-production

   # Block suspicious IPs at firewall/WAF
   ```

3. **Preserve evidence:**
   ```bash
   # Save all logs
   kubectl logs deployment/orion-api -n orion-production --since=24h > incident-logs.txt

   # Get current state
   kubectl get all -n orion-production > incident-state.txt
   ```

4. **Notify:**
   - Security team (IMMEDIATELY)
   - Legal team
   - Management
   - Affected users (if required by GDPR)

5. **DO NOT:**
   - Delete logs
   - Restart systems (until told by security team)
   - Communicate publicly

**Escalation:** IMMEDIATE escalation to CISO/Security Team

---

## 📞 Escalation Contacts

### Primary On-Call
- **PagerDuty:** https://orion.pagerduty.com
- **Phone:** +43 XXX XXXXXXX

### Escalation Chain
1. **L1:** On-call Engineer (0-30 min)
2. **L2:** Team Lead (30-60 min)
3. **L3:** Engineering Manager (1-2 hours)
4. **L4:** CTO (>2 hours or P1 incidents)

### Specialist Teams
- **Database:** database-team@orion-architekt.at
- **Security:** security@orion-architekt.at
- **Infrastructure:** infra@orion-architekt.at

---

## 🛠️ Tools & Resources

### Monitoring Dashboards
- **Grafana:** https://monitoring.orion-architekt.at
- **Prometheus:** https://prometheus.orion-architekt.at
- **Logs:** https://logs.orion-architekt.at (if ELK configured)

### Documentation
- **Runbooks:** `/runbooks/`
- **Architecture Diagrams:** `/docs/architecture/`
- **API Docs:** https://api.orion-architekt.at/docs

### Communication
- **Incident Channel:** `#incidents`
- **Status Page:** https://status.orion-architekt.at

---

## 📝 Incident Report Template

```markdown
# Incident Report: [Title]

**Incident ID:** INC-YYYY-MM-DD-NNN
**Date:** YYYY-MM-DD
**Severity:** P1/P2/P3/P4
**Status:** Resolved / Investigating / Mitigated

## Summary
Brief description of what happened

## Impact
- **Users Affected:** X users (X%)
- **Duration:** X hours X minutes
- **Services Affected:** API, Database, etc.
- **Revenue Impact:** €X (if applicable)

## Timeline (All times in CET)
- **HH:MM** - Incident detected
- **HH:MM** - On-call engineer paged
- **HH:MM** - Root cause identified
- **HH:MM** - Mitigation applied
- **HH:MM** - Service restored
- **HH:MM** - Incident closed

## Root Cause
Detailed explanation of what caused the incident

## Resolution
What was done to fix the issue

## Action Items
- [ ] Preventive measure 1 (Owner: @user, Due: YYYY-MM-DD)
- [ ] Improve monitoring (Owner: @user, Due: YYYY-MM-DD)
- [ ] Update documentation (Owner: @user, Due: YYYY-MM-DD)

## Lessons Learned
- What went well
- What could be improved
- What we learned
```

---

**Remember:** Stay calm, communicate clearly, and focus on restoring service first!
