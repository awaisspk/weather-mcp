from weather import mcp


if __name__ == "__main__":
    # Run the FastMCP server with stdio transport
    mcp.run(transport='stdio')
