# RIS Austria Integration Research
## Rechtsinformationssystem Österreich - Legal Database Integration

**Document Version:** 1.0
**Date:** 2026-04-11
**Status:** Research & Implementation Planning
**Related:** orion_kb_validation.py (line 208 TODO)

---

## Executive Summary

The Austrian Legal Information System (Rechtsinformationssystem Österreich - RIS) at `https://www.ris.bka.gv.at` is the official platform for Austrian federal and state law. This document provides comprehensive research findings on integration possibilities, technical approaches, and implementation recommendations for the ORION Architekt AT system.

**Key Finding:** RIS does not provide a public REST API. Integration requires alternative approaches including web scraping, manual monitoring, or third-party legal database APIs.

---

## 1. API Availability and Access Method

### 1.1 Official API Status

**Current Status (as of January 2025):**
- **No Public REST API Available**
- **No Official JSON/XML API Endpoints**
- RIS is primarily a web-based interface designed for human interaction
- The system uses server-side rendering with form-based searches

### 1.2 Available Access Methods

#### Method 1: Web Interface (Manual)
- **URL:** https://www.ris.bka.gv.at
- **Access:** Public, no authentication required
- **Sections Available:**
  - Bundesrecht (Federal Law)
  - Landesrecht (State Law) - for all 9 Austrian states
  - Gemeinderecht (Municipal Law)
  - Judikatur (Case Law)
  - Kundmachungen (Official Announcements)

#### Method 2: Direct URL Construction
- RIS allows direct linking to specific legal documents via URL parameters
- URLs follow predictable patterns for certain document types
- **Example Pattern:**
  ```
  https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=[NUMBER]
  ```

#### Method 3: Automated Search via HTTP Requests
- Search forms can be automated using HTTP POST/GET requests
- Requires parsing HTML responses (no structured data format)
- Subject to potential structural changes in the website

#### Method 4: RSS Feeds (Limited)
- Some sections may offer RSS feeds for new publications
- Coverage is limited and not comprehensive
- Primarily for Bundesgesetzblatt (Federal Law Gazette) updates

### 1.3 Third-Party Solutions

#### Legal Database Providers
Several commercial providers offer structured access to Austrian legal data:

1. **JUSLINE (jusline.at)**
   - Structured legal database
   - May offer API access (commercial)
   - Better data structure than RIS

2. **Lexis Nexis / Austrian Standards**
   - Professional legal databases
   - Commercial licensing required
   - May include API access

3. **Austrian Parliament Data Services**
   - Some parliamentary data available via open data initiatives
   - Limited to federal legislation

---

## 2. Authentication Requirements

### 2.1 RIS Public Website
- **Authentication:** None required for public access
- **Registration:** Not available/not required
- **API Keys:** Not applicable (no API)
- **Rate Limiting:** Not officially documented, but excessive automated requests may be blocked

### 2.2 Best Practices for Web Access
- Implement respectful scraping with delays between requests
- Use appropriate User-Agent headers
- Cache responses to minimize server load
- Recommended delay: 2-5 seconds between requests
- Access during off-peak hours when possible

---

## 3. Endpoint Documentation (Web-Based Access)

### 3.1 Federal Law (Bundesrecht)

#### Search Endpoint
```
URL: https://www.ris.bka.gv.at/Bundesrecht/
Method: GET/POST
Type: Web Form
```

**Key Parameters:**
- `Abfrage`: Query type (e.g., "Bundesnormen")
- `Suchworte`: Search terms
- `Index`: Result index for pagination
- `ImRisSeitXX`: Date constraints

**Relevant for Building Regulations:**
- Bauordnungen (Building codes) - primarily state law
- Technische Bauvorschriften (Technical building regulations)
- References to OIB directives in federal context

### 3.2 State Law (Landesrecht)

#### State-Specific Endpoints
Each of Austria's 9 states has dedicated sections:

```
Tirol: https://www.ris.bka.gv.at/Landesrecht/Tirol/
Wien: https://www.ris.bka.gv.at/Landesrecht/Wien/
Vorarlberg: https://www.ris.bka.gv.at/Landesrecht/Vorarlberg/
Steiermark: https://www.ris.bka.gv.at/Landesrecht/Steiermark/
Salzburg: https://www.ris.bka.gv.at/Landesrecht/Salzburg/
Oberösterreich: https://www.ris.bka.gv.at/Landesrecht/Oberösterreich/
Niederösterreich: https://www.ris.bka.gv.at/Landesrecht/Niederösterreich/
Kärnten: https://www.ris.bka.gv.at/Landesrecht/Kärnten/
Burgenland: https://www.ris.bka.gv.at/Landesrecht/Burgenland/
```

