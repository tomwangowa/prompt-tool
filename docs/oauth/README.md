# Google OAuth Verification Documentation

This directory contains all documents required for Google OAuth consent screen verification (Phase -1).

---

## 📋 Document Index

| Document | Purpose | Status |
|----------|---------|--------|
| `google-oauth-verification-application.md` | Complete verification application with questionnaire answers | ✅ Ready |
| `privacy-policy.md` | Privacy policy template (must publish to website) | ✅ Ready |
| `submission-checklist.md` | Step-by-step submission checklist | ✅ Ready |
| `README.md` | This overview document | ✅ Ready |

---

## 🎯 Quick Start

### For Engineering Lead

**Week -2 (Immediate Actions)**:

1. **Review Application Document** (30 min)
   - Read `google-oauth-verification-application.md`
   - Customize with your organization details (marked with `[Your ...]`)
   - Fill in domain names, email addresses

2. **Publish Privacy Policy** (1 hour)
   - Use template from `privacy-policy.md`
   - Customize with your details
   - Publish to `https://[your-domain].com/privacy`
   - Verify it's publicly accessible

3. **Configure Google Cloud** (2-3 hours)
   - Follow steps in `submission-checklist.md` Phase 1
   - Create OAuth 2.0 Client ID
   - Configure consent screen
   - Test OAuth flow locally

4. **Create Media** (3-4 hours)
   - Record demo video (2-3 minutes)
   - Take 5 screenshots
   - Upload video to YouTube (unlisted) or Google Drive

5. **Submit for Verification** (1 hour)
   - Complete questionnaire using prepared answers
   - Upload video and screenshots
   - Submit application

**Total Time**: 10-15 hours spread over 2-3 days

---

## 📊 Submission Timeline

```
Week -2
├── Day 1-2: Preparation (domain, privacy policy, Google Cloud setup)
├── Day 3: Test OAuth flow
├── Day 4: Record demo video
├── Day 5: Take screenshots
└── Day 6: Submit verification

Week -1 to Week 0: Monitor verification status
└── Expected: Approval within 1-2 weeks

Week 1: Proceed to Phase 1 (Internal Alpha)
```

---

## ✅ Pre-Submission Checklist

Use `submission-checklist.md` for detailed steps. Quick check:

**Must Have (Blocking)**:
- [ ] Privacy policy published and accessible
- [ ] Domain verified in Google Search Console
- [ ] OAuth 2.0 Client ID created
- [ ] OAuth consent screen configured (all fields)
- [ ] Scopes added: `drive.file`, `userinfo.email`
- [ ] OAuth flow tested successfully
- [ ] Demo video recorded and uploaded
- [ ] 5 screenshots prepared

**Nice to Have**:
- [ ] Terms of service published
- [ ] App logo (120x120px)
- [ ] `userinfo.profile` scope (optional)

---

## 🎬 Demo Video Requirements

**Duration**: 2-3 minutes
**Resolution**: 1920x1080 (1080p minimum)
**Format**: MP4 (H.264 codec)

**Must Show**:
1. OAuth consent screen with app name and scopes
2. User clicking "Allow" button
3. Redirect back to app
4. Signed in status ("Signed in as...")
5. Sync to Google Drive
6. Verification in Drive web UI (folder and files visible)

**Script**: See Section 7 in `google-oauth-verification-application.md`

---

## 📸 Screenshot Requirements

**Quantity**: 5 screenshots minimum
**Size**: 1280x720 minimum
**Format**: PNG or JPG

**Required Screenshots**:
1. OAuth consent screen
2. Signed in status in app
3. Initial sync dialog
4. Google Drive folder with files
5. Sync status indicator

**Quality Standards**:
- Clear and readable
- No personal information (use demo@example.com)
- Professional appearance
- Consistent UI theme

---

## 🔧 Environment Variables

After creating OAuth 2.0 Client ID, add to `.env`:

```bash
# Copy from Google Cloud Console → Credentials
GOOGLE_OAUTH_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx

# Match your environment
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501
```

See root `.env.example` for template (updated).

---

## 📞 Support Contacts

**Google Cloud Support**
- Support Cases: https://console.cloud.google.com/support
- Documentation: https://support.google.com/cloud/answer/9110914

**Internal Contacts**
- Engineering Lead: [Name / Email]
- DevOps: [Name / Email]
- Product Manager: [Name / Email]

---

## ⚠️ Important Notes

### OAuth Verification is REQUIRED for:
- ✅ Public beta testing (Week 2+)
- ✅ General availability (Week 14+)
- ✅ Enterprise adoption (IT departments require verified apps)
- ✅ Removing "unverified app" warning

### Unverified App is ACCEPTABLE for:
- ✅ Internal alpha testing (Week 1)
- ✅ Development and testing
- ✅ Personal use with your own Google account

### Privacy Policy is MANDATORY
- Google will NOT verify apps without a publicly accessible privacy policy
- Must be accessible without login
- Must cover all data collection and usage
- Use template from `privacy-policy.md` and customize

### Domain Verification is REQUIRED
- Verify domain in Google Search Console BEFORE submission
- Add TXT record to DNS
- Verification can take 24-48 hours

---

## 🚀 Next Steps After Approval

1. **Receive Approval Email**
   - Verify "Approved" status in Google Cloud Console
   - Test OAuth flow (should show NO warning)

2. **Update Team**
   - Announce approval to team
   - Update project timeline

3. **Proceed to Phase 0**
   - Complete infrastructure setup (Week 0)
   - Prepare for Phase 1 (Internal Alpha, Week 1)

4. **Archive Approval**
   - Save approval email
   - Document case ID
   - Update spec document status

---

## 📚 Additional Resources

**Google Documentation**
- OAuth 2.0 Overview: https://developers.google.com/identity/protocols/oauth2
- OAuth Verification Guide: https://support.google.com/cloud/answer/9110914
- Drive API Quickstart: https://developers.google.com/drive/api/quickstart/python

**Prompt Tool Specs**
- Main Spec: `../spec/google-drive-sync-spec.md` (v1.1)
- Spec Review: `../spec/google-drive-sync-spec-review-v1.1.md`

**Configuration**
- App Config: `../../config/config.yaml`
- Environment Variables: `../../.env.example`

---

**Document Status**: ✅ Complete and Ready
**Last Updated**: 2026-01-12
**Owner**: Engineering Lead

**Action Required**: Begin submission process in Week -2!
