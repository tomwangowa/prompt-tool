# Feature Specification: Google Drive Sync with OAuth Authentication

## 1. Background/Context

**Current State**

The AI Prompt Engineering Consultant tool currently supports two prompt storage mechanisms:
- **Browser LocalStorage**: Used in production mode via `streamlit-local-storage` library. Data persists only in the user's browser and is vulnerable to browser cache clearing.
- **JSON Export/Import**: Manual file-based backup mechanism where users can download prompts as JSON and re-import them later.
- **SQLite Database**: Backend storage for prompt metadata, analysis scores, and tags.

Both storage modes are available in two UI paradigms:
- **Conversation Mode**: Chat-based interface for single-round prompt optimization
- **Classic Mode**: Traditional multi-step form interface

**Problem Statement**

Current storage solutions have significant limitations:
1. **Data Loss Risk**: LocalStorage can be cleared by users accidentally or browser maintenance, causing permanent data loss
2. **No Cross-Device Access**: Users cannot access their prompts from different devices
3. **No Cloud Backup**: No automatic backup mechanism exists beyond manual JSON export
4. **Collaboration Limitations**: Users cannot share prompt libraries with team members
5. **Manual Sync Burden**: Users must remember to export/import JSON files manually

**Business Value**

- **Data Safety**: Automatic cloud backup prevents user data loss, increasing trust
- **User Retention**: Cross-device sync encourages continued usage across work contexts
- **Premium Feature Potential**: Google Drive sync can be positioned as a premium feature
- **Professional Use Case**: Teams can share optimized prompts, expanding B2B market
- **Reduced Support**: Fewer "lost my data" support tickets

**User Impact**

- Users gain peace of mind knowing their prompt optimizations are safely backed up
- Seamless experience across desktop, laptop, and tablet devices
- Ability to collaborate by sharing Google Drive folders with colleagues
- Automatic sync eliminates manual export/import workflow

**Assumptions**

- Users have Google accounts (99% of professionals do)
- Users are comfortable granting Google Drive access to the application
- Internet connectivity is available for sync operations (offline support with queue)
- Google Drive API quota limits are sufficient for typical usage patterns
- Users want automatic sync rather than manual control (configurable setting)

---

## 2. Requirements

### Functional Requirements

**FR-1: Google OAuth Authentication**
- Users must be able to authenticate with Google OAuth 2.0
- Support "Sign in with Google" flow using official Google Identity libraries
- Securely store and refresh OAuth tokens
- Acceptance Criteria:
  - "Sign in with Google" button appears in both Conversation and Classic modes
  - Successful authentication redirects user back to the app with active session
  - Token refresh happens automatically before expiration
  - User can view connected account email in settings

**FR-2: Automatic Prompt Sync to Google Drive**
- Automatically sync optimized prompts to a designated Google Drive folder
- Create folder structure: `/Prompt Tool/prompts/` if not exists
- Sync triggers: after saving prompt, after editing prompt, on manual refresh
- Acceptance Criteria:
  - New prompts appear in Google Drive within 5 seconds of save
  - Folder structure is created automatically on first sync
  - Sync status indicator shows "Syncing..." → "Synced" → timestamp
  - Failed syncs are queued for retry (max 3 attempts)

**FR-3: Bidirectional Sync (Drive → Local)**
- Pull prompts from Google Drive on app load and manual refresh
- Detect changes made in Google Drive directly (e.g., via Drive web interface)
- Merge remote prompts with local prompts intelligently
- Acceptance Criteria:
  - On app startup, fetch latest prompts from Google Drive
  - Manual "Sync Now" button in both UI modes
  - New prompts from Drive appear in local library within 5 seconds
  - Sync activity log shows what was pulled/pushed

**FR-4: Conflict Resolution**
- Detect conflicts when same prompt modified locally and remotely
- Provide user-friendly conflict resolution UI
- Offer options: Keep Local, Keep Remote, Keep Both (rename), Manual Merge
- Acceptance Criteria:
  - Conflict detection based on `updated_at` timestamp and prompt `id`
  - Conflict dialog shows diff view (side-by-side comparison)
  - User choice is persisted and sync completes
  - No data loss during conflict resolution

**FR-5: Offline Support with Sync Queue**
- Allow app to function offline with local storage
- Queue sync operations when offline
- Automatically sync queue when connection restored
- Acceptance Criteria:
  - App shows "Offline Mode" indicator when no internet
  - Prompts saved locally are queued for upload
  - Queue persists across app restarts
  - Queue processes automatically on reconnection

**FR-6: Selective Sync Settings**
- Allow users to enable/disable Google Drive sync
- Provide option to sync only specific tags or categories
- Support manual sync mode (sync only on button click)
- Acceptance Criteria:
  - Settings panel with "Enable Google Drive Sync" toggle
  - "Auto-sync" vs "Manual sync" mode selector
  - Tag filter: "Sync these tags only: [tag1, tag2]"
  - Settings persist across sessions

**FR-7: Sign Out and Account Management**
- Users can sign out of Google account
- Clear local OAuth tokens on sign out
- Option to "Disconnect and Keep Local Data" or "Disconnect and Clear All Data"
- Acceptance Criteria:
  - "Sign Out" button in settings
  - Confirmation dialog explains data implications
  - Tokens revoked via Google API on sign out
  - UI returns to unauthenticated state

**FR-8: Sync Status Visibility**
- Display sync status in UI (syncing, synced, offline, error)
- Show last sync timestamp
- Provide sync history/activity log
- Acceptance Criteria:
  - Persistent sync status badge/icon in header
  - Clicking status shows detailed sync log (last 50 operations)
  - Error states show actionable error messages
  - Success states show green checkmark with timestamp

### Non-Functional Requirements

