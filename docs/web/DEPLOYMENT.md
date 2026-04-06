# GENESIS Web Deployment Guide

**Status**: ✅ GitHub Pages configured and ready
**Live URL**: https://alvoradozerouno.github.io/ORION-Architekt-AT/

---

## 🚀 Quick Deploy (GitHub Pages)

### Option 1: Automatic (Recommended)

**Already configured!** Every push to `main` with changes in `docs/web/**` triggers automatic deployment.

```bash
# Make changes to docs/web/index.html
git add docs/web/
git commit -m "Update landing page"
git push origin main

# Wait 1-2 minutes → Live at GitHub Pages URL
```

### Option 2: Manual Trigger

1. Go to: **Actions** tab on GitHub
2. Select: **Deploy Web Interface** workflow
3. Click: **Run workflow** → **Run workflow**
4. Wait ~1-2 minutes for deployment

---

## 🔧 GitHub Pages Setup (First Time)

**If not already enabled:**

1. **Repository Settings**:
   ```
   Repository → Settings → Pages
   ```

2. **Source Configuration**:
   - Source: **GitHub Actions** (not "Deploy from branch")
   - This allows our custom workflow to deploy

3. **Verify Deployment**:
   - After first push, check **Actions** tab
   - Workflow "Deploy Web Interface" should run
   - Green checkmark = successful deployment

4. **Get URL**:
   - Settings → Pages shows deployed URL
   - Format: `https://USERNAME.github.io/REPOSITORY/`
   - Example: `https://alvoradozerouno.github.io/ORION-Architekt-AT/`

---

## 🌐 Custom Domain Setup (Optional)

### Step 1: Purchase Domain

Recommended providers:
- **Cloudflare** (€10/year, includes DDoS protection)
- **Namecheap** (€12/year)
- **Google Domains** (€12/year)

Example domains:
- `genesis-at.com` ✅ (recommended)
- `genesis-austria.com`
- `genesis-safety.com`

### Step 2: DNS Configuration

**At your domain provider (e.g., Cloudflare):**

#### For `www.genesis-at.com`:
```
Type: CNAME
Name: www
Target: alvoradozerouno.github.io
Proxy: ✅ (if Cloudflare) or DNS only
TTL: Auto
```

#### For root `genesis-at.com`:
```
Type: A
Name: @
IPv4: 185.199.108.153
TTL: Auto

Type: A
Name: @
IPv4: 185.199.109.153
TTL: Auto

Type: A
Name: @
IPv4: 185.199.110.153
TTL: Auto

Type: A
Name: @
IPv4: 185.199.111.153
TTL: Auto
```

**DNS Propagation**: Wait 5-60 minutes for DNS to propagate worldwide.

### Step 3: GitHub Configuration

1. **Create CNAME file**:
   ```bash
   echo "www.genesis-at.com" > docs/web/CNAME
   git add docs/web/CNAME
   git commit -m "Add custom domain CNAME"
   git push origin main
   ```

2. **GitHub Settings**:
   - Repository → Settings → Pages
   - Custom domain: `www.genesis-at.com`
   - Click **Save**
   - ✅ **Enforce HTTPS** (wait 1-5 minutes for SSL cert)

3. **Verify**:
   - Visit `https://www.genesis-at.com`
   - Should show GENESIS landing page
   - Check SSL padlock in browser

### Step 4: Redirect Root to WWW (Optional)

**Cloudflare Page Rule**:
```
URL: genesis-at.com/*
Forwarding URL: 301 - Permanent Redirect
Destination: https://www.genesis-at.com/$1
```

---

## 🔒 SSL/HTTPS

**GitHub Pages** provides **automatic HTTPS** via Let's Encrypt:

- ✅ **Free SSL certificate**
- ✅ **Auto-renewal** every 90 days
- ✅ **Forced HTTPS** (redirect HTTP → HTTPS)

**Custom domain**: SSL certificate issued automatically when you:
1. Add CNAME file
2. Configure custom domain in Settings → Pages
3. Wait 1-5 minutes for certificate provisioning

**Troubleshooting**:
- If "Enforce HTTPS" is grayed out, wait 5-10 minutes
- DNS must be correctly configured first
- Check DNS propagation: https://dnschecker.org

---

## 📧 Email Form Backend

### Current: FormSubmit (Free)

**Already configured** in `index.html`:

```html
<form action="https://formsubmit.co/esteurer72@gmail.com" method="POST">
```

**Features**:
- ✅ Free forever
- ✅ No backend required
- ✅ Spam protection
- ✅ Email notifications
- ✅ GDPR compliant

