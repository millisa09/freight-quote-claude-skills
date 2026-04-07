# Installation Guide

## Standard Install (freight-quote + carrier-incident-report)

### 1. Download the `.skill` file
Go to the [Releases](../../releases) page and download the skill you want.

### 2. Add your config
Copy `config.example.json` → save as `config.json` in the same folder as your
skill, and fill in your brokerage details. This is the only file you ever need
to edit.

### 3. Upload to Claude or Cowork

**In Cowork:**
1. Open Cowork desktop app
2. Settings (gear icon) → Skills → Upload Skill
3. Select your `.skill` file → Upload
4. The skill is now active in all your sessions

**In Claude.ai:**
1. Go to claude.ai → Settings → Skills
2. Click "Upload Skill" → select the `.skill` file
3. Active immediately

### 4. Test it
Type: `"quote this load — flatbed, Chicago to Dallas, 42,000 lbs, $1,850"`

You should get a PDF quote in your branding within seconds.

---

## Gmail MCP Setup (required for rfq-email-scanner)

The RFQ scanner connects to your Gmail via Gmail MCP — a secure bridge that
lets Claude read (but never auto-send) your emails.

### Step 1 — Enable Gmail MCP in Claude

**In Claude.ai:**
1. Settings → Connectors → Gmail → Connect
2. Sign in with your Google account
3. Grant read access (the skill only reads — it never sends without your approval)

**In Cowork:**
1. Settings → Integrations → Gmail MCP
2. Follow the OAuth flow to connect your Google account

### Step 2 — Verify the connection
Type: `"Check if my Gmail is connected"`
Claude should confirm it can see your inbox.

### Step 3 — Run your first scan
Type: `"Scan my inbox for any RFQ emails from the last 48 hours"`

Claude will search for rate request emails, extract load details, and present
them to you for review before any action is taken.

---

## Security Notes

- Claude **never auto-sends** emails on your behalf. Every draft is shown to
  you for review and approval first.
- Gmail MCP uses read-only OAuth by default. Your credentials are never stored
  in the skill files.
- `config.json` contains your brokerage info only — no passwords or API keys.
  Never commit `config.json` to a public GitHub repo.

### Add config.json to .gitignore
If you fork this repo, protect your info:

```bash
echo "config.json" >> .gitignore
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| PDF doesn't generate | Run `pip install reportlab` in your terminal |
| Incident report fails | Run `pip install python-docx` |
| Gmail scan returns nothing | Confirm Gmail MCP is connected in Settings |
| Wrong branding on PDF | Check your `config.json` — make sure it's named exactly `config.json` |
| Skill doesn't trigger | Try more explicit phrasing: "generate a freight quote PDF" |

---

## Updating a Skill

To update to a newer version:
1. Download the new `.skill` file from Releases
2. In Claude/Cowork → Settings → Skills → Remove old version
3. Upload new `.skill` file
4. Your `config.json` carries over — no need to re-enter your info
