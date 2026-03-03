#!/usr/bin/env bash
# setup.sh -- Claude Email Agent Interactive Setup
# Just run: bash setup.sh
# No technical knowledge required -- we'll guide you through everything.

set -e

BOLD=$(tput bold 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")
GREEN=$(tput setaf 2 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
CYAN=$(tput setaf 6 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")

print_header() {
  echo ""
  echo "${BOLD}${CYAN}$1${RESET}"
  echo "$(echo "$1" | sed "s/./─/g")"
}

print_ok()   { echo "  ${GREEN}✓${RESET}  $1"; }
print_warn() { echo "  ${YELLOW}⚠${RESET}  $1"; }
print_info() { echo "  ${CYAN}ℹ${RESET}  $1"; }

# ─── Welcome ──────────────────────────────────────────────────────────────────
clear 2>/dev/null || true
echo ""
echo "${BOLD}${CYAN}"
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║           Claude Email Agent — Setup Wizard             ║"
echo "  ║                                                          ║"
echo "  ║  Supports: Gmail · Outlook · Yahoo · iCloud · Any IMAP  ║"
echo "  ║  No coding required. Takes about 10-15 minutes.         ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo "${RESET}"
echo "  Press ENTER at any prompt to accept the default value shown in [brackets]."
echo ""
read -rp "  Ready? Press ENTER to begin..." _unused

# ─── Step 1: Folder/Project Name ──────────────────────────────────────────────
print_header "Step 1 of 9: Name Your Agent"
echo ""
echo "  This folder is currently named: ${BOLD}$(basename "$(pwd)")${RESET}"
echo ""
echo "  You can rename it to something meaningful, like:"
echo "    my-email-agent    work-email-bot    support-agent"
echo ""
read -rp "  New folder name (or press ENTER to keep current name): " new_name
if [ -n "$new_name" ]; then
  CURRENT_DIR=$(pwd)
  PARENT_DIR=$(dirname "$CURRENT_DIR")
  NEW_PATH="$PARENT_DIR/$new_name"
  if [ -d "$NEW_PATH" ]; then
    print_warn "A folder named "$new_name" already exists. Keeping current name."
  else
    cd ..
    mv "$(basename "$CURRENT_DIR")" "$new_name"
    cd "$new_name"
    print_ok "Folder renamed to: $new_name"
  fi
else
  print_ok "Keeping current folder name: $(basename "$(pwd)")"
fi

# ─── Step 2: Check Python ─────────────────────────────────────────────────────
print_header "Step 2 of 9: Checking Your Computer"
echo ""
echo "  Checking for Python (required to run the agent)..."
if ! command -v python3 &>/dev/null; then
  echo ""
  echo "  ${RED}${BOLD}Python 3 is not installed.${RESET}"
  echo ""
  echo "  Please install Python 3 first:"
  echo "    Mac:     https://www.python.org/downloads/"
  echo "    Windows: https://www.python.org/downloads/"
  echo "    Linux:   sudo apt install python3 python3-pip"
  echo ""
  exit 1
fi
PYTHON=$(command -v python3)
PY_VERSION=$($PYTHON --version 2>&1)
print_ok "Python found: $PY_VERSION"

# ─── Step 3: Email Provider ───────────────────────────────────────────────────
print_header "Step 3 of 9: Which Email Provider Are You Using?"
echo ""
echo "  ${BOLD}1) Gmail${RESET}                      (Google account — gmail.com)"
echo "  ${BOLD}2) Outlook / Microsoft 365${RESET}    (work or personal — outlook.com, hotmail.com)"
echo "  ${BOLD}3) Yahoo Mail${RESET}                 (yahoo.com)"
echo "  ${BOLD}4) iCloud Mail${RESET}                (Apple — icloud.com, me.com)"
echo "  ${BOLD}5) Other / Custom IMAP${RESET}        (Zoho, Fastmail, ProtonMail Bridge, corporate)"
echo ""
read -rp "  Choose [1-5, default: 1]: " provider_choice

# Initialise credential variables (will be filled per provider)
EMAIL_PROVIDER=""
IMAP_HOST=""
IMAP_PORT="993"
SMTP_HOST=""
SMTP_PORT="587"
EMAIL_ADDRESS=""
EMAIL_APP_PASSWORD=""
OUTLOOK_CLIENT_ID=""
OUTLOOK_CLIENT_SECRET=""
OUTLOOK_TENANT_ID=""
MISSING_CREDS=false

case "$provider_choice" in

  # ── Gmail ──────────────────────────────────────────────────────────────────
  1|"")
    EMAIL_PROVIDER="gmail"
    print_ok "Email provider: Gmail"
    echo ""
    echo "  ${BOLD}Gmail uses Google OAuth2 — your password is never shared.${RESET}"
    echo "  We will walk you through creating a credentials.json file in Step 8."
    ;;

  # ── Outlook / Microsoft 365 ────────────────────────────────────────────────
  2)
    EMAIL_PROVIDER="outlook"
    print_ok "Email provider: Outlook / Microsoft 365"
    echo ""
    print_header "  Outlook Setup: Azure App Registration"
    echo ""
    echo "  Outlook uses Microsoft Graph API. You need to register an app in Azure."
    echo "  This sounds technical but just means filling out a form — follow these steps:"
    echo ""
    echo "  ${BOLD}1.${RESET} Go to: ${CYAN}https://portal.azure.com${RESET}"
    echo "     Sign in with the Microsoft account that owns the inbox."
    echo ""
    echo "  ${BOLD}2.${RESET} In the search bar, type "App registrations" and click it."
    echo "     Click ${BOLD}+ New registration${RESET}."
    echo "     - Name: anything (e.g. "Email Agent")"
    echo "     - Supported account types: "Accounts in any organizational directory"
    echo "       and personal Microsoft accounts" (covers both work and personal)"
    echo "     - Redirect URI: select "Public client/native" and enter: http://localhost"
    echo "     Click ${BOLD}Register${RESET}."
    echo ""
    echo "  ${BOLD}3.${RESET} On the app overview page, copy these two values:"
    echo "     - Application (client) ID"
    echo "     - Directory (tenant) ID"
    echo "     ${YELLOW}Note: if this is a personal outlook.com/hotmail.com account,"
    echo "     use "consumers" as the Tenant ID instead of the GUID shown.${RESET}"
    echo ""
    echo "  ${BOLD}4.${RESET} Go to ${BOLD}Certificates & secrets${RESET} > ${BOLD}+ New client secret${RESET}."
    echo "     Give it a description, choose an expiry, click Add."
    echo "     ${RED}Copy the "Value" immediately — you cannot see it again after leaving this page.${RESET}"
    echo ""
    echo "  ${BOLD}5.${RESET} Go to ${BOLD}API permissions${RESET} > ${BOLD}+ Add a permission${RESET} > ${BOLD}Microsoft Graph${RESET} > ${BOLD}Delegated${RESET}."
    echo "     Add these permissions: Mail.Read  Mail.Send  Mail.ReadWrite  offline_access"
    echo "     Then click ${BOLD}Grant admin consent${RESET} (work tenants may need IT admin approval)."
    echo ""
    echo "  ─────────────────────────────────────────────────────────────────"
    read -rp "  Press ENTER when you have your Client ID, Tenant ID, and Client Secret..." _unused
    echo ""
    read -rp "  Application (Client) ID: " OUTLOOK_CLIENT_ID
    while [ -z "$OUTLOOK_CLIENT_ID" ]; do
      print_warn "Client ID cannot be empty."
      read -rp "  Application (Client) ID: " OUTLOOK_CLIENT_ID
    done
    read -rp "  Directory (Tenant) ID [or type "consumers" for personal accounts]: " OUTLOOK_TENANT_ID
    while [ -z "$OUTLOOK_TENANT_ID" ]; do
      print_warn "Tenant ID cannot be empty."
      read -rp "  Directory (Tenant) ID: " OUTLOOK_TENANT_ID
    done
    read -rp "  Client Secret Value: " OUTLOOK_CLIENT_SECRET
    while [ -z "$OUTLOOK_CLIENT_SECRET" ]; do
      print_warn "Client secret cannot be empty."
      read -rp "  Client Secret Value: " OUTLOOK_CLIENT_SECRET
    done
    print_ok "Outlook credentials saved."
    ;;

  # ── Yahoo Mail ─────────────────────────────────────────────────────────────
  3)
    EMAIL_PROVIDER="yahoo"
    IMAP_HOST="imap.mail.yahoo.com"
    IMAP_PORT="993"
    SMTP_HOST="smtp.mail.yahoo.com"
    SMTP_PORT="587"
    print_ok "Email provider: Yahoo Mail"
    echo ""
    print_header "  Yahoo Mail Setup: App Password"
    echo ""
    echo "  Yahoo requires an "App Password" — a special password just for this agent."
    echo "  Your main Yahoo password is never used or stored."
    echo ""
    echo "  ${BOLD}1.${RESET} Go to: ${CYAN}https://myaccount.yahoo.com/security${RESET}"
    echo "     (Sign in to your Yahoo account if needed)"
    echo ""
    echo "  ${BOLD}2.${RESET} Scroll down to "App passwords" and click ${BOLD}Generate app password${RESET}."
    echo "     - Select "Other app" from the dropdown"
    echo "     - Type a name: Email Agent"
    echo "     - Click ${BOLD}Generate${RESET}"
    echo "     ${RED}Copy the 16-character password — you will not see it again.${RESET}"
    echo ""
    echo "  ${BOLD}3.${RESET} Make sure IMAP is enabled:"
    echo "     Yahoo Mail > Settings (gear icon) > More Settings > Mailboxes"
    echo "     Make sure the IMAP toggle is ON."
    echo ""
    echo "  ─────────────────────────────────────────────────────────────────"
    read -rp "  Press ENTER when you have your app password ready..." _unused
    echo ""
    read -rp "  Your Yahoo email address: " EMAIL_ADDRESS
    while [ -z "$EMAIL_ADDRESS" ]; do
      print_warn "Email address cannot be empty."
      read -rp "  Your Yahoo email address: " EMAIL_ADDRESS
    done
    read -rp "  Your 16-character app password: " EMAIL_APP_PASSWORD
    while [ -z "$EMAIL_APP_PASSWORD" ]; do
      print_warn "App password cannot be empty."
      read -rp "  Your 16-character app password: " EMAIL_APP_PASSWORD
    done
    print_ok "Yahoo credentials saved."
    ;;

  # ── iCloud Mail ────────────────────────────────────────────────────────────
  4)
    EMAIL_PROVIDER="icloud"
    IMAP_HOST="imap.mail.me.com"
    IMAP_PORT="993"
    SMTP_HOST="smtp.mail.me.com"
    SMTP_PORT="587"
    print_ok "Email provider: iCloud Mail"
    echo ""
    print_header "  iCloud Mail Setup: App-Specific Password"
    echo ""
    echo "  iCloud requires an "App-Specific Password" for third-party apps."
    echo "  Your Apple ID password is never used or stored."
    echo ""
    echo "  ${BOLD}1.${RESET} Go to: ${CYAN}https://appleid.apple.com${RESET}"
    echo "     Sign in with your Apple ID."
    echo ""
    echo "  ${BOLD}2.${RESET} Click ${BOLD}Sign-In and Security${RESET} > ${BOLD}App-Specific Passwords${RESET}."
    echo "     Click the ${BOLD}+${RESET} button."
    echo "     Name it: Email Agent"
    echo "     ${RED}Copy the generated password — it looks like: xxxx-xxxx-xxxx-xxxx${RESET}"
    echo ""
    echo "  ${BOLD}3.${RESET} Make sure iCloud Mail / IMAP is enabled:"
    echo "     On iPhone: Settings > [Your Name] > iCloud > Mail (toggle ON)"
    echo "     On Mac: System Settings > Apple ID > iCloud > Mail (check ON)"
    echo "     Or at: iCloud.com > Settings > Mail (toggle ON)"
    echo ""
    echo "  ${BOLD}4.${RESET} Your username is your full iCloud email address:"
    echo "     e.g.  you@icloud.com  or  you@me.com  or  you@mac.com"
    echo ""
    echo "  ─────────────────────────────────────────────────────────────────"
    read -rp "  Press ENTER when you have your app-specific password ready..." _unused
    echo ""
    read -rp "  Your iCloud email address (e.g. you@icloud.com): " EMAIL_ADDRESS
    while [ -z "$EMAIL_ADDRESS" ]; do
      print_warn "Email address cannot be empty."
      read -rp "  Your iCloud email address: " EMAIL_ADDRESS
    done
    read -rp "  Your app-specific password (xxxx-xxxx-xxxx-xxxx): " EMAIL_APP_PASSWORD
    while [ -z "$EMAIL_APP_PASSWORD" ]; do
      print_warn "App-specific password cannot be empty."
      read -rp "  Your app-specific password: " EMAIL_APP_PASSWORD
    done
    print_ok "iCloud credentials saved."
    ;;

  # ── Other / Custom IMAP ────────────────────────────────────────────────────
  5)
    EMAIL_PROVIDER="imap"
    print_ok "Email provider: Custom IMAP/SMTP"
    echo ""
    print_header "  Custom IMAP Setup"
    echo ""
    echo "  Common providers and their settings:"
    echo "    Zoho Mail:           imap.zoho.com  :993  /  smtp.zoho.com  :587"
    echo "    Fastmail:            imap.fastmail.com:993 /  smtp.fastmail.com:587"
    echo "    ProtonMail Bridge:   127.0.0.1      :1143  /  127.0.0.1     :1025"
    echo "    Corporate / Other:   check with your IT department or provider docs"
    echo ""
    read -rp "  IMAP host (e.g. imap.yourdomain.com): " IMAP_HOST
    while [ -z "$IMAP_HOST" ]; do
      print_warn "IMAP host cannot be empty."
      read -rp "  IMAP host: " IMAP_HOST
    done
    read -rp "  IMAP port [default: 993]: " IMAP_PORT
    IMAP_PORT="${IMAP_PORT:-993}"
    read -rp "  SMTP host (e.g. smtp.yourdomain.com): " SMTP_HOST
    while [ -z "$SMTP_HOST" ]; do
      print_warn "SMTP host cannot be empty."
      read -rp "  SMTP host: " SMTP_HOST
    done
    read -rp "  SMTP port [default: 587]: " SMTP_PORT
    SMTP_PORT="${SMTP_PORT:-587}"
    read -rp "  Your email address: " EMAIL_ADDRESS
    while [ -z "$EMAIL_ADDRESS" ]; do
      print_warn "Email address cannot be empty."
      read -rp "  Your email address: " EMAIL_ADDRESS
    done
    echo "  Enter your password or app password for this email account."
    echo "  (Many providers require an app password, not your main login password.)"
    read -rp "  Password or app password: " EMAIL_APP_PASSWORD
    while [ -z "$EMAIL_APP_PASSWORD" ]; do
      print_warn "Password cannot be empty."
      read -rp "  Password or app password: " EMAIL_APP_PASSWORD
    done
    print_ok "IMAP credentials saved."
    ;;

