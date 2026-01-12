# OAuth Verification Submission Checklist

**Target Date**: Week -2 (2 weeks before Phase 1)
**Estimated Time**: 4-6 hours to prepare
**Owner**: Engineering Lead + DevOps

---

## Phase 1: Preparation (Week -2, Day 1-2)

### Domain and Hosting

- [ ] **Domain Verified**
  - Verify domain in Google Search Console
  - Add TXT record to DNS
  - Confirm verification status: ✅ Verified
  - URL: https://search.google.com/search-console

- [ ] **Privacy Policy Published**
  - URL: `https://[your-domain].com/privacy`
  - Content: Use template from `privacy-policy.md`
  - Test accessibility (open in incognito mode)
  - Ensure publicly accessible (no login required)
  - Add link to app footer

- [ ] **Terms of Service Published** (Optional but Recommended)
  - URL: `https://[your-domain].com/terms`
  - Test accessibility
  - Add link to app footer

---

### Google Cloud Console Setup

- [ ] **Create Google Cloud Project**
  - Project Name: `prompt-tool-oauth`
  - Project ID: `prompt-tool-oauth-[random]`
  - Billing: Enable (even if using free tier)
  - Location: https://console.cloud.google.com/

- [ ] **Enable APIs**
  - Google Drive API: Enable
  - Google OAuth2 API: Enable (usually auto-enabled)
  - Google+ API: NOT needed (deprecated)

- [ ] **Create OAuth 2.0 Client ID**
  - Navigate to: APIs & Services → Credentials
  - Click: Create Credentials → OAuth 2.0 Client ID
  - Application type: **Web application**
  - Name: `Prompt Tool Web Client`
  - Authorized JavaScript origins:
    - `http://localhost:8501` (development)
    - `https://[your-staging-domain].com` (staging)
    - `https://[your-domain].com` (production)
  - Authorized redirect URIs:
    - `http://localhost:8501` (development)
    - `https://[your-staging-domain].com` (staging)
    - `https://[your-domain].com` (production)
  - Click: Create
  - **SAVE** Client ID and Client Secret to `.env` file

- [ ] **Configure OAuth Consent Screen**
  - Navigate to: APIs & Services → OAuth consent screen
  - User Type: **External** (for public users)
  - App name: `Prompt Tool - AI Prompt Optimizer`
  - User support email: `support@[your-domain].com`
  - App logo: Upload 120x120px PNG/JPG (from `assets/logo-120x120.png`)
  - Application homepage: `https://[your-domain].com`
  - Application privacy policy: `https://[your-domain].com/privacy`
  - Application terms of service: `https://[your-domain].com/terms` (if available)
  - Authorized domains: `[your-domain].com`
  - Developer contact: `dev@[your-domain].com`
  - Click: Save and Continue

- [ ] **Add OAuth Scopes**
  - Navigate to: OAuth consent screen → Scopes
  - Click: Add or Remove Scopes
  - Select:
    - ✅ `https://www.googleapis.com/auth/drive.file` - "See and download files created with this app"
    - ✅ `https://www.googleapis.com/auth/userinfo.email` - "See your email address"
    - ✅ `https://www.googleapis.com/auth/userinfo.profile` - "See your personal info" (optional)
  - Click: Update
  - Verify scopes appear in list

---

### Testing OAuth Flow

- [ ] **Test in Development Environment**
  - Start app: `streamlit run app.py`
  - Navigate to: http://localhost:8501
  - Click: "Sign in with Google"
  - Verify: OAuth consent screen appears
  - Verify: Shows correct app name and logo
  - Verify: Lists correct scopes
  - Verify: "Unverified app" warning appears (expected)
  - Click: Allow (accept warning)
  - Verify: Redirected back to app
  - Verify: Shows "✅ Signed in as [your-email]"
  - Verify: Can sync prompts to Drive
  - Verify: Folder created in Drive: `/Prompt Tool/prompts/`
  - Verify: Files uploaded to Drive

- [ ] **Test with Multiple Accounts**
  - Test with personal Google account
  - Test with Google Workspace account (if available)
  - Verify both work correctly

- [ ] **Test Token Refresh**
  - Sign in
  - Wait 1 hour (or manually expire token in session)
  - Verify: Token refreshes automatically
  - Verify: No re-authentication required

- [ ] **Test Sign Out**
  - Click: "Sign Out" button
  - Verify: Returns to unauthenticated state
  - Verify: Token revoked (check Google Account permissions)

---

## Phase 2: Media Creation (Week -2, Day 3-4)

### Demo Video Recording

