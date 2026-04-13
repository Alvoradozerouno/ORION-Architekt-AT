# ORION Architekt-AT - Disaster Recovery Runbook

**Version:** 1.0.0
**Last Updated:** 2026-04-12
**Owner:** ORION Engineering Team

---

## 🎯 Recovery Objectives

### RTO (Recovery Time Objective)
**Target:** <1 hour
- Time from disaster declaration to service restoration

### RPO (Recovery Point Objective)
**Target:** <15 minutes
- Maximum acceptable data loss

### Service Level Objectives
- **Availability:** 99.9% (43.2 min downtime/month)
- **Data Durability:** 99.999999999% (11 nines)

---

## 📊 Disaster Scenarios

### Scenario 1: Complete Database Loss
**Likelihood:** Low
**Impact:** Critical
**RTO:** 1 hour
**RPO:** 15 minutes

### Scenario 2: Complete Infrastructure Failure
**Likelihood:** Very Low
**Impact:** Critical
**RTO:** 2 hours
**RPO:** 30 minutes

### Scenario 3: Data Corruption
**Likelihood:** Low
**Impact:** High
**RTO:** 4 hours
**RPO:** 1 hour (restore from last clean backup)

### Scenario 4: Ransomware Attack
**Likelihood:** Medium
**Impact:** Critical
**RTO:** 4-8 hours
**RPO:** Latest clean backup (pre-infection)

### Scenario 5: Regional Outage (AWS/Cloud Provider)
**Likelihood:** Low
**Impact:** Critical
**RTO:** 2 hours (failover to secondary region)
**RPO:** 5 minutes (replication lag)

---

## 🔄 Backup Strategy

### Database Backups

#### Continuous WAL Archiving
**Technology:** PostgreSQL WAL (Write-Ahead Logging)
**Frequency:** Continuous
**Retention:** 7 days

**Configuration:**
```sql
-- In postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backup/wal/%f && cp %p /backup/wal/%f'
max_wal_senders = 3
```

**Storage:**
- Primary: S3 bucket `s3://orion-backups-primary/wal/`
- Secondary: Azure Blob Storage (cross-cloud redundancy)

#### Full Backups
**Technology:** pg_basebackup
**Frequency:** Daily at 02:00 CET
**Retention:** 30 days

**Automated Script:**
```bash
#!/bin/bash
# /opt/orion/backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgres"
S3_BUCKET="s3://orion-backups-primary/database"

# Create backup
pg_basebackup -h postgres -U postgres -D "$BACKUP_DIR/backup_$DATE" \
  -Ft -z -P -v

# Upload to S3
aws s3 sync "$BACKUP_DIR/backup_$DATE" "$S3_BUCKET/backup_$DATE/"

# Upload to Azure (cross-cloud)
azcopy copy "$BACKUP_DIR/backup_$DATE" \
  "https://orionbackups.blob.core.windows.net/backups/backup_$DATE" \
  --recursive

# Cleanup old backups (30 days)
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} \;

# Verify backup
pg_restore -l "$BACKUP_DIR/backup_$DATE/base.tar.gz" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Backup verified: backup_$DATE"
else
  echo "❌ Backup verification failed: backup_$DATE"
  # Alert on-call team
fi
```

**Cron Schedule:**
```cron
0 2 * * * /opt/orion/backup-database.sh >> /var/log/orion-backup.log 2>&1
```

### Application Data Backups

#### File Uploads (IFC, PDFs, etc.)
**Storage:** S3 with versioning enabled
**Frequency:** Real-time (versioning)
**Retention:** 90 days

**Configuration:**
```bash
# Enable S3 versioning
aws s3api put-bucket-versioning \
  --bucket orion-uploads \
  --versioning-configuration Status=Enabled

# Enable lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket orion-uploads \
  --lifecycle-configuration file://s3-lifecycle.json
```

