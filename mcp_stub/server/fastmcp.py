"""Stub implementation of FastMCP for offline testing."""

class FastMCP:  # pragma: no cover - simple stub for offline agents
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def register_tool(self, *args, **kwargs):
        return None

    def run(self, *args, **kwargs):
        raise RuntimeError("FastMCP stub does not execute tools.")
