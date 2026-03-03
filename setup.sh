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

print_step() {
  echo ""
  echo "${BOLD}${GREEN}▶ $1${RESET}"
}

print_info() {
  echo "  ${CYAN}ℹ${RESET}  $1"
}

print_warn() {
  echo "  ${YELLOW}⚠${RESET}  $1"
}

print_ok() {
  echo "  ${GREEN}✓${RESET}  $1"
}

ask() {
  echo ""
  printf "  ${BOLD}$1${RESET} "
}

# ─── Welcome ──────────────────────────────────────────────────────────────────
clear 2>/dev/null || true
echo ""
echo "${BOLD}${CYAN}"
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║           Claude Email Agent — Setup Wizard             ║"
echo "  ║                                                          ║"
echo "  ║  This wizard will help you set up your AI email agent.  ║"
echo "  ║  It takes about 10-15 minutes. No coding required.      ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo "${RESET}"
echo "  Press ENTER at any prompt to accept the default value shown in [brackets]."
echo ""
read -rp "  Ready? Press ENTER to begin..." _unused

# ─── Step 1: Folder/Project Name ──────────────────────────────────────────────
print_header "Step 1 of 8: Name Your Agent"
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
print_header "Step 2 of 8: Checking Your Computer"
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

# ─── Step 3: Deployment location ──────────────────────────────────────────────
print_header "Step 3 of 8: Where Will the Agent Run?"
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

# ─── Step 4: Reply mode ───────────────────────────────────────────────────────
print_header "Step 4 of 8: Draft or Auto-Send?"
echo ""
echo "  ${BOLD}Option 1 — Save as drafts (STRONGLY RECOMMENDED)${RESET}"
echo "    Claude writes the reply, but saves it to your Gmail Drafts folder."
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

# ─── Step 5: Email filter mode ────────────────────────────────────────────────
print_header "Step 5 of 8: Which Emails Should the Agent Respond To?"
echo ""
echo "  ${BOLD}Option 1 — Specific people only (whitelist)${RESET}"
echo "    Only reply to emails from people you list."
echo "    ${GREEN}Most safe. Best for auto-send or cautious start.${RESET}"
echo "    Example: only respond to your team, or only to clients."
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
    echo "  Example: alice@company.com, bob@company.com"
    echo ""
    read -rp "  Allowed email addresses: " whitelist_input
    while [ -z "$whitelist_input" ]; do
      print_warn "You must enter at least one email address for whitelist mode."
      read -rp "  Allowed email addresses: " whitelist_input
    done
    ONLY_REPLY_TO="$whitelist_input"
    print_ok "Whitelist set: $ONLY_REPLY_TO"
    ;;
  3)
    EMAIL_FILTER_MODE="all"
    IGNORE_SENDERS=""
    print_warn "No filter — the agent will respond to all emails."
    ;;
  *)
    EMAIL_FILTER_MODE="blocklist"
    echo ""
    echo "  ${BOLD}Default spam/newsletter senders are already blocked:${RESET}"
    echo "  noreply@, no-reply@, mailer-daemon@, postmaster@, donotreply@"
    echo ""
    read -rp "  Add more blocked patterns? (comma-separated, or press ENTER to skip): " extra_ignore
    if [ -n "$extra_ignore" ]; then
      IGNORE_SENDERS="$IGNORE_SENDERS,$extra_ignore"
    fi
    print_ok "Blocklist mode active."
    ;;
esac

# ─── Step 6: Anthropic API Key ────────────────────────────────────────────────
print_header "Step 6 of 8: Anthropic API Key (Claude AI)"
echo ""
echo "  The agent uses Claude AI (made by Anthropic) to write email replies."
echo "  You need an API key from Anthropic. Here is how to get one:"
echo ""
echo "  ${BOLD}1.${RESET} Go to: ${CYAN}https://console.anthropic.com${RESET}"
echo "  ${BOLD}2.${RESET} Sign up or log in"
echo "  ${BOLD}3.${RESET} Click "API Keys" in the left sidebar"
echo "  ${BOLD}4.${RESET} Click "Create Key", give it a name, copy the key"
echo "  ${BOLD}5.${RESET} It starts with: sk-ant-..."
echo ""
echo "  ${YELLOW}Cost: roughly $4-5 per month at 100 emails/day (very affordable)${RESET}"
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