**NFR-1: Performance**
- Initial sync of 100 prompts must complete within 10 seconds on broadband
- Incremental sync (1-5 prompts) must complete within 2 seconds
- UI must remain responsive during background sync (non-blocking)
- OAuth authentication flow must complete within 5 seconds (Google's responsibility)

**NFR-2: Scalability**
- Support up to 1000 prompts per user without performance degradation
- Handle Google Drive API rate limits gracefully (exponential backoff)
- Batch API requests when syncing multiple prompts (max 50 per batch)

**NFR-3: Availability**
- App must function in offline mode with graceful degradation
- Google API failures must not crash the application
- Fallback to local storage if Drive API unavailable
- 99% success rate for sync operations under normal conditions

**NFR-4: Security**
- OAuth tokens stored using Streamlit secrets or secure session storage
- Tokens never logged or exposed in client-side code
- Use Google Drive API minimal required scopes: `drive.file` (not `drive.readonly`)
- Support token revocation via Google OAuth consent screen
- All API calls over HTTPS only

**NFR-5: Usability**
- Authentication flow must be intuitive (< 3 clicks to sign in)
- Sync errors must provide user-friendly explanations (not technical jargon)
- Settings must be accessible within 2 clicks from main screen
- Conflict resolution UI must be understandable by non-technical users

**NFR-6: Compatibility**
- Support latest 2 versions of Chrome, Firefox, Safari, Edge
- Mobile-responsive design for tablet devices (iPad, Android tablets)
- Work with both personal Google accounts and Google Workspace accounts
- Compatible with existing LocalStorage and SQLite storage systems

---

## 3. Technical Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Streamlit UI                        │
│  ┌──────────────────┐            ┌──────────────────┐      │
│  │ Conversation Mode│            │   Classic Mode   │      │
│  └────────┬─────────┘            └────────┬─────────┘      │
│           │                               │                 │
│           └───────────────┬───────────────┘                 │
│                           │                                 │
│                    ┌──────▼────────┐                        │
│                    │ Google Auth UI │                       │
│                    │  - Sign In     │                       │
│                    │  - Sign Out    │                       │
│                    │  - Status      │                       │
│                    └──────┬────────┘                        │
└───────────────────────────┼─────────────────────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │ GoogleDriveSync    │ (New Service Layer)
                  │  - sync_prompt()   │
                  │  - pull_prompts()  │
                  │  - resolve_conflict│
                  └─────────┬──────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────▼────┐    ┌───────▼────────┐  ┌────▼────────┐
    │ OAuth    │    │ Drive API      │  │ Sync Queue  │
    │ Manager  │    │ Client         │  │ (Local DB)  │
    └─────┬────┘    └───────┬────────┘  └────┬────────┘
          │                 │                 │
          │                 │                 │
    ┌─────▼─────────────────▼─────────────────▼────────┐
    │           Google Cloud Services                  │
    │  - OAuth 2.0 Server                              │
    │  - Google Drive API v3                           │
    └──────────────────────────────────────────────────┘
```

### New Components

#### 1. `google_auth.py` - OAuth Manager

```python
import os
import json
import secrets
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class GoogleAuthManager:
    """
    Manages Google OAuth 2.0 authentication flow.
    Uses google-auth and google-auth-oauthlib libraries.

    IMPORTANT: This implementation uses Streamlit's query_params for OAuth callback.
    The OAuth flow works as follows:
    1. User clicks "Sign in with Google" link (not button)
    2. Browser redirects to Google OAuth consent screen
    3. User authorizes the app
    4. Google redirects back to app with ?code=xxx in URL
    5. App detects code in query_params and exchanges for token
    6. Credentials stored in st.session_state
    """

    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self):
        """Initialize OAuth manager with session state credentials"""
        if 'google_credentials' not in st.session_state:
            st.session_state.google_credentials = None
        if 'oauth_state' not in st.session_state:
            st.session_state.oauth_state = None

        self.credentials = st.session_state.google_credentials
        self.client_config = self._load_client_config()

    def _load_client_config(self) -> dict:
        """Load OAuth client configuration from environment variables"""
        return {
            "web": {
                "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8501")]
            }
        }

    def initiate_oauth_flow(self) -> str:
        """
        Generate OAuth URL for user to authenticate.

        Returns:
            str: Authorization URL to redirect user to Google login
        """
        # Generate and store CSRF state token
        state = secrets.token_urlsafe(32)
        st.session_state.oauth_state = state

        # Create OAuth flow
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=self.client_config["web"]["redirect_uris"][0]
        )

        # Generate authorization URL with PKCE
        auth_url, _ = flow.authorization_url(
            access_type='offline',  # Request refresh token
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent screen for refresh token
        )

        return auth_url

    def handle_oauth_callback(self, code: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            dict: User info (email, name)

        Raises:
            Exception: If token exchange fails or state mismatch
        """
        # Validate state parameter (CSRF protection)
        # Note: In production, also validate state from URL query params

        # Create flow for token exchange
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=self.client_config["web"]["redirect_uris"][0]
        )

        # Exchange code for token
        flow.fetch_token(code=code)

        # Store credentials in session state
        self.credentials = flow.credentials
        st.session_state.google_credentials = self.credentials

        # Get user info
        user_info = self.get_user_info()
        return user_info

    def refresh_token(self) -> bool:
        """
        Refresh expired access token using refresh token.

        Returns:
            bool: True if refresh successful, False otherwise
        """
        if not self.credentials or not self.credentials.refresh_token:
            return False

        try:
            # Refresh token
            self.credentials.refresh(Request())
            st.session_state.google_credentials = self.credentials
            return True
        except Exception as e:
            # Refresh failed, clear credentials
            st.session_state.google_credentials = None
            self.credentials = None
            return False

    def revoke_token(self) -> bool:
        """
        Revoke token on sign out.

        Returns:
            bool: True if revocation successful
        """
        if not self.credentials:
            return True

        try:
            # Revoke token via Google API
            import requests
            requests.post('https://oauth2.googleapis.com/revoke',
                params={'token': self.credentials.token},
                headers={'content-type': 'application/x-www-form-urlencoded'})

            # Clear credentials
            st.session_state.google_credentials = None
            st.session_state.oauth_state = None
            self.credentials = None
            return True
        except Exception:
            # Even if revocation fails, clear local credentials
            st.session_state.google_credentials = None
            self.credentials = None
            return False

    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated with valid credentials.

        Returns:
            bool: True if authenticated and token valid
        """
        if not self.credentials:
            return False

        # Check if token expired
        if self.credentials.expired:
            # Try to refresh
            if self.credentials.refresh_token:
                return self.refresh_token()
            else:
                return False

        return True

    def get_user_info(self) -> dict:
        """
        Get authenticated user's email and name from Google API.

        Returns:
            dict: {'email': str, 'name': str}
        """
        if not self.credentials:
            return None

        try:
            # Use Google OAuth2 API to get user info
            service = build('oauth2', 'v2', credentials=self.credentials)
            user_info = service.userinfo().get().execute()

            return {
                'email': user_info.get('email'),
                'name': user_info.get('name', user_info.get('email'))
            }
        except Exception:
            return {'email': 'Unknown', 'name': 'Unknown'}
```

#### 2. `google_drive_client.py` - Drive API Client

```python
import time
import json
from collections import deque
from datetime import datetime
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
import io

class GoogleDriveClient:
    """
    Wrapper for Google Drive API v3 operations.
    Handles file upload, download, search, update with rate limiting.

    Rate Limiting Strategy:
    - Max 10 requests per second (Google Drive API best practice)
    - Uses sliding window to track recent requests
    - Automatically throttles when limit approached
    """

    FOLDER_NAME = "Prompt Tool"
    PROMPTS_FOLDER = "prompts"
    MAX_REQUESTS_PER_SECOND = 10

    def __init__(self, credentials):
        self.service = build('drive', 'v3', credentials=credentials)
        self.folder_id = None
        self.prompts_folder_id = None

        # Rate limiting: track timestamps of last N requests
        self.request_times = deque(maxlen=self.MAX_REQUESTS_PER_SECOND)

    def _throttle(self):
        """
        Ensure we don't exceed MAX_REQUESTS_PER_SECOND.
        Blocks until it's safe to make another request.
        """
        now = time.time()

        # If we have max requests in the window, check if we need to wait
        if len(self.request_times) == self.MAX_REQUESTS_PER_SECOND:
            oldest_request = self.request_times[0]
            elapsed = now - oldest_request

            # If all N requests were within 1 second, wait
            if elapsed < 1.0:
                sleep_time = 1.0 - elapsed
                time.sleep(sleep_time)

        # Record this request
        self.request_times.append(time.time())

    def ensure_folder_structure(self) -> str:
        """
        Create /Prompt Tool/prompts/ folder structure in Drive root if not exists.

        Returns:
            str: Prompts folder ID
        """
        self._throttle()

        # Search for "Prompt Tool" folder
        query = f"name='{self.FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        files = response.get('files', [])

        if files:
            self.folder_id = files[0]['id']
        else:
            # Create "Prompt Tool" folder in root
            self._throttle()
            folder_metadata = {
                'name': self.FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            self.folder_id = folder['id']

        # Now create "prompts" subfolder
        self._throttle()
        query = f"name='{self.PROMPTS_FOLDER}' and '{self.folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        files = response.get('files', [])

        if files:
            self.prompts_folder_id = files[0]['id']
        else:
            # Create "prompts" subfolder
            self._throttle()
            subfolder_metadata = {
                'name': self.PROMPTS_FOLDER,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.folder_id]
            }
            subfolder = self.service.files().create(
                body=subfolder_metadata,
                fields='id'
            ).execute()
            self.prompts_folder_id = subfolder['id']

        return self.prompts_folder_id

    def upload_prompt(self, prompt_data: dict) -> str:
        """
        Upload prompt as JSON file to Drive.

        Args:
            prompt_data: Prompt dictionary with all fields

        Returns:
            str: Google Drive file ID
        """
        if not self.prompts_folder_id:
            self.ensure_folder_structure()

        self._throttle()

        # Convert prompt to JSON
        json_content = json.dumps(prompt_data, ensure_ascii=False, indent=2)
        media = MediaIoBaseUpload(
            io.BytesIO(json_content.encode('utf-8')),
            mimetype='application/json',
            resumable=True
        )

        # Create file metadata
        file_metadata = {
            'name': f"{prompt_data['id']}.json",
            'parents': [self.prompts_folder_id],
            'mimeType': 'application/json'
        }

        # Upload file
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, modifiedTime'
        ).execute()

        return file['id']

    def download_prompt(self, file_id: str) -> dict:
        """
        Download prompt JSON from Drive.

        Args:
            file_id: Google Drive file ID

        Returns:
            dict: Prompt data
        """
        self._throttle()

        # Download file content
        request = self.service.files().get_media(fileId=file_id)
        content = request.execute()

        # Parse JSON
        prompt_data = json.loads(content.decode('utf-8'))
        return prompt_data

    def list_prompts(self, modified_after: datetime = None) -> List[dict]:
        """
        List all prompts in prompts folder.

        Args:
            modified_after: Optional filter for modified date

        Returns:
            List[dict]: List of file metadata (id, name, modifiedTime)
        """
        if not self.prompts_folder_id:
            self.ensure_folder_structure()

        self._throttle()

        query = f"'{self.prompts_folder_id}' in parents and trashed=false"
        if modified_after:
            modified_str = modified_after.isoformat() + 'Z'
            query += f" and modifiedTime > '{modified_str}'"

        all_files = []
        page_token = None

        # Handle pagination (max 1000 files per request, but we use 100 for safety)
        while True:
            self._throttle()
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, modifiedTime)',
                pageSize=100,
                pageToken=page_token
            ).execute()

            files = response.get('files', [])
            all_files.extend(files)

            page_token = response.get('nextPageToken')
            if not page_token:
                break

        return all_files

    def update_prompt(self, file_id: str, prompt_data: dict) -> bool:
        """
        Update existing prompt file.

        Args:
            file_id: Google Drive file ID
            prompt_data: Updated prompt data

        Returns:
            bool: True if successful
        """
        self._throttle()

        # Convert prompt to JSON
        json_content = json.dumps(prompt_data, ensure_ascii=False, indent=2)
        media = MediaIoBaseUpload(
            io.BytesIO(json_content.encode('utf-8')),
            mimetype='application/json',
            resumable=True
        )

        # Update file
        self.service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id, modifiedTime'
        ).execute()

        return True

    def delete_prompt(self, file_id: str) -> bool:
        """
        Delete prompt file from Drive (move to trash).

        Args:
            file_id: Google Drive file ID

        Returns:
            bool: True if successful
        """
        self._throttle()

        self.service.files().delete(fileId=file_id).execute()
        return True

    def batch_upload(self, prompts: List[dict]) -> dict:
        """
        Batch upload multiple prompts.
        Note: Google Drive API doesn't support true batch uploads for files,
        so we upload sequentially with rate limiting.

        Args:
            prompts: List of prompt dictionaries

        Returns:
            dict: {
                'successful': int,
                'failed': int,
                'file_ids': List[str]
            }
        """
        result = {
            'successful': 0,
            'failed': 0,
            'file_ids': []
        }

        for prompt in prompts:
            try:
                file_id = self.upload_prompt(prompt)
                result['file_ids'].append(file_id)
                result['successful'] += 1
            except Exception as e:
                result['failed'] += 1

        return result
```

#### 3. `google_drive_sync.py` - Sync Orchestrator

```python
import threading
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class SyncStatus(Enum):
    """Sync status enumeration"""
    UNKNOWN = "unknown"
    SYNCED = "synced"
    SYNCING = "syncing"
    OFFLINE = "offline"
    ERROR = "error"