**Building Codes by State:**
- Tiroler Bauordnung (TBO)
- Wiener Bauordnung (WBO)
- Vorarlberger Baugesetz
- Steiermärkisches Baugesetz
- Salzburger Baupolizeigesetz
- OÖ Bautechnikgesetz
- NÖ Bauordnung
- Kärntner Bauordnung
- Burgenländisches Baugesetz

### 3.3 Official Gazettes (Gesetzblätter)

#### Bundesgesetzblatt (BGBl)
```
URL: https://www.ris.bka.gv.at/Bundesgesetzblatt/
Method: GET
```

**Parameters:**
- Year (Jahr)
- Part (Teil I, II, III)
- Number (Nummer)

#### Landesgesetzblätter (LGBl)
State-specific law gazettes for tracking new legislation and amendments.

**Monitoring Strategy:**
- Check monthly for building regulation updates
- Focus on "Bautechnik" and "Baurecht" categories
- Track amendment dates for version control

---

## 4. Data Formats and Response Structures

### 4.1 Current RIS Format

**Response Type:** HTML (server-rendered)

**Typical Structure:**
```html
<div class="ContentHeader">
  <h1>[Law Title]</h1>
</div>
<div class="Fundstelle">
  BGBl. [Publication Details]
</div>
<div class="Inhalt">
  [Legal Text with Paragraphs]
</div>
```

**Challenges:**
- No structured JSON/XML responses
- HTML structure may change without notice
- Text embedded in complex DOM structures
- Requires robust HTML parsing

### 4.2 Extractable Data Points

For each legal document, the following can typically be extracted:

```json
{
  "document_type": "Bundesgesetz|Verordnung|Landesgesetz",
  "title": "Full legal name",
  "short_title": "Abbreviation (e.g., TBO 2022)",
  "publication": {
    "gazette": "BGBl|LGBl",
    "year": "2023",
    "number": "145",
    "part": "I"
  },
  "valid_from": "2023-05-25",
  "valid_until": null,
  "last_amended": {
    "date": "2024-01-15",
    "reference": "BGBl I 2024/12"
  },
  "legal_area": "Baurecht",
  "paragraphs": [
    {
      "number": "§ 1",
      "heading": "Geltungsbereich",
      "text": "..."
    }
  ],
  "annexes": [],
  "ris_url": "https://www.ris.bka.gv.at/...",
  "checksum": "md5_hash_of_content"
}
```

### 4.3 Recommended Internal Format

For ORION knowledge base storage:

```python
{
    "regulation_id": "TBO_2022_v1.3",
    "regulation_type": "state_building_code",
    "state": "tirol",
    "name_de": "Tiroler Bauordnung 2022",
    "abbreviation": "TBO 2022",
    "publication_reference": "LGBl. Nr. 55/2022",
    "valid_from": "2022-07-01",
    "valid_until": null,
    "current_version": "1.3",
    "version_history": [
        {
            "version": "1.3",
            "date": "2024-06-01",
            "amendment": "LGBl. Nr. 34/2024",
            "changes": ["§ 4 Abs 2 amended", "§ 15a inserted"]
        }
    ],
    "ris_url": "https://www.ris.bka.gv.at/...",
    "last_checked": "2026-04-11T10:30:00Z",
    "content_hash": "sha256_hash",
    "relevance_score": 0.95,
    "tags": ["bauordnung", "gebäudehöhe", "brandschutz"],
    "related_standards": ["OIB-RL 1", "OIB-RL 2"]
}
```

---

## 5. Implementation Recommendations

### 5.1 Recommended Approach: Hybrid Strategy

Given the lack of official API, implement a **three-tier strategy**:

#### Tier 1: Manual Periodic Review (PRIMARY)
**For critical building regulations:**
- Quarterly manual review of RIS for each relevant state building code
- Document review dates and version numbers
- Update knowledge base manually with verified changes
- Most reliable for regulatory compliance

**Frequency:**
- Building codes: Quarterly review
- OIB directives: When new versions announced (typically 3-year cycle)
- Federal regulations: Bi-annual review

#### Tier 2: Automated Change Detection (SECONDARY)
**For monitoring updates:**
- Scheduled checks (monthly) of specific RIS pages
- Hash-based change detection on key legal texts
- Alert system when changes detected
- Human verification required before updating knowledge base

