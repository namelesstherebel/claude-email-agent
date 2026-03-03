#!/usr/bin/env bash
# setup.sh -- Interactive initializer for claude-email-agent
# Run once after cloning: bash setup.sh

set -e

echo ""
echo "Claude Email Agent -- Setup"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required but not installed."
    exit 1
fi
PYTHON=$(command -v python3)
echo "Using Python: $PYTHON"
echo ""

# Step 1: Deploy mode
echo "Where will this agent run?"
echo "  1) local  -- on this machine"
echo "  2) server -- as a systemd service or Docker container"
read -rp "Choose [1/2, default: 1]: " deploy_choice
case "$deploy_choice" in
    2) DEPLOY_MODE="server" ;;
    *) DEPLOY_MODE="local" ;;
esac
echo "  -> Deploy mode: $DEPLOY_MODE"
echo ""

# Step 2: Reply mode
echo "How should the agent handle replies?"
echo "  1) draft -- save as Gmail drafts (RECOMMENDED)"
echo "  2) send  -- auto-send immediately"
read -rp "Choose [1/2, default: 1]: " reply_choice
case "$reply_choice" in
    2) REPLY_MODE="send" ;;
    *) REPLY_MODE="draft" ;;
esac
echo "  -> Reply mode: $REPLY_MODE"
echo ""

# Step 3: Poll interval
read -rp "How often to check for new emails (seconds)? [default: 60]: " poll_interval
POLL_INTERVAL_SECONDS="${poll_interval:-60}"
echo "  -> Poll interval: ${POLL_INTERVAL_SECONDS}s"
echo ""

# Step 4: Anthropic API key
echo "Enter your Anthropic API key (from https://console.anthropic.com):"
read -rp "ANTHROPIC_API_KEY: " api_key
echo ""

# Step 5: Write .env
cat > .env <<EOF
ANTHROPIC_API_KEY=${api_key}
DEPLOY_MODE=${DEPLOY_MODE}
REPLY_MODE=${REPLY_MODE}
POLL_INTERVAL_SECONDS=${POLL_INTERVAL_SECONDS}
ONLY_REPLY_TO=
IGNORE_SENDERS=noreply@,no-reply@,mailer-daemon@,postmaster@
LABEL_AFTER_REPLY=AI-Replied
MODEL=claude-haiku-4-5
MAX_TOKENS=1024
EOF
echo ".env file created."
echo ""

# Step 6: Install dependencies
echo "Installing Python dependencies..."
$PYTHON -m pip install --quiet --upgrade pip
$PYTHON -m pip install --quiet -r requirements.txt
echo "Dependencies installed."
echo ""

# Step 7: Check credentials.json
if [ ! -f "credentials.json" ]; then
    echo "ACTION REQUIRED: Add credentials.json"
    echo "1. Go to https://console.cloud.google.com"
    echo "2. Create a project and enable the Gmail API"
    echo "3. Create OAuth 2.0 credentials (Desktop app type)"
    echo "4. Download as credentials.json and place it in this directory"
    echo ""
fi

echo "Setup complete!"
echo ""
if [ "$DEPLOY_MODE" = "local" ]; then
    echo "To start the agent:"
    echo "  Foreground: python3 agent.py"
    echo "  Background: nohup python3 agent.py &"
else
    echo "To deploy as a systemd service:"
    echo "  sudo cp deploy/claude-email-agent.service /etc/systemd/system/"
    echo "  sudo systemctl enable claude-email-agent"
    echo "  sudo systemctl start claude-email-agent"
    echo ""
    echo "Or with Docker:"
    echo "  docker build -t claude-email-agent ."
fi
echo ""
echo "Remember: start in DRAFT mode and review replies before enabling auto-send."
