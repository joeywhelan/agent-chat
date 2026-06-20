# Plan: Elastic Agent Builder & Official Agent Skills
## Notebook Demo

---

## Overview

Hands-on, runnable notebook walkthrough of Agent Builder's OOTB natural language query capabilities and the Official Elastic Agent Skills (authn, authz, ES|QL NL query, file ingest/transform).

---

## Notebook Structure

---

### Section 0 — Prerequisites & Setup
**Goal:** Get a reader from zero to a running environment in one section.

Cells:
- Install dependencies: `elasticsearch-py`, `requests`, `python-dotenv`
- Environment config: `ES_URL`, `ES_API_KEY`, `KIBANA_URL` loaded from `.env`
- Health-check cell: ping Elasticsearch + Kibana, print cluster name and version
- Optional: create a demo index with sample e-commerce or log data if not already present

**Skill referenced:** `cloud-setup`, `cloud-create-project` (link to skill SKILL.md in markdown cell)

---

### Section 1 — Agent Chat: Natural Language Query Writing (Kibana GUI)
**Goal:** Show how Agent Chat in Kibana translates plain English into ES|QL queries against a synthetic e-commerce dataset, with no code required.

**Format:** Notebook with markdown cells and `[SCREENSHOT]` placeholders. This is a GUI walkthrough, not an API demo.