esac

# ─── Step 4: Deployment location ──────────────────────────────────────────────
print_header "Step 4 of 9: Where Will the Agent Run?"
echo ""
echo "  ${BOLD}Option 1 — My computer (local)${RESET}"
echo "    The agent runs while your computer is on and this terminal is open."
echo "    Good for trying it out. Free — no server costs."
echo ""
echo "  ${BOLD}Option 2 — A server (always-on)${RESET}"
echo "    The agent runs 24/7 on a Linux server (e.g. DigitalOcean, AWS, etc.)"
echo "    Best for production use. Requires a server you can SSH into."
echo ""
read -rp "  Choose [1/2, default: 1]: " deploy_choice
case "$deploy_choice" in
  2) DEPLOY_MODE="server" ;;
  *) DEPLOY_MODE="local" ;;
esac
print_ok "Deploy mode: $DEPLOY_MODE"

# ─── Step 5: Reply mode ───────────────────────────────────────────────────────
print_header "Step 5 of 9: Draft or Auto-Send?"
echo ""
echo "  ${BOLD}Option 1 — Save as drafts (STRONGLY RECOMMENDED)${RESET}"
echo "    Claude writes the reply, but saves it to your Drafts folder."
echo "    You review it, then decide whether to send it yourself."
echo "    Start here. You can switch to auto-send after you trust the replies."
echo ""
echo "  ${BOLD}Option 2 — Auto-send${RESET}"
echo "    Claude writes AND sends the reply automatically. No review."
echo "    ${YELLOW}⚠  Only enable this after reviewing at least a week of drafts.${RESET}"
echo ""
read -rp "  Choose [1/2, default: 1]: " reply_choice
case "$reply_choice" in
  2)
    REPLY_MODE="send"
    echo ""
    print_warn "You chose auto-send. We will set up an email whitelist to keep it safe."
    ;;
  *) REPLY_MODE="draft" ;;
