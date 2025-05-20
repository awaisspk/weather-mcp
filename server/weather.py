from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-mcp/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API. With proper error handling."""

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error fetching {url}: {e}")
            return None


def format_alert(feature: dict) -> str:
    """ format an alert feature into a readable string """

    props: dict = feature["properties"]
    return f"""
    Event: {props.get('event', 'Unknown')}
    Area: {props.get('areaDesc', 'Unknown')}
    Severity: {props.get('severity', 'Unknown')}
    Description: {props.get('description', 'No description available')}
    Instructions: {props.get('instruction', 'No specific instructions provided')}
    """


@mcp.tool()
async def get_alerts(state: str) -> str:
    """ Get weather alerts for a US state
    Args:
        state: The two-letter US state code (e.g. "CA", "NY")
    Returns:
        A string containing the weather alerts for the state
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found"

    if not data["features"]:
        return "No active alerts for this state"

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)
