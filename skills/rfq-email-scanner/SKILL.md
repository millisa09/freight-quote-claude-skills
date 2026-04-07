---
name: rfq-email-scanner
description: >
  Scan Gmail for incoming RFQ and rate request emails, extract load details, and
  draft quote replies ready for review. Use this skill when someone says "check my
  emails for RFQs", "scan my inbox for quote requests", "any rate requests come in?",
  "did anyone send a freight quote request", "check for new RFQs", "what quote emails
  do I have", or "scan inbox for loads". Also trigger when the user asks to process
  or respond to a batch of incoming rate requests. Requires Gmail MCP to be connected.
  Never auto-sends — always presents drafts for broker review and approval first.
---

# RFQ Email Scanner

Connects to Gmail, finds rate request emails, extracts load details, and drafts
quote replies — all presented for broker review before any action is taken.

> **Requires:** Gmail MCP connected in your Claude/Cowork environment.
> See INSTALL.md for Gmail MCP setup instructions.

---

## Step 1 — Confirm Gmail Connection

Before scanning, verify Gmail MCP is available. If not connected, tell the user:

> "I need Gmail access to scan for RFQ emails. Go to Settings → Connectors → Gmail
> and connect your account, then come back and try again."

---

## Step 2 — Search for RFQ Emails

Search Gmail using these query terms (combine with OR logic):

```
subject:(quote OR rate OR RFQ OR "need a truck" OR "freight quote" OR "can you cover" OR pricing OR "rate request")
is:unread
newer_than:7d
```

Also check:
- Emails with load details in the body (origin, destination, weight, dims)
- Replies to existing quote threads asking for updated pricing
- Emails from known shipper domains (if the broker has provided a list)

Retrieve up to **20 emails** per scan unless the user specifies a different window.

---

## Step 3 — For Each RFQ Email Found

Extract these fields from the email body:

| Field | Look For |
|---|---|
| Sender name + company | From field + email signature |
| Origin | "from", "pickup at", "origin", city/state/zip |
| Destination | "to", "deliver to", "destination" |
| Commodity | What is being shipped |
| Weight | lbs, tons, weight |
| Dimensions | L x W x H, length, width, height |
| Service type | flatbed, reefer, van, LTL, Conestoga, hot shot |
| Requested pickup date | "pickup", "available", "ready" |
| Requested delivery date | "delivery", "due", "needed by" |
| Any rate already mentioned | If shipper gave a target rate |

If fields are missing and cannot be inferred, flag them as **[UNKNOWN — confirm
with shipper]** in the draft rather than asking the broker to go back and re-read.

---

## Step 4 — Present a Summary Table

Before drafting replies, show a summary of all RFQs found:

```
Found 3 RFQ emails in the last 7 days:

| # | From | Lane | Weight | Service | Received |
|---|------|------|--------|---------|----------|
| 1 | Seth Geller / Machinery Network | PA → MN | 13,000 lbs | Conestoga LTL | Today 9:14am |
| 2 | Karen Rode / Campetella USA | MA → CA | 8,500 lbs | Flatbed | Yesterday 3:41pm |
| 3 | Gina M. / Kelly Pipe | TX → OH | 44,000 lbs | Flatbed | 3 days ago |

Which would you like me to draft quote replies for? (Say "all", "1 and 3", or a number)
```

---

## Step 5 — Draft Quote Replies

For each selected RFQ, draft a reply email in this format:

```
Subject: Re: [Original Subject] — Freight Quote | [Broker Company]

Hi [Sender First Name],

Thank you for reaching out. Please see our quote below for the shipment
described.

QUOTE SUMMARY
Origin:        [Extracted origin]
Destination:   [Extracted destination]
Service Type:  [Service type]
Weight:        [Weight]
Equipment:     [Equipment]
Estimated Rate: $[RATE — TO BE FILLED IN BY BROKER]

This quote is valid for [X] business days from today.

To move forward, please reply to confirm and we will get your load covered.

Best regards,
[Broker Contact Name]
[Broker Company] | [MC#]
[Phone] | [Email]
```

**Important:** Leave `$[RATE — TO BE FILLED IN BY BROKER]` as a clear placeholder.
Never insert a rate. The broker sets the rate — the skill drafts everything else.

---

## Step 6 — Option to Generate Full PDF Quote

After presenting the draft reply, ask:

> "Would you like me to generate a full PDF quote for any of these?
> Just give me the rate and I'll build it."

If yes, hand off to the `freight-quote` skill with the extracted load data
pre-populated. The broker only needs to supply the dollar amount.

---

## Output Summary

For each RFQ processed, present:
1. Extracted load details (confirm accuracy)
2. Draft reply email (ready to copy or send after broker review)
3. Option to generate PDF quote

Always end with:
> "Please review each draft before sending. I have not sent anything — all emails
> require your approval."

---

## Privacy & Security Notes

- This skill **reads** email only — it never sends without explicit broker confirmation
- Email content is used only to extract load details — not stored or logged
- For brokers with multiple Gmail accounts, specify which account to scan
