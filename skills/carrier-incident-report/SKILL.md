---
name: carrier-incident-report
description: >
  Document carrier service failures and draft professional response emails.
  Use this skill whenever there is a service failure, violation, or dispute
  involving a carrier on any load. Triggers include: missed delivery appointments,
  driver unreachable, tracking non-compliance, DOT/safety violations, misrepresentation
  of driver location or status, detention disputes, cargo damage or shortage, driver
  refusing to communicate, re-brokering without consent, or any situation where you
  need to document a carrier failure for internal records or payment dispute purposes.
  Also trigger when someone says "start an incident report", "document this carrier",
  "write up this load", "I need to file on this carrier", or "carrier dropped the ball".
  Generates a formal Word document incident report AND drafts both a carrier-facing
  and customer-facing email based on the facts of the incident.
---

# Carrier Incident Report

Documents carrier failures professionally and generates both a Word incident report
and two draft emails — one to the carrier, one to the customer.

---

## Step 1 — Gather Incident Facts

Extract the following from the conversation. Ask only for what's missing:

| Field | Required | Notes |
|---|---|---|
| Load / Pro Number | Yes | Your internal load reference |
| Carrier Name | Yes | Legal carrier name |
| MC / DOT Number | If known | |
| Driver Name | If known | |
| Driver Phone | If known | |
| Dispatcher Name / Contact | If known | |
| Origin | Yes | City, ST |
| Destination | Yes | City, ST |
| Commodity | Yes | What was being shipped |
| Pickup Date | Yes | |
| Delivery Date (scheduled) | Yes | |
| Violation / Failure Type | Yes | See categories below |
| Timeline of Events | Yes | What happened, in order, with times |
| Customer Name | Yes | Who the load was for |
| Financial Impact | If applicable | Detention, re-delivery costs, claims |
| Resolution Status | Yes | Open / Resolved / Pending |

### Violation Categories
- Missed delivery appointment
- Driver unreachable / no check-ins
- GPS / tracking non-compliance
- Cargo damage or shortage
- Driver misrepresenting location
- Detention dispute
- Late pickup
- Re-brokering without consent
- Equipment failure or wrong equipment
- DOT / safety violation
- Other (specify)

---

## Step 2 — Generate the Report

Using the gathered facts, produce:

### A) Incident Report Document (Word .docx)

Structure:
```
CARRIER INCIDENT REPORT
[Broker Company] | [MC#] | [Date]

LOAD INFORMATION
- Load #, Carrier, MC#, Driver, Equipment
- Origin → Destination, Commodity, Pickup/Delivery dates

INCIDENT SUMMARY
- 2–3 sentence plain-language summary of what happened

TIMELINE OF EVENTS
- Bullet list: [Date/Time] — Event description

VIOLATION / FAILURE TYPE
- Category + specific details

FINANCIAL IMPACT
- Any costs incurred or at risk

RESOLUTION STATUS
- Current status and next steps

DOCUMENTATION
- Note any emails, calls, screenshots referenced
```

### B) Email to Carrier

Tone: firm, factual, professional. Reference the load number. State the violation
clearly. Request explanation or resolution. Note impact on future bookings if severe.

Template:
```
Subject: Load #[NUMBER] — Service Failure Notice | [Carrier Name]

[Carrier/Dispatcher Name],

This message serves as formal documentation of a service failure on Load #[NUMBER]...

[State the facts clearly]

We request [explanation / resolution / credit] by [date].

This incident has been documented in our carrier file. Please respond...
```

### C) Email to Customer

Tone: reassuring, apologetic, solution-focused. Do not place blame on carrier by name
unless customer specifically asks. Focus on what is being done to resolve it.

Template:
```
Subject: Load #[NUMBER] — Service Update | [Broker Company]

[Customer Name],

We want to keep you informed regarding your shipment...

[Brief factual summary without excessive detail]

Here is where things stand and what we are doing...

We apologize for any inconvenience and appreciate your patience.
```

---

## Step 3 — Output

Present:
1. The incident report `.docx` file for download
2. The carrier email draft (in conversation, ready to copy)
3. The customer email draft (in conversation, ready to copy)

Ask: "Would you like me to adjust the tone on either email, or add any additional
documentation notes to the report?"

---

## Notes

- Never make legal claims or accusations in the carrier email — state facts only
- Never share carrier identity with customer unless broker chooses to
- Always recommend the broker review both emails before sending
- This report is for internal documentation and dispute resolution purposes
