from fastmcp import FastMCP
from tosc_editor_lib import (
    create_new_tosc_file,
    load_tosc_file,
    write_tosc_file,
    add_label,
    add_button,
    embed_lua_script,
)

# Create the server instance, passing the server name and all the functions
# that should be exposed as tools.
mcp_server = FastMCP(
    "touchosc_editor",
    create_new_tosc_file,
    load_tosc_file,
    write_tosc_file,
    add_label,
    add_button,
    embed_lua_script,
)

if __name__ == "__main__":
    mcp_server.run()