**Implementation:**
```python
def detect_ris_changes(url, previous_hash):
    """
    Check if RIS document has changed
    Returns: (changed: bool, new_hash: str, timestamp: datetime)
    """
    response = requests.get(url, timeout=10)
    content = extract_legal_text(response.text)
    new_hash = hashlib.sha256(content.encode()).hexdigest()

    changed = new_hash != previous_hash
    return changed, new_hash, datetime.now(timezone.utc)
```

#### Tier 3: Web Scraping (FALLBACK)
**For specific data extraction:**
- Used only when specific information needed
- Implement robust error handling
- Respectful rate limiting (2-5 second delays)
- Log all scraping activities
- Have manual fallback for failures

### 5.2 Technology Stack

#### HTML Parsing
```python
# Recommended libraries
import requests
from bs4 import BeautifulSoup
import lxml

# Alternative: Scrapy for more complex scraping
from scrapy import Spider
```

#### Recommended Libraries
1. **BeautifulSoup4** - HTML parsing
2. **requests** - HTTP client (already in use)
3. **lxml** - Fast XML/HTML processing
4. **selenium** (optional) - If JavaScript rendering needed
5. **schedule** - For automated periodic checks

#### Example Implementation
```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import hashlib
import time

class RISMonitor:
    """Monitor RIS Austria for building regulation updates"""

    BASE_URL = "https://www.ris.bka.gv.at"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ORION-Architekt-AT/1.0 (Building Compliance Monitor; contact@example.com)'
        })

    def get_state_building_code_url(self, state: str) -> str:
        """Get URL for state building code"""
        state_codes = {
            'tirol': 'Eli/Landesgesetzblatt/2022/55',
            'wien': 'Eli/Landesgesetzblatt/Wien/...',
            # ... other states
        }
        path = state_codes.get(state.lower())
        if path:
            return f"{self.BASE_URL}/{path}"
        return None

    def fetch_document(self, url: str) -> Optional[str]:
        """Fetch RIS document with rate limiting"""
        time.sleep(2)  # Respectful delay
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_legal_text(self, html: str) -> Dict:
        """Extract structured data from RIS HTML"""
        soup = BeautifulSoup(html, 'lxml')

        # Extract title
        title_elem = soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else None

        # Extract publication info
        publication_elem = soup.find('div', class_='Fundstelle')
        publication = publication_elem.get_text(strip=True) if publication_elem else None

        # Extract content
        content_elem = soup.find('div', class_='Inhalt')
        content = content_elem.get_text(strip=True) if content_elem else None

        # Calculate content hash for change detection
        content_hash = None
        if content:
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        return {
            'title': title,
            'publication': publication,
            'content': content,
            'content_hash': content_hash,
            'fetch_timestamp': datetime.now(timezone.utc).isoformat()
        }

    def check_for_updates(self, state: str, last_known_hash: str) -> Dict:
        """Check if building code has been updated"""
        url = self.get_state_building_code_url(state)
        if not url:
            return {'error': f'Unknown state: {state}'}

        html = self.fetch_document(url)
        if not html:
            return {'error': 'Failed to fetch document'}

        data = self.extract_legal_text(html)

        has_changed = data['content_hash'] != last_known_hash

        return {
            'state': state,
            'url': url,
            'changed': has_changed,
            'current_hash': data['content_hash'],
            'previous_hash': last_known_hash,
            'title': data['title'],
            'publication': data['publication'],
            'checked_at': data['fetch_timestamp']
        }
```

### 5.3 Integration into orion_kb_validation.py

**Replace TODO at line 208 with:**

