# ORION Architekt-AT - Backup Verification Procedures

**Version:** 1.0.0
**Last Updated:** 2026-04-12
**Owner:** Database Team / ORION Engineering

---

## 🎯 Purpose

This document defines procedures for verifying database backups to ensure they are:
1. **Restorable** - Can be successfully restored
2. **Complete** - Contain all expected data
3. **Consistent** - Data integrity is maintained
4. **Timely** - Meet RPO requirements

**Why This Matters:** An untested backup is Schrödinger's backup - it both exists and doesn't exist until you try to restore it.

---

## 📅 Verification Schedule

### Daily (Automated)
✅ **Basic Integrity Check** - Verify backup file is not corrupted
- **Time:** Immediately after backup (02:05 CET)
- **Duration:** ~5 minutes
- **Automated:** Yes

### Weekly (Automated)
✅ **Metadata Verification** - Check backup contains expected schemas/tables
- **Time:** Sunday 03:00 CET
- **Duration:** ~15 minutes
- **Automated:** Yes

### Monthly (Manual)
🧪 **Full Restore Test** - Complete restore to test environment
- **Time:** First Sunday of month, 04:00 CET
- **Duration:** ~2 hours
- **Automated:** Partially (manual verification required)

### Quarterly (Manual)
🏥 **DR Drill** - Full disaster recovery simulation
- **Time:** Last Sunday of quarter, planned in advance
- **Duration:** ~4 hours
- **Automated:** No (documented procedure)

---

## 🔍 Daily Verification Procedures

### 1. Automated Integrity Check

**Performed by:** K8s CronJob (built into backup job)

**Process:**
```bash
#!/bin/bash
# Run automatically after backup completion

BACKUP_FILE="postgres_20260412_020000.tar.gz"
BACKUP_DIR="/tmp/verify"

# 1. Download backup from S3
aws s3 cp "s3://orion-backups-primary/database/$BACKUP_FILE" "$BACKUP_DIR/"
aws s3 cp "s3://orion-backups-primary/database/$BACKUP_FILE.sha256" "$BACKUP_DIR/"

# 2. Verify checksum
cd "$BACKUP_DIR"
sha256sum -c "$BACKUP_FILE.sha256"
if [ $? -eq 0 ]; then
  echo "✅ Checksum verification PASSED"
else
  echo "❌ Checksum verification FAILED"
  exit 1
fi

# 3. Extract archive
tar -tzf "$BACKUP_FILE" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Archive extraction test PASSED"
else
  echo "❌ Archive is corrupted"
  exit 1
fi

# 4. Test pg_restore can list contents
tar -xzf "$BACKUP_FILE"
EXTRACT_DIR=$(ls -d postgres_* | head -1)
pg_restore --list "$EXTRACT_DIR/orion_db.dump" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ pg_restore listing PASSED"
else
  echo "❌ Backup file is corrupted or incompatible"
  exit 1
fi

# 5. Check backup metadata
cat "$EXTRACT_DIR/metadata.json"
EXPECTED_DB="orion_db"
ACTUAL_DB=$(jq -r '.database' "$EXTRACT_DIR/metadata.json")

if [ "$EXPECTED_DB" = "$ACTUAL_DB" ]; then
  echo "✅ Metadata verification PASSED"
else
  echo "❌ Metadata mismatch - expected $EXPECTED_DB, got $ACTUAL_DB"
  exit 1
fi

# Cleanup
rm -rf "$BACKUP_DIR"

echo "=========================================="
echo "✅ All daily verification checks PASSED"
echo "=========================================="
```

**Success Criteria:**
- ✅ Checksum matches
- ✅ Archive can be extracted
- ✅ pg_restore can list contents
- ✅ Metadata is correct

**Failure Response:**
- Alert on-call engineer immediately
- Mark backup as failed
- Trigger manual backup
- Investigate root cause

---

## 📊 Weekly Verification Procedures

### 2. Metadata & Schema Verification

**Performed by:** Automated script + manual review

