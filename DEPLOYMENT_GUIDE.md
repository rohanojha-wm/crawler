# 🚀 Complete Deployment Guide

This guide walks you through deploying your URL monitoring system to GitHub with a clean database and enabling the persistent dashboard.

## 📋 **Prerequisites**

- ✅ Git installed and configured
- ✅ GitHub account with repository created
- ✅ Local monitoring system working (Flask app running)

## 🧹 **Step 1: Clean the Database**

Your current database has accumulated test data. Let's clean it before deployment:

```bash
# Run the interactive cleanup tool
python clean_database.py
```

**Choose Option 1** (recommended): Keeps your URL configurations but removes historical ping data.

### **What gets cleaned:**
- ❌ **Removed**: All ping results and historical data (~90KB → ~4KB)
- ✅ **Preserved**: Your URL configurations (urls.csv will be the source of truth)
- ✅ **Preserved**: Database schema and structure

## 📦 **Step 2: Choose Your Persistence Strategy**

You have **3 options** for database persistence:

### **Option A: Artifact-Based Persistence** ⭐ **RECOMMENDED**
- **Retention**: 90 days
- **Repository Impact**: None
- **Best for**: Most users

### **Option B: Git-Based Persistence**  
- **Retention**: Forever
- **Repository Impact**: Database grows in git history
- **Best for**: Long-term historical analysis

### **Option C: No Persistence** (Current)
- **Retention**: Current run only
- **Repository Impact**: None
- **Best for**: Simple alerting only

## 🚀 **Step 3: Deploy to GitHub**

### **3.1 Initialize Git Repository (if not done)**

```bash
# Initialize git if this isn't already a git repository
git init

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### **3.2 Choose and Configure Workflow**

#### **For Artifact-Based Persistence (RECOMMENDED):**

```bash
# Copy the persistent workflow over the current one
cp .github/workflows/url-monitor-persistent.yml .github/workflows/url-monitor.yml

# Remove the git-based workflow (not needed)
rm .github/workflows/url-monitor-git-persistence.yml
```

#### **For Git-Based Persistence:**

```bash
# Copy the git-based workflow over the current one
cp .github/workflows/url-monitor-git-persistence.yml .github/workflows/url-monitor.yml

# Remove the artifact-based workflow (not needed)
rm .github/workflows/url-monitor-persistent.yml
```

#### **For No Persistence (current setup):**

```bash
# Keep the current workflow as-is
# .github/workflows/url-monitor.yml is already configured
```

### **3.3 Add Files to Git**

```bash
# Add all project files
git add .

# Check what's being added
git status

# Should include:
# - All Python files (app.py, ci_monitor*.py, etc.)
# - All templates and static files
# - GitHub workflows (.github/workflows/)
# - Requirements and documentation
# - Clean database (monitoring.db - small after cleanup)
# - CSV file with your URLs
```

### **3.4 Commit and Push**

```bash
# Commit everything
git commit -m "🚀 Initial URL monitoring system deployment

- Flask dashboard with card-based drill-down UI
- Hierarchical group/country organization  
- Persistent database monitoring (artifact-based)
- GitHub Actions workflows with proper permissions
- Country-code cookie support
- Failed request tracking and analysis
- Read-only production interface
- Comprehensive security configuration"

# Push to GitHub
git push -u origin main
```

## ⚙️ **Step 4: Configure GitHub Repository**

### **4.1 Enable GitHub Pages**

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Source: Select **"GitHub Actions"**
4. This allows workflows to deploy reports to GitHub Pages

### **4.2 Set Up Secrets (Optional)**

For Slack notifications, add secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add: `SLACK_WEBHOOK_URL` (if you want Slack notifications)

### **4.3 Verify Workflow Permissions**

Your workflows already have proper permissions configured:
- ✅ Contents: read/write (as needed)
- ✅ Actions: read/write (for artifacts)
- ✅ Pages: write (for dashboard deployment)
- ✅ Issues: write (for failure alerts)

## 🔄 **Step 5: First Run and Verification**

### **5.1 Trigger First Workflow**

```bash
# Option 1: Manual trigger via GitHub UI
# Go to Actions tab → Select workflow → "Run workflow"

# Option 2: Push a small change to trigger
echo "# URL Monitoring System" > README_STATUS.md
git add README_STATUS.md
git commit -m "Trigger initial monitoring run"
git push
```

### **5.2 Monitor First Run**

1. Go to **Actions** tab in your GitHub repository
2. Watch the workflow run
3. First run should:
   - ✅ Create new database (if using persistent mode)
   - ✅ Monitor your URLs from urls.csv
   - ✅ Generate reports
   - ✅ Deploy to GitHub Pages
   - ✅ Upload artifacts (if using artifact mode)

### **5.3 Verify Dashboard Access**

After successful deployment:

- **GitHub Pages**: `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/reports/`
- **Artifacts**: Go to Actions → Select run → Download artifacts

## 📊 **Step 6: Ongoing Management**

### **6.1 Adding/Modifying URLs**

```bash
# Edit your CSV file
nano urls.csv

# Add your URLs in format:
# url,group_name,countryCode
# https://your-site.com,Production,US

# Commit and push
git add urls.csv
git commit -m "Add new URLs for monitoring"
git push

# Workflow will automatically run and start monitoring new URLs
```

### **6.2 Monitoring Health**

- **Scheduled Runs**: Every 30 minutes automatically
- **Manual Runs**: Actions tab → "Run workflow"
- **Failure Alerts**: Automatic GitHub issues created
- **Dashboard**: Updated with each run

### **6.3 Database Growth (Persistent Modes)**

#### **Artifact-Based:**
- Database grows ~1-2KB per run
- 90-day retention (automatic cleanup)
- Estimate: ~2MB total for 30 days

#### **Git-Based:**
- Database committed to repository
- Grows repository size permanently
- Monitor with: `git ls-files -s monitoring.db`

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **"No URLs loaded" Error:**
```bash
# Check your CSV format
head -5 urls.csv

# Should show:
# url,group_name,countryCode
# https://example.com,Production,US
```

#### **Workflow Permission Errors:**
- Verify GitHub Pages is enabled
- Check workflow permissions in repository settings

#### **Database Too Large:**
```bash
# Clean and recommit
python clean_database.py
git add monitoring.db
git commit -m "Clean database for deployment"
git push
```

#### **Artifact Not Found (2nd run):**
- First run creates the artifact
- Second run downloads it
- This is normal behavior

## 📈 **Success Indicators**

After deployment, you should see:

✅ **GitHub Actions**: Green checkmarks for workflow runs
✅ **GitHub Pages**: Dashboard accessible at your Pages URL  
✅ **Artifacts**: Database artifacts uploaded (if using artifact mode)
✅ **Issues**: Automatic issue creation on failures (if any)
✅ **Monitoring**: URLs being pinged every 30 minutes
✅ **Historical Data**: Persistent data accumulating over time

## 🎉 **You're Live!**

Your URL monitoring system is now:

- 🌐 **Deployed to GitHub** with automatic workflows
- 📊 **Dashboard accessible** via GitHub Pages
- 💾 **Persistent data** accumulating between runs
- 🔔 **Automatic alerting** via GitHub issues
- 🔒 **Securely configured** with minimal permissions
- 🌍 **Geographic monitoring** with country-specific cookies
- 📱 **Mobile-friendly** responsive interface

## 📞 **Need Help?**

Check the workflow logs in the Actions tab for detailed information about each step. All workflows include comprehensive logging for troubleshooting.

---

**Ready to monitor your URLs with enterprise-grade reliability!** 🚀