esac
print_ok "Reply mode: $REPLY_MODE"

# ─── Step 6: Email filter mode ────────────────────────────────────────────────
print_header "Step 6 of 9: Which Emails Should the Agent Respond To?"
echo ""
echo "  ${BOLD}Option 1 — Specific people only (whitelist)${RESET}"
echo "    Only reply to emails from people you list."
echo "    ${GREEN}Most safe. Best for auto-send or cautious start.${RESET}"
echo ""
echo "  ${BOLD}Option 2 — Everyone except blocked senders (blocklist)${RESET}"
echo "    Reply to all emails EXCEPT newsletters, spam, and auto-generated messages."
echo "    ${YELLOW}Broader — good for customer support or public-facing inboxes.${RESET}"
echo ""
echo "  ${BOLD}Option 3 — All emails (no filter)${RESET}"
echo "    Reply to every email that lands in your inbox."
echo "    ${RED}⚠  Not recommended unless you are very confident in your setup.${RESET}"
echo ""
read -rp "  Choose [1/2/3, default: 1]: " filter_choice

ONLY_REPLY_TO=""
IGNORE_SENDERS="noreply@,no-reply@,mailer-daemon@,postmaster@,donotreply@"
EMAIL_FILTER_MODE="blocklist"

case "$filter_choice" in
  1)
    EMAIL_FILTER_MODE="whitelist"
    echo ""
    echo "  ${BOLD}Enter the email addresses you want the agent to respond to.${RESET}"
    echo "  Separate multiple addresses with commas."
    echo "  You can use partial matches: @company.com matches everyone at that domain."
    echo "  Example: alice@company.com, bob@company.com, @trustedcorp.com"
    echo ""
    read -rp "  Allowed email addresses: " whitelist_input
    while [ -z "$whitelist_input" ]; do
      print_warn "You must enter at least one email address for whitelist mode."
      read -rp "  Allowed email addresses: " whitelist_input
    done
    ONLY_REPLY_TO="$whitelist_input"
    print_ok "Whitelist set."
    ;;
  3)
    EMAIL_FILTER_MODE="all"
    IGNORE_SENDERS=""
    print_warn "No filter — the agent will respond to all emails."
    ;;
  *)
    EMAIL_FILTER_MODE="blocklist"
    echo ""
    echo "  Default blocked patterns: noreply@, no-reply@, mailer-daemon@, postmaster@, donotreply@"
    echo ""
    read -rp "  Add more blocked patterns? (comma-separated, or press ENTER to skip): " extra_ignore
    if [ -n "$extra_ignore" ]; then
      IGNORE_SENDERS="$IGNORE_SENDERS,$extra_ignore"
    fi
    print_ok "Blocklist mode active."
    ;;
