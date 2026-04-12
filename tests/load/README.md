# ORION Load Testing Guide

## Quick Start

### 1. Install Locust
```bash
pip install locust
```

### 2. Run Basic Load Test (100 users)
```bash
cd tests/load
locust -f locustfile.py --host=http://localhost
```

Then open http://localhost:8089 and configure:
- **Users:** 100
- **Spawn rate:** 10 users/second

### 3. Run Headless (CI/CD)
```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --html=load-test-report.html \
  --csv=load-test-results
```

## Test Scenarios

### Baseline Test (Normal Traffic)
Simulates typical production load:
```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=100 \
  --spawn-rate=10 \
  --run-time=10m \
  --headless
```

**Expected Results:**
- **Response Time (P95):** <300ms
- **Response Time (P99):** <1000ms
- **Error Rate:** <0.1%
- **Throughput:** >100 req/sec

### Stress Test (High Load)
Tests system under heavy load:
```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=1000 \
  --spawn-rate=50 \
  --run-time=15m \
  --headless
```

**Expected Results:**
- **Response Time (P95):** <1000ms
- **Response Time (P99):** <3000ms
- **Error Rate:** <1%
- **Throughput:** >500 req/sec

### Spike Test (Sudden Traffic Burst)
Simulates sudden traffic spike:
```bash
# Start with 10 users
locust -f locustfile.py \
  --host=http://localhost \
  --users=10 \
  --spawn-rate=10 \
  --run-time=2m \
  --headless

# Then spike to 5000 users for 1 minute
locust -f locustfile.py \
  --host=http://localhost \
  --users=5000 \
  --spawn-rate=500 \
  --run-time=1m \
  --headless
```

**Expected Results:**
- System should auto-scale within 2 minutes
- No complete outage
- Graceful degradation (rate limiting kicks in)

### Soak Test (Long Duration)
Tests for memory leaks and stability:
```bash
locust -f locustfile.py \
  --host=http://localhost \
  --users=200 \
  --spawn-rate=20 \
  --run-time=24h \
  --headless
```

**Monitor:**
- Memory usage (should be stable)
- Response times (shouldn't degrade)
- Database connection pool
- Redis memory

## User Distribution

The load test simulates realistic user behavior:

| User Type | Weight | Rate Limit | Behavior |
|-----------|--------|------------|----------|
| Anonymous | 50% | None | Browse docs, health checks |
| Free Tier | 30% | 100/min | Basic calculations |
| Premium | 15% | 1000/min | Bulk operations |
| Enterprise | 5% | 10000/min | Heavy batch processing |

## Performance Targets (SLOs)

### Latency Targets
- **P50 (Median):** <100ms
- **P95:** <300ms
- **P99:** <1000ms

### Availability
- **Uptime:** 99.9% (43.2 min downtime/month)

### Error Rate
- **Target:** <0.1%
- **Warning:** >0.5%
- **Critical:** >1%

## CI/CD Integration

Add to `.github/workflows/ci-cd.yml`:

```yaml
load-test:
  name: Load Testing
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Start services
      run: docker-compose -f docker-compose.production.yml up -d

    - name: Wait for services
      run: sleep 60

    - name: Run load test
      run: |
        pip install locust
        locust -f tests/load/locustfile.py \
          --host=http://localhost \
          --users=100 \
          --spawn-rate=10 \
          --run-time=3m \
          --headless \
          --html=load-test-report.html \
          --csv=load-test-results

    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: load-test-results
        path: |
          load-test-report.html
          load-test-results_*.csv

    - name: Stop services
      if: always()
      run: docker-compose -f docker-compose.production.yml down
```

## Interpreting Results

### Good Results ✅
```
Response time percentiles:
 - 50%: 85ms
 - 95%: 245ms
 - 99%: 890ms

Total requests: 120,450
Failed requests: 12 (0.01%)
Requests/sec: 201.5
```

### Warning Signs ⚠️
```
Response time percentiles:
 - 50%: 150ms (↑)
 - 95%: 600ms (↑↑)
 - 99%: 2500ms (↑↑↑)

Failed requests: 1,205 (1%) ⚠️
Database connection pool: 95% usage ⚠️
```

### Critical Issues 🔴
```
Response time percentiles:
 - 50%: 500ms (CRITICAL)
 - 95%: 3000ms (CRITICAL)
 - 99%: timeout

Failed requests: 15,000 (12.5%) 🔴
Error: Connection pool exhausted 🔴
Error: Redis timeout 🔴
```

## Troubleshooting

### High Response Times
1. Check database query performance
2. Review Redis cache hit ratio
3. Check CPU/memory usage
4. Look for N+1 query problems

### High Error Rate
1. Check logs for exceptions
2. Verify rate limiting settings
3. Check database connections
4. Verify external API status

### Memory Leaks
1. Monitor memory over 24h
2. Check for unclosed connections
3. Review Redis memory policy
4. Check for large cached objects

## Best Practices

1. **Run load tests regularly** - Weekly for staging, before each production release
2. **Test with production data size** - Use realistic database sizes
3. **Monitor during tests** - Watch Grafana dashboards
4. **Compare trends** - Track performance over time
5. **Test failure scenarios** - Kill database, Redis, etc.

## Next Steps

After running load tests:
1. Document baseline performance metrics
2. Set up automated alerts for regressions
3. Add load tests to CI/CD pipeline
4. Create performance budget (max response times)
5. Schedule quarterly capacity planning reviews
