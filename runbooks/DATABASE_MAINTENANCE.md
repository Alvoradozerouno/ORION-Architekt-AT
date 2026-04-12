# ORION Architekt-AT - Database Maintenance Runbook

**Version:** 1.0.0
**Last Updated:** 2026-04-12
**Owner:** Database Team / ORION Engineering

---

## 📋 Regular Maintenance Schedule

### Daily Tasks (Automated)
- ✅ **02:00 CET** - Full database backup
- ✅ **Continuous** - WAL archiving to S3
- ✅ **Every hour** - Vacuum analyze (autovacuum)

### Weekly Tasks
- 🔧 **Sunday 03:00 CET** - Full vacuum analyze
- 🔧 **Sunday 04:00 CET** - Reindex critical tables
- 📊 **Monday** - Review slow query log
- 📊 **Friday** - Review database growth trends

### Monthly Tasks
- 🧪 **1st Sunday** - Backup restore test
- 📈 **Last Friday** - Capacity planning review
- 🔍 **Mid-month** - Index usage analysis
- 📝 **End of month** - Performance report

### Quarterly Tasks
- 🏥 **Q1, Q2, Q3, Q4** - Full database health check
- 🔄 **Every quarter** - Disaster recovery drill
- 📊 **Every quarter** - Database statistics reset

---

## 🔧 Routine Maintenance Procedures

### 1. Manual Vacuum

**When to use:**
- After large DELETE operations
- After bulk updates
- When autovacuum is falling behind

**Procedure:**
```sql
-- Check table bloat first
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
  n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Vacuum specific table (non-blocking)
VACUUM ANALYZE tablename;

-- Vacuum all tables (use during maintenance window)
VACUUM ANALYZE;

-- Full vacuum (requires table lock - use sparingly)
VACUUM FULL ANALYZE tablename;
```

**Monitoring:**
```sql
-- Check vacuum progress
SELECT
  pid,
  now() - query_start AS duration,
  query
FROM pg_stat_activity
WHERE query LIKE '%VACUUM%';
```

### 2. Reindexing

**When to use:**
- Index bloat detected
- After version upgrades
- Performance degradation on indexed queries

**Procedure:**
```sql
-- Check index bloat
SELECT
  schemaname,
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) AS size
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(schemaname||'.'||indexname) DESC;

-- Reindex specific index (CONCURRENT = no locks)
REINDEX INDEX CONCURRENTLY index_name;

-- Reindex table (all indexes)
REINDEX TABLE CONCURRENTLY table_name;

-- Reindex entire database (during maintenance window)
REINDEX DATABASE CONCURRENTLY orion_db;
```

**Note:** REINDEX CONCURRENTLY requires PostgreSQL 12+

### 3. Analyzing Statistics

**When to use:**
- After bulk data loads
- When query plans seem suboptimal
- After major schema changes

**Procedure:**
```sql
-- Analyze specific table
ANALYZE tablename;

-- Analyze all tables
ANALYZE;

-- Check last analyze time
SELECT
  schemaname,
  tablename,
  last_analyze,
  last_autoanalyze
FROM pg_stat_user_tables
ORDER BY last_analyze NULLS FIRST;
```

### 4. Connection Pool Management

**Check active connections:**
```sql
-- Current connection count
SELECT count(*) FROM pg_stat_activity;

-- Connections by state
SELECT
  state,
  count(*)
FROM pg_stat_activity
GROUP BY state;

-- Long-running queries
SELECT
  pid,
  now() - pg_stat_activity.query_start AS duration,
  query,
  state
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '5 minutes'
ORDER BY duration DESC;
```

**Kill stuck connections:**
```sql
-- Cancel query (graceful)
SELECT pg_cancel_backend(pid);

-- Terminate connection (forceful)
SELECT pg_terminate_backend(pid);

-- Kill all idle connections older than 1 hour
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND now() - state_change > interval '1 hour'
  AND pid <> pg_backend_pid();
```

---

## 📊 Performance Monitoring

### 1. Slow Queries

**Enable slow query logging:**
```sql
-- Set threshold to 100ms
ALTER DATABASE orion_db SET log_min_duration_statement = 100;

-- Or in postgresql.conf:
log_min_duration_statement = 100
```

**Analyze slow queries:**
```sql
-- Top slow queries
SELECT
  calls,
  total_exec_time,
  mean_exec_time,
  query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Queries by total time
SELECT
  calls,
  total_exec_time,
  query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

### 2. Index Usage Analysis

**Check unused indexes:**
```sql
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

**Check missing indexes:**
```sql
-- Sequential scans on large tables (might need indexes)
SELECT
  schemaname,
  tablename,
  seq_scan,
  seq_tup_read,
  idx_scan,
  seq_tup_read / seq_scan AS avg_seq_tup,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
WHERE seq_scan > 0
  AND schemaname = 'public'
ORDER BY seq_tup_read DESC
LIMIT 20;
```

### 3. Table Size Monitoring

**Check table sizes:**
```sql
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Database size:**
```sql
SELECT
  pg_database.datname,
  pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;
```

---

## 🚨 Troubleshooting

### High CPU Usage

**Diagnose:**
```sql
-- Find CPU-intensive queries
SELECT
  pid,
  now() - query_start AS duration,
  state,
  query
