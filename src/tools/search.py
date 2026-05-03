"""Splunk search tool implementation."""

from client import SplunkClient

# Initialize Splunk client
client = SplunkClient()


async def search_splunk_impl(
    query: str,
    earliest_time: str = "-1h",
    latest_time: str = "now",
    max_results: int = 100
) -> str:
    """Execute a Splunk search query and return results."""
    try:
        results = await client.search(query, earliest_time, latest_time, max_results)

        output = f"Splunk search results for: '{query}'\n"
        output += f"Found {len(results)} results:\n\n"

        for i, result in enumerate(results[:10]):
            output += f"Result {i+1}:\n"
            for key, value in result.items():
                output += f"  {key}: {value}\n"
            output += "\n"

        if len(results) > 10:
            output += f"... and {len(results) - 10} more results\n"

        return output
    except Exception as e:
        return f"Search failed: {str(e)}"