```python
def check_ris_updates(bundesland: str, rechtsgebiet: str = "Baurecht") -> Dict:
    """
    Prüft das Rechtsinformationssystem Österreich auf Aktualisierungen.

    Implementation Strategy:
    - Hash-based change detection on known building code URLs
    - Manual verification flag for human review
    - Alerts when changes detected but no automatic updates

    Args:
        bundesland: Bundesland (z.B. "tirol", "wien")
        rechtsgebiet: Rechtsgebiet (default: "Baurecht")

    Returns:
        Dict mit Informationen über Updates und Änderungen
    """
    cache_key = _get_cache_key(f"ris_{bundesland}_{rechtsgebiet}")
    cached = _get_cached(cache_key)
    if cached:
        return cached

    # Known URLs and content hashes for building codes
    BUILDING_CODE_URLS = {
        "tirol": {
            "url": "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=LrT&Gesetzesnummer=20000460",
            "name": "Tiroler Bauordnung 2022 (TBO 2022)",
            "last_known_hash": "stored_in_config_or_db",
            "last_verified": "2026-01-15"
        },
        "wien": {
            "url": "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=LrW&Gesetzesnummer=20000006",
            "name": "Bauordnung für Wien (BO für Wien)",
            "last_known_hash": "stored_in_config_or_db",
            "last_verified": "2026-01-15"
        },
        # Add other states...
    }

    result = {
        "bundesland": bundesland,
        "rechtsgebiet": rechtsgebiet,
        "status": "info",
        "letzter_check": datetime.now(timezone.utc).isoformat(),
        "updates_gefunden": False,
        "manual_verification_required": False,
    }

    state_info = BUILDING_CODE_URLS.get(bundesland.lower())
    if not state_info:
        result["nachricht"] = f"Bundesland '{bundesland}' nicht in Monitoring-Liste"
        result["hinweis"] = "Bitte manuell auf ris.bka.gv.at prüfen"
        _set_cache(cache_key, result)
        return result

    # Try to fetch and check for changes
    try:
        response = _safe_request(state_info["url"])
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', class_='Inhalt')

            if content:
                current_hash = hashlib.sha256(
                    content.get_text().encode('utf-8')
                ).hexdigest()

                # Compare with last known hash
                if current_hash != state_info["last_known_hash"]:
                    result["updates_gefunden"] = True
                    result["manual_verification_required"] = True
                    result["status"] = "warning"
                    result["nachricht"] = f"⚠️ ÄNDERUNG ERKANNT: {state_info['name']}"
                    result["hinweis"] = (
                        f"Der Inhalt der Bauordnung hat sich seit {state_info['last_verified']} geändert. "
                        "Bitte manuell verifizieren und Knowledge Base aktualisieren."
                    )
                    result["ris_url"] = state_info["url"]
                    result["current_hash"] = current_hash
                    result["previous_hash"] = state_info["last_known_hash"]
                else:
                    result["status"] = "ok"
                    result["nachricht"] = f"✓ {state_info['name']} - keine Änderungen"
                    result["content_hash"] = current_hash
            else:
                result["status"] = "error"
                result["nachricht"] = "Konnte RIS-Inhalt nicht parsen"
                result["hinweis"] = "RIS-Website-Struktur möglicherweise geändert"

    except Exception as e:
        result["status"] = "error"
        result["nachricht"] = f"Fehler bei RIS-Abfrage: {str(e)}"
        result["hinweis"] = "Bitte manuell auf ris.bka.gv.at prüfen"

    result["quelle"] = SOURCES["ris"]
    result["building_code_url"] = state_info["url"]
    result["last_verified_date"] = state_info["last_verified"]

    _set_cache(cache_key, result)
    return result
```

### 5.4 Data Persistence Strategy

**Store tracking data:**
```python
# Add to orion_kb_validation.py configuration section

RIS_TRACKING = {
    "tirol": {
        "bauordnung": {
            "url": "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=LrT&Gesetzesnummer=20000460",
            "title": "Tiroler Bauordnung 2022",
            "last_hash": "abc123...",
            "last_verified": "2026-04-01",
            "version": "LGBl. Nr. 55/2022 idF LGBl. Nr. 34/2024"
        }
    },
    # ... other states
}

def update_ris_tracking(state: str, doc_type: str, new_hash: str, new_version: str):
    """Update tracking information after manual verification"""
    if state in RIS_TRACKING and doc_type in RIS_TRACKING[state]:
        RIS_TRACKING[state][doc_type]["last_hash"] = new_hash
        RIS_TRACKING[state][doc_type]["last_verified"] = datetime.now().date().isoformat()
        RIS_TRACKING[state][doc_type]["version"] = new_version
        # Persist to JSON file or database
```

---

## 6. Rate Limits and Usage Restrictions

### 6.1 Known Limitations

**Official Documentation:** None available

**Observed Behavior:**
- No official rate limits published
- Website appears to allow reasonable automated access
- Excessive requests may trigger IP-based blocking
- No API quotas (as no API exists)

### 6.2 Recommended Limits

**Self-Imposed Restrictions:**
```python
RATE_LIMITS = {
    "requests_per_minute": 10,
    "requests_per_hour": 100,
    "min_delay_seconds": 2,
    "max_concurrent": 1
}
```