**Process:**
```bash
#!/bin/bash
# Weekly verification - runs Sunday 03:00 CET

BACKUP_FILE="latest"  # Uses latest backup
VERIFY_DB="backup_verify"

# 1. Download and extract backup
aws s3 cp "s3://orion-backups-primary/database/$BACKUP_FILE.tar.gz" /tmp/
tar -xzf "/tmp/$BACKUP_FILE.tar.gz" -C /tmp/
BACKUP_DIR="/tmp/$(ls /tmp/ | grep postgres_ | head -1)"

# 2. Create temporary database
psql -c "DROP DATABASE IF EXISTS $VERIFY_DB;"
psql -c "CREATE DATABASE $VERIFY_DB;"

# 3. Restore schema only
pg_restore --dbname="$VERIFY_DB" \
  --schema-only \
  --no-owner \
  --no-acl \
  "$BACKUP_DIR/orion_db.dump"

# 4. Verify schema
echo "Checking tables..."
EXPECTED_TABLES=20  # Adjust based on your schema
ACTUAL_TABLES=$(psql -d "$VERIFY_DB" -t -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")

if [ "$ACTUAL_TABLES" -ge "$EXPECTED_TABLES" ]; then
  echo "✅ Table count: $ACTUAL_TABLES (expected: >=$EXPECTED_TABLES)"
else
  echo "❌ Table count: $ACTUAL_TABLES (expected: >=$EXPECTED_TABLES)"
  exit 1
fi

# 5. Verify critical tables exist
CRITICAL_TABLES=("users" "projects" "calculations" "audit_log")
for table in "${CRITICAL_TABLES[@]}"; do
  EXISTS=$(psql -d "$VERIFY_DB" -t -c \
    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='$table');")

  if [ "$EXISTS" = " t" ]; then
    echo "✅ Critical table exists: $table"
  else
    echo "❌ Missing critical table: $table"
    exit 1
  fi
done

# 6. Check indexes
INDEX_COUNT=$(psql -d "$VERIFY_DB" -t -c \
  "SELECT count(*) FROM pg_indexes WHERE schemaname='public';")
echo "✅ Index count: $INDEX_COUNT"

# 7. Check constraints
CONSTRAINT_COUNT=$(psql -d "$VERIFY_DB" -t -c \
  "SELECT count(*) FROM information_schema.table_constraints WHERE table_schema='public';")
echo "✅ Constraint count: $CONSTRAINT_COUNT"

# Cleanup
psql -c "DROP DATABASE $VERIFY_DB;"
rm -rf "$BACKUP_DIR" "/tmp/$BACKUP_FILE.tar.gz"

echo "=========================================="
echo "✅ Weekly verification PASSED"
echo "=========================================="
```

**Success Criteria:**
- ✅ All critical tables present
- ✅ Index count matches expectations
- ✅ Constraints restored correctly
- ✅ No schema corruption

**Report Generated:**
```
Weekly Backup Verification Report
Date: 2026-04-13
Backup: postgres_20260412_020000.tar.gz

Schema Verification:
- Tables: 25/25 ✅
- Indexes: 47/47 ✅
- Constraints: 18/18 ✅
- Critical tables: 4/4 ✅

Status: PASSED ✅
```

---

## 🧪 Monthly Verification Procedures

### 3. Full Restore Test

**Performed by:** Database team (partially automated)

**Process:**

**Step 1: Setup Test Environment (15 min)**
```bash
# Create dedicated test namespace
kubectl create namespace backup-test

# Deploy test PostgreSQL instance
kubectl apply -f k8s/postgres-test.yaml -n backup-test

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres-test -n backup-test --timeout=300s
```

**Step 2: Restore Backup (30 min)**
```bash
# Use restore job template
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: monthly-restore-test
  namespace: backup-test
spec:
  template:
    spec:
      containers:
      - name: restore
        image: postgres:15-alpine
        env:
        - name: BACKUP_FILE
          value: "postgres_20260412_020000.tar.gz"
        # ... (same as regular restore job)
EOF

# Monitor restore progress
kubectl logs -f job/monthly-restore-test -n backup-test
```

**Step 3: Verify Data Integrity (45 min)**
```sql
-- Connect to restored database
psql -h postgres-test-service -U postgres -d orion_db

-- 1. Check record counts
SELECT 'users' AS table_name, count(*) FROM users
UNION ALL
SELECT 'projects', count(*) FROM projects
UNION ALL
SELECT 'calculations', count(*) FROM calculations;

-- Expected output:
--  table_name   | count
-- -------------+-------
--  users        |  1234
--  projects     |  5678
--  calculations | 89012

-- 2. Verify data consistency
SELECT count(*) FROM projects WHERE user_id NOT IN (SELECT id FROM users);
-- Expected: 0 (no orphaned records)

-- 3. Check latest records
SELECT max(created_at) FROM audit_log;
-- Should be within RPO (15 minutes of backup time)

-- 4. Verify sample data
SELECT * FROM users WHERE email = 'test@example.com' LIMIT 1;
-- Verify critical user account exists

-- 5. Check referential integrity
SELECT conname, contype, conrelid::regclass
FROM pg_constraint
WHERE contype = 'f';  -- Foreign keys
-- All foreign keys should be present
```

**Step 4: Performance Test (30 min)**
```sql
-- Run representative queries
EXPLAIN ANALYZE
SELECT u.email, count(p.id) AS project_count
FROM users u
LEFT JOIN projects p ON u.id = p.user_id
GROUP BY u.id, u.email
ORDER BY project_count DESC
LIMIT 100;

-- Verify execution time is acceptable
-- Expected: <100ms for this query
```

**Step 5: Cleanup (5 min)**
```bash
# Delete test namespace
kubectl delete namespace backup-test
```