class GoogleDriveSync:
    """
    Orchestrates bidirectional sync between local storage and Google Drive.
    Handles conflict detection and resolution.

    IMPORTANT: All sync methods are synchronous, not async.
    Long-running sync operations should be run in background threads
    to keep the Streamlit UI responsive.
    """

    def __init__(self, drive_client: GoogleDriveClient,
                 local_storage: LocalStoragePromptDB):
        self.drive = drive_client
        self.local = local_storage
        self.sync_queue = SyncQueue()
        self._sync_lock = threading.Lock()  # Prevent concurrent syncs

    def sync_all(self) -> dict:
        """
        Full bidirectional sync (push local changes, pull remote changes).

        This method is synchronous. For background sync, call from a thread:
            thread = threading.Thread(target=self.sync_all)
            thread.start()

        Returns:
            dict: {
                'pushed': int,
                'pulled': int,
                'conflicts': int,
                'errors': List[str]
            }
        """
        with self._sync_lock:  # Ensure only one sync at a time
            result = {
                'pushed': 0,
                'pulled': 0,
                'conflicts': 0,
                'errors': []
            }

            try:
                # Step 1: Push local changes to Drive
                local_prompts = self.local.load_prompts()
                for prompt in local_prompts:
                    # Check if prompt needs syncing
                    if prompt.get('sync_status') == 'pending' or not prompt.get('drive_file_id'):
                        try:
                            self.push_prompt(prompt['id'])
                            result['pushed'] += 1
                        except Exception as e:
                            result['errors'].append(f"Push failed for {prompt['id']}: {str(e)}")

                # Step 2: Pull remote changes from Drive
                remote_prompts = self.drive.list_prompts()
                for remote_file in remote_prompts:
                    try:
                        remote_data = self.drive.download_prompt(remote_file['id'])

                        # Check if prompt exists locally
                        local_prompt = self.local.load_prompt_by_id(remote_data['id'])

                        if local_prompt:
                            # Check for conflicts
                            if self.detect_conflicts(local_prompt, remote_data):
                                result['conflicts'] += 1
                                # Store conflict for later resolution
                                # (actual resolution happens in UI)
                            else:
                                # Update local with remote if remote is newer
                                if remote_data['updated_at'] > local_prompt['updated_at']:
                                    self._update_local_prompt(remote_data)
                        else:
                            # New prompt from Drive, add to local
                            self._add_prompt_to_local(remote_data)
                            result['pulled'] += 1

                    except Exception as e:
                        result['errors'].append(f"Pull failed for {remote_file['name']}: {str(e)}")

                # Step 3: Process offline queue
                queue_result = self.process_queue()
                result['pushed'] += queue_result.get('processed', 0)

            except Exception as e:
                result['errors'].append(f"Sync failed: {str(e)}")

            return result

    def push_prompt(self, prompt_id: str) -> bool:
        """
        Push single prompt to Drive.

        Args:
            prompt_id: Local prompt ID

        Returns:
            bool: True if successful

        Raises:
            Exception: If upload fails
        """
        prompt = self.local.load_prompt_by_id(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")

        try:
            if prompt.get('drive_file_id'):
                # Update existing file
                self.drive.update_prompt(prompt['drive_file_id'], prompt)
            else:
                # Upload new file
                drive_file_id = self.drive.upload_prompt(prompt)
                # Update local with Drive file ID
                prompt['drive_file_id'] = drive_file_id
                prompt['sync_status'] = 'synced'
                prompt['last_synced_at'] = datetime.now().isoformat()
                self.local.save_prompt(**prompt)  # Update local

            return True

        except Exception as e:
            # Queue for retry
            self.queue_offline_operation(SyncOperation(
                operation_type='push',
                prompt_id=prompt_id
            ))
            raise e

    def pull_prompts(self) -> List[dict]:
        """
        Pull all prompts from Drive.

        Returns:
            List[dict]: List of pulled prompts
        """
        pulled = []
        remote_prompts = self.drive.list_prompts()

        for remote_file in remote_prompts:
            try:
                remote_data = self.drive.download_prompt(remote_file['id'])
                local_prompt = self.local.load_prompt_by_id(remote_data['id'])

                if not local_prompt:
                    # New prompt, add to local
                    self._add_prompt_to_local(remote_data)
                    pulled.append(remote_data)
                else:
                    # Check if remote is newer
                    if remote_data['updated_at'] > local_prompt['updated_at']:
                        if self.detect_conflicts(local_prompt, remote_data):
                            # Conflict detected, don't auto-update
                            pass
                        else:
                            self._update_local_prompt(remote_data)
                            pulled.append(remote_data)

            except Exception as e:
                # Log error but continue with other prompts
                pass

        return pulled

    def detect_conflicts(self, local: dict, remote: dict) -> bool:
        """
        Detect if prompt has conflicting changes.

        A conflict occurs when:
        - Both local and remote have been modified since last sync
        - Timestamps indicate divergent changes
        - Content differs

        Args:
            local: Local prompt data
            remote: Remote prompt data

        Returns:
            bool: True if conflict detected
        """
        # If one side hasn't been synced before, no conflict
        if not local.get('last_synced_at') or not remote.get('last_synced_at'):
            return False

        # Check if both modified after last sync
        local_modified = datetime.fromisoformat(local['updated_at'])
        remote_modified = datetime.fromisoformat(remote['updated_at'])
        last_sync = datetime.fromisoformat(local['last_synced_at'])

        both_modified = (local_modified > last_sync) and (remote_modified > last_sync)

        if both_modified:
            # Check if content actually differs
            content_differs = (
                local['optimized_prompt'] != remote['optimized_prompt'] or
                local['name'] != remote['name']
            )
            return content_differs

        return False

    def resolve_conflict(self, conflict: 'Conflict',
                        resolution: 'ConflictResolution') -> dict:
        """
        Apply user's conflict resolution choice.

        Args:
            conflict: Conflict object with local and remote versions
            resolution: User's choice (KEEP_LOCAL, KEEP_REMOTE, KEEP_BOTH)

        Returns:
            dict: Resolved prompt data
        """
        if resolution == ConflictResolution.KEEP_LOCAL:
            # Overwrite remote with local
            self.drive.update_prompt(
                conflict.local_version['drive_file_id'],
                conflict.local_version
            )
            return conflict.local_version

        elif resolution == ConflictResolution.KEEP_REMOTE:
            # Overwrite local with remote
            self._update_local_prompt(conflict.remote_version)
            return conflict.remote_version

        elif resolution == ConflictResolution.KEEP_BOTH:
            # Rename local copy and create new Drive file
            local_copy = conflict.local_version.copy()
            local_copy['name'] += f" (Local Copy {datetime.now().strftime('%Y-%m-%d')})"
            local_copy['id'] = str(uuid.uuid4())  # New ID
            local_copy.pop('drive_file_id', None)  # Remove Drive ID

            # Save as new prompt
            self.local.save_prompt(**local_copy)
            self.push_prompt(local_copy['id'])

            # Also update original with remote
            self._update_local_prompt(conflict.remote_version)

            return conflict.remote_version

        return None

    def queue_offline_operation(self, operation: 'SyncOperation'):
        """
        Queue operation for later sync when offline.

        Args:
            operation: SyncOperation object
        """
        self.sync_queue.enqueue(operation)

    def process_queue(self) -> dict:
        """
        Process all queued operations.

        Returns:
            dict: {'processed': int, 'failed': int}
        """
        result = {'processed': 0, 'failed': 0}

        while True:
            operation = self.sync_queue.dequeue()
            if not operation:
                break

            try:
                if operation.operation_type == 'push':
                    self.push_prompt(operation.prompt_id)
                elif operation.operation_type == 'pull':
                    # Pull specific prompt
                    pass
                elif operation.operation_type == 'delete':
                    self.drive.delete_prompt(operation.drive_file_id)

                self.sync_queue.mark_completed(operation.operation_id)
                result['processed'] += 1

            except Exception as e:
                # Retry logic
                if operation.retry_count < 3:
                    self.sync_queue.mark_failed(
                        operation.operation_id,
                        str(e),
                        operation.retry_count + 1
                    )
                else:
                    # Max retries exceeded
                    result['failed'] += 1

        return result

    def _update_local_prompt(self, remote_data: dict):
        """Update local prompt with remote data"""
        # Implementation depends on LocalStoragePromptDB interface
        pass

    def _add_prompt_to_local(self, remote_data: dict):
        """Add new prompt from Drive to local storage"""
        self.local.save_prompt(**remote_data)
```

#### 4. `sync_queue.py` - Offline Queue Manager

```python
class SyncQueue:
    """
    Persistent queue for offline sync operations.
    Stored in SQLite database.
    """

    def __init__(self, db_path: str = "sync_queue.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def enqueue(self, operation: SyncOperation):
        """Add operation to queue"""
        pass

    def dequeue(self) -> Optional[SyncOperation]:
        """Get next operation from queue"""
        pass

    def mark_completed(self, operation_id: str):
        """Mark operation as completed"""
        pass

    def mark_failed(self, operation_id: str, error: str, retry_count: int):
        """Mark operation as failed, schedule retry"""
        pass

    def get_pending_count(self) -> int:
        """Get count of pending operations"""
        pass

    def clear_queue(self):
        """Clear all operations (on user request)"""
        pass
```

### Data Models

#### Prompt Metadata Extensions (LocalStorage JSON Format)

**IMPORTANT**: This app uses **LocalStorage** (browser storage) for prompt data, NOT SQLite for prompts.
The SQLite database is ONLY used for the sync queue (offline operations).

Prompts are stored as JSON objects in browser LocalStorage via `streamlit-local-storage` library.

```python
# Extend existing prompt structure (stored in LocalStorage as JSON)
{
    # === Existing fields (already in use) ===
    'id': 'uuid',                          # Unique prompt ID
    'name': 'string',                      # User-defined prompt name
    'original_prompt': 'string',           # Original prompt before optimization
    'optimized_prompt': 'string',          # Optimized prompt after analysis
    'analysis_scores': {},                 # Dict of analysis metrics
    'tags': [],                            # List of user tags
    'language': 'string',                  # Language code (zh_TW, en, ja)
    'created_at': 'iso8601',               # ISO 8601 timestamp
    'updated_at': 'iso8601',               # ISO 8601 timestamp

    # === NEW: Google Drive sync fields (added by this feature) ===
    'drive_file_id': 'string | null',      # Google Drive file ID (null if not synced)
    'drive_modified_time': 'iso8601 | null', # Drive's modifiedTime from API
    'last_synced_at': 'iso8601 | null',    # Last successful sync timestamp
    'sync_status': 'synced | pending | conflict | error | not_synced',  # Sync state
    'sync_error': 'string | null'          # Error message if sync failed
}
```

**Migration Strategy for Existing Users**:
- Existing prompts in LocalStorage will NOT have sync fields initially
- On first sync, sync fields will be added with default values:
  ```python
  prompt.setdefault('drive_file_id', None)
  prompt.setdefault('last_synced_at', None)
  prompt.setdefault('sync_status', 'not_synced')
  prompt.setdefault('sync_error', None)
  ```
- No data loss, fully backward compatible

**LocalStorage Key**: `"prompt_tool_prompts"` (existing key, unchanged)

#### Sync Operation Model

```python
class SyncOperation:
    operation_id: str          # UUID
    operation_type: str        # 'push' | 'pull' | 'delete'
    prompt_id: str             # Local prompt ID
    drive_file_id: str | None  # Drive file ID (for pull/delete)
    timestamp: datetime        # When operation was created
    retry_count: int           # Number of retry attempts
    status: str                # 'pending' | 'processing' | 'completed' | 'failed'
    error_message: str | None  # Error details if failed
```

#### Conflict Model

```python
class Conflict:
    prompt_id: str
    local_version: dict        # Local prompt data
    remote_version: dict       # Drive prompt data
    conflict_type: str         # 'modify_modify' | 'delete_modify'
    detected_at: datetime

class ConflictResolution(Enum):
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    KEEP_BOTH = "keep_both"
    MANUAL_MERGE = "manual_merge"
```

### API Endpoints (Google Drive API v3)

**OAuth 2.0 Endpoints:**
- Authorization URL: `https://accounts.google.com/o/oauth2/v2/auth`
- Token Exchange: `https://oauth2.googleapis.com/token`
- Token Revocation: `https://oauth2.googleapis.com/revoke`

**Drive API Endpoints:**
- Create File: `POST /drive/v3/files`
- Update File: `PATCH /drive/v3/files/{fileId}`
- Get File Metadata: `GET /drive/v3/files/{fileId}`
- Download File: `GET /drive/v3/files/{fileId}?alt=media`
- List Files: `GET /drive/v3/files?q={query}`
- Delete File: `DELETE /drive/v3/files/{fileId}`

**Example: Upload Prompt**
```python
file_metadata = {
    'name': f'{prompt_id}.json',
    'parents': [prompts_folder_id],
    'mimeType': 'application/json'
}
media = MediaFileUpload('prompt.json', mimetype='application/json', resumable=True)
file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, name, modifiedTime'
).execute()
```

### Technology Stack

**New Dependencies:**
```python
# requirements.txt additions
google-auth>=2.35.0                    # OAuth authentication
google-auth-oauthlib>=1.2.1            # OAuth flow helpers
google-auth-httplib2>=0.2.0            # HTTP transport for auth
google-api-python-client>=2.150.0      # Drive API client
aiohttp>=3.10.0                        # Async HTTP for background sync
```

**Configuration:**
```yaml
# config/config.yaml additions
google_drive:
  enabled: false                       # Enable/disable sync
  auto_sync: true                      # Auto vs manual sync
  sync_interval_seconds: 300           # Auto-sync every 5 minutes
  batch_size: 50                       # Max prompts per batch
  retry_max_attempts: 3                # Max retry for failed operations
  folder_name: "Prompt Tool"           # Drive folder name
  conflict_resolution_default: "ask_user"  # ask_user | keep_local | keep_remote
```

**Environment Variables:**
```bash
# .env additions
GOOGLE_OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501/oauth/callback
```

### Integration with Existing Code

**Changes to `app.py`:**
```python
# Add at top
from google_drive_sync import GoogleDriveSync, SyncStatus
from google_auth import GoogleAuthManager
import threading

# In sidebar, add authentication UI
if st.session_state.get('google_drive_enabled', False):
    auth_manager = GoogleAuthManager()

    # Handle OAuth callback (check URL query parameters)
    query_params = st.query_params
    if 'code' in query_params:
        try:
            auth_code = query_params['code']
            auth_manager.handle_oauth_callback(auth_code)
            # Clear query params and reload
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")

    if not auth_manager.is_authenticated():
        # Generate OAuth URL and display as clickable link
        auth_url = auth_manager.initiate_oauth_flow()
        st.markdown(f"### 🔐 Enable Google Drive Sync")
        st.markdown(f"[**Sign in with Google**]({auth_url})")
        st.caption("Click above to authorize access to Google Drive")
    else:
        user_info = auth_manager.get_user_info()
        st.success(f"✅ Signed in as {user_info['email']}")

        # Sync status indicator
        sync_status = st.session_state.get('sync_status', SyncStatus.UNKNOWN)
        last_sync = st.session_state.get('last_sync_time', None)

        if sync_status == SyncStatus.SYNCED and last_sync:
            st.info(f"✅ Synced - {last_sync}")
        elif sync_status == SyncStatus.SYNCING:
            st.warning("🔄 Syncing...")
        elif sync_status == SyncStatus.OFFLINE:
            queued = st.session_state.get('queued_operations', 0)
            st.warning(f"⚠️ Offline - {queued} operations queued")
        elif sync_status == SyncStatus.ERROR:
            st.error("❌ Sync error - Click for details")

        # Sync Now button (runs in background thread)
        if st.button("🔄 Sync Now"):
            if sync_status != SyncStatus.SYNCING:
                st.session_state.sync_status = SyncStatus.SYNCING

                def sync_in_background():
                    try:
                        sync_service = st.session_state.get('google_drive_sync')
                        result = sync_service.sync_all()
                        st.session_state.sync_status = SyncStatus.SYNCED
                        st.session_state.last_sync_time = "Just now"
                    except Exception as e:
                        st.session_state.sync_status = SyncStatus.ERROR
                        st.session_state.sync_error = str(e)

                thread = threading.Thread(target=sync_in_background, daemon=True)
                thread.start()
                st.rerun()

        if st.button("🚪 Sign Out"):
            auth_manager.revoke_token()
            st.session_state.pop('google_drive_sync', None)
            st.rerun()
```

**Changes to `LocalStoragePromptDB.save_prompt()`:**
```python
def save_prompt(self, name: str, original_prompt: str, optimized_prompt: str,
                analysis_scores: Dict = None, tags: List[str] = None,
                language: str = "zh_TW") -> str:
    # ... existing save logic ...

    # NEW: Trigger sync if Google Drive enabled
    if st.session_state.get('google_drive_enabled'):
        sync_service = st.session_state.get('google_drive_sync')
        if sync_service:
            sync_service.queue_push(prompt_id)

    return prompt_id
```

### UI Components

**Authentication UI (Both Modes)**
- Location: Sidebar top section
- Components:
  - "Sign in with Google" button (unauthenticated state)
  - User avatar + email display (authenticated state)
  - Sync status badge with color coding (green=synced, yellow=syncing, red=error)
  - "Sign Out" button

**Sync Status Indicator**
- Location: Fixed header/sidebar badge
- States:
  - ✅ Synced (green) - Last synced: 2 minutes ago
  - 🔄 Syncing... (yellow) - Uploading 3 prompts
  - ⚠️ Offline (orange) - 5 operations queued
  - ❌ Error (red) - Click for details

**Conflict Resolution Dialog**
```
┌─────────────────────────────────────────────┐
│  Conflict Detected                          │
├─────────────────────────────────────────────┤
│  The prompt "Customer Service Template" has │
│  been modified both locally and in Drive.   │
│                                             │
│  ┌─────────────────┬─────────────────┐     │
│  │  Local Version  │  Drive Version  │     │
│  ├─────────────────┼─────────────────┤     │
│  │ Updated: 2 min  │ Updated: 5 min  │     │
│  │ ago             │ ago             │     │
│  │                 │                 │     │
│  │ [Prompt text]   │ [Prompt text]   │     │
│  └─────────────────┴─────────────────┘     │
│                                             │
│  Choose resolution:                         │
│  ○ Keep Local Version                       │
│  ○ Keep Drive Version                       │
│  ○ Keep Both (will rename local copy)       │
│  ○ Manual Merge (advanced)                  │
│                                             │
│  [ Cancel ]  [ Apply Resolution ]           │
└─────────────────────────────────────────────┘
```

**Settings Panel Additions**
```
Google Drive Sync
├─ [ ] Enable Google Drive Sync
├─ Sync Mode: [●] Auto  [ ] Manual
├─ Auto-sync interval: [5 minutes ▼]
├─ Default conflict resolution: [Ask me each time ▼]
├─ Sync these tags only: [All tags ▼]
└─ [View Sync History]
```

---

## 4. Error Handling

### Input Validation

**OAuth Redirect Validation**
- Verify `state` parameter matches expected value (CSRF protection)
- Validate authorization code format before exchange
- Check redirect URI matches registered URI exactly

**Prompt Data Validation**
- Ensure prompt ID is valid UUID before syncing
- Validate JSON structure before uploading to Drive
- Check file size limits (Google Drive: 5TB per account, reasonable prompt size < 1MB)

**Token Validation**
- Verify token expiration before each API call
- Attempt token refresh if expired (< 5 minutes remaining)
- Re-authenticate if refresh fails

### Edge Cases

**Edge Case 1: User Deletes Drive Folder Manually**
- Detection: List files API returns empty or folder not found
- Handling: Show warning "Drive folder deleted. Recreate?" with [Yes] [No] buttons
- Resolution: If Yes, call `ensure_folder_structure()` and re-upload all local prompts
- Prevent data loss: Never auto-delete local data

**Edge Case 2: Duplicate Prompts (Same Name, Different ID)**
- Detection: Search Drive for existing file with same name
- Handling: Append timestamp to filename: `prompt-name-2025-01-12T14-30-00.json`
- User notification: "Duplicate name detected, renamed automatically"

**Edge Case 3: Large Prompt Library (1000+ prompts)**
- Detection: Check prompt count before full sync
- Handling: Implement pagination for Drive API list calls (pageSize=100)
- Progress indicator: "Syncing prompts: 234 / 1000 (23%)"
- Time estimate: "Estimated time remaining: 2 minutes"

**Edge Case 4: Network Interruption During Upload**
- Detection: Catch network exceptions during API call
- Handling: Use resumable upload for large files (>5MB)
- Retry logic: Exponential backoff (1s, 2s, 4s)
- Queue for later: If max retries exceeded, add to offline queue

**Edge Case 5: Google Workspace Admin Restrictions**
- Detection: API returns 403 Forbidden with "adminPolicyEnforced"
- Handling: Show user-friendly message: "Your organization restricts Drive access. Contact IT admin."
- Fallback: Offer to continue with local storage only
- Documentation: Link to Google Workspace admin setup guide

**Edge Case 6: Token Revoked While App Running**
- Detection: API returns 401 Unauthorized
- Handling: Clear stored tokens, redirect to sign-in flow
- User message: "Session expired. Please sign in again."
- Preserve unsaved work: Queue pending operations before sign-in

### Failure Scenarios

**Scenario 1: Google Drive API Rate Limit Exceeded**
- Detection: API returns 429 Too Many Requests with `Retry-After` header
- Recovery: Respect `Retry-After` delay, exponential backoff if not provided
- User Experience: Show "Google Drive is busy. Retrying in X seconds..."
- Logging: Log rate limit events for debugging
- Prevention: Implement batch operations and request throttling

**Scenario 2: Invalid OAuth Client Credentials**
- Detection: Token exchange returns 400 Bad Request
- Recovery: Not recoverable automatically
- User Message: "Configuration error. Contact administrator."
- Admin Action: Check `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in .env
- Documentation: Provide setup guide for creating OAuth credentials

**Scenario 3: Drive Storage Quota Exceeded**
- Detection: Upload returns 403 Forbidden with "storageQuotaExceeded"
- Recovery: Not recoverable by app
- User Message: "Google Drive storage full. Free up space or upgrade storage."
- Action Button: [Open Google Drive to Manage Storage]
- Fallback: Continue with local storage, disable auto-sync

**Scenario 4: Corrupted Prompt Data in Drive**
- Detection: JSON parse error when downloading prompt
- Recovery: Skip corrupted file, log error, continue with other prompts
- User Message: "1 prompt could not be synced (corrupted data)"
- Detail View: Show filename and error in sync history
- Manual Fix: Provide option to delete corrupted file from Drive

### Error Messages (User-Facing)

**Authentication Errors**
- ✅ Good: "Sign in failed. Please try again or check your internet connection."
- ❌ Bad: "OAuth token exchange returned HTTP 400"

**Sync Errors**
- ✅ Good: "Couldn't sync 3 prompts. They'll sync automatically when you're back online."
- ❌ Bad: "Drive API batch request failed with ConnectionResetError"

**Conflict Errors**
- ✅ Good: "This prompt was edited both here and in Drive. Choose which version to keep."
- ❌ Bad: "Conflict detected: remote.updated_at > local.updated_at"

**Storage Errors**
- ✅ Good: "Your Google Drive is full. Free up space to continue syncing."
- ❌ Bad: "quotaExceeded: The user's Drive storage quota has been exceeded"

### Retry Logic

**Strategy: Exponential Backoff with Jitter**
```python
def retry_with_backoff(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except RetryableError as e:
            if attempt == max_attempts - 1:
                raise  # Final attempt failed

            # Exponential backoff: 1s, 2s, 4s
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

**Retryable Errors**
- Network timeouts (socket.timeout)
- Connection errors (ConnectionError)
- Rate limits (429 Too Many Requests)
- Temporary server errors (500, 502, 503, 504)

**Non-Retryable Errors**
- Authentication failures (401 Unauthorized)
- Permission denied (403 Forbidden, not rate limit)
- Invalid requests (400 Bad Request)
- Not found (404 Not Found)

---

## 5. Security Considerations

### Authentication & Authorization

**OAuth 2.0 Flow**
- Use Authorization Code Flow with PKCE (Proof Key for Code Exchange) for enhanced security
- Redirect URI must be registered in Google Cloud Console
- Validate `state` parameter on callback to prevent CSRF attacks
- Never expose client secret in client-side code (Streamlit runs server-side, so this is safe)

**Google Drive API Scopes**
- Use minimal required scope: `https://www.googleapis.com/auth/drive.file`
  - This scope only grants access to files created by the app, not all Drive files
  - More secure than `drive.readonly` or full `drive` scope
- Never request `drive` scope (full Drive access) unless absolutely necessary

**Token Storage**
- Store OAuth tokens in Streamlit session state (in-memory, not persistent)
- For production: Consider using encrypted storage (e.g., `cryptography` library with Fernet)
- Never store tokens in browser LocalStorage (XSS vulnerability)
- Tokens expire after 1 hour; refresh tokens valid for 6 months (Google default)

**Token Refresh**
- Automatically refresh access token before expiration (when < 5 minutes remaining)
- Use refresh token to obtain new access token without re-authentication
- If refresh fails, prompt user to sign in again

**Token Revocation**
- On sign out, revoke tokens via Google's revocation endpoint
- This ensures tokens cannot be reused if stolen
- User can also revoke access via Google Account settings

### Data Protection

**Data at Rest**
- Google Drive files are encrypted by Google at rest (AES-256)
- Local SQLite database should be encrypted if storing sensitive prompts
  - Consider using SQLCipher for encrypted SQLite
- Session state tokens are in-memory only (cleared on session end)

**Data in Transit**
- All API calls to Google use HTTPS only (enforced by google-api-python-client)
- Verify SSL certificates (do not disable certificate verification)
- Use TLS 1.2 or higher

**PII Handling**
- User email and name are PII; handle according to privacy policy
- Do not log user emails in application logs (use user ID instead)
- Allow users to delete all data (GDPR "right to be forgotten")
- Prompt content may contain sensitive information; treat as confidential

**GDPR Compliance**
- Provide data export functionality (already exists as JSON export)
- Allow user to delete all data (local + Drive) on account deletion
- Display privacy policy link during OAuth consent
- Obtain user consent before syncing data to Drive

### Input Sanitization

**XSS Prevention**
- Streamlit automatically escapes user input in UI components
- When displaying prompt content, use `st.text_area()` or `st.code()` (both safe)
- Never use `st.markdown()` with user input unless explicitly sanitized

**SQL Injection Prevention**
- Use parameterized queries for all SQLite operations
- Never concatenate user input into SQL strings
- Example (safe):
  ```python
  cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
  ```

**JSON Injection**
- Validate JSON structure when importing prompts from Drive
- Use `json.loads()` with error handling; never use `eval()`
- Limit JSON file size (max 10MB per prompt file)

### API Security

**Rate Limiting**
- Respect Google Drive API quotas:
  - 1,000 requests per 100 seconds per user
  - 10,000 requests per 100 seconds per project
- Implement client-side throttling (max 10 requests/second)
- Use batch requests to reduce API call count

**API Key Security**
- Store OAuth client ID and secret in `.env` file (not in code)
- Never commit `.env` to version control (add to `.gitignore`)
- Rotate client secret periodically (every 90 days)

**Secure Headers**
- Streamlit sets `X-Frame-Options: DENY` by default (prevents clickjacking)
- Set `Content-Security-Policy` to restrict resource loading
- Disable directory listing in production

### Compliance

**SOC 2 (if applicable)**
- Maintain audit logs of all sync operations (who, what, when)
- Implement access controls (only authenticated users can sync)
- Regular security reviews and penetration testing

**Google Cloud Security**
- Enable Google Cloud security features:
  - Advanced Protection Program for high-risk users
  - Security Health Check recommendations
- Monitor OAuth consent screen for suspicious activity

---

## 6. Testing Strategy

### Unit Tests

**Test Framework**: `pytest` with `pytest-asyncio` for async tests

**Coverage Goal**: 85% code coverage for new modules

**google_auth.py Tests**
```python
def test_initiate_oauth_flow_returns_valid_url():
    """OAuth URL contains required parameters (client_id, redirect_uri, scope, state)"""
    pass

def test_handle_oauth_callback_with_valid_code():
    """Valid auth code exchanges for access token"""
    pass

def test_handle_oauth_callback_with_invalid_code():
    """Invalid auth code raises AuthenticationError"""
    pass

def test_refresh_token_success():
    """Expired token refreshes successfully"""
    pass

def test_refresh_token_failure_triggers_reauthentication():
    """Failed refresh clears session and redirects to login"""
    pass

def test_is_authenticated_returns_true_when_token_valid():
    pass

def test_is_authenticated_returns_false_when_token_expired():
    pass
```

**google_drive_client.py Tests**
```python
@mock.patch('google_drive_client.build')
def test_ensure_folder_structure_creates_folders(mock_build):
    """Folder structure created if not exists"""
    pass

@mock.patch('google_drive_client.build')
def test_upload_prompt_success(mock_build):
    """Prompt uploads successfully and returns file ID"""
    pass

@mock.patch('google_drive_client.build')
def test_upload_prompt_with_network_error_retries(mock_build):
    """Network error triggers retry with backoff"""
    pass

@mock.patch('google_drive_client.build')
def test_list_prompts_with_pagination(mock_build):
    """List handles pagination for >100 prompts"""
    pass

@mock.patch('google_drive_client.build')
def test_batch_upload_max_50_prompts(mock_build):
    """Batch upload splits into multiple requests if >50 prompts"""
    pass
```

**google_drive_sync.py Tests**
```python
@pytest.mark.asyncio
async def test_sync_all_pushes_new_local_prompts():
    """New local prompts are pushed to Drive"""
    pass

@pytest.mark.asyncio
async def test_sync_all_pulls_new_remote_prompts():
    """New remote prompts are pulled to local"""
    pass

@pytest.mark.asyncio
async def test_detect_conflicts_returns_true_for_modify_modify():
    """Conflict detected when both local and remote modified"""
    pass

@pytest.mark.asyncio
async def test_resolve_conflict_keep_local():
    """Keep local resolution overwrites Drive version"""
    pass

@pytest.mark.asyncio
async def test_resolve_conflict_keep_remote():
    """Keep remote resolution overwrites local version"""
    pass

@pytest.mark.asyncio
async def test_resolve_conflict_keep_both():
    """Keep both resolution creates two separate prompts"""
    pass

@pytest.mark.asyncio
async def test_queue_offline_operation_persists_to_db():
    """Offline operation saved to sync queue database"""
    pass

@pytest.mark.asyncio
async def test_process_queue_retries_failed_operations():
    """Failed operations retried with exponential backoff"""
    pass
```

**sync_queue.py Tests**
```python
def test_enqueue_adds_operation_to_db():
    pass

def test_dequeue_returns_oldest_pending_operation():
    pass

def test_mark_completed_removes_operation_from_queue():
    pass

def test_mark_failed_increments_retry_count():
    pass

def test_max_retries_moves_operation_to_failed_state():
    pass
```

### Integration Tests

**Test Environment**: Use Google Drive API test account with OAuth playground credentials

**Google Auth + Drive API Integration**
```python
@pytest.mark.integration
def test_end_to_end_oauth_and_upload():
    """
    Full flow: initiate OAuth → exchange code → upload prompt → verify in Drive
    """
    # 1. Initiate OAuth (manual step: user clicks link)
    # 2. Simulate callback with test auth code
    # 3. Upload test prompt
    # 4. Verify file exists in Drive via API
    # 5. Cleanup: delete test file
    pass

@pytest.mark.integration
def test_bidirectional_sync_with_real_drive():
    """
    1. Create prompt locally
    2. Sync to Drive
    3. Modify in Drive via API
    4. Sync back to local
    5. Verify local has Drive changes
    """
    pass

@pytest.mark.integration
def test_conflict_resolution_workflow():
    """
    1. Create prompt locally and sync
    2. Modify locally (don't sync)
    3. Modify in Drive via API
    4. Sync (should detect conflict)
    5. Resolve conflict (keep local)
    6. Verify Drive has local version
    """
    pass
```

**LocalStorage + Drive Sync Integration**
```python
@pytest.mark.integration
def test_local_storage_save_triggers_drive_sync():
    """
    Saving prompt via LocalStoragePromptDB triggers Google Drive upload
    """
    pass

@pytest.mark.integration
def test_drive_pull_updates_local_storage():
    """
    Pulling from Drive updates LocalStorage and UI reflects changes
    """
    pass
```

### E2E Tests (End-to-End)

**Test Tool**: `Playwright` for browser automation

**Critical User Flows**

**E2E Test 1: First-Time User Sign In and Sync**
```python
def test_first_time_user_signin_and_sync(page: Page):
    """
    1. Navigate to app (http://localhost:8501)
    2. Click "Sign in with Google"
    3. Complete OAuth flow (Google login page)
    4. Redirected back to app
    5. Verify "Signed in as user@example.com"
    6. Create new prompt
    7. Save prompt
    8. Verify "Sync Status: Synced" appears
    9. Open Google Drive in new tab
    10. Verify prompt file exists in /Prompt Tool/prompts/
    """
    pass
```

**E2E Test 2: Conflict Resolution UI**
```python
def test_conflict_resolution_ui(page: Page):
    """
    1. Sign in
    2. Create prompt "Test Prompt"
    3. Sync to Drive
    4. Modify prompt locally (don't sync yet)
    5. Manually modify same prompt in Drive (via API)
    6. Click "Sync Now"
    7. Verify conflict dialog appears
    8. Select "Keep Local Version"
    9. Click "Apply Resolution"
    10. Verify sync completes successfully
    11. Verify Drive has local version
    """
    pass
```

**E2E Test 3: Offline Mode and Queue Processing**
```python
def test_offline_mode_and_auto_sync(page: Page):
    """
    1. Sign in and verify connected
    2. Disconnect network (Playwright: offline mode)
    3. Create 3 new prompts
    4. Verify "Offline Mode" indicator
    5. Verify "3 operations queued" message
    6. Reconnect network
    7. Wait for auto-sync (max 10 seconds)
    8. Verify "Sync Status: Synced"
    9. Verify all 3 prompts in Drive
    """
    pass
```

**E2E Test 4: Cross-Device Sync (Simulated)**
```python
def test_cross_device_sync(page1: Page, page2: Page):
    """
    Simulate two devices by opening two browser sessions
    1. Device 1: Sign in, create prompt "Device 1 Prompt"
    2. Device 1: Wait for sync
    3. Device 2: Sign in with same account
    4. Device 2: Verify "Device 1 Prompt" appears in library
    5. Device 2: Create prompt "Device 2 Prompt"
    6. Device 1: Click "Sync Now"
    7. Device 1: Verify "Device 2 Prompt" appears
    """
    pass
```

### Performance Tests

**Test Tool**: `locust` for load testing

**Load Test 1: Sync 100 Prompts**
```python
def test_sync_100_prompts_completes_within_10_seconds():
    """
    Measure time to sync 100 prompts from scratch
    Target: < 10 seconds on broadband (10 Mbps upload)
    """
    pass
```

**Load Test 2: Concurrent Users**
```python
class PromptToolUser(HttpUser):
    @task
    def sync_prompt(self):
        """Simulate 50 concurrent users syncing prompts"""
        pass

# Run: locust -f performance_test.py --users 50 --spawn-rate 10
# Target: 95th percentile response time < 3 seconds
```

**Stress Test: 1000 Prompts**
```python
def test_sync_1000_prompts_performance():
    """
    Verify app handles large libraries without degradation
    Measure: memory usage, API call count, total time
    Target: < 2 minutes, < 500MB RAM
    """
    pass
```

### Test Environment Setup

**Requirements**
- Python 3.9+
- pytest, pytest-asyncio, pytest-mock
- playwright (with browser drivers)
- locust
- Google Drive API test account

**Mock Services**
```python
# tests/mocks/mock_drive_service.py
class MockDriveService:
    """
    Mock Google Drive API for unit tests.
    Simulates file upload, download, list operations without real API calls.
    """
    def __init__(self):
        self.files = {}  # In-memory file storage

    def files(self):
        return MockFilesResource(self.files)
```

**Test Data**
```python
# tests/fixtures/test_prompts.py
SAMPLE_PROMPTS = [
    {
        "id": "test-prompt-1",
        "name": "Customer Service Template",
        "original_prompt": "...",
        "optimized_prompt": "...",
        "tags": ["customer-service", "template"]
    },
    # ... more test prompts
]
```

---

## 7. Deployment Plan

### Deployment Strategy

**Approach**: Feature Flag Rollout with Phased Enablement

This strategy allows us to:
- Deploy code to production without immediately activating the feature
- Test in production environment with limited users
- Rollback easily if critical issues discovered
- Gather real-world feedback before full launch

**Why Feature Flags?**
- Minimize risk: Code is deployed but inactive until flag enabled
- Gradual rollout: Enable for small user cohorts first
- A/B testing: Compare sync vs non-sync user satisfaction
- Emergency rollback: Disable flag without redeploying code

### Rollout Phases

#### Phase -1: OAuth Verification (Week -2 to Week 0) **[NEW - CRITICAL]**

**IMPORTANT**: Google OAuth consent screen verification must be completed BEFORE Phase 1 begins.
This is a BLOCKING requirement for public beta testing.

**Week -2: Submit OAuth Application for Verification**

**Actions**:
1. Create Google Cloud Project for OAuth credentials
2. Configure OAuth consent screen:
   - App name: "Prompt Tool - AI Prompt Optimizer"
   - User support email
   - App logo (if available)
   - Privacy policy URL (must be publicly accessible)
   - Terms of service URL (optional but recommended)
   - Authorized domains: your-domain.com
3. Add OAuth scopes:
   - `https://www.googleapis.com/auth/drive.file` (limited scope)
   - `https://www.googleapis.com/auth/userinfo.email` (for user info)
4. Submit app for verification:
   - Complete verification questionnaire
   - Provide app description and screenshots
   - Explain why Drive access is needed
   - Upload demo video (recommended)
5. Register OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs:
     - `http://localhost:8501` (development)
     - `https://staging.your-domain.com` (staging)
     - `https://your-domain.com` (production)

**Week -1: Monitor Verification Status**

**Expected Timeline**: 1-2 weeks for verification (Google's estimate)

**Possible Outcomes**:
- **Approved**: Proceed to Phase 0
- **Pending**: Wait for Google review, may take up to 4 weeks
- **Additional info requested**: Respond promptly with requested details
- **Rejected**: Address issues and resubmit

**Contingency**:
- If verification not complete by Week 0: Use "unverified app" warning for internal alpha testing only (Week 1)
- Public beta (Week 2+) REQUIRES verified app status

**Verification Checklist**:
- [ ] Privacy policy published and accessible
- [ ] OAuth consent screen configured completely
- [ ] Demo video uploaded showing OAuth flow
- [ ] Verification questionnaire submitted
- [ ] Monitoring submission status daily

**Resources**:
- Google OAuth Verification Guide: https://support.google.com/cloud/answer/9110914
- Verification status dashboard: Google Cloud Console → APIs & Services → OAuth consent screen

---

#### Phase 0: Pre-Deployment (Week 0)

**Prerequisites**:
- ✅ OAuth verification submitted (Week -2)
- ⏳ OAuth verification in progress (or completed)

**Infrastructure Setup**
- Set up feature flag system (use `config/config.yaml` or environment variable)
  ```yaml
  feature_flags:
    google_drive_sync_enabled: false
    google_drive_sync_beta_users: []  # List of beta user emails
  ```
- Create `.env.example` with OAuth configuration template
- Set up staging environment with OAuth credentials (using unverified app if needed)

**Documentation Preparation**
- User guide: "How to Enable Google Drive Sync"
- Admin guide: OAuth setup and troubleshooting
- FAQ: Common questions and answers
- Known limitations document (for unverified app warning, if applicable)

**Stakeholder Communication**
- Announce upcoming feature to users (email, in-app banner)
- Gather initial interest for beta testing (sign-up form)
- Internal team training session
- Brief team on OAuth verification status

#### Phase 1: Internal Alpha Testing (Week 1)

**Target Users**: Internal team only (5-10 people)

**Deployment Steps**
1. Deploy code to staging environment
2. Enable feature flag for internal team emails only
3. Monitor application logs for errors
4. Verify OAuth flow completes successfully
5. Test sync operations (push, pull, conflicts)

**Success Criteria**
- Zero critical bugs (P0: app crashes, data loss)
- OAuth success rate > 95%
- Sync success rate > 90%
- Positive feedback from internal team

**Monitoring**
- Log all sync operations with user ID, timestamp, status
- Set up alerts for:
  - OAuth failures > 5% of attempts
  - Sync failures > 10% of operations
  - API rate limit errors > 10 per hour

**Rollback Trigger**
- Critical data loss reported
- OAuth failures > 20%
- App crashes related to sync feature

#### Phase 2: Closed Beta (Week 2-3)

**Target Users**: 50-100 selected beta testers from sign-up form

**Deployment Steps**
1. Deploy to production environment (feature flag OFF)
2. Add beta user emails to `google_drive_sync_beta_users` list
3. Enable feature flag for beta users only
4. Send beta invite emails with instructions
5. Collect feedback via in-app survey and email

**Beta Selection Criteria**
- Mix of heavy users (>50 prompts) and new users
- Different devices (desktop, tablet)
- Different browsers (Chrome, Firefox, Safari)
- Geographic diversity (different time zones for API latency)

**Feedback Collection**
- In-app survey after first sync: "How was your experience?"
- Weekly check-in email: "Any issues this week?"
- Private Slack/Discord channel for real-time feedback
- Analytics: Track sync frequency, conflict resolution choices

**Success Criteria**
- User satisfaction score > 4/5
- Sync success rate > 95%
- Conflict resolution rate > 90% (no stuck conflicts)
- Zero data loss incidents
- Average sync time < 3 seconds for typical library (20 prompts)

**Known Issues Tolerance**
- Minor UI bugs acceptable (e.g., button text cutoff)
- Performance issues on extreme edge cases (>500 prompts)
- Cosmetic issues in Safari if functionality works

#### Phase 3: Public Rollout (Week 4-6)

**Gradual Percentage Rollout**

**Week 4**: 10% of active users
- Enable feature flag for 10% of users (random selection)
- Monitor for increased support tickets
- Verify infrastructure scales (API rate limits, server load)

**Week 5**: 50% of active users
- If Week 4 successful, increase to 50%
- Continue monitoring metrics
- Address any issues discovered in 10% rollout

**Week 6**: 100% of users (General Availability)
- Enable feature flag for all users
- Remove feature flag code in next release (cleanup)
- Celebrate launch 🎉

**Success Metrics (Week 4-6)**
- Sync adoption rate > 30% within first week of availability
- Support ticket volume increase < 20%
- App crash rate unchanged from pre-launch baseline
- Sync success rate maintained > 95%

**Communication**
- In-app banner: "New Feature: Sync your prompts to Google Drive!"
- Blog post: "Never Lose Your Prompts Again"
- Social media announcement
- Email to all users with tutorial video

### Database Migrations

**New Tables Required (SQLite Only for Sync Queue)**

**IMPORTANT**: The `prompts.db` SQLite database is NOT used for storing prompts in this application.
Prompts are stored in browser LocalStorage. SQLite is ONLY used for:
1. The **sync_queue** table (offline operation queue)
2. The legacy `prompts` table exists but is not actively used in production mode

```sql
-- sync_queue table for offline operations (NEW TABLE)
CREATE TABLE IF NOT EXISTS sync_queue (
    operation_id TEXT PRIMARY KEY,
    operation_type TEXT NOT NULL,  -- 'push' | 'pull' | 'delete'
    prompt_id TEXT NOT NULL,
    drive_file_id TEXT,
    timestamp DATETIME NOT NULL,
    retry_count INTEGER DEFAULT 0,
    status TEXT NOT NULL,  -- 'pending' | 'processing' | 'completed' | 'failed'
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_queue_status ON sync_queue(status);
CREATE INDEX idx_sync_queue_prompt_id ON sync_queue(prompt_id);

-- NOTE: We do NOT alter the prompts table because prompts are stored in LocalStorage,
-- not in SQLite. The prompts table in prompts.db is only used in legacy/development mode.
```

**Migration Script**
```python
# migrations/add_google_drive_sync.py
def upgrade():
    """Apply migration"""
    conn = sqlite3.connect('prompts.db')
    cursor = conn.cursor()

    # Create sync_queue table
    cursor.execute(CREATE_SYNC_QUEUE_SQL)

    # Add columns to prompts (with error handling for already-exists)
    for column in SYNC_COLUMNS:
        try:
            cursor.execute(f"ALTER TABLE prompts ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass  # Column already exists (idempotent)

    conn.commit()
    conn.close()

def downgrade():
    """Rollback migration (if needed)"""
    # Drop sync_queue table
    # Remove sync columns (not possible in SQLite, requires table recreation)
    pass
```

**Migration Execution**
- Run during deployment: `python migrations/add_google_drive_sync.py`
- Zero downtime: New columns have defaults, app remains functional
- Rollback plan: If rollback needed, sync_queue table can be ignored

### Monitoring & Alerts

**Key Metrics to Monitor**

```yaml
# Monitoring Dashboard (e.g., Grafana, Datadog)
metrics:
  authentication:
    - oauth_initiate_count (counter)
    - oauth_success_count (counter)
    - oauth_failure_count (counter)
    - oauth_success_rate (gauge, %)

  sync_operations:
    - sync_push_count (counter)
    - sync_pull_count (counter)
    - sync_success_count (counter)
    - sync_failure_count (counter)
    - sync_success_rate (gauge, %)
    - sync_duration_seconds (histogram, p50/p95/p99)

  conflicts:
    - conflicts_detected_count (counter)
    - conflicts_resolved_count (counter)
    - conflicts_unresolved_count (gauge)

  offline_queue:
    - queue_size (gauge)
    - queue_age_seconds (gauge, oldest operation)

  google_api:
    - api_calls_count (counter, by endpoint)
    - api_errors_count (counter, by error code)
    - api_rate_limit_errors (counter)

  user_adoption:
    - sync_enabled_users (gauge)
    - active_sync_users_daily (gauge)
    - prompts_synced_total (counter)
```

**Alert Thresholds**

```yaml
alerts:
  critical:  # Page on-call engineer immediately
    - name: "High OAuth Failure Rate"
      condition: oauth_success_rate < 80%
      duration: 5m

    - name: "High Sync Failure Rate"
      condition: sync_success_rate < 85%
      duration: 5m

    - name: "Data Loss Detected"
      condition: data_loss_events > 0
      duration: 1m

  warning:  # Notify team, investigate during business hours
    - name: "Elevated API Errors"
      condition: api_errors_count > 50/hour
      duration: 15m

    - name: "Large Offline Queue"
      condition: queue_size > 1000
      duration: 30m

    - name: "Slow Sync Performance"
      condition: sync_duration_p95 > 5s
      duration: 10m

  info:  # Log for trends, no immediate action
    - name: "Feature Adoption"
      condition: sync_enabled_users increased by 20%
      duration: 1d
```

**Logging Strategy**

```python
# Log all sync operations
logger.info("Sync operation started", extra={
    "user_id": user_id,
    "operation_type": "push",
    "prompt_id": prompt_id,
    "prompt_count": 1
})

logger.info("Sync operation completed", extra={
    "user_id": user_id,
    "operation_type": "push",
    "prompt_id": prompt_id,
    "duration_seconds": 1.23,
    "status": "success"
})

# Log errors with context
logger.error("Sync operation failed", extra={
    "user_id": user_id,
    "operation_type": "push",
    "prompt_id": prompt_id,
    "error_code": "RATE_LIMIT_EXCEEDED",
    "error_message": "Quota exceeded for quota metric...",
    "retry_count": 2
})
```

### Rollback Plan

**Rollback Triggers**
- Critical data loss (any user reports data disappeared)
- OAuth success rate drops below 70% for > 10 minutes
- Sync success rate drops below 80% for > 15 minutes
- App crash rate increases by > 50% compared to baseline
- Security vulnerability discovered (e.g., token leak)

**Rollback Procedure (< 5 minutes)**

1. **Immediate: Disable Feature Flag**
   ```bash
   # Production server
   echo "google_drive_sync_enabled: false" > config/config.yaml
   # Or set environment variable
   export GOOGLE_DRIVE_SYNC_ENABLED=false
   # Restart app (auto-reloads config)
   ```

2. **Verify Rollback Success**
   - Check monitoring: sync operation metrics drop to zero
   - Verify app still functional (local storage still works)
   - Check user-facing UI: sync buttons/indicators hidden

3. **Communication**
   - Post status page update: "Google Drive sync temporarily disabled"
   - Send email to beta users (if in Phase 2): "We've paused sync to investigate an issue"

4. **Investigation**
   - Pull logs for time window when issue occurred
   - Identify root cause
   - Develop fix and test in staging

5. **Gradual Re-Enable**
   - Fix deployed to staging and tested
   - Enable for internal team first (Phase 1 repeat)
   - If stable for 24 hours, resume phased rollout

**Data Safety**
- Rollback does NOT delete any data (local or Drive)
- Users retain all prompts in LocalStorage
- Prompts already synced to Drive remain there
- Re-enabling sync will resume from last sync point (no duplicates)

**Rollback Testing**
- Practice rollback procedure in staging monthly
- Measure time to rollback: target < 5 minutes
- Document lessons learned and update procedure

---

## 8. Success Metrics

### Key Performance Indicators (KPIs)

**Adoption Metrics**
- **Sync Enablement Rate**: % of active users who enable Google Drive sync
  - Target: 40% within 30 days of general availability
  - Measurement: `sync_enabled_users / total_active_users * 100`
  - Tracked: Daily via analytics dashboard

- **Feature Activation Rate**: % of users who complete OAuth flow after clicking "Sign in"
  - Target: 85% (15% drop-off acceptable for OAuth consent screen)
  - Measurement: `oauth_success / oauth_initiated * 100`
  - Tracked: Real-time in monitoring system

- **Active Sync Users**: Number of users who sync at least once per week
  - Target: 70% of users who enabled sync
  - Measurement: Count distinct users with `last_synced_at` within 7 days
  - Tracked: Weekly cohort analysis

**Reliability Metrics**
- **Sync Success Rate**: % of sync operations that complete successfully
  - Target: 95% (industry standard for sync services)
  - Measurement: `successful_syncs / total_sync_attempts * 100`
  - Tracked: Real-time with 5-minute alert window

- **Conflict Resolution Rate**: % of conflicts resolved without user dropping off
  - Target: 90% (10% may close dialog and ignore conflict)
  - Measurement: `conflicts_resolved / conflicts_detected * 100`
  - Tracked: Daily

- **Data Loss Incidents**: Number of reports of missing prompts
  - Target: Zero (absolute requirement)
  - Measurement: Manual tracking via support tickets + automated detection
  - Tracked: Immediately flagged as P0 incident

**Performance Metrics**
- **Average Sync Time**: Median time for single prompt sync
  - Target: < 2 seconds (p50)
  - Measurement: `sync_duration_seconds` histogram median
  - Tracked: Real-time with p50, p95, p99 percentiles

- **Initial Sync Time**: Time to sync existing library on first enable
  - Target: < 10 seconds for 100 prompts on broadband
  - Measurement: `initial_sync_duration` (tagged separately)
  - Tracked: Per user, aggregated weekly

- **Offline Queue Processing Time**: Time to clear queue after reconnection
  - Target: < 5 seconds for 10 queued operations
  - Measurement: `queue_processing_duration`
  - Tracked: When queue is processed

**User Satisfaction Metrics**
- **Feature Satisfaction Score**: In-app survey rating
  - Target: 4.0/5.0 or higher
  - Measurement: "How satisfied are you with Google Drive sync?" (1-5 scale)
  - Tracked: Survey after first sync + quarterly pulse

- **Net Promoter Score (NPS)**: Likelihood to recommend feature
  - Target: NPS > 30 (good for B2B SaaS features)
  - Measurement: "How likely are you to recommend this feature?" (0-10)
  - Tracked: Quarterly survey

- **Support Ticket Volume**: Number of sync-related support tickets
  - Target: < 5% of total support volume
  - Measurement: Manual tagging of tickets by category
  - Tracked: Weekly support team review

### Success Criteria (Go/No-Go for Full Launch)

**Phase 2 → Phase 3 Decision (Closed Beta → Public Rollout)**

Must meet ALL criteria to proceed:
1. ✅ Sync success rate > 95% over 7-day period
2. ✅ Zero data loss incidents in beta
3. ✅ User satisfaction score > 4.0/5.0
4. ✅ OAuth success rate > 85%
5. ✅ Conflict resolution rate > 90%
6. ✅ No P0 or P1 bugs open
7. ✅ Average sync time < 3 seconds (p95)
8. ✅ Positive feedback from > 80% of beta users

If any criterion fails:
- Extend beta period by 1 week
- Address issues identified
- Re-evaluate criteria

**Post-Launch Success (30 days after GA)**

Feature considered successful if:
1. ✅ Adoption rate > 30%
2. ✅ Sync success rate maintained > 95%
3. ✅ Data loss incidents = 0
4. ✅ Support ticket volume < 5% of total
5. ✅ NPS > 30
6. ✅ Week-over-week active sync users growth > 5%

### Monitoring Dashboard

**Real-Time Dashboard (Engineering Team)**
```
Google Drive Sync - Live Metrics
─────────────────────────────────────────────
Sync Operations (Last 1 Hour)
  Success Rate: 97.2% ✅        Target: >95%
  Total Syncs: 1,234
  Failed Syncs: 35
  Avg Duration: 1.8s (p50)     Target: <2s
  p95 Duration: 3.2s           Target: <5s

Authentication (Last 24 Hours)
  OAuth Success Rate: 89.3% ✅  Target: >85%
  Sign-ins: 456
  Failures: 49

Conflicts (Last 7 Days)
  Detected: 23
  Resolved: 21 (91.3%) ✅      Target: >90%
  Pending: 2

Offline Queue
  Current Size: 12             Target: <100
  Oldest Operation: 3m ago     Target: <30m

Errors (Last 1 Hour)
  Rate Limit: 2
  Network Timeout: 8
  Auth Expired: 1
  Other: 3

Alerts
  ⚠️ Warning: API errors elevated (52/hour)
```

**User Adoption Dashboard (Product Team)**
```
Google Drive Sync - Adoption Metrics
─────────────────────────────────────────────
Overall Adoption
  Enabled Users: 4,523 (38.2% of active)
  Target: 40% by Day 30
  Days Since Launch: 24
  On Track: ✅

Weekly Active Sync Users
  This Week: 3,167 (70.0% of enabled)
  Last Week: 2,945
  Growth: +7.5% ✅

Feature Activation Funnel
  Clicked "Sign In": 5,234 (100%)
  Completed OAuth: 4,523 (86.4%) ✅
  First Sync: 4,211 (93.1%)
  Synced >5 times: 3,167 (70.0%)

User Satisfaction
  Avg Rating: 4.3/5 ✅
  NPS: +42 ✅
  Responses: 287

Prompts Synced
  Total: 67,845
  Per User Avg: 15.2
  Max: 412 (power user!)
```

### Review Schedule

**Daily Review (Engineering Lead)**
- Check sync success rate
- Review critical alerts (if any)
- Quick scan of error logs for patterns
- Time: 5 minutes

**Weekly Review (Full Team)**
- Deep dive into metrics trends
- Review support tickets related to sync
- Analyze failed syncs (why did they fail?)
- Discuss feature improvements based on data
- Time: 30 minutes

**Monthly Review (Product & Engineering)**
- Assess progress toward adoption target
- Review user satisfaction survey results
- Identify top 3 pain points from feedback
- Plan next iteration features (e.g., selective sync by tag)
- Time: 1 hour

**Quarterly Review (Leadership)**
- ROI analysis: cost of implementation vs user value
- Decide on future investment (e.g., support other cloud providers?)
- Strategic alignment with product roadmap
- Time: 2 hours

---

## Tasks

Implementation task breakdown for development team:

### Phase 1: Foundation (Week 1-2)
- [ ] Set up Google Cloud Project and create OAuth 2.0 credentials
- [ ] Create `google_auth.py` module with OAuth flow implementation
- [ ] Implement token storage in Streamlit session state
- [ ] Add OAuth callback handler to `app.py`
- [ ] Create "Sign in with Google" UI in both Conversation and Classic modes
- [ ] Write unit tests for `google_auth.py` (>80% coverage)
- [ ] Test OAuth flow end-to-end in local environment

### Phase 2: Drive API Integration (Week 3-4)
- [ ] Create `google_drive_client.py` wrapper for Drive API v3
- [ ] Implement `ensure_folder_structure()` to create `/Prompt Tool/prompts/`
- [ ] Implement `upload_prompt()`, `download_prompt()`, `list_prompts()`
- [ ] Implement `batch_upload()` for efficient bulk operations
- [ ] Add retry logic with exponential backoff for API calls
- [ ] Write unit tests with mocked Drive API service
- [ ] Integration test with real Drive API (test account)

### Phase 3: Sync Engine (Week 5-6)
- [ ] Create `google_drive_sync.py` orchestrator
- [ ] Implement `push_prompt()` to upload single prompt
- [ ] Implement `pull_prompts()` to download from Drive
- [ ] Implement `detect_conflicts()` based on timestamps
- [ ] Implement conflict resolution strategies (keep local/remote/both)
- [ ] Create `sync_queue.py` for offline operation management
- [ ] Add database migration for sync_queue table and prompt sync fields
- [ ] Write unit tests for sync logic
- [ ] Integration test for bidirectional sync

### Phase 4: UI Components (Week 7)
- [ ] Add sync status indicator to sidebar (both modes)
- [ ] Create "Sync Now" button with loading state
- [ ] Build conflict resolution dialog with diff view
- [ ] Add sync settings panel (enable/disable, auto/manual)
- [ ] Implement sync history/activity log view
- [ ] Add user account display (email, sign out button)
- [ ] Test UI responsiveness on desktop and tablet

### Phase 5: Error Handling & Edge Cases (Week 8)
- [ ] Implement user-friendly error messages for all failure scenarios
- [ ] Add offline detection and queue UI indicator
- [ ] Handle Google Drive quota exceeded gracefully
- [ ] Handle revoked tokens (redirect to sign-in)
- [ ] Add rate limiting protection (client-side throttling)
- [ ] Test all edge cases (duplicate names, deleted folders, large libraries)

### Phase 6: Testing (Week 9)
- [ ] Complete unit test suite (target: 85% coverage)
- [ ] Write integration tests for all critical paths
- [ ] Set up Playwright for E2E tests
- [ ] Write E2E tests for: first-time sign-in, conflict resolution, offline mode, cross-device sync
- [ ] Run performance tests (100 prompts, 1000 prompts)
- [ ] Load test with 50 concurrent users

### Phase 7: Documentation & Deployment Prep (Week 10)
- [ ] Write user documentation: "Getting Started with Google Drive Sync"
- [ ] Write admin guide: OAuth setup, troubleshooting
- [ ] Create FAQ document
- [ ] Set up feature flag in `config/config.yaml`
- [ ] Configure monitoring (metrics, logging, alerts)
- [ ] Set up staging environment with OAuth credentials
- [ ] Prepare rollback procedure document

### Phase 8: Alpha Testing (Week 11)
- [ ] Deploy to staging environment
- [ ] Enable feature for internal team (5-10 users)
- [ ] Monitor logs and metrics daily
- [ ] Collect feedback from internal users
- [ ] Fix critical bugs (P0/P1)
- [ ] Performance tuning based on real usage

### Phase 9: Beta Testing (Week 12-13)
- [ ] Deploy to production (feature flag OFF)
- [ ] Select 50-100 beta users
- [ ] Enable feature flag for beta users
- [ ] Send beta invite emails
- [ ] Monitor metrics and collect feedback
- [ ] Address beta feedback and fix bugs
- [ ] Run final go/no-go checklist

### Phase 10: Public Launch (Week 14+)
- [ ] Week 14: Enable for 10% of users
- [ ] Week 15: Enable for 50% of users
- [ ] Week 16: Enable for 100% of users (General Availability)
- [ ] Publish launch announcement (blog, email, social media)
- [ ] Monitor adoption metrics and support tickets
- [ ] Celebrate launch with team 🎉

---

## Open Questions & Risks

### Open Questions

1. **OAuth Consent Screen Verification**
   - Q: Does Google require app verification for OAuth consent screen?
   - Impact: If yes, verification can take 1-2 weeks and delays launch
   - Mitigation: Start verification process early in Phase 1
   - Owner: Engineering Lead

2. **Drive API Quotas**
   - Q: What are the exact quota limits for our expected usage?
   - Impact: If quotas insufficient, may hit rate limits during peak usage
   - Mitigation: Contact Google Cloud support for quota increase if needed
   - Owner: DevOps

3. **Conflict Resolution UX**
   - Q: Should we provide "auto-resolve" option (always keep local/remote)?
   - Impact: UX complexity vs user control trade-off
   - Mitigation: User research with beta users, iterate based on feedback
   - Owner: Product Manager

4. **Sync Interval**
   - Q: What is optimal auto-sync interval? (every 5 min, 10 min, 30 min?)
   - Impact: Affects API usage and battery life on mobile
   - Mitigation: Make configurable, default to 5 minutes, gather analytics
   - Owner: Product Manager

5. **Google Workspace Compatibility**
   - Q: Are there specific requirements for Google Workspace accounts?
   - Impact: Enterprise users may have admin restrictions
   - Mitigation: Test with Workspace account early, document admin setup
   - Owner: Engineering Lead

### Risks & Mitigation

**Risk 1: OAuth Verification Delays Launch**
- Probability: Medium (30%)
- Impact: High (2-week delay)
- Mitigation:
  - Start verification process in Week 1 (parallel to development)
  - Use "unverified app" warning for beta testing (acceptable)
  - Only verified app needed for public launch
- Owner: Engineering Lead

**Risk 2: Google Drive API Rate Limits**
- Probability: Medium (40%)
- Impact: Medium (degraded performance during peak)
- Mitigation:
  - Implement client-side throttling (max 10 req/sec)
  - Use batch API calls where possible
  - Monitor quota usage and request increase proactively
  - Implement queue system to smooth out request spikes
- Owner: Backend Engineer

**Risk 3: User Data Loss Due to Bug**
- Probability: Low (5%)
- Impact: Critical (user trust, potential legal issues)
- Mitigation:
  - Extensive testing in alpha/beta phases
  - Never delete data without explicit user confirmation
  - Always download from Drive before overwriting
  - Maintain sync history log for audit trail
  - Have backup/restore plan documented
- Owner: Engineering Lead + QA

**Risk 4: Poor Adoption (<20%)**
- Probability: Medium (30%)
- Impact: Medium (feature underutilized, wasted effort)
- Mitigation:
  - Prominent feature promotion in UI and email
  - Tutorial video showing value proposition
  - In-app tips: "Tip: Enable sync to never lose your prompts!"
  - Gather feedback on why users don't enable (survey)
- Owner: Product Manager

**Risk 5: Conflicts Confuse Users**
- Probability: Medium (40%)
- Impact: Medium (support burden, user frustration)
- Mitigation:
  - Simple, visual conflict resolution UI with clear explanations
  - Default to "Keep Both" to avoid accidental data loss
  - Add "Learn More" link to help doc explaining conflicts
  - Monitor conflict resolution rate as success metric
- Owner: UX Designer + Product Manager

**Risk 6: Streamlit Session State Limitations**
- Probability: Low (10%)
- Impact: Medium (need alternative token storage)
- Mitigation:
  - Research Streamlit session state limitations early
  - If needed, use encrypted file storage or database for tokens
  - Test with long-running sessions (hours)
- Owner: Backend Engineer

**Risk 7: Cross-Browser Compatibility Issues**
- Probability: Low (15%)
- Impact: Low (affects subset of users)
- Mitigation:
  - Test OAuth flow in Chrome, Firefox, Safari, Edge during alpha
  - Use Playwright for automated cross-browser E2E tests
  - Document known issues for beta testers
- Owner: QA Engineer

---

## Dependencies

### External Services
- **Google Cloud Platform**: OAuth 2.0 server, Drive API v3
  - Status: Production-ready, 99.95% SLA
  - Cost: Free tier (generous), pay-per-use beyond quota
  - Risk: API changes (low, versioned API with deprecation policy)

- **Google Drive Storage**: User's personal Drive accounts
  - Status: Production-ready
  - Dependency: Users must have Google accounts (99% of target users do)
  - Risk: User quota limits (communicate storage usage to users)

### Internal Dependencies
- **Streamlit Framework**: Core app framework
  - Version: >=1.28.0 (current: 1.28.0)
  - Risk: Streamlit session state behavior changes (low, stable API)

- **LocalStoragePromptDB**: Existing storage layer
  - Status: Stable, in production
  - Change: Minor modifications to `save_prompt()` to trigger sync
  - Risk: Low (backward compatible)

- **SQLite Database**: Sync queue storage
  - Status: Stable, in production
  - Change: Add new table `sync_queue`, add columns to `prompts`
  - Risk: Low (migration tested)

### Python Libraries (New Dependencies)
```
google-auth>=2.35.0
google-auth-oauthlib>=1.2.1
google-auth-httplib2>=0.2.0
google-api-python-client>=2.150.0
aiohttp>=3.10.0
```
- All libraries: Stable, mature, well-maintained by Google
- Risk: Low (breaking changes rare, versioned)

### Infrastructure
- **Internet Connectivity**: Required for sync operations
  - Mitigation: Offline mode with queue gracefully handles disconnections

- **OAuth Redirect URI**: Must be registered in Google Cloud Console
  - Dependency: DevOps to configure production URL
  - Risk: Low (one-time setup)

### Team Dependencies
- **UX Designer**: Conflict resolution dialog mockups (Week 6)
- **QA Engineer**: Test plan and execution (Week 9)
- **DevOps**: Production deployment, monitoring setup (Week 10)
- **Support Team**: Training on new feature, FAQ preparation (Week 11)
- **Marketing**: Launch announcement, user communication (Week 14)

---

## Future Enhancements (Out of Scope for V1)

### V1.1: Enhanced Sync Features
- **Selective Sync by Tag**: Only sync prompts with specific tags
  - Use Case: Separate work prompts from personal prompts
- **Shared Folders**: Share prompt libraries with team members via Drive sharing
  - Use Case: Team collaboration on prompt templates
- **Sync Analytics**: Show user stats (total synced, storage used, sync frequency)

### V1.2: Alternative Cloud Providers
- **Dropbox Integration**: For users who prefer Dropbox
- **OneDrive Integration**: For Microsoft 365 users
- **S3-Compatible Storage**: For enterprise self-hosted solutions

### V1.3: Advanced Conflict Resolution
- **Smart Merge**: Auto-merge non-conflicting sections (like git merge)
- **Version History**: View and restore previous versions (leverage Drive revisions)
- **3-Way Merge UI**: Show base version + both changes for manual merge

### V1.4: Mobile App Support
- **iOS App**: Native app with background sync
- **Android App**: Native app with background sync
- **Sync to Mobile**: Access prompts on smartphone

### V1.5: Performance Optimizations
- **Incremental Sync**: Only sync changed fields, not entire prompt
- **Compression**: Compress prompts before upload (save bandwidth)
- **CDN Caching**: Cache frequently accessed prompts

### V2.0: Collaborative Features
- **Real-Time Collaboration**: Multiple users editing same prompt simultaneously (Google Docs-style)
- **Comments & Reviews**: Team members can comment on prompts
- **Approval Workflows**: Submit → Review → Approve process for team prompts

---

## Document Metadata

**Version**: 1.1 (Updated)
**Date**: 2026-01-12
**Author**: Claude Code (AI Specification Generator)
**Status**: Updated - Ready for Final Review
**Reviewers**: Engineering Lead, Product Manager, UX Designer
**Estimated Implementation**: 16 weeks (OAuth Verification + Alpha to GA)
**Target Launch**: Q2 2026

**Revision History**
- **v1.1 (2026-01-12)**: Updated spec addressing critical review findings
  - ✅ **CRITICAL FIX**: Resolved Streamlit OAuth flow implementation (Lines 221-422, 510-579)
    - Replaced non-existent `st.redirect()` with `st.query_params` approach
    - Added complete OAuth flow with query parameter handling
    - Implemented CSRF protection with state parameter
  - ✅ **IMPORTANT FIX**: Changed async/await to threading model (Lines 723-1040)
    - All sync methods now synchronous with threading for background operations
    - Added `threading.Lock()` to prevent concurrent syncs
    - Streamlit-compatible implementation
  - ✅ **IMPORTANT FIX**: Added rate limiting implementation (Lines 424-721)
    - Sliding window rate limiting (max 10 req/sec)
    - Automatic throttling in `_throttle()` method
    - Prevents Google Drive API rate limit errors
  - ✅ **IMPORTANT FIX**: Clarified LocalStorage vs SQLite architecture (Lines 1080-1123, 2091-2120)
    - Prompts stored in browser LocalStorage (JSON), not SQLite
    - SQLite only for sync queue (offline operations)
    - Backward compatible migration strategy documented
  - ✅ **IMPORTANT FIX**: Added OAuth verification phase (Lines 1972-2027)
    - New Phase -1 (Week -2 to 0) for Google OAuth verification
    - Detailed verification checklist and timeline
    - Contingency plan if verification delayed
  - Minor fixes: Enhanced code comments, improved error handling examples

- v1.0 (2026-01-12): Initial specification created

**Changes from v1.0 to v1.1**:
| Component | Change | Reason |
|-----------|--------|--------|
| `google_auth.py` | Complete rewrite with `st.query_params` | Streamlit doesn't have `st.redirect()` |
| `google_drive_client.py` | Added `_throttle()` method | Rate limiting missing |
| `google_drive_sync.py` | Removed `async`/`await`, added threading | Streamlit is synchronous |
| `app.py` integration | Added OAuth callback handler | Handle `?code=xxx` in URL |
| Data Models | Clarified LocalStorage JSON format | Confusion about SQLite usage |
| Deployment Plan | Added Phase -1 (OAuth verification) | Critical blocker for launch |
| Timeline | 14 weeks → 16 weeks | Account for OAuth verification |

**Review Status**:
- ✅ Spec Review Assistant: Reviewed (Score: A / 95/100)
- ⏳ Engineering Lead: Pending review of v1.1 updates
- ⏳ Product Manager: Pending review
- ⏳ UX Designer: Pending review

**Related Documents**
- **Spec Review Report**: `docs/spec/google-drive-sync-spec-review.md` (generated 2026-01-12)
- User Guide: "Getting Started with Google Drive Sync" (to be written)
- Admin Guide: "OAuth Setup and Troubleshooting" (to be written)
- API Documentation: Google Drive API v3 - https://developers.google.com/drive/api/v3/reference
- Google OAuth Verification Guide: https://support.google.com/cloud/answer/9110914

**Approval Sign-Off** (v1.1):
- [ ] Engineering Lead: _______________  Date: ______
- [ ] Product Manager: _______________  Date: ______
- [ ] UX Designer: _______________  Date: ______
- [ ] Security Lead: _______________  Date: ______

**Next Steps**:
1. Engineering Lead: Validate OAuth flow implementation approach
2. DevOps: Initiate Google OAuth verification (Phase -1, Week -2)
3. All stakeholders: Review and approve updated spec
4. Once approved: Begin Phase 1 (Internal Alpha)