esac

# ─── Step 7: Anthropic API Key ────────────────────────────────────────────────
print_header "Step 7 of 9: Anthropic API Key (Claude AI)"
echo ""
echo "  The agent uses Claude AI to write email replies."
echo "  You need an API key from Anthropic:"
echo ""
echo "  ${BOLD}1.${RESET} Go to: ${CYAN}https://console.anthropic.com${RESET}"
echo "  ${BOLD}2.${RESET} Sign up or log in"
echo "  ${BOLD}3.${RESET} Click "API Keys" in the left sidebar > "Create Key""
echo "  ${BOLD}4.${RESET} Copy the key — it starts with: sk-ant-..."
echo ""
echo "  ${YELLOW}Cost: roughly $4-5 per month at 100 emails/day${RESET}"
echo ""
read -rp "  Paste your Anthropic API key here: " api_key
while [ -z "$api_key" ]; do
  print_warn "API key cannot be empty."
  read -rp "  Paste your Anthropic API key here: " api_key
done
if [[ "$api_key" != sk-ant-* ]]; then
  print_warn "That key does not start with sk-ant- — double-check you copied the full key."
  read -rp "  Continue anyway? [y/N]: " confirm_key
  if [[ "$confirm_key" != "y" && "$confirm_key" != "Y" ]]; then
    echo "  Exiting. Re-run setup.sh when you have the correct key."
    exit 1
  fi