FROM pg_stat_activity
ORDER BY query_start
LIMIT 10;
```

**Solutions:**
1. Kill problematic queries
2. Add missing indexes
3. Optimize query (EXPLAIN ANALYZE)
4. Scale vertically (more CPU)

### High Memory Usage

**Diagnose:**
```sql
-- Check shared buffer usage
SELECT * FROM pg_stat_bgwriter;

-- Check cache hit ratio
SELECT
  sum(heap_blks_read) AS heap_read,
  sum(heap_blks_hit) AS heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
FROM pg_statio_user_tables;
```

**Solutions:**
1. Increase shared_buffers (PostgreSQL.conf)
2. Increase effective_cache_size
3. Reduce work_mem for specific queries

### Lock Contention

**Diagnose:**
```sql
-- Check current locks
SELECT
  locktype,
  relation::regclass,
  mode,
  transactionid AS tid,
  virtualtransaction AS vtid,
  pid,
  granted
FROM pg_catalog.pg_locks
WHERE NOT granted
ORDER BY relation;

-- Find blocking queries
SELECT
  blocked_locks.pid AS blocked_pid,
  blocked_activity.usename AS blocked_user,
  blocking_locks.pid AS blocking_pid,
  blocking_activity.usename AS blocking_user,
  blocked_activity.query AS blocked_statement,
  blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
  ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
  AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
  AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
  AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
  AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
  AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
  AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
  AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
  AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
  AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

**Solutions:**
1. Kill blocking query
2. Increase lock timeout
3. Optimize application logic

### Out of Disk Space

**Diagnose:**
```bash
# Check disk usage
kubectl exec -it postgres-0 -n orion-production -- df -h

# Check database size
psql -c "SELECT pg_size_pretty(pg_database_size('orion_db'));"
```

**Emergency Solutions:**
```sql
-- Drop old partitions (if using partitioning)
DROP TABLE old_partition;

-- Truncate log tables
TRUNCATE TABLE audit_log WHERE created_at < now() - interval '90 days';

-- Vacuum full to reclaim space (requires downtime)
VACUUM FULL;
```

**Long-term Solutions:**
1. Increase disk size
2. Implement data archiving
3. Enable table partitioning
4. Clean up old data

---

## 🔐 Security Maintenance

### 1. User Management

**List users and permissions:**
```sql
-- List all users
\du

-- Check user permissions on database
SELECT * FROM pg_user;

-- Check table permissions
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public';
```

**Create readonly user:**
```sql
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE orion_db TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;
```

### 2. Password Rotation

**Rotate database password:**
```bash
# Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# Update in PostgreSQL
kubectl exec -it postgres-0 -n orion-production -- psql -c \
  "ALTER USER orion WITH PASSWORD '$NEW_PASSWORD';"

# Update K8s secret
kubectl create secret generic orion-secrets \
  --from-literal=POSTGRES_PASSWORD="$NEW_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart API pods to pick up new secret
kubectl rollout restart deployment/orion-api -n orion-production
```

### 3. SSL/TLS Configuration

**Enforce SSL connections:**
```sql
-- In postgresql.conf:
ssl = on
ssl_cert_file = '/var/lib/postgresql/server.crt'
ssl_key_file = '/var/lib/postgresql/server.key'

-- Require SSL for specific user
ALTER USER orion SET ssl_is_compulsory = on;
```

---

## 📝 Maintenance Windows

### Planned Maintenance Window

**Standard window:** Sunday 02:00-06:00 CET

**Procedure:**
1. **T-7 days:** Notify users via status page
2. **T-1 day:** Final notification
3. **T-0:**
   - Enable maintenance mode
   - Stop API (scale to 0)
   - Take full backup
   - Perform maintenance tasks
   - Verify database health
   - Start API (scale up)
   - Smoke tests
   - Disable maintenance mode
4. **T+1 hour:** Monitor for issues

### Emergency Maintenance

**Procedure:**
1. Declare incident (P1/P2)
2. Notify on-call team
3. Take snapshot/backup
4. Perform emergency fix
5. Verify fix
6. Post-incident review

---

## 📈 Capacity Planning

### Growth Metrics to Track

**Monthly monitoring:**
```sql
-- Database size growth
SELECT
  date_trunc('month', now()) AS month,
  pg_size_pretty(pg_database_size('orion_db')) AS current_size;

-- Table growth
SELECT
  schemaname,
  tablename,
  n_live_tup,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Connection usage trend
SELECT
  max(numbackends) AS max_connections,
  date_trunc('day', stats_reset) AS day
FROM pg_stat_database
WHERE datname = 'orion_db'
GROUP BY day
ORDER BY day DESC;
```

### Scaling Thresholds

**Vertical scaling triggers:**
- CPU usage >70% for 1 week
- Memory usage >80% for 1 week
- Disk usage >75%
- Connection pool >80% utilized

**Horizontal scaling (read replicas):**
- Read queries >70% of total queries
- High SELECT latency (P95 >100ms)
- Reporting queries impacting OLTP performance

---

## 🔗 Related Documentation

- [Disaster Recovery Runbook](DISASTER_RECOVERY.md)
- [Incident Response Runbook](INCIDENT_RESPONSE.md)
- [Backup Verification Procedures](BACKUP_VERIFICATION.md)

---

**Last Maintenance:** [DATE]
**Next Scheduled Maintenance:** [DATE]
**Database Version:** PostgreSQL 15.x