**Implementation:**
```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute=10):
        self.requests_per_minute = requests_per_minute
        self.requests = []

    def wait_if_needed(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req_time for req_time in self.requests
            if now - req_time < timedelta(minutes=1)
        ]

        # If at limit, wait
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0]).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.requests.append(now)
```

### 6.3 Best Practices

1. **Timing:**
   - Run automated checks during off-peak hours (late evening/early morning CET)
   - Stagger checks for different states
   - Implement exponential backoff on errors

2. **Identification:**
   - Use descriptive User-Agent
   - Include contact information
   - Example: `ORION-Architekt-AT/1.0 (Automated Building Code Monitor; contact@example.com)`

3. **Error Handling:**
   - Respect HTTP 429 (Too Many Requests) responses
   - Implement circuit breaker pattern for repeated failures
   - Fall back to manual notification on persistent errors

---

## 7. Fallback Strategies

### 7.1 Primary Fallback: Manual Monitoring

**Process:**
1. **Monthly Manual Checks:**
   - Visit RIS website manually
   - Check each relevant state building code
   - Document version numbers and last amendment dates

2. **Subscription to Official Channels:**
   - Subscribe to Landesgesetzblatt notifications (if available)
   - Monitor OIB website for directive updates
   - Join professional mailing lists (Ziviltechniker associations)

3. **Documentation:**
   - Maintain spreadsheet with last verified dates
   - Record amendment numbers and dates
   - Track version history

**Template:**
```csv
State,Regulation,Last_Verified,Version,Amendment_Ref,Next_Check,Notes
Tirol,TBO 2022,2026-04-01,1.3,LGBl 34/2024,2026-07-01,No changes
Wien,BO Wien,2026-04-01,2023,LGBl 5/2023,2026-07-01,Check § 4
```

### 7.2 Secondary Fallback: Email Alerts

**Setup:**
- Configure email notifications for failed automated checks
- Weekly digest of RIS monitoring status
- Immediate alerts for detected changes

```python
def send_ris_alert(state: str, details: Dict):
    """Send email alert when RIS change detected"""
    subject = f"ORION: RIS Update Detected - {state.capitalize()}"
    body = f"""
    RIS Change Detection Alert

    State: {state}
    Regulation: {details['title']}
    URL: {details['url']}

    Previous Hash: {details['previous_hash']}
    Current Hash: {details['current_hash']}

    Action Required:
    1. Manually verify changes on RIS website
    2. Update ORION knowledge base if necessary
    3. Update version tracking

    Checked: {details['checked_at']}
    """
    # Send via configured email service
```

### 7.3 Tertiary Fallback: Third-Party Services

**Commercial Options:**
1. **JUSLINE.at**
   - May offer structured access
   - Contact for API availability and pricing

2. **Legal Tech Platforms**
   - LexisNexis
   - Austrian Standards Online
   - May provide API access with subscription

3. **Professional Associations**
   - Bundeskammer der Architekten und Ingenieurkonsulenten
   - May provide update services to members

### 7.4 Emergency Procedures

**If all automated systems fail:**

1. **Immediate Actions:**
   - Switch to 100% manual verification
   - Notify users of potential data staleness
   - Document in system status

2. **Communication:**
   - Display warning in ORION interface
   - Inform users to verify critical regulations independently
   - Provide direct RIS links

3. **Gradual Recovery:**
   - Investigate failure cause
   - Restore automated monitoring cautiously
   - Increase manual verification frequency until stability confirmed

---

## 8. Legal and Compliance Considerations

### 8.1 Terms of Use

**RIS Website:**
- Public access for information purposes
- No explicit prohibition of automated access in reasonable amounts
- No robots.txt restrictions on legal content
- Attribution to RIS recommended

**Compliance:**
```python
# Include attribution in all extracted content
attribution = {
    "source": "Rechtsinformationssystem des Bundes (RIS)",
    "url": "https://www.ris.bka.gv.at",
    "access_date": datetime.now().isoformat(),
    "note": "Official legal texts - verify on RIS for legal certainty"
}
```

### 8.2 Data Usage Rights

**Copyright:**
- Austrian legal texts are generally public domain
- Official publications can be reproduced
- No copyright restrictions on law texts themselves

**Liability:**
- ORION must include disclaimer: "Unofficial text - verify on RIS for legal purposes"
- No legal liability assumed for accuracy
- Users must verify critical information

