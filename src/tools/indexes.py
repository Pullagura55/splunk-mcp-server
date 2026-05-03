"""Splunk indexes tool implementation."""

from client import SplunkClient

# Initialize Splunk client
client = SplunkClient()


async def get_splunk_indexes_impl() -> str:
    """Get list of available Splunk indexes."""
    try:
        indexes = await client.get_indexes()

        output = "Available Splunk indexes:\n\n"
        for index in indexes:
            output += f"• {index['name']}: {index['datatype']} "
            output += f"({index['totalEventCount']} events, {index['currentDBSizeMB']} MB)\n"

        return output
    except Exception as e:
        return f"Failed to get indexes: {str(e)}"