# ─── Step 7: Google OAuth Setup ───────────────────────────────────────────────
print_header "Step 7 of 8: Google Gmail Access"
echo ""
echo "  The agent needs permission to read and reply to your Gmail."
echo "  Google uses a secure system called OAuth — your password is NEVER shared."
echo ""
echo "  ${BOLD}You need to create a "credentials.json" file. Here is exactly how:${RESET}"
echo ""
echo "  ${BOLD}1.${RESET} Go to: ${CYAN}https://console.cloud.google.com${RESET}"
echo "     (Sign in with the Google account whose Gmail you want to use)"
echo ""
echo "  ${BOLD}2.${RESET} Create a new project:"
echo "     - Click the project dropdown at the top left"
echo "     - Click "New Project""
echo "     - Name it anything (e.g. "email-agent") and click "Create""
echo ""
echo "  ${BOLD}3.${RESET} Enable Gmail API:"
echo "     - In the search bar, type "Gmail API""
echo "     - Click on "Gmail API" in the results"
echo "     - Click the blue "Enable" button"
echo ""
echo "  ${BOLD}4.${RESET} Create OAuth credentials:"
echo "     - In the left menu, go to: APIs & Services > Credentials"
echo "     - Click "+ Create Credentials" > "OAuth client ID""
echo "     - If prompted, click "Configure Consent Screen" first:"
echo "       * Choose "External", click Create"
echo "       * Fill in App name (e.g. "My Email Agent")"
echo "       * Fill in your email for support and developer contact"
echo "       * Click Save and Continue through the rest (defaults are fine)"
echo "       * On the "Test users" page, add your own Gmail address"
echo "       * Click Save and Continue, then Back to Dashboard"
echo "     - Back in Credentials, click "+ Create Credentials" > "OAuth client ID""
echo "     - Application type: choose "Desktop app""
echo "     - Name it anything, click "Create""
echo "     - Click the download icon (⬇) to download the JSON file"
echo ""
echo "  ${BOLD}5.${RESET} Move the downloaded file:"
echo "     - Rename it to: credentials.json"
echo "     - Move it into this folder: $(pwd)"
echo ""
echo "${YELLOW}  ─────────────────────────────────────────────────────────────${RESET}"
read -rp "  Press ENTER when you have placed credentials.json in this folder..." _unused
echo ""
if [ ! -f "credentials.json" ]; then
  print_warn "credentials.json not found in $(pwd)"
  echo "  You can re-run setup.sh later once you have it."
  echo "  The .env file has already been saved with your other settings."
  MISSING_CREDS=true
else
  print_ok "credentials.json found!"
  MISSING_CREDS=false
fi

# ─── Step 8: Poll interval ────────────────────────────────────────────────────
print_header "Step 8 of 8: How Often to Check Email"
echo ""
echo "  How often should the agent check for new emails?"
echo "  60 seconds is a good balance. You can always change this later in .env"
echo ""
read -rp "  Check every how many seconds? [default: 60]: " poll_interval
POLL_INTERVAL_SECONDS="${poll_interval:-60}"
print_ok "Will check every ${POLL_INTERVAL_SECONDS} seconds."

# ─── Write .env ───────────────────────────────────────────────────────────────
echo ""
echo "  Saving your settings to .env..."

cat > .env <<ENVEOF
# Claude Email Agent Configuration
# Generated by setup.sh -- edit any value here and restart the agent

# ── Anthropic (Claude AI) ──────────────────────────────────────
ANTHROPIC_API_KEY=${api_key}

# ── Deployment ────────────────────────────────────────────────
DEPLOY_MODE=${DEPLOY_MODE}