**Recommended Disclaimer:**
```
Rechtlicher Hinweis:
Die dargestellten Gesetzestexte sind unverbindliche Abschriften.
Rechtlich verbindlich sind ausschließlich die im Rechtsinformationssystem
des Bundes (RIS) kundgemachten Fassungen. Eine Haftung für die Richtigkeit
und Vollständigkeit wird nicht übernommen.

Quelle: https://www.ris.bka.gv.at
```

### 8.3 GDPR Considerations

**Personal Data:**
- Legal texts contain no personal data
- System logs may contain user queries - handle per GDPR

**Data Retention:**
- Cache legal texts as needed
- Log automated access for monitoring
- Retain version history for audit trail

---

## 9. Testing and Validation

### 9.1 Test Cases

```python
# test_ris_integration.py

def test_ris_url_accessibility():
    """Test that RIS URLs are accessible"""
    urls = [
        "https://www.ris.bka.gv.at",
        "https://www.ris.bka.gv.at/Bundesrecht/",
        "https://www.ris.bka.gv.at/Landesrecht/Tirol/",
    ]
    for url in urls:
        response = requests.get(url)
        assert response.status_code == 200

def test_ris_content_extraction():
    """Test HTML parsing of RIS content"""
    html = """<div class="Inhalt">§ 1 Test paragraph</div>"""
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', class_='Inhalt')
    assert content is not None
    assert '§ 1' in content.get_text()

def test_hash_change_detection():
    """Test change detection via content hashing"""
    text1 = "§ 1 Original text"
    text2 = "§ 1 Modified text"
    hash1 = hashlib.sha256(text1.encode()).hexdigest()
    hash2 = hashlib.sha256(text2.encode()).hexdigest()
    assert hash1 != hash2

def test_rate_limiting():
    """Test that rate limiting is enforced"""
    limiter = RateLimiter(requests_per_minute=10)
    start = time.time()
    for _ in range(12):
        limiter.wait_if_needed()
    elapsed = time.time() - start
    assert elapsed >= 60  # Should take at least 1 minute for 12 requests
```

### 9.2 Monitoring

**Metrics to Track:**
- Number of RIS checks performed
- Success/failure rate
- Average response time
- Number of changes detected
- Manual verification completion rate

```python
RIS_METRICS = {
    "checks_total": 0,
    "checks_successful": 0,
    "checks_failed": 0,
    "changes_detected": 0,
    "avg_response_time_ms": 0,
    "last_check": None,
    "consecutive_failures": 0
}
```

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up basic RIS URL monitoring
- [ ] Implement HTML parsing for one state (Tirol)
- [ ] Create hash-based change detection
- [ ] Test against live RIS website

### Phase 2: Expansion (Week 3-4)
- [ ] Add all 9 state building codes
- [ ] Implement rate limiting
- [ ] Create alert system for detected changes
- [ ] Set up automated testing

### Phase 3: Integration (Week 5-6)
- [ ] Integrate into orion_kb_validation.py
- [ ] Replace TODO at line 208
- [ ] Add configuration for tracked URLs
- [ ] Create manual verification workflow

### Phase 4: Automation (Week 7-8)
- [ ] Schedule periodic checks (monthly)
- [ ] Implement email notifications
- [ ] Create admin dashboard for monitoring
- [ ] Document manual verification process

### Phase 5: Optimization (Week 9-10)
- [ ] Optimize parsing performance
- [ ] Add caching layer
- [ ] Improve error recovery
- [ ] User documentation

---

## 11. Required Dependencies

### Python Packages
```txt
# requirements.txt additions

# Web scraping and parsing
beautifulsoup4==4.12.3
lxml==5.1.0

# Already included (verify versions)
requests==2.31.0

# Optional but recommended
selenium==4.18.0  # If JavaScript rendering needed
scrapy==2.11.0    # For more complex scraping
schedule==1.2.0   # For automated periodic checks

# Testing
pytest-html==4.1.1
responses==0.25.0  # For mocking HTTP in tests
```

### Installation
```bash
pip install beautifulsoup4 lxml schedule
```

---

## 12. Code Examples

### Complete Working Example

