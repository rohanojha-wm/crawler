# Database Persistence Options for GitHub Actions

This document explains how to implement persistent SQLite database storage in GitHub Actions to maintain historical monitoring data between workflow runs.

## 🎯 **Why Persistent Database?**

### **Current Limitations (Stateless):**
- ❌ No historical data between runs
- ❌ No trending analysis 
- ❌ No long-term performance insights
- ❌ Each run starts fresh

### **Benefits of Persistent Database:**
- ✅ **Historical Analytics**: Trend analysis over weeks/months
- ✅ **Rich Dashboard**: Same data as local Flask app
- ✅ **Performance Tracking**: Response time trends
- ✅ **Reliability Metrics**: Long-term success rates
- ✅ **Drill-Down Capability**: Group → Country → Individual requests

## 🔧 **Implementation Options**

### **Option 1: Artifact-Based Persistence** ⭐ **RECOMMENDED**

**Files:**
- `.github/workflows/url-monitor-persistent.yml`
- `ci_monitor_persistent.py` 
- `generate_historical_report.py`

**How it works:**
```
Run #1: Create new database → Save as artifact
Run #2: Download artifact → Update database → Save updated artifact  
Run #3: Download artifact → Update database → Save updated artifact
```

**Pros:**
- ✅ Simple implementation
- ✅ No repository bloat
- ✅ Fast downloads (artifacts are cached)
- ✅ Automatic cleanup after 90 days
- ✅ No git conflicts

**Cons:**
- ⚠️ 90-day maximum retention
- ⚠️ Lost if artifacts are manually deleted

**Setup:**
```bash
# Replace existing workflow
cp .github/workflows/url-monitor-persistent.yml .github/workflows/url-monitor.yml

# The scripts will automatically handle database persistence
git add .
git commit -m "Enable persistent database monitoring"
git push
```

### **Option 2: Git Repository Persistence**

**Files:**
- `.github/workflows/url-monitor-git-persistence.yml`
- `ci_monitor_persistent.py`
- `generate_historical_report.py`

**How it works:**
```
Run #1: Create database → Commit to repository
Run #2: Pull latest → Update database → Commit changes
Run #3: Pull latest → Update database → Commit changes
```

**Pros:**
- ✅ Permanent persistence (never expires)
- ✅ Version controlled database history
- ✅ Always available with repository
- ✅ Can track database changes over time

**Cons:**
- ⚠️ Repository size grows over time
- ⚠️ Binary files not ideal for git
- ⚠️ Potential merge conflicts
- ⚠️ Every run creates a commit

**Setup:**
```bash
# Use git-based workflow
cp .github/workflows/url-monitor-git-persistence.yml .github/workflows/url-monitor.yml

# Add database to gitignore initially (will be managed by workflow)
echo "monitoring.db" >> .gitignore

git add .
git commit -m "Enable git-persistent database monitoring"
git push
```

### **Option 3: External Database** (Advanced)

**Services:**
- AWS RDS (PostgreSQL/MySQL)
- Google Cloud SQL  
- Azure SQL Database
- PlanetScale (MySQL)
- Supabase (PostgreSQL)

**How it works:**
```
Run #1: Connect to cloud database → Insert results
Run #2: Connect to cloud database → Insert results  
Run #3: Connect to cloud database → Insert results
```

**Pros:**
- ✅ Professional database hosting
- ✅ Unlimited retention
- ✅ Advanced querying capabilities
- ✅ Scalable and reliable
- ✅ No repository impact

**Cons:**
- ⚠️ Monthly costs ($5-50+)
- ⚠️ Complex setup
- ⚠️ Requires credentials management
- ⚠️ Network dependencies

## 📊 **Comparison Matrix**

| Feature | Artifacts | Git Repo | External DB |
|---------|-----------|----------|-------------|
| **Setup Complexity** | 🟢 Simple | 🟡 Medium | 🔴 Complex |
| **Cost** | 🟢 Free | 🟢 Free | 🔴 $5-50/month |
| **Retention** | 🟡 90 days | 🟢 Forever | 🟢 Forever |
| **Repository Impact** | 🟢 None | 🔴 Grows over time | 🟢 None |
| **Reliability** | 🟡 Good | 🟢 Excellent | 🟢 Excellent |
| **Performance** | 🟢 Fast | 🟡 Medium | 🟡 Network dependent |
| **Data Portability** | 🟡 GitHub only | 🟢 With repo | 🟡 Service dependent |

