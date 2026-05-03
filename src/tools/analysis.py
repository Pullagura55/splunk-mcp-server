"""Splunk log analysis tool implementation."""

from client import SplunkClient

# Initialize Splunk client
client = SplunkClient()


async def analyze_splunk_logs_impl(
    analysis_type: str,
    index: str = "main",
    time_range: str = "-24h"
) -> str:
    """Perform automated log analysis."""
    try:
        results = await client.analyze_logs(analysis_type, index, time_range)

        output = f"Log Analysis: {analysis_type.replace('_', ' ').title()}\n"
        output += f"Index: {index} | Time: {time_range}\n\n"

        for section, data in results.items():
            output += f"### {section.replace('_', ' ').title()}\n"
            if isinstance(data, list):
                for item in data:
                    output += f"• {item}\n"
            elif isinstance(data, dict):
                for key, value in data.items():
                    output += f"• {key}: {value}\n"
            else:
                output += f"{data}\n"
            output += "\n"

        return output
    except Exception as e:
        return f"Analysis failed: {str(e)}"