fi
print_ok "API key saved."

# ─── Step 8: Provider-specific credentials (Gmail only at this step) ──────────
if [ "$EMAIL_PROVIDER" = "gmail" ]; then
  print_header "Step 8 of 9: Google Gmail Access (OAuth)"
  echo ""
  echo "  Gmail uses a secure system called OAuth — your password is NEVER shared."
  echo "  You will create a credentials.json file from Google Cloud Console."
  echo ""
  echo "  ${BOLD}1.${RESET} Go to: ${CYAN}https://console.cloud.google.com${RESET}"
  echo "     Sign in with the Google account whose Gmail you want to use."
  echo ""
  echo "  ${BOLD}2.${RESET} Create a new project:"
  echo "     - Click the project dropdown (top left) > New Project"
  echo "     - Name it anything (e.g. "email-agent") and click Create"
  echo ""
  echo "  ${BOLD}3.${RESET} Enable Gmail API:"
  echo "     - In the search bar, type "Gmail API" and select it"
  echo "     - Click the blue Enable button"
  echo ""
  echo "  ${BOLD}4.${RESET} Create OAuth credentials:"
  echo "     - Go to: APIs & Services > Credentials"
  echo "     - Click + Create Credentials > OAuth client ID"
  echo "     - If prompted to configure the consent screen first:"
  echo "       * Choose External, fill in your app name and email, click Save"
  echo "       * Under Test users, add your own Gmail address"
  echo "       * Click Back to Dashboard"
  echo "     - Back in Credentials: + Create Credentials > OAuth client ID"
  echo "     - Application type: Desktop app"
  echo "     - Click Create, then the download icon (⬇) to get the JSON file"
  echo ""
  echo "  ${BOLD}5.${RESET} Place the file:"
  echo "     - Rename the downloaded file to: credentials.json"
  echo "     - Move it into this folder: $(pwd)"
  echo ""
  read -rp "  Press ENTER when credentials.json is in this folder..." _unused
  echo ""
  if [ ! -f "credentials.json" ]; then
    print_warn "credentials.json not found. You can place it here later and re-run:"
    echo "    python3 -c "from gmail_client import get_gmail_service; get_gmail_service()""
    MISSING_CREDS=true
  else
    print_ok "credentials.json found!"
    MISSING_CREDS=false
  fi