## 🚀 **Quick Implementation Guide**

### **Step 1: Choose Your Approach**

**For most users:** Use **Artifact-Based Persistence** (Option 1)

### **Step 2: Install Files**

The following files are already created for you:
- ✅ `ci_monitor_persistent.py` - Uses same database schema as Flask app
- ✅ `generate_historical_report.py` - Creates rich historical reports
- ✅ `url-monitor-persistent.yml` - Artifact-based workflow
- ✅ `url-monitor-git-persistence.yml` - Git-based workflow

### **Step 3: Enable Persistent Monitoring**

```bash
# Option 1: Artifact-based (RECOMMENDED)
cp .github/workflows/url-monitor-persistent.yml .github/workflows/url-monitor.yml

# Option 2: Git-based  
cp .github/workflows/url-monitor-git-persistence.yml .github/workflows/url-monitor.yml

# Commit and push
git add .
git commit -m "🚀 Enable persistent database monitoring"
git push
```

### **Step 4: Verify It's Working**

1. **Check Workflow Runs**: Go to your repository → Actions tab
2. **Look for Database Messages**: Logs should show "Found existing database" after first run
3. **View Enhanced Reports**: GitHub Pages will show historical data
4. **Check Artifacts**: Artifacts section should contain `monitoring-database`

## 📈 **What You Get with Persistent Database**

### **Enhanced GitHub Pages Reports:**
- 📊 **Historical Trends**: 1h, 3h, 1d, 7d, 30d comparisons
- 📈 **Group Statistics**: Success rates by group over time
- 🌍 **Country Analysis**: Performance by geographic region
- 📉 **Failure Tracking**: Detailed failure history and patterns

### **Rich Data Analysis:**
```sql
-- Examples of what becomes possible:
SELECT AVG(success_rate) FROM daily_stats WHERE group_name = 'Production';
SELECT response_time_trend FROM weekly_analysis WHERE country_code = 'US';
SELECT failure_patterns FROM historical_failures WHERE url LIKE '%api%';
```

### **Professional Monitoring:**
- 🔄 **Continuous History**: Never lose monitoring data
- 📊 **Business Intelligence**: Long-term trend analysis
- 🚨 **Smart Alerting**: Context-aware failure detection
- 📈 **Performance Insights**: Response time optimization

## 🔍 **Monitoring Database Growth**

### **Artifact Method:**
```bash
# Database size is shown in workflow logs
# Typical growth: ~1-2KB per monitoring run
# 30-day estimate: ~1-2MB for 15 URLs monitored every 30 minutes
```

### **Git Method:**
```bash
# Check repository size impact
git ls-files -s monitoring.db

# Monitor growth over time
git log --oneline --grep="Update monitoring database"
```

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **"No database found" on second run:**
```bash
# Check artifact retention in workflow
retention-days: 90  # Make sure this is set

# Verify artifact upload/download steps
- name: Upload updated database
- name: Download previous database
```

#### **Database corruption:**
```bash
# Manual reset (will lose historical data)
# Delete the artifact in GitHub UI or wait for natural expiration
```

#### **Repository too large (Git method):**
```bash
# Switch to artifact method
cp .github/workflows/url-monitor-persistent.yml .github/workflows/url-monitor.yml

# Remove database from git
git rm monitoring.db
git commit -m "Switch to artifact-based persistence"
```

## 🎉 **Success Metrics**

After implementing persistent database, you should see:

✅ **"Found existing database"** in workflow logs (after first run)
✅ **Historical data** in GitHub Pages reports  
✅ **Trend charts** showing data over multiple time periods
✅ **Database artifacts** or **commits** (depending on method chosen)
✅ **Enhanced failure analysis** with historical context

## 🔄 **Migration Path**

### **From Stateless to Persistent:**
1. Keep existing workflow running
2. Deploy persistent workflow alongside
3. Verify persistent workflow works
4. Replace original workflow
5. Remove old stateless files

### **Between Persistence Methods:**
```bash
# Artifact → Git
# Download latest artifact, commit as initial database

# Git → Artifact  
# Extract database from git, upload as initial artifact

# Any → External
# Export SQLite data, import to cloud database
```

Your monitoring system now has enterprise-grade persistence capabilities! 🎉

## 📞 **Need Help?**

Check the workflow logs for detailed information:
- Database size and status
- Artifact upload/download success
- Historical data generation
- Report deployment status