# ── Reply mode: draft = save to Drafts, send = auto-send ──────
REPLY_MODE=${REPLY_MODE}

# ── Polling interval (seconds) ────────────────────────────────
POLL_INTERVAL_SECONDS=${POLL_INTERVAL_SECONDS}

# ── Email filter mode ─────────────────────────────────────────
# whitelist = ONLY reply to emails listed in ONLY_REPLY_TO
# blocklist = reply to all EXCEPT patterns in IGNORE_SENDERS
# all       = reply to everything (not recommended)
EMAIL_FILTER_MODE=${EMAIL_FILTER_MODE}

# ── Whitelist: only reply to these senders (used when EMAIL_FILTER_MODE=whitelist)
# Comma-separated. Can be full email or partial match (e.g. @mycompany.com)
ONLY_REPLY_TO=${ONLY_REPLY_TO}

# ── Blocklist: never reply to these patterns (used when EMAIL_FILTER_MODE=blocklist or all)
IGNORE_SENDERS=${IGNORE_SENDERS}

# ── Gmail label applied to processed emails ────────────────────
LABEL_AFTER_REPLY=AI-Replied

# ── Claude model (do not change unless you know why) ──────────
MODEL=claude-haiku-4-5
MAX_TOKENS=1024
ENVEOF
print_ok ".env saved."

# ─── Install dependencies ─────────────────────────────────────────────────────
echo ""
echo "  Installing Python packages (this may take a minute)..."
$PYTHON -m pip install --quiet --upgrade pip
$PYTHON -m pip install --quiet -r requirements.txt
print_ok "Packages installed."

# ─── First-run auth (if credentials.json exists) ──────────────────────────────
if [ "$MISSING_CREDS" = "false" ]; then
  echo ""
  echo "  ${BOLD}Almost done! Let's connect to your Gmail account.${RESET}"
  echo ""
  echo "  A browser window will open asking you to sign in to Google."
  echo "  Sign in with the Gmail account you want the agent to manage."
  echo "  You may see a warning that says "This app is not verified" --"
  echo "  click "Advanced" then "Go to [your app name] (unsafe)" to continue."
  echo "  (This is normal for personal apps you create yourself.)"
  echo ""
  read -rp "  Press ENTER to open the browser and authorize Gmail access..." _unused
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
echo "    Reply mode:  ${BOLD}$REPLY_MODE${RESET}"
echo "    Filter mode: ${BOLD}$EMAIL_FILTER_MODE${RESET}"
if [ -n "$ONLY_REPLY_TO" ]; then
echo "    Whitelist:   ${BOLD}$ONLY_REPLY_TO${RESET}"
fi
echo "    Check every: ${BOLD}${POLL_INTERVAL_SECONDS}s${RESET}"
echo ""

echo "  ${BOLD}One more thing: customize your agent persona${RESET}"
echo "  Open ${CYAN}config.py${RESET} and fill in the SYSTEM_PROMPT section with:"
echo "    - Your name"
echo "    - What your inbox is for (customer support, scheduling, etc.)"
echo "    - Any FAQs, policies, or business context"
echo "  The more detail you add, the better the replies will be."
echo ""

if [ "$MISSING_CREDS" = "true" ]; then
  echo "  ${YELLOW}⚠  Still needed: credentials.json from Google Cloud Console${RESET}"
  echo "  Once you have it, place it in this folder and run:"
  echo "    ${BOLD}python3 -c "from gmail_client import get_gmail_service; get_gmail_service()"${RESET}"
  echo ""
fi

echo "  ${BOLD}To start the agent:${RESET}"
if [ "$DEPLOY_MODE" = "local" ]; then
  echo "    ${BOLD}python3 agent.py${RESET}"
  echo ""
  echo "  The agent will run while this terminal is open."
  echo "  Press Ctrl+C to stop it."
else
  echo "  See the README for server deployment instructions."
fi
echo ""