else
  print_header "Step 8 of 9: Credentials Review"
  echo ""
  print_ok "Credentials already collected in Step 3. Nothing more needed here."
fi

# ─── Step 9: Poll interval ────────────────────────────────────────────────────
print_header "Step 9 of 9: How Often to Check Email"
echo ""
echo "  How often should the agent check for new emails?"
echo "  60 seconds is a good default."
echo ""
read -rp "  Check every how many seconds? [default: 60]: " poll_interval
POLL_INTERVAL_SECONDS="${poll_interval:-60}"
print_ok "Will check every ${POLL_INTERVAL_SECONDS} seconds."

# ─── Write .env ───────────────────────────────────────────────────────────────
echo ""
echo "  Saving your settings to .env..."

cat > .env <<ENVEOF
# Claude Email Agent Configuration
# Generated by setup.sh — edit any value here and restart the agent

# ── Email Provider ────────────────────────────────────────────
# gmail | outlook | yahoo | icloud | imap
EMAIL_PROVIDER=${EMAIL_PROVIDER}

# ── Anthropic (Claude AI) ─────────────────────────────────────
ANTHROPIC_API_KEY=${api_key}

# ── Deployment ───────────────────────────────────────────────
DEPLOY_MODE=${DEPLOY_MODE}

# ── Reply mode ───────────────────────────────────────────────
REPLY_MODE=${REPLY_MODE}

