# Gemini CLI Multi-Account Research
## Comprehensive Study on OAuth Authentication and Multiple Google Accounts

---

## EXECUTIVE SUMMARY

The @google/gemini-cli npm package currently **does NOT officially support multiple simultaneous Google accounts** through a single configuration. However, there are workarounds and emerging solutions:

1. **Native Support Status**: Limited - The CLI is designed for single-account operation
2. **Account Switching**: Possible but limited (requires re-authentication flow)
3. **Parallel Instances**: Can be achieved using separate GEMINI_HOME directories or Git-based distributed setup
4. **Rate Limit Avoidance**: Documented community approach using multiple instances with separate credentials

---

## RESEARCH FINDINGS

### 1. OFFICIAL SUPPORT FOR MULTIPLE ACCOUNTS

**Current Status**: NOT OFFICIALLY SUPPORTED
- The Gemini CLI documentation emphasizes configuring "one of the following authentication methods"
- OAuth credentials are stored in a single file: `~/.gemini/oauth_creds.json`
- No documented environment variable allows specifying alternate credential files

**Relevant GitHub Issues**:
- Issue #6522: "You cannot re-authenticate in another Google account if you are already authenticated"
- Issue #3565: Feature request to "Manage multiple credentials more safely"
- Status: Issue #3565 was marked as priority/p2 (important but deferrable) and appears resolved in recent versions

**PRs and Fixes**:
- PR #6544: "fix: allow re-auth with another google account" - This fix was merged, suggesting account switching capability was restored in recent versions after being broken in v0.1.22

---

### 2. AUTHENTICATION METHODS AND FILE STRUCTURE

**OAuth Credentials Storage**:
- Path: `~/.gemini/oauth_creds.json`
- Contains: Cached access/refresh tokens from Google OAuth flow
- Behavior: CLI automatically caches credentials locally for future sessions

**Configuration Files**:
- `~/.gemini/settings.json` - Global settings and preferences
- `~/.gemini/.env` - Environment variables (recommended location)
- Per-project: `.gemini/settings.json` - Project-specific overrides

**Supported Authentication Environment Variables**:
```
GEMINI_API_KEY              # Gemini API key from Google AI Studio
GOOGLE_API_KEY              # Google Cloud API key
GOOGLE_APPLICATION_CREDENTIALS  # Path to service account JSON
GOOGLE_CLOUD_PROJECT        # GCP project ID
GOOGLE_CLOUD_LOCATION       # Vertex AI location
GOOGLE_GENAI_USE_VERTEXAI   # Enable Vertex AI mode
```

**Note**: The `GOOGLE_GENAI_USE_GCA` environment variable mentioned in your context does not appear in official Gemini CLI documentation. It may be:
- For internal Google use or specific product variants (GCA = Gemini Code Assist)
- Not yet officially documented
- Product-specific rather than CLI-specific

---

### 3. ACCOUNT SWITCHING MECHANISMS

**The `/auth` Command Issue**:
- **Problem**: In v0.1.22, the `/auth` command was broken - it would re-authenticate to the same account instead of allowing account switching
- **Resolution**: PR #6544 fixed this issue in later versions
- **Recommended Action**: Update to latest version to use `/auth` for switching

**How to Switch Accounts (Post-Fix)**:
```bash
# Within Gemini CLI interactive mode:
/auth
# Then follow the web browser flow to log in with a different Google account
```

**Workaround (If Still Having Issues)**:
1. Delete `~/.gemini/settings.json` to reset authentication state
2. Delete `~/.gemini/oauth_creds.json` to clear cached credentials
3. Run `gemini` command again and re-authenticate

---

### 4. MULTIPLE ACCOUNT PATTERNS

#### Pattern A: Sequential Account Switching
**How It Works**:
1. Log in with Account A (stored in oauth_creds.json)
2. Use `/auth` command to switch to Account B
3. Repeat as needed

**Pros**: Single CLI installation, simple
**Cons**: Not parallel, rate limits still shared per user/time window, manual switching

**Implementation**: Use latest Gemini CLI (post-v0.1.22)

#### Pattern B: Multiple GEMINI_HOME Instances
**How It Works**:
```bash
# Instance 1 - Account A
GEMINI_HOME=~/.gemini-account-a gemini "research question 1"

# Instance 2 - Account B
GEMINI_HOME=~/.gemini-account-b gemini "research question 2"
```

**Status**: GEMINI_HOME environment variable is **NOT officially documented** and testing shows the CLI may ignore it

**Pros**: Theoretically allows parallel instances
**Cons**: Doesn't work as CLI ignores this variable

