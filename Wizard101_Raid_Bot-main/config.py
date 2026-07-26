"""Bot configuration — reads .env (see .env.example)."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # fine if python-dotenv isn't installed; env vars still work

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
REMINDER_MINUTES = int(os.environ.get("REMINDER_MINUTES", "10"))

# Test mode: for trying the bot alone, with no one else around.
#   - one person can fill EVERY role (the "one spot per person" rule is off)
#   - reminders fire fast (a raid a couple minutes out still pings you)
#   - a /testreport command posts the monthly report on demand
# Set TEST_MODE=true in .env only while testing. Keep it false in production.
TEST_MODE = os.environ.get("TEST_MODE", "false").strip().lower() in (
    "1", "true", "yes", "on")

if not DISCORD_TOKEN:
    raise SystemExit(
        "DISCORD_TOKEN is not set. Copy .env.example to .env and add "
        "your bot token."
    )
