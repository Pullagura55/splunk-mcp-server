"""Splunk events tool implementation."""

from client import SplunkClient

# Initialize Splunk client
client = SplunkClient()


async def send_to_splunk_impl(
    event: dict,
    source: str = None,
    sourcetype: str = None,
    index: str = None
) -> str:
    """Send event to Splunk via HTTP Event Collector."""
    try:
        await client.send_event(event, source, sourcetype, index)

        output = "Event sent to Splunk successfully!\n"
        output += f"• Source: {source or 'default'}\n"
        output += f"• Sourcetype: {sourcetype or 'json'}\n"
        output += f"• Index: {index or 'main'}\n"

        return output
    except Exception as e:
        return f"Failed to send event: {str(e)}"