**Success Criteria:**
- ✅ Restore completes without errors
- ✅ All tables present with expected row counts
- ✅ No orphaned records or integrity violations
- ✅ Latest data is within RPO window (15 min)
- ✅ Query performance is acceptable
- ✅ All foreign keys and constraints active

**Monthly Report:**
```markdown
# Monthly Backup Restore Test Report

**Date:** 2026-04-06
**Backup:** postgres_20260412_020000.tar.gz
**Backup Age:** 6 hours
**Tester:** Database Team

## Results

### Restore Metrics
- Restore Duration: 28 minutes
- Database Size: 12.4 GB
- Record Count: 95,924 total records

### Data Integrity
- ✅ All tables present (25/25)
- ✅ Row counts match production
- ✅ No orphaned records
- ✅ All constraints active
- ✅ Latest record within RPO (8 min old)

### Performance
- ✅ Sample query: 67ms (target: <100ms)
- ✅ Index scan working correctly
- ✅ All indexes valid

### Issues Found
None

### Status: PASSED ✅

**Next Test:** 2026-05-04
```

---

## 🏥 Quarterly DR Drill

### 4. Full Disaster Recovery Simulation

**Duration:** 4 hours
**Participants:** Database team, SRE, Engineering leads
**Notification:** All stakeholders informed 2 weeks in advance

**Scenario:** Simulated complete data center failure

**Procedure:**

**Hour 1: Disaster Declaration & Assessment**
1. Declare simulated disaster (09:00 CET)
2. Activate DR team
3. Confirm primary database is "down"
4. Identify latest valid backup
5. Estimate downtime

**Hour 2: Secondary Environment Setup**
1. Provision secondary database instance
2. Configure networking
3. Update DNS for test domain
4. Verify connectivity

**Hour 3: Data Restoration**
1. Download backup from S3 (cross-region)
2. Verify backup integrity
3. Restore database
4. Run integrity checks
5. Verify replication lag

**Hour 4: Application Testing & Validation**
1. Deploy application to secondary
2. Run smoke tests
3. Execute critical user journeys
4. Performance testing
5. Rollback simulation
6. Document lessons learned

**Success Criteria:**
- ✅ RTO <1 hour (from decision to go live)
- ✅ RPO <15 minutes (data loss minimal)
- ✅ All data integrity checks pass
- ✅ Application fully functional
- ✅ Performance within acceptable range

**Drill Report Template:** See [DR Runbook](DISASTER_RECOVERY.md)

---

## 🚨 Failure Response Procedures

### When Verification Fails

**Immediate Actions:**
1. **Alert:** Page on-call engineer (P1 incident)
2. **Isolate:** Mark backup as failed
3. **Trigger:** Immediate new backup
4. **Investigate:** Root cause analysis

**Investigation Checklist:**
- [ ] Check backup job logs
- [ ] Verify S3 permissions
- [ ] Check disk space on backup source
- [ ] Review database health during backup
- [ ] Check for concurrent operations (locks)
- [ ] Verify backup script version

**Resolution:**
1. Fix root cause
2. Run manual backup
3. Verify new backup
4. Update procedures if needed
5. Postmortem within 48 hours

---

## 📊 Verification Metrics

### Track Over Time

**Backup Success Rate:**
```promql
(backup_success_total / backup_attempts_total) * 100
```

**Target:** >99.5%

**Verification Success Rate:**
```promql
(verification_success_total / verification_attempts_total) * 100
```

**Target:** 100%

**Average Restore Time:**
```promql
avg(restore_duration_seconds)
```

**Target:** <30 minutes

---

## 📝 Verification Log Template

```markdown
# Backup Verification Log

**Date:** 2026-04-12
**Backup File:** postgres_20260412_020000.tar.gz
**Verification Type:** Daily Integrity Check
**Performed By:** Automated CronJob

## Checks Performed
- [x] Checksum verification
- [x] Archive extraction
- [x] pg_restore listing
- [x] Metadata validation

## Results
- Checksum: ✅ PASSED
- Extraction: ✅ PASSED
- Restore listing: ✅ PASSED
- Metadata: ✅ PASSED

## Metrics
- Backup size: 4.2 GB
- Verification duration: 4 minutes 32 seconds
- Backup age: 3 hours 15 minutes

## Status: PASSED ✅

## Notes
None

**Next Verification:** 2026-04-13 02:05 CET
```

---

## 🔗 Related Documentation

- [Disaster Recovery Runbook](DISASTER_RECOVERY.md)
- [Database Maintenance Runbook](DATABASE_MAINTENANCE.md)
- [Backup CronJob Configuration](../k8s/jobs/postgres-backup-cronjob.yaml)
- [Incident Response Runbook](INCIDENT_RESPONSE.md)

---

**Last Verification:** [DATE]
**Last Successful Restore Test:** [DATE]
**Last DR Drill:** [DATE]
**Next Scheduled Verification:** Daily 02:05 CET
