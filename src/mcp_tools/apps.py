"""Splunk apps tool implementation."""

from client import SplunkClient

# Initialize Splunk client
client = SplunkClient()


async def get_splunk_apps_impl() -> str:
    """Get list of installed Splunk apps."""
    try:
        apps = await client.get_apps()

        output = "Installed Splunk apps:\n\n"
        for app in apps:
            status = "enabled" if not app["disabled"] else "disabled"
            visibility = "visible" if app["visible"] else "hidden"
            output += f"• {app['name']} (v{app['version']}): {app['label']} [{status}, {visibility}]\n"

        return output
    except Exception as e:
        return f"Failed to get apps: {str(e)}"