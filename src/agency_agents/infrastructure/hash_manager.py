import hashlib
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from agency_agents.core.models import Agent
from agency_agents.core.converter import ConverterEngine

MANIFEST_VERSION = 3

# One line per (tool, agent) so a manifest can cover every per-agent tool at
# once. A tool-less v2 manifest cannot be told apart from a stale one, which is
# exactly how `verify claude-code` ended up comparing against antigravity hashes.
MANIFEST_HEADER = (
    "# convert-outputs manifest v3 — one line per (tool, agent), per-agent tools only.",
    "# Regenerate one tool: python -m agency_agents update-manifest <tool>",
    "# Regenerate all:     python -m agency_agents update-manifest --all",
    "# Hashes are platform-neutral (UTF-8, LF) and cover every rendered file for the agent.",
)

ManifestKey = Tuple[str, str]  # (tool_kebab, agent_slug)


class ManifestError(Exception):
    """Raised when the hash manifest cannot be parsed or is the wrong version."""


class HashManager:
    """
    Handles the generation and verification of content hashes.
    Migrates the logic of scripts/test-convert-outputs.sh and convert-outputs.sha256.
    """
    @staticmethod
    def calculate_hash(content: str) -> str:
        """Calculates the SHA256 hash of a string."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def agent_hash(self, agent: Agent, tool_kebab: str, engine: ConverterEngine) -> Optional[str]:
        """Hash of every rendered file for one agent under one tool, or None."""
        outputs = engine.convert_agent_for_tool(agent, tool_kebab)
        if not outputs:
            return None
        return self.calculate_hash("".join(content for _, content in outputs))

    @staticmethod
    def _line(tool_kebab: str, slug: str, digest: str) -> str:
        return f"agent\t{tool_kebab}\t{slug}\t{digest}"

    def generate_manifest(self, agents: List[Agent], tool_kebab: str, engine: ConverterEngine) -> List[str]:
        """Generates v3 manifest lines for a single tool: one per agent."""
        lines = []
        for agent in agents:
            digest = self.agent_hash(agent, tool_kebab, engine)
            if digest is not None:
                lines.append(self._line(tool_kebab, agent.slug, digest))
        return lines

    def parse_manifest(self, manifest_path: Path) -> Tuple[int, Dict[ManifestKey, str]]:
        """Returns (version, {(tool, slug): hash}).

        Raises ManifestError for missing, malformed, or tool-less v2 manifests so
        a stale file can never be silently compared against the wrong tool.
        """
        if not manifest_path.exists():
            raise ManifestError(f"Manifest file not found: {manifest_path}")

        version = 0
        entries: Dict[ManifestKey, str] = {}
        for raw in manifest_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                if "manifest v" in line:
                    try:
                        version = int(line.split("manifest v", 1)[1].split()[0])
                    except (IndexError, ValueError):
                        pass
                continue
            parts = line.split("\t")
            if parts[0] != "agent":
                continue  # non-agent entries are not verified yet
            if len(parts) == 3:
                raise ManifestError(
                    "Manifest is v2 (tool-less): it cannot say which tool its hashes "
                    "belong to. Regenerate it with: python -m agency_agents update-manifest --all"
                )
            if len(parts) != 4:
                raise ManifestError(f"Malformed manifest line: {raw!r}")
            _, tool_kebab, slug, digest = parts
            entries[(tool_kebab, slug)] = digest
        return version, entries

    def verify_manifest(
        self,
        manifest_path: Path,
        agents: List[Agent],
        tool_kebab: str,
        engine: ConverterEngine,
    ) -> List[str]:
        """Verifies one tool's entries against current conversion output."""
        version, entries = self.parse_manifest(manifest_path)
        if version != MANIFEST_VERSION:
            return [
                f"Unsupported manifest version {version or 'unknown'} (expected v{MANIFEST_VERSION}). "
                "Regenerate it with: python -m agency_agents update-manifest --all"
            ]

        tool_entries = {slug: digest for (tool, slug), digest in entries.items() if tool == tool_kebab}
        if not tool_entries:
            return [
                f"Manifest has no entries for tool '{tool_kebab}'. "
                f"Regenerate it with: python -m agency_agents update-manifest {tool_kebab}"
            ]

        mismatches = []
        roster = set()
        for agent in agents:
            roster.add(agent.slug)
            expected = tool_entries.get(agent.slug)
            if expected is None:
                mismatches.append(f"missing entry: agent={agent.slug} tool={tool_kebab}")
                continue
            if self.agent_hash(agent, tool_kebab, engine) != expected:
                mismatches.append(f"hash mismatch: agent={agent.slug} tool={tool_kebab}")

        for slug in sorted(set(tool_entries) - roster):
            mismatches.append(f"stale entry: agent={slug} tool={tool_kebab} (not in roster)")

        return mismatches

    def update_tool(
        self,
        manifest_path: Path,
        agents: List[Agent],
        tool_kebab: str,
        engine: ConverterEngine,
    ) -> int:
        """Replaces one tool's entries, preserving every other tool's lines."""
        _, entries = self.parse_manifest(manifest_path) if manifest_path.exists() else (MANIFEST_VERSION, {})
        entries = {key: digest for key, digest in entries.items() if key[0] != tool_kebab}

        count = 0
        for agent in agents:
            digest = self.agent_hash(agent, tool_kebab, engine)
            if digest is not None:
                entries[(tool_kebab, agent.slug)] = digest
                count += 1

        self.write_manifest(manifest_path, entries)
        return count

    def update_all(
        self,
        manifest_path: Path,
        agents: List[Agent],
        tools: Iterable[str],
        engine: ConverterEngine,
    ) -> int:
        """Regenerates the whole manifest for the given per-agent tools."""
        entries: Dict[ManifestKey, str] = {}
        for tool_kebab in tools:
            for agent in agents:
                digest = self.agent_hash(agent, tool_kebab, engine)
                if digest is not None:
                    entries[(tool_kebab, agent.slug)] = digest

        self.write_manifest(manifest_path, entries)
        return len(entries)

    @staticmethod
    def write_manifest(manifest_path: Path, entries: Dict[ManifestKey, str]) -> None:
        """Writes a deterministic v3 manifest: sorted by tool, then agent slug."""
        lines = list(MANIFEST_HEADER)
        for tool_kebab, slug in sorted(entries):
            lines.append(HashManager._line(tool_kebab, slug, entries[(tool_kebab, slug)]))
        manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