- [ ] **Prepare Recording Environment**
  - Close unnecessary tabs/apps
  - Use incognito mode (clean browser state)
  - Set screen resolution: 1920x1080
  - Test audio (clear, no background noise)
  - Prepare test data (15-20 sample prompts)

- [ ] **Record Video** (Follow script in `google-oauth-verification-application.md`)
  - Duration: 2-3 minutes
  - Content:
    - ✅ Introduction (0:00-0:15)
    - ✅ OAuth consent screen (0:15-0:30)
    - ✅ Sign in flow (0:30-1:00)
    - ✅ Initial sync (1:00-1:30)
    - ✅ Verify in Google Drive (1:30-2:00)
    - ✅ Cross-device sync demo (2:00-2:30) (optional)
    - ✅ Conclusion (2:30-3:00)
  - Recording tool: Loom / OBS Studio / QuickTime

- [ ] **Edit Video** (If Needed)
  - Trim unnecessary parts
  - Add captions (optional but helpful)
  - Export as MP4 (H.264 codec)
  - Check file size < 100MB

- [ ] **Upload Video**
  - Option A: YouTube (unlisted)
    - Upload to YouTube
    - Set visibility: **Unlisted**
    - Copy video URL
  - Option B: Google Drive
    - Upload to your Drive
    - Set sharing: **Anyone with link can view**
    - Copy shareable link
  - Test: Open link in incognito mode to verify accessibility

---

### Screenshots

- [ ] **Screenshot 1: OAuth Consent Screen**
  - File: `screenshots/1-oauth-consent-screen.png`
  - Content: Google's consent screen with app name, scopes, "Allow" button
  - Size: 1280x720 minimum
  - Format: PNG

- [ ] **Screenshot 2: Signed In Status**
  - File: `screenshots/2-signed-in-status.png`
  - Content: App showing "✅ Signed in as demo@example.com"
  - Size: 1280x720 minimum
  - Format: PNG

- [ ] **Screenshot 3: Initial Sync Dialog**
  - File: `screenshots/3-initial-sync-prompt.png`
  - Content: "Sync your prompts?" dialog
  - Size: 1280x720 minimum
  - Format: PNG

- [ ] **Screenshot 4: Google Drive Folder**
  - File: `screenshots/4-drive-folder-structure.png`
  - Content: Drive web UI showing `/Prompt Tool/prompts/` folder with JSON files
  - Size: 1280x720 minimum
  - Format: PNG

- [ ] **Screenshot 5: Sync Status**
  - File: `screenshots/5-sync-status-indicator.png`
  - Content: App showing sync status ("Synced", "Syncing", "Offline")
  - Size: 1280x720 minimum
  - Format: PNG

- [ ] **Quality Check**
  - All screenshots clear and readable
  - No personal info visible (use demo@example.com)
  - Consistent UI theme
  - Professional appearance

---

## Phase 3: Verification Questionnaire (Week -2, Day 5)

- [ ] **Prepare Questionnaire Answers**
  - Use answers from `google-oauth-verification-application.md` Section 2
  - Customize with your specific details:
    - [ ] Organization name
    - [ ] Contact email addresses
    - [ ] Domain names
    - [ ] User base estimate
  - Review for accuracy and completeness

- [ ] **Review Application Description**
  - Use description from Section 3
  - Ensure it clearly explains:
    - [ ] What the app does
    - [ ] Why it needs Drive access
    - [ ] How it uses the `drive.file` scope
    - [ ] User benefits

---

## Phase 4: Submission (Week -2, Day 6)

### Pre-Flight Check

- [ ] **Final Verification**
  - [ ] Privacy policy URL is live and accessible
  - [ ] Domain is verified in Google Search Console
  - [ ] OAuth consent screen is complete (no missing fields)
  - [ ] All scopes are added correctly
  - [ ] OAuth flow tested successfully
  - [ ] Demo video is uploaded and accessible
  - [ ] All 5 screenshots are ready
  - [ ] Questionnaire answers are prepared

### Submit for Verification

- [ ] **Publish App**
  - Navigate to: OAuth consent screen
  - Current status: "Testing"
  - Click: **"Publish App"** button
  - Confirm: Changes app to "In Production" status
  - Warning: "Your app will need verification" - Click OK

- [ ] **Start Verification Process**
  - Button appears: **"Prepare for Verification"**
  - Click: Prepare for Verification
  - Complete verification form:
    - [ ] App description (paste from prepared answers)
    - [ ] Justification for scopes (paste from prepared answers)
    - [ ] Video link (YouTube or Drive URL)
    - [ ] Upload 5 screenshots
    - [ ] Homepage URL: `https://[your-domain].com`
    - [ ] Privacy policy URL: `https://[your-domain].com/privacy`
    - [ ] Terms of service URL: `https://[your-domain].com/terms` (if available)
    - [ ] Developer contact email: `dev@[your-domain].com`
  - Review all information carefully
  - Click: **"Submit for Verification"**

