# Compliance Mapping Agent

Maps security findings to enterprise compliance frameworks — **NIST CSF 2.0**, **COSO ERM**, and **SOC 2** — using bundled reference data (RAG pattern) to prevent hallucinated control IDs.

## How It Works

```
intake → research → review → report
            ↑          |
            +--- feedback loop
```

1. **Intake** — Collects your security findings (or loads the bundled demo)
2. **Research** — Loads local framework reference files first (RAG), then augments with web search only when needed. Never invents control IDs.
3. **Review** — Presents the mappings for user validation (with feedback loop for corrections)
4. **Report** — Generates a structured HTML compliance report

### Anti-Hallucination Design

The agent ships with verified reference data in `data/`:

| File | Contents |
|------|----------|
| `nist_csf_2.0.json` | All 6 functions, categories, and subcategories with official IDs |
| `coso_erm.json` | All 5 components and 20 principles |
| `soc2_tsc.json` | All Trust Services Criteria (CC1–CC9) with control IDs |

The research node **must** load these files before mapping. Web search is only used to fill gaps not covered by the reference data. Every control ID in the output traces back to either the local reference or a URL.

## Quick Test (Demo Mode)

The agent includes `data/demo_findings.json` — a real security audit of the Hive framework itself (9 findings). To test:

```bash
# 1. Clone and setup
git clone https://github.com/adenhq/hive.git && cd hive
./quickstart.sh

# 2. Copy the agent into exports/
cp -r path/to/compliance_mapper exports/

# 3. Validate
PYTHONPATH=core:exports python -m compliance_mapper validate
# → "Agent is valid"

# 4. Run with the demo findings
PYTHONPATH=core:exports python -m compliance_mapper run \
  --findings "Use the demo findings from demo_findings.json — a security audit of the Hive framework"
```

When the agent asks which frameworks, say **"all three"** and it will map all 9 findings to NIST CSF 2.0, COSO ERM, and SOC 2.

## Agent Structure

```
compliance_mapper/
├── README.md
├── __init__.py
├── __main__.py              # CLI entry point
├── agent.json               # Full graph definition
├── agent.py                 # Python agent class + goal/edges
├── config.py                # Runtime config
├── mcp_servers.json         # MCP tool server config
├── data/                    # Reference data (RAG)
│   ├── nist_csf_2.0.json   # NIST CSF 2.0 controls
│   ├── coso_erm.json        # COSO ERM principles
│   ├── soc2_tsc.json        # SOC 2 Trust Services Criteria
│   └── demo_findings.json   # Demo: Hive security audit findings
└── nodes/
    └── __init__.py          # Node definitions
```

## Why This Agent

Built after doing a security audit of the Hive codebase itself — the audit found 9 real vulnerabilities, and manually mapping them to NIST/COSO/SOC 2 was tedious. This agent automates that workflow: feed it findings, get a compliance-ready report with cited control references.

## Required Tools

`web_search`, `web_scrape`, `save_data`, `load_data`, `list_data_files`, `serve_file_to_user`