**Customization**:
- Change recipient email in form action
- Add `_next` parameter for custom thank-you page
- Add `_subject` parameter for custom email subject

### Future: Custom Backend (Production)

**Option A: AWS Lambda + API Gateway**
```
Cost: ~€1-5/month for 1,000 submissions
Pros: Scalable, serverless, full control
Cons: Requires AWS account, more setup
```

**Option B: Netlify Forms**
```
Cost: Free (100 submissions/month), then €19/month
Pros: Built-in spam filtering, easy setup
Cons: Lock-in to Netlify
```

**Option C: Google Forms + Google Apps Script**
```
Cost: Free
Pros: Familiar, spreadsheet integration
Cons: Not as professional, limited customization
```

---

## 📊 Analytics Setup

### Google Analytics 4 (Recommended)

**Step 1: Create GA4 Property**

1. Go to: https://analytics.google.com
2. Create account (if new)
3. Create property: "GENESIS Website"
4. Get Measurement ID (format: `G-XXXXXXXXXX`)

**Step 2: Add to Website**

Edit `docs/web/index.html` and replace placeholder:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX'); <!-- Replace with your Measurement ID -->
</script>
```

**Step 3: Verify**

1. Visit your website
2. GA4 → Reports → Realtime
3. Should see 1 active user (you)

### Alternative: Plausible Analytics

**Privacy-focused, GDPR-compliant**:
- Cost: €9/month (10k pageviews)
- Pros: No cookies, lightweight, GDPR-friendly
- Cons: Paid only

---

## 🚀 Alternative Hosting Platforms

### Option 1: Vercel (Recommended for Custom Domain)

**Pros**:
- ✅ Faster than GitHub Pages
- ✅ Free SSL
- ✅ Global CDN
- ✅ Automatic previews for PRs
- ✅ Free tier (generous)

**Setup**:
1. Sign up: https://vercel.com
2. Import GitHub repo
3. Set root directory: `docs/web`
4. Deploy → Auto-deploys on push

**Cost**: Free (Hobby tier)

### Option 2: Netlify

**Pros**:
- ✅ Built-in form handling (100/month free)
- ✅ Free SSL
- ✅ Global CDN
- ✅ Split testing A/B

**Setup**:
1. Sign up: https://netlify.com
2. Import GitHub repo
3. Build command: (none)
4. Publish directory: `docs/web`

**Cost**: Free (Starter tier)

### Option 3: Cloudflare Pages

**Pros**:
- ✅ Fastest CDN globally
- ✅ Unlimited bandwidth (free)
- ✅ Free SSL
- ✅ DDoS protection

**Setup**:
1. Sign up: https://pages.cloudflare.com
2. Connect GitHub
3. Build settings: None (static)
4. Output: `docs/web`

**Cost**: Free (unlimited)

---

## 📁 File Structure (Production)

```
docs/web/
├── index.html              # Main landing page ✅
├── CNAME                   # Custom domain (optional)
├── favicon.ico             # Browser icon (TODO)
├── robots.txt              # SEO crawler instructions (TODO)
├── sitemap.xml             # SEO sitemap (TODO)
├── .well-known/            # Security & verification (optional)
│   └── security.txt        # Security contact info
├── images/                 # Future: logos, screenshots
│   ├── logo.svg
│   ├── hero-bg.jpg
│   └── feature-*.png
└── README.md               # This guide ✅
```

---

## ✅ Pre-Launch Checklist

### Content & Functionality
- [x] Landing page HTML created
- [ ] Update FormSubmit email to production email
- [ ] Add Google Analytics Measurement ID
- [ ] Add favicon.ico
- [ ] Add Open Graph meta tags (social sharing)
- [ ] Test demo form submission
- [ ] Test all navigation links
- [ ] Proofread all copy

### Performance & SEO
- [ ] Run Google PageSpeed Insights
- [ ] Add robots.txt
- [ ] Add sitemap.xml
- [ ] Test mobile responsiveness
- [ ] Test cross-browser (Chrome, Firefox, Safari, Edge)
- [ ] Optimize images (if added)
- [ ] Add meta description for SEO

### Security & Compliance
- [ ] HTTPS enforced (automatic with GitHub Pages)
- [ ] Add security.txt (optional)
- [ ] Review GDPR compliance (FormSubmit is compliant)
- [ ] Add privacy policy link (if collecting emails)
- [ ] Add cookie consent banner (if using GA)

### GitHub Configuration
- [x] GitHub Pages enabled
- [x] Deployment workflow created
- [ ] Repository description updated
- [ ] Repository topics added (see .github/GITHUB_TOPICS.md)
- [ ] Social preview image uploaded (1280x640px)
- [ ] Website URL added to About section

### Marketing & Launch
- [ ] LinkedIn announcement drafted
- [ ] GitHub Discussions announcement
- [ ] Email to pilot customers (use ZIVILTECHNIKER_EMAILS.md)
- [ ] Submit to Product Hunt (optional)
- [ ] Submit to Hacker News Show HN (optional)

---

## 🔄 Deployment Workflow

**Current automated workflow** (.github/workflows/deploy-web.yml):

```yaml
Trigger: Push to main (docs/web/** changes) OR manual dispatch
↓
Checkout repository
↓
Setup GitHub Pages
↓
Upload docs/web/ as artifact
↓
Deploy to GitHub Pages
↓
Live in ~1-2 minutes ✅
```

**Manual deployment**:
```bash
# Method 1: Via GitHub Actions UI
Actions → Deploy Web Interface → Run workflow

# Method 2: Via gh CLI
gh workflow run deploy-web.yml

# Method 3: Push changes
git add docs/web/
git commit -m "Update website"
git push
```

---

## 📈 Monitoring & Maintenance

### Health Checks

**Uptime Monitoring** (Free):
- **UptimeRobot**: https://uptimerobot.com (Free, 50 monitors)
- **Pingdom**: https://pingdom.com (Free trial)
- **StatusCake**: https://statuscake.com (Free tier)

**Setup**:
1. Create account
2. Add monitor: `https://alvoradozerouno.github.io/ORION-Architekt-AT/`
3. Alert email: `esteurer72@gmail.com`
4. Check interval: 5 minutes

### Analytics Review

**Weekly**:
- Check visitor count
- Review top pages
- Check form submissions
- Review traffic sources

**Monthly**:
- Analyze user behavior
- A/B test improvements
- Update content based on data
- Review bounce rate

---

## 🆘 Troubleshooting

### Deployment Fails

**Check**:
1. GitHub Actions → View logs
2. Ensure `docs/web/index.html` exists
3. Verify workflow file syntax
4. Check repository permissions (Settings → Actions → General)

**Fix**:
```bash
# Re-trigger deployment
git commit --allow-empty -m "Trigger deployment"
git push
```

### Custom Domain Not Working

**Check**:
1. DNS propagation: https://dnschecker.org
2. CNAME file exists: `docs/web/CNAME`
3. GitHub Settings → Pages shows custom domain
4. Wait 5-60 minutes after DNS changes

**Fix**:
```bash
# Verify DNS
dig www.genesis-at.com
# Should show CNAME to alvoradozerouno.github.io

# Or
nslookup www.genesis-at.com
```

### HTTPS Not Enforcing

**Check**:
1. DNS correctly configured (must point to GitHub)
2. CNAME file contains correct domain
3. Wait 1-5 minutes after adding custom domain

**Fix**:
- Remove custom domain in GitHub Settings → Pages
- Wait 1 minute
- Re-add custom domain
- Wait for SSL provisioning (~5 minutes)

### Form Not Submitting

**Check**:
1. FormSubmit email verified (check spam folder for verification)
2. Form action URL correct
3. Form method is `POST`
4. Browser console for JavaScript errors

**Fix**:
```html
<!-- Verify form structure -->
<form action="https://formsubmit.co/YOUR_EMAIL" method="POST">
  <input type="email" name="email" required>
  <button type="submit">Submit</button>
</form>
```

---

## 📞 Support & Resources

**Documentation**:
- GitHub Pages: https://docs.github.com/pages
- Custom Domains: https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site
- FormSubmit: https://formsubmit.co/documentation

**Questions**:
- Email: esteurer72@gmail.com
- GitHub Issues: https://github.com/Alvoradozerouno/ORION-Architekt-AT/issues

**Community**:
- GitHub Discussions: (Enable in Settings → Features)
- Stack Overflow: Tag with `github-pages`

---

## 🎉 Success Metrics

**30 Days**:
- 500+ unique visitors
- 50+ demo form submissions
- 10+ GitHub stars from website traffic
- 5+ pilot customer conversions

**90 Days**:
- 2,000+ unique visitors
- 200+ demo requests
- 50+ GitHub stars
- 20+ active pilot customers

**Track with**:
- Google Analytics (visitors, sessions, bounce rate)
- FormSubmit (form submissions)
- GitHub Insights (traffic, referrers)

---

**Deployment prepared and ready for launch! 🚀**