# ── Polling interval (seconds) ───────────────────────────────
POLL_INTERVAL_SECONDS=${POLL_INTERVAL_SECONDS}

# ── Email filter mode ─────────────────────────────────────────
EMAIL_FILTER_MODE=${EMAIL_FILTER_MODE}

# ── Whitelist (EMAIL_FILTER_MODE=whitelist) ───────────────────
ONLY_REPLY_TO=${ONLY_REPLY_TO}

# ── Blocklist (EMAIL_FILTER_MODE=blocklist or all) ────────────
IGNORE_SENDERS=${IGNORE_SENDERS}

# ── Gmail label applied to processed emails ───────────────────
LABEL_AFTER_REPLY=AI-Replied

# ── Claude model ─────────────────────────────────────────────
MODEL=claude-haiku-4-5
MAX_TOKENS=1024

# ── Outlook / Microsoft 365 credentials ──────────────────────
# (Only used when EMAIL_PROVIDER=outlook)
OUTLOOK_CLIENT_ID=${OUTLOOK_CLIENT_ID}
OUTLOOK_CLIENT_SECRET=${OUTLOOK_CLIENT_SECRET}
OUTLOOK_TENANT_ID=${OUTLOOK_TENANT_ID}

# ── IMAP/SMTP credentials ─────────────────────────────────────
# (Used for yahoo, icloud, imap providers)
EMAIL_ADDRESS=${EMAIL_ADDRESS}
EMAIL_APP_PASSWORD=${EMAIL_APP_PASSWORD}
IMAP_HOST=${IMAP_HOST}
IMAP_PORT=${IMAP_PORT}
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
ENVEOF
print_ok ".env saved."

# ─── Install dependencies ─────────────────────────────────────────────────────
echo ""
echo "  Installing Python packages (this may take a minute)..."
$PYTHON -m pip install --quiet --upgrade pip
$PYTHON -m pip install --quiet -r requirements.txt
print_ok "Packages installed."

# ─── First-run Gmail auth (if credentials.json exists) ───────────────────────
if [ "$EMAIL_PROVIDER" = "gmail" ] && [ "$MISSING_CREDS" = "false" ]; then
  echo ""
  echo "  ${BOLD}Connecting to your Gmail account...${RESET}"
  echo "  A browser window will open. Sign in to Google and click Allow."
  echo "  You may see a warning — click Advanced > Go to [app name] to continue."
  echo ""
  read -rp "  Press ENTER to open the browser..." _unused
  $PYTHON -c "from gmail_client import get_gmail_service; get_gmail_service()" && print_ok "Gmail connected!"
fi

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║                    Setup Complete!                       ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo "${RESET}"
echo "  ${BOLD}Your settings:${RESET}"
echo "    Email provider: ${BOLD}$EMAIL_PROVIDER${RESET}"
echo "    Reply mode:     ${BOLD}$REPLY_MODE${RESET}"
echo "    Filter mode:    ${BOLD}$EMAIL_FILTER_MODE${RESET}"
[ -n "$ONLY_REPLY_TO" ] && echo "    Whitelist:      ${BOLD}$ONLY_REPLY_TO${RESET}"
echo "    Check every:    ${BOLD}${POLL_INTERVAL_SECONDS}s${RESET}"
echo ""
echo "  ${BOLD}Next: customize your agent persona${RESET}"
echo "  Open ${CYAN}config.py${RESET} and update the SYSTEM_PROMPT with your name,"
echo "  what your inbox is for, and any FAQs or policies."
echo "  The more detail you add, the better the replies will be."
echo ""
if [ "$EMAIL_PROVIDER" = "gmail" ] && [ "$MISSING_CREDS" = "true" ]; then
  echo "  ${YELLOW}⚠  Still needed: credentials.json from Google Cloud Console${RESET}"
  echo "  Once you have it, place it here and run:"
  echo "    python3 -c "from gmail_client import get_gmail_service; get_gmail_service()""
  echo ""
fi
echo "  ${BOLD}To start the agent:${RESET}"
if [ "$DEPLOY_MODE" = "local" ]; then
  echo "    ${BOLD}python3 agent.py${RESET}"
  echo "  Press Ctrl+C to stop it."
else
  echo "  See the README for server deployment instructions."
fi
echo ""
