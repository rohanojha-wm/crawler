# GitHub Actions Security and Permissions

This document explains the security configuration and permissions used in the URL monitoring workflows.

## 🔒 **Security Principles**

### **Principle of Least Privilege**
Each workflow is granted only the minimum permissions required to function properly. This reduces the attack surface and limits potential damage if a workflow is compromised.

### **Explicit Permissions**
Rather than relying on default permissions (which can be overly broad), we explicitly declare exactly what each workflow needs.

## 🛡️ **Permission Breakdown by Workflow**

### **Standard Monitoring Workflow** (`url-monitor.yml`)

```yaml
permissions:
  contents: read      # To checkout repository
  actions: read       # To download artifacts
  pages: write        # To deploy to GitHub Pages
  id-token: write     # For GitHub Pages deployment
  issues: write       # To create issues on monitoring failures
```

**Why each permission is needed:**
- `contents: read` - Required to access repository files and checkout code
- `actions: read` - Needed to download previous monitoring artifacts
- `pages: write` - Required to deploy monitoring reports to GitHub Pages
- `id-token: write` - Required for secure GitHub Pages deployment with OIDC
- `issues: write` - Allows creation of GitHub issues when monitoring failures occur

### **Artifact-Based Persistent Workflow** (`url-monitor-persistent.yml`)

```yaml
permissions:
  contents: read      # To checkout repository
  actions: write      # To upload/download artifacts (database persistence)
  pages: write        # To deploy to GitHub Pages
  id-token: write     # For GitHub Pages deployment
  issues: write       # To create issues on monitoring failures
```

**Additional permissions:**
- `actions: write` - Required to upload the persistent database as artifacts for future runs

### **Git-Based Persistent Workflow** (`url-monitor-git-persistence.yml`)

```yaml
permissions:
  contents: write     # To checkout repository AND commit database changes
  actions: write      # To upload/download artifacts
  pages: write        # To deploy to GitHub Pages
  id-token: write     # For GitHub Pages deployment
  issues: write       # To create issues on monitoring failures
```

**Additional permissions:**
- `contents: write` - Required to commit the updated database back to the repository

### **Test Workflow** (`test-monitor.yml`)

```yaml
permissions:
  contents: read      # To checkout repository
  actions: write      # To upload test artifacts
```

**Minimal permissions for testing:**
- Only needs to read code and upload test results

## 🚨 **Security Risks Mitigated**

### **Without Explicit Permissions:**
- ❌ Workflows might have excessive access to repository contents
- ❌ Could potentially access or modify sensitive repository settings
- ❌ Might have broader access to GitHub APIs than necessary
- ❌ Harder to audit what each workflow actually does

### **With Explicit Permissions:**
- ✅ **Least Privilege**: Each workflow has only what it needs
- ✅ **Clear Audit Trail**: Permissions are visible and documented
- ✅ **Reduced Attack Surface**: Limited potential for abuse
- ✅ **Compliance**: Meets security best practices

## 🔍 **Permission Descriptions**

### **Read Permissions:**
| Permission | Description | Risk Level |
|------------|-------------|------------|
| `contents: read` | Access to repository files | 🟢 Low |
| `actions: read` | Read workflow runs and artifacts | 🟢 Low |
| `metadata: read` | Read repository metadata | 🟢 Low |

### **Write Permissions:**
| Permission | Description | Risk Level |
|------------|-------------|------------|
| `contents: write` | Modify repository files | 🟡 Medium |
| `actions: write` | Create/modify artifacts | 🟡 Medium |
| `pages: write` | Deploy to GitHub Pages | 🟡 Medium |
| `issues: write` | Create/modify issues | 🟡 Medium |
| `id-token: write` | OIDC token generation | 🟡 Medium |

### **Admin Permissions (NOT USED):**
| Permission | Description | Risk Level |
|------------|-------------|------------|
| `administration: write` | Repository admin access | 🔴 High |
| `security-events: write` | Security alerts | 🔴 High |
| `pull-requests: write` | Modify pull requests | 🟠 Medium-High |

## 🛠️ **Implementation Details**

### **GitHub Pages Security:**
```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}  # Uses scoped token
    publish_dir: ./monitoring-results
    destination_dir: reports
```

The `GITHUB_TOKEN` is automatically scoped to the declared permissions.

### **Issue Creation Security:**
```yaml
- name: Create Issue on Failures
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        # Only creates issues, cannot modify repository
      })
```

Limited to issue creation only, cannot access other repository functions.

### **Artifact Security:**
```yaml
- name: Upload database
  uses: actions/upload-artifact@v3
  with:
    name: monitoring-database
    retention-days: 90  # Automatic cleanup
```

Artifacts are scoped to the repository and have automatic retention limits.

## 🔐 **Token Security**

### **Automatic Token Scoping:**
GitHub automatically creates a scoped `GITHUB_TOKEN` for each workflow run with exactly the permissions declared in the workflow file.

### **Secret Management:**
```yaml
env:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}  # Optional external service
```

External secrets (like Slack webhooks) are optional and use GitHub's secure secret storage.

## 📋 **Security Checklist**

Before deploying workflows, verify:

- [ ] ✅ **Explicit permissions declared** in all workflow files
- [ ] ✅ **Minimum required permissions** only
- [ ] ✅ **No admin permissions** unless absolutely necessary
- [ ] ✅ **External secrets** are optional and documented
- [ ] ✅ **Artifact retention** limits are set
- [ ] ✅ **Token scoping** is understood and documented

## 🚀 **Deployment Security**

### **Repository Settings:**
1. **Actions permissions**: Set to "Allow select actions and reusable workflows"
2. **Workflow permissions**: Set to "Read repository contents and packages permissions"
3. **Allow GitHub Actions to create and approve pull requests**: Disabled (not needed)

### **Branch Protection:**
Consider enabling branch protection rules:
- Require pull request reviews
- Require status checks to pass
- Restrict pushes to main branch

## 🔄 **Regular Security Review**

### **Monthly Review:**
- [ ] Review workflow permissions are still minimal
- [ ] Check for unused workflows or permissions
- [ ] Audit artifact retention and cleanup
- [ ] Review external integrations (Slack, etc.)

### **After Changes:**
- [ ] Verify new workflows have explicit permissions
- [ ] Test workflows work with minimal permissions
- [ ] Document any new permission requirements

## 🆘 **Security Incident Response**

### **If Workflow is Compromised:**
1. **Disable the workflow** immediately in GitHub settings
2. **Revoke any external tokens** (Slack webhooks, etc.)
3. **Review audit logs** for unauthorized actions
4. **Update permissions** to be even more restrictive
5. **Re-enable** only after security review

### **Contact Information:**
- GitHub Security: https://github.security
- Repository maintainer: [Your contact info]

## 📚 **Additional Resources**

- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Automatic token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Permissions for the GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)

---

**Security is everyone's responsibility!** 🛡️

Regular security reviews and following the principle of least privilege keep our monitoring system secure while maintaining full functionality.