**Sub-section A — Synthetic Data Generator (code cell)**
- Python cell using `faker` + `elasticsearch-py` to generate and index ~5,000 synthetic e-commerce documents into `demo-ecommerce` index
- Fields: `order_id`, `customer_id`, `customer_name`, `customer_region`, `order_date`, `status` (placed/shipped/delivered/returned), `product_category`, `product_name`, `product_description`, `unit_price`, `quantity`, `total_amount`, `payment_method`
- `product_description` descriptions are written with cross-category semantic overlap (e.g. "home office", "fitness and recovery", "eco-friendly") so that semantic queries surface matches across categories that keyword search would miss
- Explicit mapping cell: dates as `date`, prices as `float`, IDs as `keyword`, free text as `text` with `keyword` sub-field; `product_description` mapped as `semantic_text` (no explicit inference id — defaults to the project's configured model)
- Bulk indexing note: documents land immediately; embeddings for `product_description` are generated asynchronously server-side — wait ~60 seconds before running semantic queries
- Verification cell: doc count + sample document

**Sub-section B — Agent Chat Walkthrough (markdown + screenshots)**

Markdown setup cell: how to open Agent Chat in Kibana (Kibana → Search → Agent Builder → Chat), selecting the default agent, and pointing it at the `demo-ecommerce` index.

Walk through 5 natural language prompts, each as its own markdown cell with:
- The plain-English question asked
- `[SCREENSHOT: Agent Chat response]`
- The ES|QL the agent generated, shown as a code block (copied from the chat response)
- One-line annotation of what the query does

Prompts:
1. *"What are the top 5 product categories by total revenue?"* — standard aggregation; agent produces `STATS` + `SORT` + `LIMIT`
2. *"How has daily order volume trended over the past 3 months?"* — time-series; agent uses `BUCKET(order_date, 1 day)` with date math
3. *"Which regions have the highest average order value, broken down by order status?"* — grouped aggregation across two dimensions
4. *"Find products that someone setting up a home office would be most likely to buy"* — **semantic query** against `product_description`; surfaces Electronics work-peripherals, the Desk Lamp from Home & Garden, and *Deep Work* from Books even though none contain the phrase "home office" in `product_category` or `product_name`
5. *"Build me a Kibana dashboard with panels for revenue by category, daily order trend, order status breakdown, and top regions by average order value"* — **dashboard generation**; Agent Chat creates a multi-panel Lens dashboard directly from the natural language request

Closing markdown cell: observations on accuracy, how the agent infers field names and date math from the index mapping, and when to iterate on the prompt vs edit the ES|QL directly. Call out prompt 4: the agent chose a semantic query because it detected the `semantic_text` field — no user configuration required. Call out prompt 5: the dashboard request bypasses ES|QL entirely and goes straight to Kibana visualisation.

**Key callout:** No mapping knowledge required from the user. The agent reads the index schema and grounds its queries in actual field names — including recognising when a `semantic_text` field enables meaning-based search, and when a request calls for a Kibana dashboard rather than a raw query.

---

### Section 2 — Elastic Agent Skills with Claude Code: `elasticsearch-esql`
**Goal:** Show what the `elasticsearch-esql` skill actually does inside a Claude Code session — install it, point it at the demo-ecommerce index, and walk through progressively complex natural language prompts that produce correct, idiomatic ES|QL.

**Format:** Markdown cells with the exact prompts to give Claude Code, `[SCREENSHOT]` placeholders for the session output, and the resulting ES|QL shown as code blocks.

**Sub-section A — Install & Setup (markdown cell)**

Explain what Elastic Agent Skills are: self-contained `SKILL.md` packages that drop into agentic IDEs. The `description` field is the sole trigger — the agent reads it to decide when to activate the skill.

Installation cell (terminal commands, not runnable notebook code):
```bash
npx skills add elastic/agent-skills --all
```

Markdown cell: verify installation by running the following command and confirming the Elastic skills appear:
```bash
npx skills list | grep elastic
```
Show the `SKILL.md` frontmatter inline so the reader understands the trigger mechanism.

Configure credentials — Claude Code needs ES_URL and ES_API_KEY in the environment:
```bash
export ELASTICSEARCH_URL="https://your-project.es.us-east-1.aws.elastic.cloud"
export ELASTICSEARCH_API_KEY="your-scoped-api-key"
```

**Sub-section B — Prompts Walkthrough (markdown cells + screenshots)**

Each prompt is its own markdown cell containing:
- Context: what the reader should type into Claude Code
- `[SCREENSHOT: Claude Code session showing skill activation + ES|QL output]`
- The ES|QL the skill produced, as a code block
- One-line note on what ES|QL feature the skill used correctly (date math, STATS, SORT, etc.)

Prompts — mix of query types against the `demo-ecommerce` index:

1. **Filtered time-series**
   > *"Show me daily order volume for the last 90 days, only for delivered orders"*
   — `WHERE status == "delivered" AND order_date > NOW() - 90 days | STATS count = COUNT() BY BUCKET(order_date, 1 day)`; skill applies correct ES|QL date math and `BUCKET` syntax

2. **Top-N ranking with iterative refinement** — show the back-and-forth
   > *"Who are the top 10 customers by lifetime spend, and how many orders has each placed?"*  
   > *(follow-up)* *"Now break that down by region as well"*
   — initial: `STATS total_spend = SUM(total_amount), order_count = COUNT() BY customer_id, customer_name | SORT total_spend DESC | LIMIT 10`; skill modifies the query to add `customer_region` to the `BY` clause, demonstrating conversational context retention

3. **Semantic search across categories** — **semantic query**; meaning-based retrieval without keyword matching
   > *"Which products are customers buying for physical fitness and recovery, regardless of which category they're listed under?"*
   — skill issues a semantic query against `product_description`; results span Sports (Foam Roller, Resistance Bands, Yoga Mat) **and** Electronics (Fitness Tracker) **and** Clothing (Running Shoes, Yoga Pants) — categories a keyword filter on `product_category == "Sports"` would miss entirely; follows with `STATS total_spend = SUM(total_amount), order_count = COUNT() BY product_name, product_category | SORT total_spend DESC`

4. **Multi-condition aggregation** — return rate by category vs. overall average
   > *"What is the return rate for each product category, and which categories are above the overall return rate?"*
   — skill computes per-category return rate with `STATS` + conditional counting, then uses `EVAL` to flag categories above the overall average; demonstrates a two-pass aggregation pattern in a single ES|QL pipeline

5. **Full-text search** — keyword `MATCH` across `product_description`, contrasted with the semantic search above
   > *"Find all products whose descriptions mention 'wireless' or 'bluetooth', and show total units sold and revenue for each"*
   — skill issues a `MATCH` query on `product_description` with boolean OR, then aggregates with `STATS SUM(quantity), SUM(total_amount) BY product_name`; illustrates when exact keyword retrieval is the right tool vs. vector similarity in prompt 3

Closing markdown cell: what the skill is doing under the hood — reading the mapping, applying ES|QL syntax rules from the SKILL.md instructions, and catching common mistakes (e.g. using Query DSL syntax in an ES|QL context). Call out prompt 3 vs. prompt 5: both search `product_description`, but prompt 3 uses semantic similarity (vector search on the `semantic_text` field) while prompt 5 uses full-text `MATCH` — the skill selects the right retrieval method based on the intent expressed in the natural language request.

**Key callout:** The skill is not calling an external service — it's instruction context injected into Claude Code's prompt. The quality difference comes from Elastic-authored ES|QL patterns and Kibana knowledge baked into the SKILL.md.

---

### Section 3 — Teardown (Terraform)
**Goal:** Destroy the Elastic Serverless project cleanly via Terraform, mirroring how it was created in Section 0.

**Format:** Markdown cells with terminal commands. Not runnable notebook code — same pattern as the Claude Code install cells in Section 2.

Cells:
- Markdown: remind the reader that the project is billable and should be destroyed when the demo is complete
- Verify Terraform state still matches the live project before destroying:
  ```bash
  terraform plan
  ```
- Destroy the project:
  ```bash
  terraform destroy
  ```
- Confirm in the Elastic Cloud console that the project no longer appears
- Markdown closing cell: note that Terraform state file should also be cleaned up if the repo is being shared or archived

---

### Notebook Conventions
- Each section opens with a `## Overview` markdown cell and closes with a `## Key Takeaways` cell
- Credential setup uses env vars — no hardcoded values
- Screenshot placeholders use the format `[SCREENSHOT: description]`
- Terminal commands are shown as bash code blocks, not runnable notebook cells
- README.md in the repo root lists prerequisites and setup steps

---

## Sequencing & Dependencies

| Step | Deliverable | Depends on |
|------|-------------|------------|
| 1 | Terraform: provision Serverless project (Section 0 — you) | — |
| 2 | Write and validate Section 1 (Agent Chat + synthetic data) | Step 1 |
| 3 | Write and validate Section 2 (Claude Code + elasticsearch-esql skill) | Step 1 |
| 4 | Write Section 3 (Terraform teardown — you) | Step 1 |
| 5 | Publish notebook to GitHub repo with README | Steps 2–4 |

---

## Reference Links

- Elastic Agent Builder docs: https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder
- Official Agent Skills repo: https://github.com/elastic/agent-skills
- Agent Skills standard: https://agentskills.io
- elasticsearch-esql skill: https://github.com/elastic/agent-skills/blob/main/skills/elasticsearch/elasticsearch-esql/SKILL.md
- Kibana Agent Builder API reference: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/kibana-api
