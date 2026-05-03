"""Splunk alerts tool implementation."""

from client import SplunkClient

# Initialize Splunk client
client = SplunkClient()


async def create_splunk_alert_impl(
    name: str,
    search: str,
    cron_schedule: str,
    actions: list = []
) -> str:
    """Create a Splunk alert."""
    try:
        await client.create_alert(name, search, cron_schedule, actions)

        output = f"Successfully created alert '{name}':\n"
        output += f"• Search: {search}\n"
        output += f"• Schedule: {cron_schedule}\n"
        output += f"• Actions: {', '.join(actions) if actions else 'none'}\n"

        return output
    except Exception as e:
        return f"Failed to create alert: {str(e)}"