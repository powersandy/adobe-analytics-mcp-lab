# L611: Data Mirror and MCP — Modern Connectivity for Customer Journey Analytics

**Adobe Summit 2026 Lab** | *lab number: L611*

---

## Introduction

This lab explores two Adobe capabilities that change how data gets into Customer Journey Analytics and how you interact with it once it's there.

**Data Mirror** keeps CJA in sync with your external data warehouse automatically — at the row level, using Change Data Capture (CDC). When a record is inserted, updated, or deleted at the source, the change propagates through the Adobe Experience Platform data lake and into CJA without any export scripts, batch jobs, or manual refresh.

**The CJA MCP Server** implements the Model Context Protocol, connecting AI coding tools like Cursor directly to your live CJA environment. Instead of navigating Analysis Workspace to build reports and segments, you describe what you want in plain language and the agent builds it.

Together, these two capabilities address the two most common friction points in analytics work: getting accurate data in, and getting insights out fast.

---

### Goals

After completing this lab, you will walk away with the following knowledge:

- What Data Mirror is, how CDC-based ingestion works, and when to use it over batch or incremental connectors
- How to recognize the three relational schema descriptor fields required for Data Mirror
- What the Model Context Protocol (MCP) is and how it connects AI clients to live analytics data
- How to connect Cursor to the CJA MCP Server and verify the connection
- How to create CJA Analysis Workspace projects using only natural language prompts
- How to audit your CJA component library for health, waste, and duplicate segments at scale
- How to build simple and sequential segments through conversation — including complex THEN logic with time restrictions

---

### Prerequisites

Before starting this lab, confirm you have the following:

- Basic familiarity with CJA — you know what a data view, workspace, and segment are
- Cursor installed and running on your lab computer
- Your Adobe IMS credentials (Experience Cloud login) available
- CJA access provisioned for the lab sandbox (your lab setup confirms this)
- No coding experience required — all exercises use natural language prompts

---

### Customer Scenario

The lab is built around **Luma**, a fictional multi-channel retail brand selling apparel and accessories online and in stores.

Your role: you are a CJA analyst at Luma. Your team is responsible for maintaining accurate customer journey data and delivering timely insights to the marketing and e-commerce teams. You face two persistent challenges:

1. **Data freshness** — Luma's product catalog and campaign data live in external cloud systems (BigQuery, Azure Blob, S3). Every time a product price changes or a campaign window closes, someone has to manually export a file and re-upload it. Reports go stale between refreshes.
2. **Analysis speed** — Building a workspace from scratch takes 30+ minutes. Your team spends more time assembling panels than interpreting results.

This lab shows you how to solve both.

---

### Technical Architecture

Two capabilities, two data flows:

```
DATA MIRROR — keeping CJA in sync with your warehouse
─────────────────────────────────────────────────────
  Source Warehouse                AEP                    CJA
  ┌─────────────┐    CDC     ┌──────────┐  Dataset  ┌─────────┐
  │  BigQuery   │──────────▶│ Source   │──────────▶│         │
  │  Azure Blob │  (insert/ │ Connector │           │  Data   │
  │  Amazon S3  │  update/  │    +      │           │  View   │
  └─────────────┘   delete) │ Relational│           │         │
                            │  Schema  │           └─────────┘
                            └──────────┘

CJA MCP SERVER — natural language access to your CJA data
──────────────────────────────────────────────────────────
  AI Client                MCP Server              CJA APIs
  ┌────────┐   MCP/HTTPS  ┌──────────┐   REST    ┌─────────┐
  │ Cursor │◀────────────▶│  CJA MCP │◀─────────▶│  CJA    │
  │        │   (tools,    │  Server  │           │  APIs   │
  └────────┘    results)  └──────────┘           └─────────┘
```

> **Note:** Data Mirror requires a one-time setup in AEP (schema, dataset, source connector). Once configured, it runs continuously. The CJA MCP Server is already hosted — you connect to it in Lesson 2 with a single JSON config entry.

---

**Before you begin — confirm your setup:**

