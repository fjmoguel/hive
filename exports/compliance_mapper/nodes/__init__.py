"""Node definitions for Compliance Mapping Agent."""

from framework.graph import NodeSpec

# Node 1: Intake (client-facing)
intake_node = NodeSpec(
    id="intake",
    name="Finding Intake",
    description="Collect security findings from the user and clarify scope",
    node_type="event_loop",
    client_facing=True,
    max_node_visits=0,
    input_keys=["findings_input"],
    output_keys=["findings_list", "frameworks"],
    success_criteria=(
        "A structured list of security findings is captured, each with a title, "
        "description, and severity. Target frameworks are confirmed."
    ),
    system_prompt="""\
You are a compliance intake specialist. The user has security findings to map to governance frameworks.

**CRITICAL: You do NOT do any research yourself. You only collect and structure the input.**

**STEP 1 — Read and clarify (text only, NO tool calls):**
1. Read the findings provided
2. If the user says "use demo" or "demo findings", tell them you'll use the bundled demo_findings.json (a real security audit of the Hive framework)
3. Ask which frameworks to map against. Suggest: NIST CSF 2.0, COSO ERM, SOC 2 (all three recommended)
4. Confirm the list of findings you'll be mapping — restate each one briefly

Keep it concise. If findings are already clear, just confirm and ask which frameworks.

**STEP 2 — After user confirms, call set_output:**
- set_output("findings_list", "JSON array: [{title, description, severity}, ...] — or 'demo_findings.json' if using the demo file")
- set_output("frameworks", "Comma-separated list, e.g. NIST CSF 2.0, COSO ERM, SOC 2")

That's it. Once you call set_output, the research node takes over.
""",
    tools=[],
)

# Node 2: Research (RAG pattern: load local references first, then augment with web search)
research_node = NodeSpec(
    id="research",
    name="Framework Research",
    description="Load framework reference files and map each finding to specific controls",
    node_type="event_loop",
    max_node_visits=0,
    input_keys=["findings_list", "frameworks"],
    output_keys=["control_references", "mapping_notes"],
    success_criteria=(
        "Each finding has at least one mapped control from each target framework, "
        "with official control IDs and descriptions sourced from the reference files."
    ),
    system_prompt="""\
You are a compliance research agent. Given security findings and target frameworks, map each finding to specific controls.

**CRITICAL: You MUST load the local reference files FIRST. They contain verified control IDs. Do NOT invent control IDs from memory.**

## Phase 1 — Load reference data (MANDATORY first step)

Use load_data to read the bundled framework files. These contain verified control IDs:
  load_data(filename="nist_csf_2.0.json")
  load_data(filename="coso_erm.json")
  load_data(filename="soc2_tsc.json")

Also load the findings if provided as a file:
  load_data(filename="demo_findings.json")

Read each file carefully. These are your ground truth for control IDs.

## Phase 2 — Map findings to controls

For EACH finding, search the loaded reference data for matching controls:

- **NIST CSF 2.0**: Match to function (GV/ID/PR/DE/RS/RC) → category → subcategory.
  Use the exact subcategory ID (e.g., PR.DS-01, not "data security").
- **COSO ERM**: Match to component → principle number.
  Use "Principle N" format (e.g., Principle 10, not "risk identification").
- **SOC 2**: Match to criteria category → control ID.
  Use the exact ID (e.g., CC6.1, not "logical access").

## Phase 3 — Augment with web search (ONLY if needed)

If a finding doesn't map cleanly to any control in the reference files, use web_search to find the correct mapping:
  - Search: "NIST CSF 2.0 [topic] subcategory"
  - Search: "SOC 2 [topic] trust services criteria"
  - Prioritize nist.gov, aicpa.org, coso.org results

**NEVER invent a control ID. If you can't find a match, note it as a gap.**

## Phase 4 — Output

Call set_output (one key at a time, separate turns):
- set_output("control_references", "JSON: {finding_title: [{framework, control_id, control_name, description, source}, ...]}")
- set_output("mapping_notes", "Any gaps, ambiguities, or findings that don't map cleanly")

The 'source' field should be "local_reference" for controls from the bundled files, or a URL for web-sourced controls.
""",
    tools=["web_search", "web_scrape", "load_data", "save_data", "list_data_files"],
)

# Node 3: Review (client-facing)
review_node = NodeSpec(
    id="review",
    name="Review Mappings",
    description="Present the compliance mappings to the user for validation",
    node_type="event_loop",
    client_facing=True,
    max_node_visits=0,
    input_keys=["findings_list", "control_references", "mapping_notes", "frameworks"],
    output_keys=["approved", "feedback"],
    success_criteria=(
        "The user has reviewed the mappings and either approved or provided "
        "feedback for refinement."
    ),
    system_prompt="""\
Present the compliance mappings to the user for review.

**STEP 1 — Present (text only, NO tool calls):**
For each finding, show:
1. Finding title and severity
2. Mapped controls per framework (ID + name)
3. Any gaps or notes

End by asking: Are the mappings accurate? Should any be adjusted?

**STEP 2 — After user responds, call set_output:**
- set_output("approved", "true") — if satisfied
- set_output("approved", "false") — if changes needed
- set_output("feedback", "What to adjust, or empty string")
""",
    tools=[],
)

# Node 4: Report (client-facing, terminal)
report_node = NodeSpec(
    id="report",
    name="Generate Compliance Report",
    description="Generate a structured compliance mapping report as HTML",
    node_type="event_loop",
    client_facing=True,
    max_node_visits=0,
    input_keys=["findings_list", "control_references", "mapping_notes", "frameworks"],
    output_keys=["delivery_status"],
    success_criteria=(
        "An HTML compliance mapping report has been saved and presented to the user."
    ),
    system_prompt="""\
Generate a compliance mapping report as an HTML file.

IMPORTANT: save_data requires TWO separate arguments: filename and data.
Call it like: save_data(filename="compliance_report.html", data="<html>...</html>")

**STEP 1 — Generate and save the HTML report (tool calls):**

Report structure:
- Title: "Compliance Mapping Report" with date
- Executive Summary: finding count, frameworks covered, overall posture
- Findings Table: severity, title, mapped controls per framework
- Detailed Mappings: for each finding, control details with citations
- Remediation Priority Matrix: ordered by severity
- Framework Coverage: which NIST functions / COSO components are affected
- References: source URLs

Use clean HTML with minimal embedded CSS. Color-code severities.

Save: save_data(filename="compliance_report.html", data="<html>...</html>")
Then: serve_file_to_user(filename="compliance_report.html", label="Compliance Mapping Report")

**STEP 2 — Present to user (text only):**
Share the link, summarize key mappings, ask if they need anything else.

**STEP 3 — When done:** set_output("delivery_status", "completed")
""",
    tools=["save_data", "serve_file_to_user", "load_data", "list_data_files"],
)