```python
#!/usr/bin/env python3
"""
RIS Austria Integration - Complete Example
Demonstrates change detection for Austrian building codes
"""

import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime, timezone
from typing import Dict, Optional
import time
import json

class RISIntegration:
    """
    Integration with Austrian Legal Information System (RIS)
    for monitoring building code updates
    """

    BASE_URL = "https://www.ris.bka.gv.at"

    # Known URLs for state building codes (Bauordnungen)
    BUILDING_CODES = {
        "tirol": {
            "url": "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=LrT&Gesetzesnummer=20000460",
            "name": "Tiroler Bauordnung 2022",
            "short": "TBO 2022"
        },
        "wien": {
            "url": "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=LrW&Gesetzesnummer=20000006",
            "name": "Bauordnung für Wien",
            "short": "BO Wien"
        },
        "vorarlberg": {
            "url": "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=LrVbg&Gesetzesnummer=20000108",
            "name": "Vorarlberger Baugesetz",
            "short": "VlbgBauG"
        },
        # Add other states as needed
    }

    def __init__(self, cache_file: str = "ris_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ORION-Architekt-AT/1.0 (Building Code Monitor; compliance@example.com)'
        })

    def _load_cache(self) -> Dict:
        """Load cached hashes and timestamps"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def fetch_document(self, url: str) -> Optional[str]:
        """Fetch document from RIS with rate limiting"""
        time.sleep(2)  # Be respectful to the server

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_content(self, html: str) -> Optional[Dict]:
        """Extract legal content from RIS HTML"""
        soup = BeautifulSoup(html, 'lxml')

        # Find the main content
        content_div = soup.find('div', class_='Inhalt')
        if not content_div:
            # Try alternative selectors
            content_div = soup.find('div', id='content')

        if not content_div:
            return None

        # Extract text content
        text = content_div.get_text(separator='\n', strip=True)

        # Find title
        title_elem = soup.find('h1') or soup.find('div', class_='ContentHeader')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown"

        # Find publication reference
        fundstelle = soup.find('div', class_='Fundstelle')
        publication = fundstelle.get_text(strip=True) if fundstelle else "Unknown"

        # Calculate hash
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

        return {
            'title': title,
            'publication': publication,
            'content': text,
            'hash': content_hash,
            'length': len(text)
        }

    def check_state(self, state: str) -> Dict:
        """
        Check a specific state's building code for updates

        Returns:
            Dict with status, changes, and metadata
        """
        state_lower = state.lower()

        if state_lower not in self.BUILDING_CODES:
            return {
                'status': 'error',
                'message': f'Unknown state: {state}',
                'states_available': list(self.BUILDING_CODES.keys())
            }

        code_info = self.BUILDING_CODES[state_lower]
        url = code_info['url']

        # Fetch document
        html = self.fetch_document(url)
        if not html:
            return {
                'status': 'error',
                'state': state,
                'message': 'Failed to fetch document from RIS'
            }

        # Extract content
        content = self.extract_content(html)
        if not content:
            return {
                'status': 'error',
                'state': state,
                'message': 'Failed to parse RIS HTML - structure may have changed'
            }

        # Check cache for previous version
        cache_key = f"{state_lower}_building_code"
        previous_data = self.cache.get(cache_key, {})
        previous_hash = previous_data.get('hash')

        # Detect changes
        has_changed = previous_hash and (content['hash'] != previous_hash)

        result = {
            'status': 'success',
            'state': state,
            'code_name': code_info['name'],
            'code_short': code_info['short'],
            'url': url,
            'current_hash': content['hash'],
            'previous_hash': previous_hash,
            'has_changed': has_changed,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'title': content['title'],
            'publication': content['publication'],
            'content_length': content['length']
        }

        if has_changed:
            result['message'] = f"⚠️ CHANGE DETECTED in {code_info['short']}"
            result['action_required'] = "Manual verification needed - update knowledge base"
        elif previous_hash:
            result['message'] = f"✓ No changes in {code_info['short']}"
        else:
            result['message'] = f"ℹ First check of {code_info['short']} - establishing baseline"

        # Update cache
        self.cache[cache_key] = {
            'hash': content['hash'],
            'last_checked': result['checked_at'],
            'title': content['title'],
            'publication': content['publication']
        }
        self._save_cache()

        return result

    def check_all_states(self) -> Dict:
        """Check all monitored states for updates"""
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'states_checked': 0,
            'changes_detected': 0,
            'errors': 0,
            'details': {}
        }

        for state in self.BUILDING_CODES.keys():
            result = self.check_state(state)
            results['details'][state] = result
            results['states_checked'] += 1

            if result['status'] == 'error':
                results['errors'] += 1
            elif result.get('has_changed', False):
                results['changes_detected'] += 1

        return results

    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status"""
        status = {
            'monitored_states': list(self.BUILDING_CODES.keys()),
            'cache_entries': len(self.cache),
            'last_checks': {}
        }

        for state, code in self.BUILDING_CODES.items():
            cache_key = f"{state}_building_code"
            if cache_key in self.cache:
                status['last_checks'][state] = {
                    'name': code['name'],
                    'last_checked': self.cache[cache_key].get('last_checked', 'Never'),
                    'current_version': self.cache[cache_key].get('publication', 'Unknown')
                }

        return status


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("RIS Austria Integration - Building Code Monitor")
    print("=" * 80)
    print()

    # Initialize
    ris = RISIntegration()

    # Check monitoring status
    print("Current Monitoring Status:")
    print("-" * 80)
    status = ris.get_monitoring_status()
    print(f"Monitored states: {', '.join(status['monitored_states'])}")
    print()

    # Check a specific state
    print("Checking Tirol building code...")
    result = ris.check_state("tirol")
    print(f"Status: {result['status']}")
    print(f"Message: {result.get('message', 'N/A')}")
    if result['status'] == 'success':
        print(f"Title: {result['title']}")
        print(f"Publication: {result['publication']}")
        print(f"URL: {result['url']}")
        print(f"Hash: {result['current_hash'][:16]}...")
        print(f"Changed: {result['has_changed']}")
    print()

    # Check all states (commented out to avoid excessive requests)
    # print("Checking all states...")
    # all_results = ris.check_all_states()
    # print(json.dumps(all_results, indent=2, ensure_ascii=False))
```

