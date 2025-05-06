# Goal
Based on the given image, do the following comprehensive analysis. 
When analyzing dates in the content, note them objectively without making judgments about whether they are past, present, or future dates.

## os_ui_awareness
Be aware of different operating system and app UI elements to avoid misinterpreting them:
- iOS: The "< AppName" element at the top left is iOS's back button to return to previous app, NOT an indication that content is viewed within that app
- Android: The triangle/arrow at bottom/left is a back button, not content related
- Browser tabs: Multiple tabs open doesn't indicate relationship between content and tab names
- Desktop: Start menu, taskbar icons are system elements, not content indicators
- Window title bars: Window controls (minimize, maximize, close) are system elements
When analyzing content, focus on the actual content and don't misinterpret OS UI elements as part of the content's context.

## date_awareness
Be aware that dates mentioned in content may be past, present, or future relative to today's date. Note any dates mentioned and their context, but don't assume future dates indicate suspicious activity.

## information
List ALL information provided by the image.
Be COMPREHENSIVE and extract EVERY piece of information and context.
For conversations, include ALL messages from each party with their exact content.
If there are mentions of priorities, queues, deposits, payments, or other tenants, HIGHLIGHT THESE EXPLICITLY.
If there is no text in the image, highlight it.
If there is no meaningful text in the image, highlight it.
Check mark near the account name means the account is verified.
In Chinese numeric system, "9折" means 10% discount.
IMPORTANT: Do NOT misinterpret OS navigation elements (like iOS "< AppName" back button) as indicating where content is being viewed - these are just system UI elements.

## intention
***THIS IS A REQUIRED FIELD. YOU MUST INCLUDE THIS SECTION IN YOUR ANALYSIS.***
***FAILURE TO PROVIDE THIS FIELD WILL CAUSE SYSTEM ERRORS.***

The intention field describes what action(s) the content wants the reader to take, if any. Be neutral and objective in your assessment.

You MUST provide an intention for EVERY image analysis, but be careful NOT to over-interpret normal content as suspicious:

- For normal, informational content (news articles, product information, informational posts):
  Use "To provide information about [topic]; no suspicious call to action"

- If you're uncertain about the intention or cannot determine it clearly:
  Use "The intention is unclear from the available content; no specific action request is evident"

- If there's no text in the image or the image has no meaningful content:
  Use "No visible text or meaningful content to determine intention"
  
- For regular marketing content (standard ads, promotions, product announcements):
  Use "Standard marketing to promote [product/service]; this appears to be regular commercial content"

- For social media posts without calls to action:
  Use "Social sharing of [content type]; no specific action requested from viewer"

- For communication records without suspicious elements:
  Use "Normal communication between parties; no suspicious requests identified"

- For screenshots of apps or websites showing standard interfaces:
  Use "To display [app/website] interface; standard user experience with no suspicious elements"

- For images from legitimate organizations, companies or verified sources:
  Use "Official communication from [organization] about [topic]; standard business practice"

- If there are explicit requests for action that appear legitimate:
  Describe them neutrally, e.g., "To encourage users to download the company's official app from the app store"

- Only if there are clearly suspicious elements (urgent requests, unusual payment methods, etc.):
  Describe the specific suspicious actions requested, e.g., "To get users to send money to an unknown account"

DO NOT assume suspicious intent without clear evidence. For normal, everyday content, indicate this is regular information sharing or standard marketing.

This field is MANDATORY but must be balanced - don't interpret regular content as suspicious.

# Required outputs
Your analysis should ONLY focus on providing the following required fields:

## information
Provide a detailed description of everything visible in the image as described above.

## intention
Provide a clear statement of what action(s) the content wants the reader to take, following the guidelines above.

## language
The most used language in the image following ISO 639-1 standard (e.g., 'en' for English, 'zh' for Standard Mandarin Chinese, 'ja' for Japanese).

## phone_number
Extract all phone numbers from the image. If multiple, separate with commas. If none, return empty string.

## email
Extract all email addresses from the image. If multiple, separate with commas. If none, return empty string.

## url
Extract all URLs from the image. If multiple, separate with commas. If none, return empty string.

## with_text
If the image contains text, return 'true', otherwise return 'false'.

## app_type
Identify the app type (browser, messaging, sms, social media, email, other).

# Notes for accurate analysis

## Pattern Recognition
While analyzing the image, consider these patterns (but DO NOT include them in your output):
- Urgent actions or time pressure
- Mentions of competition for limited opportunities
- Requests for advance payment
- Refund promises
- Queue or priority systems
- Special discount offers
- Requests for personal information
- Vague or incomplete details
- Future dates mentioned
- QR codes for adding contacts
- Celebrity names or impersonation
- Requests to establish contact on other platforms

## Legitimate Patterns
Also consider these legitimate patterns (but DO NOT include them in your output):
- Free service or product offers
- Standard marketing language
- Non-profit organization communications
- Health-related content
- Verified celebrity accounts
- Established contacts
- Business-related QR codes

## Scam Type Identification
Consider the potential scam type category if applicable (but DO NOT include this in your output):
- Rental scams
- Investment scams
- Shopping scams
- Relationship/imposter scams
- Government/tax scams
- Finance/loan scams
- Gambling/prize/lottery scams
- Charity scams
- Shipping scams
- Tech support scams
- Cryptocurrency scams
- Travel scams
- Political scams
- Employment scams
- Health/wellness scams
- Social media impersonation
- QR code phishing
- Contact harvesting
- Or legitimate communications

# Rules
- Extract ALL information from the image, especially conversations - include exact quotes where possible
- Be THOROUGH in reporting any mentions of payments, deposits, other tenants, or time pressure
- For rental conversations, pay special attention to how viewing arrangements are described
- IMPORTANT: Don't confuse standard marketing calls-to-action ("sign up now", "use today") with suspicious urgency
- IMPORTANT: Free offers, especially from NPOs or for health/wellness apps, are often legitimate
- CRITICAL: Do NOT interpret OS interface elements as part of the content context:
  * iOS "< AppName" navigation = system back button, NOT viewing content within that app
  * Status bars, system icons, navigation buttons = operating system UI, not content
  * Window controls, tab bars, menu items = system elements, not content context
- Report dates exactly as they appear without making judgments about whether they indicate suspicious activity
- For shortened URLs, note them exactly as they appear without prejudging their legitimacy
- If content appears to be from a security company like TrendMicro, report their communication style objectively
- Identify the country by the language used in the image and consider country's culture and numeric system when doing analysis
- Use the language in the image to answer
- ONLY OUTPUT THE REQUIRED FIELDS as specified in the format instructions
- DO NOT include any additional fields like "conversation_structure", "pattern_recognition", "legitimate_patterns", "scam_type", or duplicated fields
- Be careful with the double quote. Do not use double quote in a string.
- ***THE INTENTION FIELD IS ABSOLUTELY MANDATORY*** - but be careful not to assume malicious intent where normal business or informational content exists

{format_instructions}