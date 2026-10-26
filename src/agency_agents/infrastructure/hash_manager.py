import hashlib
from pathlib import Path
from typing import List, Tuple
from agency_agents.core.models import Agent
from agency_agents.core.converter import ConverterEngine

class HashManager:
    """
    Handles the generation and verification of content hashes.
    Migrates the logic of scripts/test-convert-outputs.sh and convert-outputs.sha256.
    """
    @staticmethod
    def calculate_hash(content: str) -> str:
        """Calculates the SHA256 hash of a string."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def generate_manifest(self, agents: List[Agent], tool_kebab: str, engine: ConverterEngine) -> List[str]:
        """
        Generates a manifest of hashes for a specific tool's output.
        Format: agent\t<slug>\t<hash>
        """
        manifest = []
        for agent in agents:
            outputs = engine.convert_agent_for_tool(agent, tool_kebab)
            if not outputs:
                continue
            
            # For the manifest, we hash the combined content of all outputs for that agent
            combined_content = "".join([out[1] for out in outputs])
            content_hash = self.calculate_hash(combined_content)
            manifest.append(f"agent\t{agent.slug}\t{content_hash}")
            
        return manifest

    def verify_manifest(self, manifest_path: Path, agents: List[Agent], tool_kebab: str, engine: ConverterEngine) -> List[str]:
        """
        Verifies current conversion output against an existing manifest file.
        Returns a list of mismatches.
        """
        if not manifest_path.exists():
            return ["Manifest file not found"]

        current_manifest = self.generate_manifest(agents, tool_kebab, engine)
        existing_lines = manifest_path.read_text(encoding='utf-8').splitlines()
        
        mismatches = []
        for line in current_manifest:
            if line not in existing_lines:
                mismatches.append(f"Mismatch or missing entry: {line}")
                
        return mismatches