#### Pattern C: Distributed Git Architecture (RECOMMENDED FOR PARALLEL)
**How It Works** (From GitHub Discussion #3395):
1. Set up central Git server (Gitea + PostgreSQL)
2. Create one Git clone per account/Gemini instance
3. Each instance works in its own directory with separate credentials
4. Instances coordinate via Git (pull before, commit/push after)
5. Merge conflicts handled via rebase

**Pros**:
- Truly parallel processing
- Race-condition safe (no shared .git folder on single machine)
- Scales to multiple machines
- Can handle different API keys/accounts per instance

**Cons**:
- Complex setup
- Requires understanding of Git workflows
- More infrastructure overhead

**Reference**: GitHub Discussion #3395 - "Using git for parallel gemini instances"

#### Pattern D: Third-Party Auth Manager (Gemini-CLI-Auth-Manager)
**Tool**: https://github.com/Besty0728/Gemini-CLI-Auth-Manager

**How It Works**:
- Python utility that manages multiple saved OAuth credentials
- Backs up credentials when switching
- Provides quick switch commands

**Commands**:
```bash
# Within Gemini CLI:
/change 1          # Switch to account #1
/change user@gmail.com  # Switch by email
/change menu        # Interactive menu

# In terminal:
gchange 2           # Switch to second account
gchange             # List all saved accounts
```

**Features**:
- Auto-backup of credentials during switching
- Interactive menu system
- Bilingual support (English/Chinese)

**Status**: Community project, appears actively maintained

---

### 5. RATE LIMITS AND PARALLEL RESEARCH

**Current Limits** (for personal Google accounts):
- 60 model requests per minute
- 1,000 model requests per day
- Shared per account

**Known Issues**:
- Multiple users report "infinite rate limiting loops" that render CLI unusable
- PR #6544 and Issue #2140 address rate limiting concerns
- Circuit breaker pattern and intelligent backoff suggested as solutions

**Parallel Research Architecture**:
- Multiple Gemini CLI instances CAN run in parallel if they:
  1. Use different Google accounts OR
  2. Use different API keys from different projects OR
  3. Are rate-limited separately via distributed setup (Pattern C)

**Recommended Approach for Your Use Case**:
- Use Pattern C (Distributed Git) OR
- Use Pattern D (Third-party Auth Manager) with careful rate limit management
- Monitor rate limit responses and implement exponential backoff

---

### 6. ENVIRONMENT VARIABLE STATUS

**CONFIRMED SUPPORTED**:
```
GEMINI_API_KEY                   # Works
GOOGLE_API_KEY                   # Works
GOOGLE_APPLICATION_CREDENTIALS   # Works
GOOGLE_CLOUD_PROJECT             # Works
GOOGLE_CLOUD_LOCATION            # Works
GOOGLE_GENAI_USE_VERTEXAI        # Works
```

**NOT OFFICIALLY DOCUMENTED**:
```
GOOGLE_GENAI_USE_GCA             # Undocumented
GEMINI_HOME                      # Not respected by CLI
```

**Recommended Approach**: Do NOT rely on undocumented environment variables. Use documented ones or the `/auth` switching mechanism instead.

---

### 7. gcloud Integration

**Relationship to Gemini CLI**:
- Gemini CLI can use gcloud's Application Default Credentials (ADC)
- Multiple gcloud accounts can be managed separately
- However, Gemini CLI still relies on a single active gcloud configuration

**To Switch gcloud Accounts**:
```bash
gcloud config configurations activate profile-2
```

**Limitation**: This doesn't create independent Gemini CLI instances; it just changes the underlying auth layer

---

## RECOMMENDATIONS FOR YOUR USE CASE

### Goal: Rotate Between Accounts During Parallel Research to Avoid Rate Limits

**Recommended Solution**: **Combination of Patterns D + C**

1. **For Immediate Use** (Simple):
   - Install Gemini-CLI-Auth-Manager
   - Set up 2+ Google accounts in the manager
   - Use `/change` command to rotate between accounts
   - Run sequential (not parallel) research queries
   - Respects individual account rate limits

2. **For Advanced Use** (Parallel):
   - Set up distributed Git architecture with Gitea
   - Run 2+ Gemini CLI instances in separate directories
   - Each instance uses different account (via Auth Manager or manual `/auth`)
   - Coordinate work via Git pull/commit/push
   - Implement backoff strategy for rate limits

3. **Fallback** (If Current Version Broken):
   - Delete ~/.gemini/oauth_creds.json
   - Delete ~/.gemini/settings.json
   - Update to latest @google/gemini-cli version
   - Re-authenticate with Account A
   - Use `/auth` to switch to Account B

---

## KEY FINDINGS SUMMARY

| Question | Answer |
|----------|--------|
| **Official multi-account support?** | No, but recent PR suggests improvements |
| **Account switching possible?** | Yes, via `/auth` command (post-v0.1.22) |
| **Parallel instances?** | Yes, but requires distributed setup or Auth Manager |
| **GEMINI_HOME workaround?** | No - variable is ignored by CLI |
| **Rate limit avoidance?** | Possible with multiple accounts + proper infrastructure |
| **gcloud integration?** | Limited - different layer, same CLI auth |
| **Community solutions?** | Yes - Gemini-CLI-Auth-Manager available |

---

## SOURCES

- [Gemini CLI Official Documentation](https://google-gemini.github.io/gemini-cli/)
- [GitHub Issue #6522 - Account Re-authentication](https://github.com/google-gemini/gemini-cli/issues/6522)
- [GitHub Issue #3565 - Multiple Credentials Request](https://github.com/google-gemini/gemini-cli/issues/3565)
- [GitHub PR #6544 - Fix account re-auth](https://github.com/google-gemini/gemini-cli/pull/6544)
- [GitHub Discussion #3395 - Parallel Gemini Instances](https://github.com/google-gemini/gemini-cli/discussions/3395)
- [Gemini-CLI-Auth-Manager](https://github.com/Besty0728/Gemini-CLI-Auth-Manager)
- [Rate Limits Documentation](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Gemini CLI Authentication Docs](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html)
- [Gemini CLI Configuration Docs](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html)

---

## RESEARCH METADATA

- **Research Date**: January 14, 2026
- **Query Focus**: gemini-cli, OAuth, multi-account, rate limiting
- **Sources**: Official docs, GitHub issues/PRs/discussions, npm package info, community tools
- **Confidence Level**: High - based on official documentation and merged PR evidence
