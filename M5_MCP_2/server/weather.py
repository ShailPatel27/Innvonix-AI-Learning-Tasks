from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

NWS_API_BASE = "https://weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
        
def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction', 'No specific instructions provided')}
        """
        
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

# NEW TOOL: Fetches weather forecasts for coordinates
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get the weather forecast for a specific location using latitude and longitude coordinates.

    Args:
        latitude: Latitude coordinate (e.g., 37.7749 for San Francisco)
        longitude: Longitude coordinate (e.g., -122.4194 for San Francisco)
    """
    # Step 1: Query points endpoint to find grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    
    if not points_data or "properties" not in points_data:
        return "Could not determine weather grid location for these coordinates."
        
    forecast_url = points_data["properties"].get("forecast")
    if not forecast_url:
        return "Forecast endpoint not available for this location."
        
    # Step 2: Fetch the actual forecast data
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data or "properties" not in forecast_data:
        return "Could not retrieve forecast data."
        
    periods = forecast_data["properties"].get("periods", [])
    if not periods:
        return "No forecast periods returned."
        
    # Step 3: Format the forecast chunks
    forecast_lines = []
    for period in periods[:3]:  # Grab the next 3 forecast blocks (e.g. Tonight, Tomorrow, Tomorrow Night)
        name = period.get("name", "Unknown time")
        temperature = period.get("temperature", "N/A")
        unit = period.get("temperatureUnit", "F")
        detailed = period.get("detailedForecast", "No details provided.")
        forecast_lines.append(f"**{name}**: {temperature}°{unit}\n{detailed}")
        
    return "\n\n".join(forecast_lines)

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"

if __name__ == "__main__":
    mcp.run()