---

## 13. Conclusion and Next Steps

### Summary

The RIS Austria integration faces the challenge of **no official API**, requiring alternative approaches:

1. **Recommended Primary Approach:** Manual periodic review with hash-based change detection
2. **Automation Level:** Semi-automated monitoring with human verification
3. **Risk Level:** Low (conservative approach ensures compliance)
4. **Maintenance Effort:** Moderate (quarterly manual reviews + automated monitoring)

### Immediate Actions

1. **Implement Basic Monitoring (This Week):**
   - Add hash-based change detection for 3 key states (Tirol, Wien, Vorarlberg)
   - Set up monthly automated checks
   - Create alert system for detected changes

2. **Update orion_kb_validation.py (Next Week):**
   - Replace TODO at line 208 with working implementation
   - Add configuration for tracked building codes
   - Integrate with existing caching system

3. **Establish Manual Process (Week 3):**
   - Document manual verification workflow
   - Create checklist for quarterly reviews
   - Train team on RIS navigation

### Long-term Strategy

1. **Monitor for API Development:**
   - Check periodically if RIS develops official API
   - Engage with legal tech community in Austria
   - Consider partnership with legal database providers

2. **Continuous Improvement:**
   - Refine HTML parsing as needed
   - Improve change detection accuracy
   - Reduce manual verification burden

3. **Alternative Data Sources:**
   - Explore third-party legal databases
   - Consider partnerships with professional associations
   - Investigate EU-level legal data initiatives

---

## References and Resources

### Official Sources
- **RIS Website:** https://www.ris.bka.gv.at
- **OIB (Austrian Institute of Building Engineering):** https://www.oib.or.at
- **Austrian Standards:** https://www.austrian-standards.at

### Technical Documentation
- **BeautifulSoup Documentation:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Requests Documentation:** https://requests.readthedocs.io/
- **Web Scraping Best Practices:** robots.txt, rate limiting, respectful crawling

### Legal References
- Austrian Copyright Law regarding official publications
- EU Open Data Directive
- GDPR compliance for automated systems

### Contact Points
- **RIS Support:** (Check website for current contact)
- **Legal Database Providers:** JUSLINE, LexisNexis Austria
- **Professional Associations:** Bundeskammer der ZiviltechnikerInnen

---

**Document Status:** Ready for Implementation
**Next Review:** 2026-10-11 (6 months)
**Maintained By:** ORION Development Team
**Related Files:**
- `/home/runner/work/ORION-Architekt-AT/ORION-Architekt-AT/orion_kb_validation.py` (line 208)
- `/home/runner/work/ORION-Architekt-AT/ORION-Architekt-AT/KB_VALIDATION_README.md`

---

*This document provides research-based recommendations for RIS Austria integration. Implementation should be done incrementally with thorough testing. Always verify legal content manually before relying on automated systems for compliance purposes.*