**s3-lifecycle.json:**
```json
{
  "Rules": [
    {
      "Id": "DeleteOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 90
      }
    },
    {
      "Id": "TransitionToGlacier",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

### Configuration Backups

#### Kubernetes Manifests
**Storage:** Git repository + S3
**Frequency:** On every change + daily snapshots

```bash
# Automated snapshot script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/k8s"

# Export all Kubernetes resources
kubectl get all --all-namespaces -o yaml > "$BACKUP_DIR/all-resources-$DATE.yaml"
kubectl get configmap --all-namespaces -o yaml > "$BACKUP_DIR/configmaps-$DATE.yaml"
kubectl get secret --all-namespaces -o yaml > "$BACKUP_DIR/secrets-$DATE.yaml"
kubectl get pvc --all-namespaces -o yaml > "$BACKUP_DIR/pvcs-$DATE.yaml"

# Encrypt and upload
tar -czf "$BACKUP_DIR/k8s-backup-$DATE.tar.gz" "$BACKUP_DIR"/*.yaml
gpg --encrypt --recipient orion-backup@orion-architekt.at \
  "$BACKUP_DIR/k8s-backup-$DATE.tar.gz"

aws s3 cp "$BACKUP_DIR/k8s-backup-$DATE.tar.gz.gpg" \
  "s3://orion-backups-primary/k8s/"
```

---

## 🚑 Recovery Procedures

### SCENARIO 1: Database Disaster Recovery

#### Prerequisites
- Access to S3 backup bucket
- PostgreSQL credentials
- Kubernetes access

#### Steps

**1. Assess Damage (0-5 minutes)**
```bash
# Check database status
kubectl get pods -n orion-production -l app=postgres
kubectl logs -n orion-production deployment/postgres --tail=100

# Check data volume
kubectl get pvc -n orion-production
kubectl describe pvc postgres-data-pvc -n orion-production
```

**2. Stop Application (5-10 minutes)**
```bash
# Prevent new writes
kubectl scale deployment orion-api --replicas=0 -n orion-production

# Verify no connections
kubectl exec -it postgres-0 -n orion-production -- \
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE datname='orion_db';"
```

**3. Identify Recovery Point (10-15 minutes)**
```bash
# List available backups
aws s3 ls s3://orion-backups-primary/database/ --recursive

# Choose recovery point (latest or specific time)
RECOVERY_POINT="20260412_020000"  # Example: 2026-04-12 02:00:00
```

**4. Restore Database (15-45 minutes)**

**Option A: Point-in-Time Recovery (PITR)**
```bash
# Download base backup
aws s3 sync "s3://orion-backups-primary/database/backup_$RECOVERY_POINT/" \
  /restore/postgres/

# Download WAL files
aws s3 sync "s3://orion-backups-primary/wal/" \
  /restore/wal/

# Create recovery.conf
cat > /restore/postgres/recovery.conf <<EOF
restore_command = 'cp /restore/wal/%f %p'
recovery_target_time = '2026-04-12 08:30:00 CET'  # Adjust as needed
recovery_target_action = 'promote'
EOF

# Restore
kubectl exec -it postgres-0 -n orion-production -- \
  pg_ctl stop -D /var/lib/postgresql/data

kubectl exec -it postgres-0 -n orion-production -- \
  rm -rf /var/lib/postgresql/data/*

kubectl exec -it postgres-0 -n orion-production -- \
  tar -xzf /restore/postgres/base.tar.gz -C /var/lib/postgresql/data

kubectl exec -it postgres-0 -n orion-production -- \
  pg_ctl start -D /var/lib/postgresql/data
```

**Option B: Full Backup Restore**
```bash
# Download backup
aws s3 sync "s3://orion-backups-primary/database/backup_$RECOVERY_POINT/" \
  /restore/postgres/

# Restore
pg_restore -h postgres -U postgres -d orion_db \
  -v -c --if-exists /restore/postgres/base.tar.gz

# Verify
psql -h postgres -U postgres -d orion_db -c "\dt"
psql -h postgres -U postgres -d orion_db -c "SELECT count(*) FROM users;"
```

**5. Verify Data Integrity (45-55 minutes)**
```bash
# Run consistency checks
psql -h postgres -U postgres -d orion_db <<EOF
-- Check for table corruption
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Verify critical tables
SELECT count(*) FROM users;
SELECT count(*) FROM projects;
SELECT count(*) FROM calculations;

-- Check for orphaned records
-- (Add specific queries for your schema)
EOF
```

**6. Restart Application (55-60 minutes)**
```bash
# Start API
kubectl scale deployment orion-api --replicas=3 -n orion-production

# Monitor startup
kubectl logs -f deployment/orion-api -n orion-production

# Verify health
curl https://api.orion-architekt.at/health
```

**7. Post-Recovery Validation (60-70 minutes)**
```bash
# Run smoke tests
pytest tests/test_integration.py -v

# Check critical functionality
curl -X POST https://api.orion-architekt.at/api/v1/berechnungen/uwert \
  -H "Content-Type: application/json" \
  -d '{"schichten":[{"material":"Beton","dicke_mm":200,"lambda_wert":2.1}]}'

# Monitor for errors
kubectl logs deployment/orion-api -n orion-production | grep -i error
```

---

### SCENARIO 2: Complete Infrastructure Failure

#### When to Use
- Entire Kubernetes cluster down
- Complete AWS region failure
- Catastrophic network failure

#### Prerequisites
- Secondary region/cluster prepared (Multi-Region Setup)
- DNS access for failover
- Recent backups accessible

#### Steps

**1. Declare Disaster (0-10 minutes)**
```bash
# Confirm primary region is down
curl https://api.orion-architekt.at/health
# timeout or unreachable

# Check AWS status
curl https://status.aws.amazon.com/

# Activate DR team
# Send alerts to all stakeholders
```

**2. Activate Secondary Region (10-30 minutes)**

**a. Restore Database in Secondary Region**
```bash
# Download latest backup to secondary region
aws s3 sync s3://orion-backups-primary/database/latest/ \
  s3://orion-backups-secondary/restore/ \
  --source-region eu-central-1 \
  --region us-east-1

# Restore database in secondary
kubectl apply -f k8s/postgres-secondary.yaml -n orion-dr
# Wait for database to be ready
```

**b. Deploy Application**
```bash
# Deploy to secondary cluster
kubectl config use-context orion-dr-cluster
kubectl apply -f k8s/deployment.yaml -n orion-dr
kubectl rollout status deployment/orion-api -n orion-dr
```

**3. DNS Failover (30-40 minutes)**
```bash
# Update DNS to point to secondary region
# Using Route53 as example:

aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234EXAMPLE \
  --change-batch file://dns-failover.json

# dns-failover.json
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.orion-architekt.at",
      "Type": "A",
      "TTL": 60,
      "ResourceRecords": [{"Value": "<SECONDARY_IP>"}]
    }
  }]
}

# Wait for DNS propagation (5-10 minutes)
```

**4. Verify Secondary System (40-60 minutes)**
```bash
# Health checks
curl https://api.orion-architekt.at/health

# Functional tests
pytest tests/test_integration.py --host=https://api.orion-architekt.at

# Monitor performance
# Check Grafana dashboards
```

**5. Communicate Status (Throughout)**
```markdown
# Status page update
**Major Outage - Failover in Progress**

We are experiencing a complete service outage in our primary region.
We are failing over to our secondary region.

- 00:00 - Outage detected
- 00:10 - DR team activated
- 00:30 - Secondary region activated
- 00:40 - DNS updated
- 01:00 - Service restored (estimated)

Next update: in 15 minutes
```

---

### SCENARIO 3: Ransomware/Data Corruption

#### Detection
- Unusual file modifications
- Database anomalies
- Security alerts
- Encryption detected

#### Immediate Actions (0-15 minutes)

**1. ISOLATE IMMEDIATELY**
```bash
# Stop all services to prevent spread
kubectl scale deployment --all --replicas=0 -n orion-production

# Block all external access
kubectl delete ingress --all -n orion-production

# Preserve evidence
kubectl get all -n orion-production > /evidence/state.txt
kubectl logs --all-containers=true --all -n orion-production > /evidence/logs.txt
```

**2. NOTIFY**
- Security team (IMMEDIATELY)
- Law enforcement (if ransomware)
- Insurance provider
- Legal team

**3. ASSESS DAMAGE**
```bash
# Find last clean backup
aws s3 ls s3://orion-backups-primary/database/ --recursive | tail -20

# Verify backup integrity
aws s3 cp s3://orion-backups-primary/database/backup_YYYYMMDD/base.tar.gz /tmp/
tar -tzf /tmp/base.tar.gz  # Should list files without errors
```

**4. RECOVER FROM CLEAN BACKUP**
```bash
# Find last known good backup (before infection)
CLEAN_BACKUP="20260410_020000"  # Example: 2 days before incident

# Restore following SCENARIO 1 procedures
# Use CLEAN_BACKUP as recovery point
```

**5. FORENSICS (After Recovery)**
- Preserve all evidence
- Work with security team
- Identify entry point
- Patch vulnerabilities

---

## 🧪 DR Testing Schedule

### Monthly DR Tests
**Scope:** Database backup verification
**Duration:** 30 minutes
**Procedure:**
1. Download latest backup
2. Restore to test environment
3. Run integrity checks
4. Document results

### Quarterly DR Drills
**Scope:** Full database recovery
**Duration:** 2 hours
**Procedure:**
1. Simulate database failure
2. Execute full recovery procedure
3. Validate data integrity
4. Document time to recovery
5. Update runbooks based on findings

### Annual DR Exercises
**Scope:** Complete infrastructure failover
**Duration:** 4 hours
**Procedure:**
1. Simulate regional outage
2. Activate secondary region
3. Failover DNS
4. Validate all services
5. Failback to primary
6. Full postmortem

---

## 📞 Emergency Contacts

### DR Team (24/7)
- **DR Coordinator:** +43 XXX XXXXXXX
- **Database Lead:** +43 XXX XXXXXXX
- **Infrastructure Lead:** +43 XXX XXXXXXX
- **Security Lead:** +43 XXX XXXXXXX

### Vendors
- **AWS Support (Enterprise):** 1-877-XXX-XXXX
- **Kubernetes Support:** support@platform.com
- **Database Consultants:** db-experts@company.com

---

## 📝 Post-Recovery Checklist

After any disaster recovery:

- [ ] **Document timeline** - All actions taken with timestamps
- [ ] **Verify data integrity** - Run consistency checks
- [ ] **Review monitoring** - Check all alerts are working
- [ ] **Update backups** - Ensure new backups are running
- [ ] **Communicate** - Notify all stakeholders
- [ ] **Schedule postmortem** - Within 48 hours
- [ ] **Update runbooks** - Document lessons learned
- [ ] **Test backups** - Verify backup process still works
- [ ] **Review RTO/RPO** - Did we meet our objectives?
- [ ] **Identify improvements** - What can we do better?

---

## 🔗 Related Documentation

- [Incident Response Runbook](INCIDENT_RESPONSE.md)
- [Database Maintenance Guide](DATABASE_MAINTENANCE.md)
- [Backup Verification Procedures](BACKUP_VERIFICATION.md)
- [Security Incident Playbook](SECURITY_INCIDENT.md)

---

**Remember:** Disaster recovery is not about IF, but WHEN. Test regularly, document thoroughly, and stay prepared!

**Last DR Test:** [DATE]
**Next DR Test:** [DATE]
**DR Test Success Rate:** [X/Y successful recoveries]
