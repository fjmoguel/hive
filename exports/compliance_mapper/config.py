"""Runtime configuration."""

from dataclasses import dataclass

from framework.config import RuntimeConfig

default_config = RuntimeConfig()


@dataclass
class AgentMetadata:
    name: str = "Compliance Mapping Agent"
    version: str = "1.0.0"
    description: str = (
        "Maps security findings to enterprise compliance frameworks "
        "(NIST CSF 2.0, COSO ERM, SOC 2) with cited control references "
        "and remediation priorities."
    )
    intro_message: str = (
        "Hi! I'm your compliance mapping assistant. Give me your security "
        "findings and I'll map them to NIST CSF 2.0, COSO ERM, and SOC 2 "
        "controls — with cited references from official sources. "
        "What findings would you like to map?"
    )


metadata = AgentMetadata()