- You can log in to CJA at [experience.adobe.com](https://experience.adobe.com)
- Cursor is installed and open on your lab computer
- You have your Adobe IMS credentials ready

---

## Environment setup

To prepare our environment today using *Cursor* we have a few setup steps to follow. Begin these steps as soon as you arrive in the lab.

### Setup 1: Open Cursor

Cursor is the sdk platform we will use today with the CJA MCP server. Open it from your application list.

<img width="168" height="38" alt="Screenshot 2026-04-03 141758" src="https://github.com/user-attachments/assets/7761c37c-bf73-475e-984a-a61a7b206a16" />

### Setup 2: Clone our Git repository

This step is a simple way to download files we need. In Github, the terminology is that we are cloning a public repository.

1. Cursor will open to a black window like this. Click on the *Clone repo* option.

<img width="448" height="179" alt="Screenshot 2026-04-03 142109" src="https://github.com/user-attachments/assets/d31260ff-eccf-459f-b4e8-739c534224a2" />

2. In the text bar that has appeared, paste the following URL and click *Clone from URL*.

```
https://github.com/Adobe-Experience-Cloud/adobe-analytics-mcp-lab
```

<img width="529" height="84" alt="AdobeExpressPhotos_26e57926bbcc47c58cfd164169b25eb8_CopyEdited" src="https://github.com/user-attachments/assets/e95c2f8d-bd7b-494b-87a5-e32dd30d68d4" />

3. Select any location, such as the desktop, for the repo to be saved.

*IMAGE:mac finder type window*

Your screen should look similar to this, afterward:

*IMAGE:cursor window*

### Setup 3: Config Cursor

Now, we just need to tell Cursor how to reach CJA and help us connect.

1. Open an agent chat via ______.

*IMAGE:agent chat open button*

2. Paste this prompt into chat so Cursor use the CJA MCP server info from our download.

```
Add my cja mcp server to the global Cursor settings.
```

<img width="479" height="89" alt="AdobeExpressPhotos_dfbdba47b8514d9b95b3c51d9ed23ac6_CopyEdited" src="https://github.com/user-attachments/assets/d7b14b05-938c-41d3-8dc9-1bb864527f9d" />

This should process quickly, taking only a few seconds. Instead of clicking through Settings menus, we are using the downloaded files and the Composer agent in Cursor to automate setup.

3. Submit this prompt to open web authentication for CJA.

```
Authenticate to CJA using mcp_auth.
```

As before, this should only take a few seconds. Cursor will hopefully make a call and produce this interactive result for you. Click *Authenticate*:

<img width="478" height="207" alt="AdobeExpressPhotos_b0c2b17aff54421b87bf69f9a614765a_CopyEdited" src="https://github.com/user-attachments/assets/27aa4344-1714-4cff-9b5d-7c368e90c9b3" />

4. On web auth, select *Experience Showcase* (if asked) and click OK.

*IMAGE: org choice*

5. On the following screen, click *Allow access*:

<img width="415" height="581" alt="AdobeExpressPhotos_c07022c6ea14438bb535f87a152922c5_CopyEdited" src="https://github.com/user-attachments/assets/6c0bc68d-edd8-4f7e-978a-3978d95b79f5" />

Now, Cursor should say some positive comments about being connected. If so, you can confirm the connection to CJA is active with a prompt like this:

```
What data views can I access?
```

If Cursor returns a small list including the L611 data view, then you are ready! *Leave the Cursor app alone until we get to the MCP tasks in a few minutes.*

**Problems connecting?**
If any of the steps above didn't work, here are the manual click instructions to ensure you are setup for Cursor.

### Manual setup instructions ###

.... INSTRUCTIONS WILL GO HERE - SETTINGS > MCP, CONNECT, ETC. ....


---

## Lesson 1 of 4 — Data Mirror

est completion: 10 min *(No Cursor needed for this lesson)*

---

### 1.1 Objectives

By the end of this lesson you will be able to:

- Explain what Data Mirror does and the problem it solves
- Describe how CDC-based ingestion differs from batch and incremental connectors
- Identify the three descriptor fields a relational schema requires for CDC
- Recognize when Data Mirror is the right tool vs. other AEP ingestion options

### 1.2 What is Data Mirror?

Most analytics teams have the same problem: data in CJA goes stale. A product price changes in the warehouse, a campaign ends, a customer profile updates — but CJA doesn't know until someone runs an export script and re-uploads a file. By then the data is hours or days old.

**Data Mirror** is an Adobe Experience Platform capability that solves this by ingesting row-level changes from external databases into the AEP data lake automatically, using **Change Data Capture (CDC)**. When a record is inserted, updated, or deleted at the source, that change flows through to AEP — and from there to CJA — without any manual intervention.

**How it works:**

1. The source database or cloud storage emits a change record (an insert, update, or delete)
2. An **AEP Source Connector** picks it up and passes it to AEP ingestion
3. A **relational schema** (a newer AEP schema type) matches the incoming record to the existing row by primary key, applies the change, and updates the version
4. The AEP **data lake** reflects the latest state of the data
5. **CJA** reads from the data lake — reports now reflect the current source of truth

**What makes relational schemas different:**
Standard XDM schemas in AEP are append-only — you can add rows but not update or delete them. Relational schemas enforce a **primary key**, track a **version field** (timestamp or integer), and support deletes via a **CDC operation type**. This is what enables Data Mirror to propagate mutations, not just inserts.

**Key capabilities:	**

- Primary key enforcement — each row has a unique, stable identifier
- CDC: inserts, updates, and deletes all propagate
- Out-of-order handling — late-arriving records are reconciled by version field
- Direct integration with BigQuery, Azure Blob Storage, Amazon S3, Snowflake, and other sources

### 1.3 Background: The Luma Retail Data Set

The lab data set is a fictional retail brand called **Luma**. It spans four tables across three cloud sources:


| Table               | Type                  | Source             | Records | Purpose                                                  |
| ------------------- | --------------------- | ------------------ | ------- | -------------------------------------------------------- |
| `web_traffic`       | Time Series / Event   | Google BigQuery    | 1,000   | Clickstream events (page views, purchases, cart actions) |
| `customer_profiles` | Record / Profile      | Google BigQuery    | 200     | Customer identity, loyalty tier, region                  |
| `products`          | Record / Lookup       | Azure Blob Storage | 50      | Product catalog with category and price                  |
| `campaigns`         | Time Series / Summary | Amazon S3          | 5       | Campaign windows, Jan–Feb 2026                           |


**How the tables relate:**

- Every event in `web_traffic` links to a customer via `person_id`
- Every event links to a product via `product_id`
- Events that occurred during an active campaign carry a `campaign_id`

**CDC fields in the data model:**

Each table carries the fields Data Mirror needs to track changes:


| Table               | Primary Key   | Version Field                            | Notes                                             |
| ------------------- | ------------- | ---------------------------------------- | ------------------------------------------------- |
| `web_traffic`       | `event_id`    | `version_no` (integer, increments 0→1→2) | BigQuery native CDC                               |
| `customer_profiles` | `person_id`   | `version_time` (datetime)                | BigQuery native CDC                               |
| `products`          | `product_id`  | `last_modified_time` (datetime)          | Cloud storage: uses `_change_request_type` column |
| `campaigns`         | `campaign_id` | `campaign_version` (datetime)            | Cloud storage: uses `_change_request_type` column |


### 1.4 Exercise: See Data Mirror in Action

Two Data Mirror setups are running during this session: a **live setup** where a change is being applied now, and a **pre-run setup** where the same change was applied earlier and has already fully propagated. CDC propagation takes longer than the lab window, so the pre-run setup lets you observe the end result without waiting.

**Part 1 — How the change is applied**

**Step 1 — The source data**

The source `products` table lives in Azure Blob Storage. The current price for **PROD-1001 (Classic Cotton T-Shirt) is $29.99**.

**Step 2 — The change**

A CDC file — `products_update.json` — is being uploaded to Azure Blob. It contains two records:

- **DELETE** (`d`): PROD-1003 (Lightweight Running Jacket) — removing this product from the catalog
- **UPDATE** (`u`): PROD-1001 (Classic Cotton T-Shirt) — price changed from $29.99 to **$24.99**

> **Note:** For cloud storage sources (Azure Blob, S3), CDC is signaled by a `_change_request_type` column on each row: `"u"` for upsert (insert or update, matched by primary key) and `"d"` for delete. This column is processed by Data Mirror during ingestion and is not stored in the AEP dataset. Database sources like BigQuery handle CDC natively through a change feed.

**Step 3 — How it travels through the pipeline**

Once the file lands in Azure Blob, here is what happens:

1. The AEP Source Connector detects the new file
2. Data Mirror reads `_change_request_type` and matches each row by primary key (`product_id`)
3. The relational schema applies the upsert: the version field (`last_modified_time`) is newer, so the record is updated
4. The delete removes PROD-1003 from the dataset
5. CJA reflects the updated catalog once ingestion completes

**Part 2 — See the completed result**

The pre-run setup has already completed this same pipeline. Open CJA on your lab computer and find a freeform table showing products and prices. Observe:

- **PROD-1001 (Classic Cotton T-Shirt)** shows **$24.99** — the update has propagated
- **PROD-1003 (Lightweight Running Jacket)** no longer appears — the delete took effect

This is the end state the live setup will reach once its propagation completes.

### 1.5 Where Data Mirror Fits

Not every ingestion scenario calls for Data Mirror. Here's how it compares:


| Method                        | Best For                             | Latency            | Supports Updates/Deletes            |
| ----------------------------- | ------------------------------------ | ------------------ | ----------------------------------- |
| Flat file / CSV upload        | One-time or ad-hoc loads             | Manual             | No                                  |
| Incremental source connectors | Append-only data streams             | Minutes–hours      | Inserts only                        |
| **Data Mirror (CDC)**         | **Live sync with mutation tracking** | **Near real-time** | **Yes — inserts, updates, deletes** |


### 1.6 Checkpoint

Take a moment to answer these before moving on:

- What happens in CJA when a record is **deleted** at the source? Does it disappear from reports?
- What are the three descriptor fields a relational schema must mark for CDC to work? *(Hint: you saw them in the data model table above)*
- Name a data scenario in your own work where Data Mirror would be more useful than a batch connector.

---

---

## 2 — Intro to CJA MCP Server

est completion: 10 min

---

### 2.1 Objectives

By the end of this lesson you will be able to:

- Explain what MCP is and how it enables AI-to-CJA connectivity
- Connect Cursor to the CJA MCP Server
- Verify that CJA tools are available in an Agent chat
- Create a simple CJA project using natural language

### 2.2 What is MCP?

**MCP (Model Context Protocol)** is an open standard for connecting AI applications to external data sources and tools. It provides a universal interface so AI clients — Cursor, Claude.ai, ChatGPT — can securely access live data and take actions on your behalf, without requiring a custom integration for each platform.

MCP is like an API for AI/LLM agents. You chat conversationally with AI tool like normal but now that AI platform can connect to CJA to pull data, build a dashboard, check components, etc.

**What the CJA MCP Server exposes:**


| Category      | What you can do                                                                   |
| ------------- | --------------------------------------------------------------------------------- |
| Discovery     | Find data views, dimensions, metrics, segments, date ranges, projects             |
| Reporting     | Run freeform reports, search dimension items                                      |
| Creation      | Create and update workspaces, segments, calculated metrics                        |
| Governance    | List component usage, find similar components, find frequently co-used components |
| Configuration | Set session defaults (data view, context)                                         |


Instead of navigating Analysis Workspace manually, you describe what you want: *"Show me mobile revenue by product category for the last 30 days"* — the agent runs the query and returns results directly.

**How it differs from Data Insights Agent in CJA/AEP**

In the CJA UI, there is a feature called Data Insights Agent or AI Assistant. It will answer simple information requests, report updates, etc. but only within your CJA/AEP context. The MCP server facilitates those too, but it is the power of the chat agent you use which takes it farther. You can give an AI like ChatGPT a complex prompt, with external references, instructing it to generate a unique CJA report app for you. This lab will explore the possibilities.



<image of CJA app for contrast - maybe>

### 2.3 Connect to the CJA MCP Server

The steps we are about to complete is ALL that is needed to set up the environment for conversational work in CJA. 

1. Open **Cursor**
2. Navigate to **File → Preferences → Cursor Settings → Tools & MCP → Add New MCP Server**
3. An editor opens with `mcp.json`. Replace its contents entirely with the following:
  ```json
   {
     "mcpServers": {
       "cja": {
         "type": "streamable-http",
         "url": "https://mcp-gateway.adobe.io/cja/mcp"
       }
     }
   }
  ```
4. Now save the file.
5. Back in **Settings → Tools & MCP**, find the **CJA** server entry and click **Connect**
6. A dialog asks for permission to open the authentication page — click **Open**
7. Your browser opens the Adobe Experience Platform login page. Click ok.
8. Return to Cursor. The CJA server entry should now show as connected, with tools listed below it.
9. Click to toggle the CJA server disabled and then enabled, to ensure agent has access in our current session.

> **Note:** Any MCP-capable OAuth client — Codex, Claude.ai, ChatGPT — connects to the same URL using the same authentication pattern. Only the configuration UI differs by client.

**Verify your connection:**

1. Open a new Agent chat (use the chat panel or press the keyboard shortcut)
2. Type: `Are my CJA tools connected?`
3. The agent should respond with a list of available tools — there are 26 in total.

**Add skills:**

1. Provide a link to the skills folder you downloaded from Github into your agent chat in Cursor.
2. Tell it to `install these skills`.
3. Await confirmation.

Now, we can proceed and explore exciting new use cases!

Lesson 3: Project curation with MCP

### 3.1 Exercise: Create a Workspace with Natural Language

With the MCP server connected, you can describe what you want to analyze and let the agent build it. The `cja-project-builder` **skill** guides the agent through a structured workflow: it discovers your available components, assembles a complete project definition, and calls `upsertProject` to create the workspace in CJA. No dragging panels. No hunting for metric IDs.

> **Note:** The MCP server provides a minimal framework to an LLM that contacts it: pull reports like this, update projects like that, etc. For advanced, customized, repeatable tasks, we can add 'skills' to our LLM for additional context. These skills will be used throughout the lab.

**Follow these prompts in order:**

1. Open a new Agent chat
2. Load the project builder skill through natural language or by invoking it excplicitly:
  ```
   Please make/build a CJA project...

   Use @cja-project-builder...
  ```
3. **Prompt — Basic project create**
  ```
   Make a simple CJA project.
  ```
   The agent uses a basic definition framework to create a project and return its link.
4. **Prompt 1 — Discover your environment:**

```
What data views do I have access to?
```

The agent calls `findDataViews` and returns a list. We have only one for this lab.
4. **Prompt 2 — Set your default data view:**

   The agent calls `setDefaultSessionDataViewId` — now every subsequent tool call uses this data view by default.
5. **Prompt 3 — Ask a data question:**
   Let's start simple to demonstrate its context inference and basic flow.

   The agent looks for context, trying to do something useful and relevant to your task. The request was for information based on report data, so it identified the components and ran CJA reports to give the answer.

1. **Prompt — Create a project:**
  The MCP server functions include project creation. Let's ask it to make that report into a project.
   For initial project create, the LLM consults references and examples. 
   The agent responds with a proposed structure — panels, visualizations, dimensions, metrics - based on your prompt. 
2. **Prompt - follow-ups**
  Try followups. Less context is needed in the active chat.

> **Tip:** Be specific in your prompts. Include time ranges ("last 30 days"), metric names ("orders", "revenue"), and dimensions ("product category") when you know them.

1. **Prompt - tedious/manual create tasks**
  Sometimes I work with a data view that I know little about. I can ask its owner questions, sometimes, but often I prefer to just peek at the components - especially the most used ones. But that is a tough task to manually drag in and copy so many components. It's a visionary task that LLMs + CJA mcp server can enable.

A. **Other prompts and sample results**
   You may try these but sometimes they will require a few minutes, per their complexity.



> **Two modes available:** The project builder works in two modes. **Template mode** (what you just did): describe a project type and the agent builds from a predefined structure. **Clone mode**: copy an existing project and adapt it — *"Copy the [Project Name] project and adapt it for the [Other Data View]"* — the agent calls `describeProject`, swaps the data view, replaces component IDs as needed, and creates a new copy.

### 2.5 Checkpoint

Discuss or reflect:

- Building that workspace manually would take 20–30 minutes. What would you build first for your own team using this approach?
- The agent called several MCP tools in sequence: `findDataViews`, `setDefaultSessionDataViewId`, `findMetrics`, `findDimensions`, `upsertProject`. You didn't need to know any of those tool names. What does that tell you about how MCP changes the analyst workflow?
- What's one thing you'd want to add to the workspace you just created?

---

- Create a CJA Analysis Workspace project using natural language prompts
- Distinguish between Template mode and Clone mode in the project builder

---

## Lesson 3 of 4 — Component Management

est completion: 15 min *(Hands-on in Cursor — three skills)*

All operations in this lesson are **read-only** — the skills report and recommend but never modify anything without your explicit confirmation.

---

### 3.1 Objectives

By the end of this lesson you will be able to:

- Run a full component audit across segments and calculated metrics
- Interpret health scores, usage classifications, and duplicate flags
- Deep-dive into a dimension's cardinality and data quality
- Identify all projects using a specific component in preparation for a replacement

### 3.2 Exercise: Run a Component Audit

Over time, every CJA org accumulates component debt: segments nobody uses, calculated metrics that are near-identical copies of each other, components owned by people who left the team two years ago. The `cja-component-audit` skill scans your entire library and produces an actionable report — without touching a single thing.

1. Open a new Agent chat
2. Load the skill:
  ```
   @cja-component-audit
  ```
3. **Prompt:**
  ```
   Audit all my components on the [Data View Name] data view.
   Include segments and calculated metrics.
  ```
4. The agent works through seven phases:

  | Phase            | What happens                                                          |
  | ---------------- | --------------------------------------------------------------------- |
  | 0 — Setup        | Confirms data view and component types                                |
  | 1 — Inventory    | Pulls full component lists with metadata, definitions, and timestamps |
  | 2 — Usage        | Classifies each component as Active, Stale, or Unused                 |
  | 3 — Duplicates   | Compares definitions; flags near-identical formulas and names         |
  | 4 — Dependencies | Maps which calculated metrics reference which segments                |
  | 5 — Ownership    | Identifies who owns what and flags high concentrations                |
  | 6 — Health       | Calculates a health score (0–100) per component type                  |
  | 7 — Report       | Generates an HTML dashboard or markdown report                        |

5. When the report is ready, review:
  - **Active / Stale / Unused** counts for segments and calculated metrics
  - **Duplicate flags** — pairs with identical or near-identical definitions
  - **Top recommendations** — what to delete, merge, rename, or archive

> **Note:** The audit is strictly read-only. It inventories and reports. It never deletes, modifies, or archives components.

> **Tip:** If the report is large, ask the agent to focus: *"Show me only the unused segments"* or *"Give me the top 5 consolidation recommendations."*

### 3.3 Exercise: Analyze a Dimension

The `cja-dimension-analysis` skill gives you a deep view into a single dimension — how many unique values it has, how skewed the distribution is, whether there are anomalies, and whether there are data quality issues like unexpected gaps or high-cardinality spikes.

1. In the same or a new Agent chat:
  ```
   @cja-dimension-analysis
  ```
2. **Prompt:**
  ```
   Analyze the Product Category dimension.
   Show me cardinality, the top values by event count, and any data quality issues.
  ```
3. The agent returns:
  - **Cardinality** — how many distinct values exist
  - **Top-N distribution** — which values dominate and by how much
  - **Skew** — Gini coefficient and top-N concentration
  - **Data quality flags** — unexpected gaps, anomalous spikes, new/disappeared values

> **Tip:** You can ask follow-up questions: *"Which product categories have the most purchases?"* or *"Are there any category values that appeared recently and might be data quality issues?"*

### 3.4 Exercise: Find and Replace a Component

Before you can safely retire or replace a segment or calculated metric, you need to know which projects use it. The `cja-component-find-replace` skill finds every project that references a specific component, so you have a complete picture before making any changes.

1. Open a new Agent chat:
  ```
   @cja-component-find-replace
  ```
2. **Prompt — find affected projects:**
  ```
   Find all projects that use the segment "[Segment Name]"
  ```
   Use a segment name from your audit report in Exercise 3.2 — ideally one flagged as stale or a duplicate.
3. Review the list of affected projects. Note how many projects would be impacted.
4. **Prompt — plan the replacement:**
  ```
   What would I need to change if I wanted to replace it
   with the segment "[Better Segment Name]"?
  ```
   The agent describes the replacement plan: which projects to update and what the component swap looks like. Actual replacement happens only after your explicit confirmation.

> **Tip:** Combine with the audit: use the health report to identify a consolidation candidate (two near-duplicate segments), find all projects using the weaker one, then plan the migration to the better one.

### 3.5 Checkpoint

- What health score did your component library receive? What was the most common issue?
- How would you incorporate a component audit into a regular governance cadence — monthly, quarterly, before a major analysis project?
- If you found that 40% of your segments were unused, what would be your first step before deleting them?

---

---

## Lesson 4 of 4 — Segment Builder

est completion: 15 min *(Hands-on in Cursor — deep dive on segmentation)*

You'll build a simple segment, a sequential segment, and attempt a challenge segment on your own. The `cja-segment-builder` skill handles the full workflow — finding existing duplicates, clarifying your intent, validating the definition, and creating — all with your confirmation before anything is saved.

---

### 4.1 Objectives

By the end of this lesson you will be able to:

- Build a general segment (AND/OR logic) from a plain-language description
- Build a sequential segment using THEN logic with a time restriction
- Understand the five key sequential pattern types in CJA
- Read and interpret the plain-language segment summary the agent produces before creation
- Apply the duplicate-check workflow to avoid segment bloat

### 4.2 Exercise: Build a Simple Segment

A general segment uses AND/OR logic to filter visitors, visits, or hits based on dimensions and metrics. This is the most common segment type.

1. Open a new Agent chat:
  ```
   @cja-segment-builder
  ```
2. **Prompt:**
  ```
   Create a segment for mobile visitors who viewed a product
   but didn't complete a purchase in the same session.
  ```
3. The agent first **checks for similar existing segments** using `findSegments` and `listSimilarTo`. Review what it finds — if a suitable segment already exists, you may not need to create a new one.
4. The agent then proposes the segment. It will show you:
  - **Name** — a suggested name based on your description
  - **Scope** — Visitor, Visit, or Hit level
  - **Plain-language rules summary** — *"Visitor where: Device Type = Mobile AND visits containing at least one product view event AND no purchase events"*
  - **Components referenced** — a table of dimensions and metrics with their IDs and how they're used
5. Review the proposal carefully. Ask for changes if needed: *"Change the scope to Visit level"* or *"Exclude cases where they removed the item from cart."*
6. When it looks right, confirm:
  ```
   Looks good, create it.
  ```
7. Note the segment ID the agent returns. You'll need it if you want to use this segment in a report or workspace.

> **Tip:** The more specific you are, the less the agent needs to ask. Include scope ("visit-level"), time windows ("within 7 days"), and explicit exclusions ("but not if they also completed a purchase later").

> **Note:** The agent never creates a segment without your explicit confirmation. It always shows you the plain-language summary and the components table first — treat this as your validation step.

### 4.3 Exercise: Build a Sequential Segment

Sequential segments use THEN logic — *"first X happened, then Y happened."* They are the most powerful segmentation capability in CJA and also the hardest to build manually. The JSON structure is complex and easy to get wrong. The segment builder handles it automatically.

1. In the same or a new Agent chat (the skill is already loaded):
2. **Prompt:**
  ```
   Create a segment for visitors who viewed the Collections page
   and then made a purchase within 2 days.
  ```
3. The agent identifies this as a sequential segment. It proposes:
  - **Scope:** Visitor level
  - **Sequence:** Checkpoint 1 → Page Name contains "collections" → THEN within 2 days → Checkpoint 2 → Event Type = purchase
  - The underlying API structure uses `sequence` with a `time-restriction` element between checkpoints
4. Review the logic, then confirm:
  ```
   Yes, create it.
  ```
5. **Optional — test the segment:**
  ```
   Run a quick report with this segment to see how many visitors qualify over the last 30 days.
  ```
   The agent calls `runReport` with the new segment applied.

> **Sequential pattern reference:**
>
>
> | Pattern                 | What it means                                                  |
> | ----------------------- | -------------------------------------------------------------- |
> | **THEN**                | `sequence` — checkpoint A happened, then checkpoint B          |
> | **THEN within X days**  | `time-restriction` element between checkpoints in the sequence |
> | **Everything before X** | `sequence-suffix` — "only before X occurred"                   |
> | **Everything after X**  | `sequence-prefix` — "only after X occurred"                    |
> | **A not followed by B** | `sequence` with `exclude-next-checkpoint` — A then "not B"     |
>

### 4.4 Exercise: Complex Segment Challenge

Try building this segment on your own. It combines multiple concepts: a distinct count condition, scope nesting, and a date-based exclusion.

**Prompt to try:**

```
Build a segment for hits during sessions where the visitor
viewed at least 3 different product categories,
but exclude sessions that happened on December 27, 2025.
```

What the agent will need to do:

- Apply a **distinct count modifier** (3 distinct values of Product Category) at the visit level
- Apply a **visitor-level exclusion** for a specific date (Day = Dec 27, 2025, using its item ID)
- Nest the conditions correctly: visit-level condition AND visitor-level exclusion

Watch how the agent breaks down the problem and what clarifying questions it asks.

> **Note:** Building this segment manually in the CJA UI requires knowing about Distinct Count operators, correct container nesting, and how date dimensions are stored as item IDs. The agent handles all of this — your job is to describe the intent clearly.

### 4.5 Checkpoint

Reflect on what you built:

- You just created three segments in 15 minutes — from plain language to live CJA segments. What would the same work look like without the MCP server?
- Look at the sequential segment. The underlying JSON for a `sequence` with a `time-restriction` is about 40 lines of nested objects. How does the agent's plain-language summary help you verify correctness without reading the JSON?
- Where else outside CJA could you use segment logic? *(Think: the same filtering logic you just described could describe a SQL WHERE clause or a BigQuery filter.)*

---

---

## Bonus — Explore More

est completion: 10 min *(Optional — try what interests you)*

---

### B.1 Objectives

- See what else is possible with 25 CJA MCP tools
- Experience ad-hoc analysis and app generation through conversation
- Understand where the CJA MCP Server fits relative to Digital Insights Agent

### B.2 Exercise: Try One of These

**Option A — Comparative Analysis**

Compare two segments or two time periods side by side:

```
Compare revenue and conversion rate between mobile and desktop visitors
for the last 30 days. Then show me how this compares to the same period last month.
```

**Option B — Metric Dependency Mapper**

Find out which of your calculated metrics depend on a specific base metric:

```
Show me which calculated metrics use the Orders metric as a component.
If you can, create a simple text map showing their dependencies.
```

**Option C — Build a Single-Page Dashboard App**

Go beyond the CJA UI entirely:

```
Using the Luma data, build a single-page HTML app that shows
the top 10 products by revenue with a bar chart.
Pull the data live through the CJA MCP tools and render it in the browser.
```

> **Note:** These prompts go beyond the structured exercises. They're meant to show what's possible when an agent has free access to 25 live CJA tools. Some may require follow-up clarifications.

### B.3 MCP vs. Digital Insights Agent

The CJA MCP Server and Adobe's Digital Insights Agent (DIA) are complementary — not competing.


|                   | Digital Insights Agent (DIA)                                   | CJA MCP Server                                                               |
| ----------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **What it is**    | Pre-built AI-guided analysis workflows within Experience Cloud | Open protocol layer that connects any MCP-capable AI client to live CJA data |
| **Best for**      | Guided, repeatable analysis flows for business users           | Custom, programmatic, and agentic workflows for analysts and developers      |
| **Client**        | Adobe Experience Cloud UI                                      | Cursor, Claude.ai, ChatGPT, or any MCP-compatible client                     |
| **Extensibility** | Adobe-managed                                                  | Scriptable, skill-based, fully extensible                                    |


Use DIA for structured guided analysis within Adobe's UI. Use the MCP Server when you want to write your own skills, combine CJA with other data sources, or drive workflows from an AI coding environment.

---

---

## Wrap-up and Q&A

est completion: 10 min

---

### Key Takeaways

1. **Data Mirror** eliminates the export-schedule-import cycle. CDC keeps your CJA data in sync with your warehouse source of truth — inserts, updates, and deletes propagate automatically.
2. **The CJA MCP Server** makes your analytics conversational. Describe what you want; the agent builds it. Workspace creation, segment building, and component governance all work through natural language.
3. **Component governance at scale** is now manageable. A 7-phase audit across hundreds of segments and calculated metrics takes a few minutes of agent work, not a week of manual review.
4. **Segmentation is accessible to everyone.** From a simple AND/OR filter to a multi-step sequential segment with time restrictions — the segment builder handles the JSON complexity so you can focus on the logic.

### Next Steps

**To connect the CJA MCP Server to your own org:**
See the *Remote MCPs for Analytics and CJA — Getting Started Guide* in the lab materials. It covers Cursor, Claude.ai, ChatGPT, and non-OAuth (server-to-server) clients.

**To set up Data Mirror for your warehouse:**
See the Data Mirror setup walkthrough in `1 data mirror/` — it covers BigQuery, Azure Blob Storage, and Amazon S3, including schema creation, CDC enablement, and the AEP source connector configuration.

**To explore more skills:**
Open `.cursor/skills/` in this repository. Skills available include: `cja-project-builder`, `cja-segment-builder`, `cja-segment-audit`, `cja-component-audit`, `cja-dimension-analysis`, `cja-component-find-replace`, and `cja-mcp-connectivity`.

**Both capabilities are currently in beta.** Your feedback matters — share it with your Adobe team contact or submit it through the lab feedback form.

---

*Adobe Summit 2026 — Lab L611 — Data Mirror and MCP: Modern Connectivity for Customer Journey Analytics*