- [ ] **Save Case Information**
  - Note Case ID (e.g., `12345678`)
  - Note submission date
  - Save confirmation email
  - Create calendar reminder: Check status every 2-3 days

---

## Phase 5: Post-Submission (Week -2 to Week 0)

### Monitoring

- [ ] **Daily Checks** (First Week)
  - Check email for Google OAuth team messages
  - Check case status: Google Cloud Console → Support → View Cases
  - Respond to questions within 24 hours

- [ ] **Weekly Updates**
  - Update team on verification status (standup/meeting)
  - Document any feedback or requests from Google
  - Adjust timeline if needed

### Response Preparation

- [ ] **Prepare for Additional Info Requests**
  - Have demo video link ready
  - Have screenshots ready
  - Have app access ready (for Google reviewers)
  - Assign someone to respond quickly

- [ ] **Escalation Plan**
  - If no response after 7 days → Follow up via support case
  - If rejected → Review feedback and prepare resubmission
  - If delayed → Consider proceeding with "unverified app" for internal alpha

---

## Success Criteria

### Verification Approved ✅

- [ ] **Received Approval Email**
  - Subject: "Your OAuth verification has been approved"
  - Case status: "Approved"
  - Verified badge appears in OAuth consent screen

- [ ] **Test Approved Flow**
  - Sign in with new account
  - Verify: NO "unverified app" warning
  - Verify: Clean consent screen
  - Confirm functionality works

- [ ] **Update Documentation**
  - Mark verification as complete in spec
  - Update timeline if needed
  - Notify stakeholders

- [ ] **Proceed to Phase 0**
  - Begin infrastructure setup
  - Prepare for internal alpha (Week 1)

---

### Verification Pending (Acceptable for Alpha)

- [ ] **Status After Week 0**
  - Still pending: OK for internal alpha (Week 1)
  - Use "unverified app" warning for internal users only
  - Document as known limitation

- [ ] **Contingency Actions**
  - Continue monitoring daily
  - Plan to delay public beta (Week 2+) if not approved
  - Prepare alternative timeline

---

### Verification Rejected (Requires Action)

- [ ] **Review Rejection Reasons**
  - Read feedback carefully
  - Identify specific issues

- [ ] **Address Issues**
  - Update privacy policy if needed
  - Provide additional documentation
  - Clarify scope usage
  - Update demo video if needed

- [ ] **Resubmit**
  - Make corrections
  - Resubmit verification request
  - Adjust timeline (add 2-4 weeks)

---

## Timeline Summary

| Day | Activity | Duration | Owner |
|-----|----------|----------|-------|
| Day 1 | Domain setup, privacy policy | 2-3 hours | DevOps |
| Day 2 | Google Cloud Console config | 2-3 hours | Engineering Lead |
| Day 3 | Test OAuth flow | 1-2 hours | Engineering Lead |
| Day 4 | Record demo video | 2-3 hours | Product/Engineering |
| Day 5 | Take screenshots | 1 hour | Product/Engineering |
| Day 6 | Review & submit | 1-2 hours | Engineering Lead |
| Week -1.5 | Follow up (if no response) | 30 min | Engineering Lead |
| Week -1 | Expected approval | - | - |
| Week 0 | Proceed to Phase 0 | - | All |

**Total Prep Time**: 10-15 hours
**Expected Verification Time**: 1-2 weeks (Google's timeline)

---

## Resources

**Google Cloud Console**
https://console.cloud.google.com/

**OAuth Consent Screen**
https://console.cloud.google.com/apis/credentials/consent

**Verification Guide**
https://support.google.com/cloud/answer/9110914

**Support Cases**
https://console.cloud.google.com/support

**Application Document**
`docs/oauth/google-oauth-verification-application.md`

**Privacy Policy Template**
`docs/oauth/privacy-policy.md`

---

## Emergency Contacts

**Primary Owner**: [Engineering Lead Name]
**Email**: [Engineering Lead Email]
**Slack**: @engineering-lead

**Backup**: [DevOps Name]
**Email**: [DevOps Email]
**Slack**: @devops

**Google Support**
https://console.cloud.google.com/support (create case if needed)

---

**Document Status**: ✅ Ready to Use
**Last Updated**: 2026-01-12
**Version**: 1.0

**Next Steps**: Begin Phase 1 (Day 1) preparation immediately!
