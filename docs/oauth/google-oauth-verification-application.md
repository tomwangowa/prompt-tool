# Google OAuth Verification Application

**Application Name**: Prompt Tool - AI Prompt Optimizer
**Developer**: [Your Organization Name]
**Submission Date**: [To be filled]
**Target Completion**: Week 0 (before Phase 1)

---

## Table of Contents

1. [OAuth Consent Screen Configuration](#1-oauth-consent-screen-configuration)
2. [Verification Questionnaire Answers](#2-verification-questionnaire-answers)
3. [Application Description](#3-application-description)
4. [Scopes Justification](#4-scopes-justification)
5. [Privacy Policy](#5-privacy-policy)
6. [Use Case Documentation](#6-use-case-documentation)
7. [Demo Video Script](#7-demo-video-script)
8. [Screenshot Requirements](#8-screenshot-requirements)
9. [Submission Checklist](#9-submission-checklist)

---

## 1. OAuth Consent Screen Configuration

### Basic Information

**App Name**
```
Prompt Tool - AI Prompt Optimizer
```

**App Logo** (Required: 120x120px PNG/JPG)
- [ ] Upload app logo to Google Cloud Console
- Recommended: Simple, professional icon representing prompts/AI
- File: `assets/logo-120x120.png`

**User Support Email**
```
support@[your-domain].com
```
*Note: Must be a verified email address in Google Cloud Console*

**Application Homepage**
```
https://[your-domain].com
```

**Application Privacy Policy URL** (Required)
```
https://[your-domain].com/privacy
```
*See Section 5 for privacy policy content*

**Application Terms of Service URL** (Optional but Recommended)
```
https://[your-domain].com/terms
```

**Authorized Domains**
```
[your-domain].com
```
*Note: Domain must be verified in Google Search Console*

---

### OAuth Scopes Requested

**Scope 1: Google Drive File Access** (Required)
```
https://www.googleapis.com/auth/drive.file
```

**Scope 2: User Email** (Required for user identification)
```
https://www.googleapis.com/auth/userinfo.email
```

**Scope 3: User Profile** (Optional - for display name)
```
https://www.googleapis.com/auth/userinfo.profile
```

---

### Branding Information

**Application Description** (Short, for consent screen)
```
Prompt Tool helps you optimize AI prompts and sync them securely to your Google Drive for backup and cross-device access.
```
*Character limit: 120 characters*

**Application Long Description**
```
Prompt Tool is an AI-powered prompt engineering consultant that analyzes and optimizes your prompts for better AI interactions.

Key Features:
- Multi-dimensional prompt analysis (completeness, clarity, structure, specificity)
- Professional-grade optimization using LLM analysis
- Support for 8 prompt types (zero-shot, few-shot, chain-of-thought, etc.)
- Multi-language interface (Traditional Chinese, English, Japanese)

Google Drive Integration:
- Secure cloud backup of your optimized prompts
- Automatic sync across devices (desktop, laptop, tablet)
- Offline mode with automatic sync when reconnected
- Conflict resolution when same prompt edited on multiple devices

We only access files created by our app in your Google Drive - we never access your other documents or files.
```

**Developer Contact Information**
```
Name: [Your Organization Name]
Email: dev@[your-domain].com
Address: [Your Business Address]
```

---

## 2. Verification Questionnaire Answers

### Section A: Application Overview

**Q1: What does your application do?**

**Answer:**
```
Prompt Tool is an AI prompt engineering consultant that helps users create better prompts for AI interactions. The application:

1. Analyzes user-provided prompts across multiple dimensions (completeness, clarity, structure, specificity)
2. Provides professional-grade optimization suggestions using large language model analysis
3. Stores optimized prompts in browser local storage by default
4. Offers Google Drive sync as an optional feature for cloud backup and cross-device access

The Google Drive integration enables users to:
- Automatically back up their optimized prompts to Google Drive
- Access their prompt library from multiple devices
- Prevent data loss if browser cache is cleared
- Share prompt libraries with team members (via Drive sharing)
- Work offline with automatic sync when reconnected
```

**Q2: Who are your users?**

**Answer:**
```
Our target users include:

1. **AI Practitioners & Developers** (40%)
   - Software engineers working with AI APIs
   - Machine learning researchers
   - Prompt engineers optimizing LLM interactions

2. **Content Creators & Writers** (30%)
   - Technical writers using AI tools
   - Marketing professionals creating AI-generated content
   - Educators developing AI-assisted learning materials

3. **Business Professionals** (20%)
   - Product managers using AI for documentation
   - Customer support teams optimizing chatbot prompts
   - Data analysts working with AI-powered tools

4. **Students & Academics** (10%)
   - Computer science students learning prompt engineering
   - Researchers experimenting with LLM interactions

Geographic Distribution: Global, with primary users in North America, Europe, and Asia.

Expected User Base: 10,000-50,000 users in first year.
```

**Q3: Why do you need access to Google Drive?**

**Answer:**
```
We need limited Google Drive access for the following specific purposes:

**Primary Use Case: Secure Cloud Backup**
Users spend significant time optimizing their prompts (5-30 minutes per prompt). Browser local storage is vulnerable to accidental clearing, causing permanent data loss. Google Drive provides:
- Automatic cloud backup
- Protection against browser cache clearing
- Cross-device synchronization
- Version history (via Drive's native features)

**Secondary Use Case: Cross-Device Access**
Users often work across multiple devices (work laptop, personal desktop, tablet). Google Drive sync enables:
- Seamless prompt library access from any device
- Real-time synchronization of changes
- Offline mode with automatic sync when reconnected

**Scope Limitation: drive.file (Not drive)**
We request ONLY the `drive.file` scope, which limits access to:
- Files created BY our application only
- We CANNOT and DO NOT access any of the user's other Drive files
- We CANNOT see or access the user's documents, spreadsheets, photos, or other data

**Alternative Considered and Rejected:**
- Local storage only: Risk of data loss
- Manual JSON export: Cumbersome, users forget to export
- Third-party cloud storage: Privacy concerns, additional account required
- Our own server storage: Privacy concerns, GDPR compliance complexity

Google Drive is the optimal solution because:
1. Most users already have Google accounts (99% of professionals)
2. Users trust Google's security and privacy controls
3. Data remains in user's own Drive (we never store it on our servers)
4. Users maintain full control (can revoke access anytime)
```

**Q4: How do you use the requested scopes?**

**Answer:**
```
**Scope: https://www.googleapis.com/auth/drive.file**

Usage Pattern:
1. **Folder Creation (First Sync Only)**
   - Create folder: /Prompt Tool/prompts/
   - Occurs once when user enables sync
   - User can see folder in their Drive

2. **Upload Prompts (On Save)**
   - When user saves/optimizes a prompt, upload as JSON file
   - Filename: {prompt_id}.json
   - Frequency: As needed (typically 1-10 per session)
   - Rate: ~1-5 API calls per upload

3. **Download Prompts (On App Load / Manual Sync)**
   - List files in /Prompt Tool/prompts/ folder
   - Download changed files based on modifiedTime
   - Frequency: On app startup + manual "Sync Now" clicks
   - Rate: ~2-20 API calls per sync (depends on prompt count)

4. **Update Prompts (On Edit)**
   - Update existing JSON file when user edits prompt
   - Frequency: As needed
   - Rate: ~1-3 API calls per update

5. **Delete Prompts (On User Delete)**
   - Move prompt file to trash (not permanent delete)
   - Frequency: Rarely (user-initiated only)
   - Rate: 1 API call per delete

**Rate Limiting:**
- Client-side throttling: Max 10 requests/second
- Typical usage: 5-50 API calls per session
- Peak usage: 100-200 API calls per session (large library sync)

**Data Format:**
- All data stored as JSON text files
- Typical file size: 1-10 KB per prompt
- Total storage per user: 1-100 MB (for 100-1000 prompts)

**Scope: https://www.googleapis.com/auth/userinfo.email**

Usage:
- Display user's email in app UI ("Signed in as user@example.com")
- Used for support ticket identification (if user contacts support)
- Never used for marketing or shared with third parties

**Scope: https://www.googleapis.com/auth/userinfo.profile** (Optional)

Usage:
- Display user's name in app UI (e.g., "Welcome, John")
- Improves user experience (personalization)
- Never used for tracking or analytics
```

---

### Section B: Security & Privacy

**Q5: How do you store and handle user credentials?**

**Answer:**
```
**Token Storage:**
- OAuth access tokens stored in Streamlit session state (in-memory only)
- Session state cleared when user closes browser/tab
- Tokens never stored in browser LocalStorage (XSS protection)
- Tokens never logged or written to disk
- Tokens never transmitted to our servers (app runs client-side in Streamlit)

**Token Lifecycle:**
- Access token expires: 1 hour (Google's default)
- Refresh token used to obtain new access tokens without re-authentication
- Refresh tokens valid: 6 months (Google's default)
- User can revoke access anytime via Google Account settings or our app's "Sign Out" button

**Token Revocation:**
- On user sign out, we call Google's revocation endpoint
- Ensures tokens cannot be reused if stolen
- Users can also revoke via: https://myaccount.google.com/permissions

**HTTPS Only:**
- All API calls to Google use HTTPS
- No mixed content (HTTP/HTTPS)
- TLS 1.2 or higher required

**CSRF Protection:**
- State parameter validated on OAuth callback
- Prevents cross-site request forgery attacks

**No Token Sharing:**
- Tokens never shared with third parties
- Tokens never transmitted to external servers
- Application is self-contained (runs on user's browser + Streamlit server)
```

**Q6: What data do you collect and store?**

**Answer:**
```
**Data Stored in Google Drive (By User Choice):**
- Optimized prompts (text)
- Prompt metadata (name, tags, creation date)
- Analysis scores (numeric metrics)
- Language preference (zh_TW, en, ja)

**Data Format:** JSON text files in user's own Google Drive
**User Control:** Users can delete files from Drive anytime
**Our Access:** We can only see files created by our app (drive.file scope)

**Data Stored in Browser Local Storage:**
- Same prompt data as above (primary storage)
- Sync queue (pending operations for offline mode)
- User preferences (language, sync settings)

**Data NOT Collected:**
- No tracking cookies
- No analytics about user behavior
- No prompt content sent to our servers
- No user email addresses stored on our servers
- No usage statistics beyond what's required for app functionality

**Data Transmission:**
- Prompt data: Browser ↔ Google Drive (direct, encrypted via HTTPS)
- LLM API calls: Browser ↔ Google Gemini API or AWS Bedrock (for prompt optimization)
- No data transmitted to our servers

**Data Retention:**
- In Google Drive: Until user deletes files
- In Browser LocalStorage: Until user clears browser data
- OAuth tokens: Until expiration or revocation

**GDPR Compliance:**
- Users can export data (JSON export feature)
- Users can delete all data (clear browser storage + delete Drive folder)
- Privacy policy includes GDPR rights
```

**Q7: How do you protect user privacy?**

**Answer:**
```
**Data Minimization:**
- Request minimal OAuth scopes (drive.file, not full drive access)
- Only store data necessary for app functionality
- No tracking or analytics beyond functional requirements

**Encryption:**
- All data transmission over HTTPS (TLS 1.2+)
- Google Drive files encrypted at rest by Google (AES-256)
- No additional encryption needed (relies on Google's infrastructure)

**Access Control:**
- Only authenticated users can access their own data
- No shared databases (each user's data in their own Drive)
- Application cannot access other users' data

**Privacy by Design:**
- Default to local storage (Google Drive sync is opt-in)
- Users explicitly authorize Google Drive access
- Clear consent screen explains what data is accessed
- Users can revoke access anytime

**Transparency:**
- Privacy policy clearly explains data usage
- In-app messaging about what sync does
- Open about LLM provider usage (Gemini/Claude)

**No Third-Party Sharing:**
- User data never shared with third parties
- No advertising or marketing use of data
- No data sales or monetization

**Compliance:**
- GDPR: Right to access, delete, export data
- CCPA: California privacy rights respected
- No children under 13 (COPPA compliance)
```

---

### Section C: Use Cases

**Q8: Provide a detailed use case of how users interact with Google Drive integration**

**Use Case 1: First-Time User Enabling Sync**

**Step-by-Step Flow:**

1. **User Opens App**
   - User visits https://[your-domain].com
   - App loads in browser (Streamlit web app)
   - Prompts stored in browser LocalStorage by default

2. **User Sees Sync Option**
   - Sidebar shows: "Enable Google Drive Sync"
   - Warning message: "⚠️ Data stored in browser only. Enable sync for cloud backup."
   - User clicks "Sign in with Google" link

3. **OAuth Consent Screen**
   - Browser redirects to Google's OAuth consent page
   - Consent screen shows:
     - App name: "Prompt Tool - AI Prompt Optimizer"
     - Requested permissions:
       * "See and download files created with this app"
       * "See your email address"
     - User reviews and clicks "Allow"

4. **Redirect Back to App**
   - Google redirects to app with authorization code
   - App exchanges code for access token
   - App displays: "✅ Signed in as user@example.com"

5. **Initial Sync**
   - App prompts: "Sync your 15 existing prompts to Google Drive?"
   - User clicks "Sync All"
   - Progress bar shows: "Syncing prompts: 15 / 15 (100%)"
   - Completion message: "🎉 All prompts synced successfully!"

6. **Folder Created in Drive**
   - User opens Google Drive
   - Sees new folder: /Prompt Tool/prompts/
   - Contains 15 JSON files (one per prompt)

7. **Ongoing Usage**
   - User creates new prompt → automatically synced within 5 seconds
   - User edits prompt → changes synced immediately
   - Sync status indicator shows: "✅ Synced - 2 minutes ago"

**API Calls Breakdown:**
- OAuth flow: 2 calls (authorization + token exchange)
- Folder creation: 4 calls (search + create parent folder + search + create subfolder)
- Initial sync (15 prompts): 15 upload calls
- Total: ~21 API calls for initial setup

---

**Use Case 2: Cross-Device Sync**

**Scenario:** User works on desktop at office, continues at home on laptop

**Step-by-Step Flow:**

1. **At Office (Desktop)**
   - User creates prompt "Customer Service Template"
   - App auto-syncs to Google Drive
   - User leaves office

2. **At Home (Laptop)**
   - User opens app on laptop
   - Clicks "Sign in with Google"
   - Completes OAuth (or uses existing session if recently authenticated)
   - App detects new prompts in Drive
   - Message: "Found 1 new prompt in Google Drive. Sync now?"
   - User clicks "Yes"
   - "Customer Service Template" appears in local library
   - User can now view and edit prompt on laptop

3. **Edit on Laptop**
   - User edits prompt on laptop
   - Changes auto-sync to Drive
   - File in Drive updated (user can verify by opening Drive)

4. **Back at Office (Desktop)**
   - User opens app on desktop again
   - App checks Drive for changes
   - Detects prompt was modified on laptop
   - Downloads updated version
   - Desktop now has latest changes from laptop

**API Calls Breakdown:**
- Desktop sync (step 1): 1 upload call
- Laptop initial sync (step 2): 2 calls (list files + download 1 file)
- Laptop edit sync (step 3): 1 update call
- Desktop sync check (step 4): 2 calls (list files + download updated file)
- Total: ~6 API calls for cross-device scenario

---

**Use Case 3: Offline Mode with Queue**

**Scenario:** User on airplane (no internet), makes changes, syncs when landing

**Step-by-Step Flow:**

1. **User Boards Airplane**
   - Loses internet connection
   - App detects offline state
   - Status indicator shows: "⚠️ Offline - changes will sync when reconnected"

2. **User Works Offline**
   - Creates 3 new prompts
   - Edits 2 existing prompts
   - All changes saved to browser LocalStorage
   - Sync operations queued (stored in SQLite database)
   - Status: "⚠️ Offline - 5 operations queued"

3. **Airplane Lands, User Gets WiFi**
   - Internet connection restored
   - App detects online state
   - Automatically processes queued operations
   - Progress: "Syncing queued operations: 5 / 5"
   - Status: "✅ Synced - All changes uploaded"

4. **Verification**
   - User opens Google Drive
   - Sees 3 new files + 2 updated files
   - All offline changes preserved

**API Calls Breakdown:**
- Offline work: 0 API calls (queued)
- Reconnection sync: 5 calls (3 uploads + 2 updates)
- Total: 5 API calls when online again

---

## 3. Application Description

### Elevator Pitch (30 seconds)
```
Prompt Tool is an AI-powered prompt engineering consultant that helps users create better prompts for AI interactions. It analyzes prompts across multiple dimensions, provides professional-grade optimization, and syncs your prompt library to Google Drive for secure backup and cross-device access.
```

### Full Description (for verification review)

**What is Prompt Tool?**

Prompt Tool is a web-based application (built with Streamlit and Python) that assists users in optimizing their prompts for large language model (LLM) interactions. As AI tools become ubiquitous, effective prompt engineering is essential for getting high-quality outputs. Our tool democratizes prompt engineering best practices.

**Core Functionality:**

1. **Prompt Analysis Engine**
   - Multi-dimensional evaluation: completeness, clarity, structure, specificity
   - Identifies gaps and improvement opportunities
   - Provides actionable recommendations

2. **Prompt Optimization**
   - Uses LLM-powered analysis (Google Gemini or AWS Bedrock Claude)
   - Applies industrial prompt engineering standards
   - Supports 8 prompt types (zero-shot, few-shot, chain-of-thought, role-playing, etc.)

3. **Multi-Language Support**
   - Traditional Chinese, English, Japanese interfaces
   - Prompt analysis works in any language
   - Cultural and linguistic considerations

4. **Prompt Library Management**
   - Store and organize optimized prompts
   - Tag-based categorization
   - Search functionality
   - Export/import as JSON

**Google Drive Integration: Why It Matters**

The average user spends 10-30 minutes optimizing a single prompt. Losing this work due to browser cache clearing is frustrating and common. Our Google Drive integration solves this by:

- **Automatic Cloud Backup**: Every saved prompt synced to user's Drive
- **Cross-Device Access**: Work on desktop, continue on laptop
- **Data Safety**: Protection against accidental data loss
- **Team Collaboration**: Share prompt libraries via Drive folders (optional)
- **Offline Support**: Queue changes when offline, sync when reconnected

**Privacy-First Design**

We prioritize user privacy:
- Google Drive sync is **opt-in** (not required)
- We use the most restrictive OAuth scope (`drive.file`) - we can only see files our app creates
- No data stored on our servers - all data stays in user's browser and Drive
- Open-source consideration (roadmap item)

**Target Market**

- **Primary**: AI practitioners, developers, prompt engineers (B2B SaaS)
- **Secondary**: Content creators, writers, educators (prosumer)
- **Geographic**: Global, cloud-delivered

**Technology Stack**

- **Frontend**: Streamlit (Python-based web framework)
- **Backend**: Python, SQLite (local only)
- **Storage**: Browser LocalStorage + Google Drive (optional)
- **LLM Providers**: Google Gemini API, AWS Bedrock (user-configured)
- **Deployment**: Docker containers, cloud-hosted

**Monetization** (Future Roadmap)

Currently free/freemium. Future plans:
- Free tier: Local storage only
- Pro tier ($9/month): Google Drive sync + priority LLM access
- Enterprise tier ($49/user/month): Team collaboration + SSO

**Why Google OAuth Verification Matters**

We're seeking verification to:
1. Remove "unverified app" warning (improves user trust)
2. Support production launch with general availability
3. Enable enterprise adoption (verified app status required by IT departments)
4. Comply with Google Cloud Platform best practices

---

## 4. Scopes Justification

### Scope 1: drive.file (Per-File Access)

**Requested Scope**
```
https://www.googleapis.com/auth/drive.file
```

**Why This Scope?**

**Option 1: drive (Full Access) - REJECTED**
- Too permissive - would allow access to ALL user files
- Privacy concern - users don't want apps seeing their documents
- Not needed - we only need access to files we create

**Option 2: drive.readonly - REJECTED**
- Read-only - cannot create or update files
- Insufficient for sync functionality

**Option 3: drive.file - SELECTED** ✅
- **Perfect fit**: Only files created by our app
- User privacy protected
- Sufficient for all our use cases
- Aligns with principle of least privilege

**What We Can Do with drive.file:**
- ✅ Create folder /Prompt Tool/prompts/
- ✅ Upload JSON files to our folder
- ✅ Read/download files we created
- ✅ Update/delete files we created
- ✅ List files in our folder

**What We CANNOT Do:**
- ❌ See user's other documents, spreadsheets, presentations
- ❌ Access user's photos or videos in Drive
- ❌ Read files created by other apps
- ❌ Search across all of user's Drive

**Technical Implementation**

```python
# Example: Creating a file with drive.file scope
from googleapiclient.discovery import build

service = build('drive', 'v3', credentials=credentials)

# Create folder (only accessible by our app)
folder_metadata = {
    'name': 'Prompt Tool',
    'mimeType': 'application/vnd.google-apps.folder'
}
folder = service.files().create(body=folder_metadata).execute()

# Upload prompt to folder
file_metadata = {
    'name': 'prompt_12345.json',
    'parents': [folder['id']],  # Our folder
    'mimeType': 'application/json'
}
media = MediaIoBaseUpload(json_content, mimetype='application/json')
file = service.files().create(
    body=file_metadata,
    media_body=media
).execute()

# Result: File only visible to our app (and user in Drive UI)
```

---

### Scope 2: userinfo.email (User Email Address)

**Requested Scope**
```
https://www.googleapis.com/auth/userinfo.email
```

**Why This Scope?**

**Use Cases:**
1. **User Identification in UI**
   - Display "Signed in as user@example.com"
   - Helps user confirm they're signed into correct account
   - UX best practice for OAuth apps

2. **Support Ticket Association**
   - If user contacts support, we can match their email
   - Helps us provide better support
   - Not used for any automated processing

3. **Account Management**
   - Display connected account in settings
   - Allow user to verify which account is syncing
   - Enable "switch accounts" functionality (future)

**What We Do with Email:**
- ✅ Display in UI ("Signed in as...")
- ✅ Associate with support tickets (manual process)
- ✅ Log in application logs (for debugging, local only)

**What We DON'T Do:**
- ❌ Send marketing emails
- ❌ Share with third parties
- ❌ Store on our servers
- ❌ Use for tracking or analytics
- ❌ Sell or monetize

**Data Handling:**
```python
# Example: Getting user email
user_info = service.userinfo().get().execute()
email = user_info['email']

# Display in UI
st.success(f"✅ Signed in as {email}")

# Store in session only (not persisted)
st.session_state.user_email = email

# On sign out, clear
st.session_state.user_email = None
```

---

### Scope 3: userinfo.profile (User Profile) - Optional

**Requested Scope** (Optional - Nice to Have)
```
https://www.googleapis.com/auth/userinfo.profile
```

**Why This Scope?**

**Use Cases:**
1. **Personalized Welcome Message**
   - Display "Welcome back, John!" instead of "Welcome back!"
   - Improves user experience
   - More friendly and personalized

2. **Avatar Display** (Future)
   - Show user's Google profile picture
   - Visual confirmation of signed-in account
   - Consistent with other Google-integrated apps

**What We Do with Profile:**
- ✅ Display name in welcome message
- ✅ Show profile picture (future feature)
- ✅ Improve personalization

**What We DON'T Do:**
- ❌ Store profile data on servers
- ❌ Track user activity
- ❌ Share with third parties
- ❌ Use for advertising

**Note**: This scope is optional. If it complicates verification, we can proceed with only `drive.file` and `userinfo.email`.

---

## 5. Privacy Policy

**Link**: https://[your-domain].com/privacy

**Status**: ⚠️ Must be published before OAuth verification submission

See separate document: `privacy-policy.md` (included with this application)

**Key Sections Required:**
1. What data we collect
2. How we use data
3. How we share data (we don't)
4. User rights (GDPR/CCPA)
5. Data retention
6. Contact information

---

## 6. Use Case Documentation

### Visual Use Case Diagram

```
User Journey: First Sync

┌─────────────────────────────────────────────────────────────────┐
│  Step 1: User Opens App                                         │
│  → Sees "Enable Google Drive Sync" option                       │
│  → Click "Sign in with Google" link                             │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: OAuth Consent Screen (Google)                          │
│  → Shows app name, logo, requested permissions                  │
│  → User reviews and clicks "Allow"                              │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Redirect to App                                        │
│  → App receives authorization code                              │
│  → Exchanges code for access token                              │
│  → Displays "✅ Signed in as user@example.com"                  │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Initial Sync Prompt                                    │
│  → "Sync your 15 existing prompts to Google Drive?"             │
│  → [Sync All] [Select Prompts] [Skip]                           │
│  → User clicks "Sync All"                                       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Sync Progress                                          │
│  → Progress bar: "Syncing prompts: 15 / 15 (100%)"              │
│  → Creates /Prompt Tool/prompts/ folder in Drive                │
│  → Uploads 15 JSON files                                        │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: Completion                                             │
│  → "🎉 All prompts synced successfully!"                        │
│  → Status: "✅ Synced - Just now"                               │
│  → User can verify in Google Drive                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Demo Video Script

**Target Duration**: 2-3 minutes
**Recording Tool**: Loom, OBS Studio, or QuickTime Screen Recording
**Resolution**: 1920x1080 (1080p)

### Video Script

**[0:00-0:15] Introduction**

> "Hi, I'm [Your Name] from [Your Organization]. Today I'll show you how Prompt Tool uses Google Drive to securely sync your AI prompts across devices."

**[0:15-0:30] Problem Statement**

> "Many users spend hours optimizing their AI prompts, but browser local storage is vulnerable to data loss. That's why we built Google Drive sync - to keep your prompts safe and accessible everywhere."

**[0:30-1:00] OAuth Flow**

*Screen: Show Prompt Tool app*

> "When a user enables sync, they click 'Sign in with Google' which opens Google's OAuth consent screen."

*Screen: Show OAuth consent screen (unverified app warning is OK)*

> "Google shows exactly what permissions we're requesting: access to files created by our app, and the user's email address. Notice we're NOT requesting full Drive access - only files our app creates."

*Click "Allow"*

> "After the user clicks Allow, they're redirected back to the app."

**[1:00-1:30] Initial Sync**

*Screen: Back to app*

> "The app confirms: 'Signed in as demo@example.com'. Now the user can sync their existing prompts."

*Click "Sync All"*

> "The app uploads each prompt as a JSON file to a dedicated folder in the user's Drive."

*Show progress bar*

> "Progress is shown in real-time. In this demo, we're syncing 15 prompts."

**[1:30-2:00] Verification in Drive**

*Open new tab: Google Drive*

> "Let's verify. Here in Google Drive, we can see the 'Prompt Tool' folder with a 'prompts' subfolder."

*Click into folder*

> "Inside are JSON files - one per prompt. These files are only accessible by our app and the user."

**[2:00-2:30] Cross-Device Sync**

*Screen: Different browser/device*

> "Now let's simulate a different device. The user signs in on their laptop..."

*Sign in flow*

> "And the app automatically detects prompts in Drive and syncs them locally. No manual export or import needed."

**[2:30-2:45] Offline Mode**

*Screen: Back to first device*

> "If the user goes offline, changes are queued and automatically synced when they're back online."

*Show offline indicator, then online sync*

**[2:45-3:00] Conclusion**

> "That's Prompt Tool's Google Drive integration. It uses minimal permissions, keeps data in the user's own Drive, and provides automatic backup across all devices. Users can revoke access anytime through Google Account settings or our app."

*Screen: Show "Sign Out" button*

> "Thanks for watching!"

### Recording Checklist

- [ ] Record in 1920x1080 resolution
- [ ] Use clear audio (lapel mic recommended)
- [ ] Show OAuth consent screen (unverified warning is OK)
- [ ] Show Google Drive folder creation
- [ ] Show files in Drive
- [ ] Demonstrate cross-device sync
- [ ] Keep under 3 minutes
- [ ] Export as MP4 (H.264 codec)
- [ ] Upload to YouTube (unlisted) or Google Drive

---

## 8. Screenshot Requirements

Google requires 3-5 screenshots showing the integration. Prepare the following:

### Screenshot 1: OAuth Consent Screen
**Filename**: `1-oauth-consent-screen.png`

**Content:**
- Google's OAuth consent screen
- Shows app name "Prompt Tool"
- Lists requested scopes
- Shows "Allow" button
- Unverified app warning visible (acceptable for submission)

**Size**: 1280x720 minimum

---

### Screenshot 2: App After Authentication
**Filename**: `2-signed-in-status.png`

**Content:**
- App UI showing "✅ Signed in as demo@example.com"
- Sync status indicator
- "Sync Now" button visible
- Clean, professional UI

**Size**: 1280x720 minimum

---

### Screenshot 3: Initial Sync Dialog
**Filename**: `3-initial-sync-prompt.png`

**Content:**
- Modal or dialog showing "Sync your 15 existing prompts to Google Drive?"
- Options: [Sync All] [Select Prompts] [Skip]
- Clear user choice

**Size**: 1280x720 minimum

---

### Screenshot 4: Google Drive Folder
**Filename**: `4-drive-folder-structure.png`

**Content:**
- Google Drive web interface
- /Prompt Tool/prompts/ folder visible
- JSON files listed (e.g., prompt_12345.json, prompt_67890.json)
- Shows our app only creates/accesses specific files

**Size**: 1280x720 minimum

---

### Screenshot 5: Sync Status Indicator
**Filename**: `5-sync-status-indicator.png`

**Content:**
- App UI showing sync status
- Examples: "✅ Synced - 2 minutes ago", "🔄 Syncing...", "⚠️ Offline - 5 ops queued"
- User can clearly see sync state

**Size**: 1280x720 minimum

---

## 9. Submission Checklist

### Pre-Submission (Complete Before Submitting)

**Documentation**
- [ ] Privacy policy published at https://[your-domain].com/privacy
- [ ] Privacy policy URL publicly accessible (test in incognito mode)
- [ ] Terms of service published (optional but recommended)
- [ ] Domain verified in Google Search Console

**Google Cloud Console**
- [ ] Google Cloud Project created
- [ ] OAuth 2.0 Client ID configured (Web application type)
- [ ] Authorized redirect URIs added (dev, staging, production)
- [ ] OAuth consent screen completed (all required fields)
- [ ] App logo uploaded (120x120px PNG/JPG)
- [ ] Support email verified
- [ ] Scopes added: drive.file, userinfo.email, (userinfo.profile)

**Media Assets**
- [ ] Demo video recorded (2-3 minutes)
- [ ] Demo video uploaded to YouTube (unlisted) or Google Drive
- [ ] 5 screenshots prepared (1280x720 minimum)
- [ ] Screenshots show actual OAuth flow (not mockups)

**Testing**
- [ ] OAuth flow tested end-to-end in development environment
- [ ] Tested with multiple Google accounts (personal, Workspace)
- [ ] Verified "unverified app" warning appears (expected before verification)
- [ ] Confirmed Drive folder creation works
- [ ] Verified file upload/download works

---

### Submission Steps

**Step 1: Submit OAuth Consent Screen for Verification**

1. Go to: Google Cloud Console → APIs & Services → OAuth consent screen
2. Click "Publish App" (changes status from Testing to In Production)
3. Click "Prepare for Verification" button
4. Complete verification questionnaire (use answers from Section 2)

**Step 2: Upload Supporting Documents**

1. Upload demo video (YouTube link or file upload)
2. Upload 5 screenshots
3. Provide homepage URL
4. Provide privacy policy URL
5. Provide terms of service URL (if applicable)

**Step 3: Submit for Review**

1. Review all information for accuracy
2. Click "Submit for Verification"
3. Note the Case ID (for tracking)
4. Check email for confirmation

---

### Post-Submission

**Monitoring**
- [ ] Check email daily for Google OAuth team responses
- [ ] Monitor case status: Google Cloud Console → Support → View Cases
- [ ] Respond to additional information requests within 24 hours
- [ ] Update team on verification status (weekly standups)

**Expected Timeline**
- Initial review: 3-5 business days
- Full verification: 1-4 weeks (typically 1-2 weeks)
- Additional info requests: Add 3-7 days per iteration

**Possible Outcomes**
1. **Approved** ✅ - Proceed to Phase 0
2. **Additional Info Requested** - Respond promptly with requested details
3. **Rejected** - Address issues and resubmit (rare if prepared properly)

**Communication Plan**
- **Week -2**: Submit application
- **Week -1.5**: Follow up if no response after 3 days
- **Week -1**: Expected approval (if all goes well)
- **Week 0**: Proceed to Phase 0 (even if still pending, use unverified app for internal alpha)

---

### Contingency Plan

**If Verification Delayed Beyond Week 0**

**Plan A: Proceed with Unverified App (Internal Alpha Only)**
- Use unverified app for Week 1 (internal team testing only)
- Accept "unverified app" warning for internal users
- Do NOT proceed to public beta (Week 2+) without verification

**Plan B: Request Expedited Review**
- Contact Google Cloud support via case system
- Explain timeline constraints (product launch deadline)
- Provide additional context if helpful

**Plan C: Delay Launch Timeline**
- If verification takes >4 weeks, delay Phase 1 start
- Adjust timeline: Week -2 → Week -X (where X = verification duration)
- Communicate revised timeline to stakeholders

---

## Contact Information for Submission

**App Developer Contact**
```
Name: [Your Full Name / Organization Name]
Email: dev@[your-domain].com
Phone: [Your Phone Number]
Address: [Your Business Address]
```

**Support Contact** (User-facing)
```
Email: support@[your-domain].com
```

**OAuth Verification Case ID** (After Submission)
```
Case ID: [Will be assigned by Google]
Submission Date: [YYYY-MM-DD]
Expected Completion: [YYYY-MM-DD]
Status: [Pending / Approved / Additional Info Requested]
```

---

## Additional Resources

**Google OAuth Verification Guide**
https://support.google.com/cloud/answer/9110914

**OAuth 2.0 for Web Server Applications**
https://developers.google.com/identity/protocols/oauth2/web-server

**Google Drive API Documentation**
https://developers.google.com/drive/api/guides/about-sdk

**OAuth Consent Screen Configuration**
https://console.cloud.google.com/apis/credentials/consent

**Google Cloud Support**
https://console.cloud.google.com/support

---

**Document Status**: ✅ Ready for Submission
**Last Updated**: 2026-01-12
**Version**: 1.0

**Next Steps:**
1. Review and customize with your actual domain/organization details
2. Publish privacy policy
3. Verify domain in Google Search Console
4. Create demo video
5. Take screenshots
6. Submit OAuth verification application
7. Monitor case status daily
