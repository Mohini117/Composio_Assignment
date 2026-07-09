"""
The 100-app research set for the Composio AI Product Ops take-home.
Grouped into the 10 categories exactly as given in the assignment brief.

Each entry is a dict:
    name  -> app name (used in search queries)
    hint  -> website / docs URL hint given in the brief (used to bias search
             towards the right domain and as a fallback fetch target)
    category -> one of the 10 categories below

This file is pure data. No logic here on purpose — agent.py imports APPS
and iterates over it. Keeping data and pipeline separate means you can
re-run on a subset (e.g. APPS[:5] for a smoke test) without touching the
pipeline code.
"""

CATEGORIES = [
    "CRM and Sales",
    "Support and Helpdesk",
    "Communications and Messaging",
    "Marketing, Ads, Email and Social",
    "Ecommerce",
    "Data, SEO and Scraping",
    "Developer, Infra and Data platforms",
    "Productivity and Project Management",
    "Finance and Fintech",
    "AI, Research and Media-native",
]

APPS = [
    # 1. CRM and Sales
    {"name": "Salesforce", "hint": "salesforce.com", "category": "CRM and Sales"},
    {"name": "HubSpot", "hint": "hubspot.com", "category": "CRM and Sales"},
    {"name": "Pipedrive", "hint": "pipedrive.com", "category": "CRM and Sales"},
    {"name": "Attio", "hint": "attio.com", "category": "CRM and Sales"},
    {"name": "Twenty", "hint": "twenty.com", "category": "CRM and Sales"},
    {"name": "Podio", "hint": "podio.com", "category": "CRM and Sales"},
    {"name": "Zoho CRM", "hint": "zoho.com/crm", "category": "CRM and Sales"},
    {"name": "Close", "hint": "close.com", "category": "CRM and Sales"},
    {"name": "Copper", "hint": "copper.com", "category": "CRM and Sales"},
    {"name": "DealCloud", "hint": "api.docs.dealcloud.com", "category": "CRM and Sales"},

    # 2. Support and Helpdesk
    {"name": "Zendesk", "hint": "zendesk.com", "category": "Support and Helpdesk"},
    {"name": "Intercom", "hint": "intercom.com", "category": "Support and Helpdesk"},
    {"name": "Freshdesk", "hint": "freshdesk.com", "category": "Support and Helpdesk"},
    {"name": "Front", "hint": "front.com", "category": "Support and Helpdesk"},
    {"name": "Pylon", "hint": "usepylon.com", "category": "Support and Helpdesk"},
    {"name": "LiveAgent", "hint": "liveagent.com", "category": "Support and Helpdesk"},
    {"name": "Plain", "hint": "plain.com", "category": "Support and Helpdesk"},
    {"name": "Help Scout", "hint": "helpscout.com", "category": "Support and Helpdesk"},
    {"name": "Gorgias", "hint": "gorgias.com", "category": "Support and Helpdesk"},
    {"name": "Gladly", "hint": "gladly.com", "category": "Support and Helpdesk"},

    # 3. Communications and Messaging
    {"name": "Slack", "hint": "slack.com", "category": "Communications and Messaging"},
    {"name": "Twilio", "hint": "twilio.com", "category": "Communications and Messaging"},
    {"name": "Zoho Cliq", "hint": "zoho.com/cliq", "category": "Communications and Messaging"},
    {"name": "Lark (Larksuite)", "hint": "open.larksuite.com", "category": "Communications and Messaging"},
    {"name": "Pumble", "hint": "pumble.com", "category": "Communications and Messaging"},
    {"name": "Discord", "hint": "discord.com", "category": "Communications and Messaging"},
    {"name": "Telegram", "hint": "core.telegram.org", "category": "Communications and Messaging"},
    {"name": "WhatsApp Business", "hint": "developers.facebook.com/docs/whatsapp", "category": "Communications and Messaging"},
    {"name": "Aircall", "hint": "aircall.io", "category": "Communications and Messaging"},
    {"name": "Vonage", "hint": "developer.vonage.com", "category": "Communications and Messaging"},

    # 4. Marketing, Ads, Email and Social
    {"name": "Google Ads", "hint": "developers.google.com/google-ads", "category": "Marketing, Ads, Email and Social"},
    {"name": "Meta Ads", "hint": "developers.facebook.com/docs/marketing-apis", "category": "Marketing, Ads, Email and Social"},
    {"name": "LinkedIn Ads", "hint": "learn.microsoft.com/linkedin/marketing", "category": "Marketing, Ads, Email and Social"},
    {"name": "GoHighLevel", "hint": "highlevel.stoplight.io", "category": "Marketing, Ads, Email and Social"},
    {"name": "Mailchimp", "hint": "mailchimp.com/developer", "category": "Marketing, Ads, Email and Social"},
    {"name": "Klaviyo", "hint": "developers.klaviyo.com", "category": "Marketing, Ads, Email and Social"},
    {"name": "systeme.io", "hint": "systeme.io", "category": "Marketing, Ads, Email and Social"},
    {"name": "Pinterest", "hint": "developers.pinterest.com", "category": "Marketing, Ads, Email and Social"},
    {"name": "Threads (Meta)", "hint": "developers.facebook.com/docs/threads", "category": "Marketing, Ads, Email and Social"},
    {"name": "SendGrid", "hint": "sendgrid.com", "category": "Marketing, Ads, Email and Social"},

    # 5. Ecommerce
    {"name": "Shopify", "hint": "shopify.dev", "category": "Ecommerce"},
    {"name": "WooCommerce", "hint": "woocommerce.com/document/woocommerce-rest-api", "category": "Ecommerce"},
    {"name": "BigCommerce", "hint": "developer.bigcommerce.com", "category": "Ecommerce"},
    {"name": "Salesforce Commerce Cloud", "hint": "developer.salesforce.com/docs/commerce", "category": "Ecommerce"},
    {"name": "Magento (Adobe Commerce)", "hint": "developer.adobe.com/commerce", "category": "Ecommerce"},
    {"name": "Squarespace", "hint": "developers.squarespace.com", "category": "Ecommerce"},
    {"name": "Ecwid", "hint": "api-docs.ecwid.com", "category": "Ecommerce"},
    {"name": "Gumroad", "hint": "gumroad.com/api", "category": "Ecommerce"},
    {"name": "Amazon Selling Partner", "hint": "developer-docs.amazon.com/sp-api", "category": "Ecommerce"},
    {"name": "fanbasis", "hint": "fanbasis.com", "category": "Ecommerce"},

    # 6. Data, SEO and Scraping
    {"name": "DataForSEO", "hint": "docs.dataforseo.com", "category": "Data, SEO and Scraping"},
    {"name": "SE Ranking", "hint": "seranking.com/api", "category": "Data, SEO and Scraping"},
    {"name": "Ahrefs", "hint": "ahrefs.com/api", "category": "Data, SEO and Scraping"},
    {"name": "MrScraper", "hint": "docs.mrscraper.com", "category": "Data, SEO and Scraping"},
    {"name": "Apify", "hint": "docs.apify.com", "category": "Data, SEO and Scraping"},
    {"name": "Firecrawl", "hint": "firecrawl.dev", "category": "Data, SEO and Scraping"},
    {"name": "Bright Data", "hint": "brightdata.com", "category": "Data, SEO and Scraping"},
    {"name": "Sherlock", "hint": "github.com/sherlock-project/sherlock", "category": "Data, SEO and Scraping"},
    {"name": "Waterfall.io", "hint": "waterfall.io", "category": "Data, SEO and Scraping"},
    {"name": "Clay", "hint": "clay.com", "category": "Data, SEO and Scraping"},

    # 7. Developer, Infra and Data platforms
    {"name": "GitHub", "hint": "docs.github.com/rest", "category": "Developer, Infra and Data platforms"},
    {"name": "Vercel", "hint": "vercel.com/docs/rest-api", "category": "Developer, Infra and Data platforms"},
    {"name": "Netlify", "hint": "docs.netlify.com/api", "category": "Developer, Infra and Data platforms"},
    {"name": "Cloudflare", "hint": "developers.cloudflare.com/api", "category": "Developer, Infra and Data platforms"},
    {"name": "Supabase", "hint": "supabase.com/docs", "category": "Developer, Infra and Data platforms"},
    {"name": "Neo4j", "hint": "neo4j.com/docs/api", "category": "Developer, Infra and Data platforms"},
    {"name": "Snowflake", "hint": "docs.snowflake.com", "category": "Developer, Infra and Data platforms"},
    {"name": "MongoDB Atlas", "hint": "mongodb.com/docs/atlas/api", "category": "Developer, Infra and Data platforms"},
    {"name": "Datadog", "hint": "docs.datadoghq.com/api", "category": "Developer, Infra and Data platforms"},
    {"name": "Sentry", "hint": "docs.sentry.io/api", "category": "Developer, Infra and Data platforms"},

    # 8. Productivity and Project Management
    {"name": "Notion", "hint": "developers.notion.com", "category": "Productivity and Project Management"},
    {"name": "Airtable", "hint": "airtable.com/developers", "category": "Productivity and Project Management"},
    {"name": "Linear", "hint": "developers.linear.app", "category": "Productivity and Project Management"},
    {"name": "Jira", "hint": "developer.atlassian.com", "category": "Productivity and Project Management"},
    {"name": "Asana", "hint": "developers.asana.com", "category": "Productivity and Project Management"},
    {"name": "Monday.com", "hint": "developer.monday.com", "category": "Productivity and Project Management"},
    {"name": "ClickUp", "hint": "clickup.com/api", "category": "Productivity and Project Management"},
    {"name": "Coda", "hint": "coda.io/developers", "category": "Productivity and Project Management"},
    {"name": "Smartsheet", "hint": "smartsheet.com/developers", "category": "Productivity and Project Management"},
    {"name": "Harvest", "hint": "help.getharvest.com/api-v2", "category": "Productivity and Project Management"},

    # 9. Finance and Fintech
    {"name": "Stripe", "hint": "stripe.com/docs/api", "category": "Finance and Fintech"},
    {"name": "Plaid", "hint": "plaid.com/docs", "category": "Finance and Fintech"},
    {"name": "Binance", "hint": "binance-docs.github.io", "category": "Finance and Fintech"},
    {"name": "Paygent Connect", "hint": "paygent (NMI-powered)", "category": "Finance and Fintech"},
    {"name": "iPayX", "hint": "ipayx.ai/docs", "category": "Finance and Fintech"},
    {"name": "QuickBooks", "hint": "developer.intuit.com", "category": "Finance and Fintech"},
    {"name": "Xero", "hint": "developer.xero.com", "category": "Finance and Fintech"},
    {"name": "Brex", "hint": "developer.brex.com", "category": "Finance and Fintech"},
    {"name": "Ramp", "hint": "docs.ramp.com", "category": "Finance and Fintech"},
    {"name": "PitchBook", "hint": "pitchbook.com", "category": "Finance and Fintech"},

    # 10. AI, Research and Media-native
    {"name": "NotebookLM", "hint": "cloud.google.com/gemini", "category": "AI, Research and Media-native"},
    {"name": "Otter AI", "hint": "help.otter.ai", "category": "AI, Research and Media-native"},
    {"name": "Fathom", "hint": "fathom.video", "category": "AI, Research and Media-native"},
    {"name": "Consensus", "hint": "consensus.app", "category": "AI, Research and Media-native"},
    {"name": "Reducto", "hint": "reducto.ai", "category": "AI, Research and Media-native"},
    {"name": "Devin", "hint": "docs.devin.ai", "category": "AI, Research and Media-native"},
    {"name": "higgsfield", "hint": "higgsfield.ai/cli", "category": "AI, Research and Media-native"},
    {"name": "Mermaid CLI", "hint": "github.com/mermaid-js/mermaid-cli", "category": "AI, Research and Media-native"},
    {"name": "YouTube Transcript", "hint": "transcriptapi.com", "category": "AI, Research and Media-native"},
    {"name": "Grain", "hint": "grain.com", "category": "AI, Research and Media-native"},
]

assert len(APPS) == 100, f"Expected 100 apps, got {len(APPS)}"

if __name__ == "__main__":
    # quick sanity check when run directly: python apps.py
    from collections import Counter
    counts = Counter(a["category"] for a in APPS)
    for cat in CATEGORIES:
        print(f"{cat:45s} {counts[cat]}")
    print(f"\nTotal: {len(APPS)}")