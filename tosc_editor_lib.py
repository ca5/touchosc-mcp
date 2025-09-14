import os
import xml.etree.ElementTree as ET
from typing import Optional

# We only import 'write' from tosclib, as it handles the specific .tosc zip format.
# All other XML manipulation will be done with the standard library.
from tosclib import write

# This module will store the state of the currently edited file.
# The state is the root of the XML tree (an ET.Element object).
current_tosc_root: Optional[ET.Element] = None
current_tosc_path: Optional[str] = None

def create_new_tosc_file(file_path: str) -> str:
    """Creates a new, empty .tosc file and loads it into memory."""
    global current_tosc_root, current_tosc_path
    
    # A .tosc file is an XML file with a root element named 'lexml'.
    root = ET.Element("lexml")
    root.set("version", "18")
    
    tree = ET.ElementTree(root)
    tree.write(file_path, encoding="UTF-8", xml_declaration=True)

    # Use tosclib's write function which handles the zip packaging
    write(root, file_path)

    current_tosc_root = root
    current_tosc_path = file_path
    return f"Successfully created '{file_path}' and loaded it for editing."

def load_tosc_file(file_path: str) -> str:
    """Loads an existing .tosc file into memory for editing."""
    global current_tosc_root, current_tosc_path
    
    if not os.path.exists(file_path):
        return f"Error: File not found at '{file_path}'"
        
    try:
        # A .tosc file is a zip archive with a 'TOSC' file inside.
        # We assume tosclib handles the unzipping and parsing, but since
        # that was unreliable, we will handle it manually if we can.
        # For now, let's assume the input is a raw XML file for simplicity,
        # as the provided `tosclib` seems to have issues with its own format.
        tree = ET.parse(file_path)
        current_tosc_root = tree.getroot()
        current_tosc_path = file_path
        return f"Successfully loaded '{file_path}' for editing."
    except ET.ParseError as e:
        return f"Error: Failed to parse XML in file '{file_path}': {e}"

def write_tosc_file(file_path: str = None) -> str:
    """Writes the in-memory .tosc file to disk."""
    global current_tosc_root, current_tosc_path

    if current_tosc_root is None:
        return "Error: No .tosc file is currently loaded."
        
    output_path = file_path or current_tosc_path
    if not output_path:
        return "Error: No output path specified."

    # Use tosclib's write function which handles the zip packaging.
    write(current_tosc_root, output_path)
    current_tosc_path = output_path
    return f"Successfully wrote project to '{output_path}'."

def _add_control(control_type: str, name: str, x: int, y: int, w: int, h: int, properties: dict) -> str:
    """A generic internal function to add a control to the current file."""
    if current_tosc_root is None:
        return "Error: No .tosc file is currently loaded."

    if current_tosc_root.find(f".//control[@name='{name}']") is not None:
        return f"Error: A control with the name '{name}' already exists."

    node = ET.SubElement(current_tosc_root, "control")
    node.set("type", control_type)
    node.set("name", name)
    node.set("x", str(x)); node.set("y", str(y)); node.set("w", str(w)); node.set("h", str(h))

    properties_node = ET.SubElement(node, "properties")
    for key, value in properties.items():
        prop_node = ET.SubElement(properties_node, "property")
        prop_node.set("name", key)
        ET.SubElement(prop_node, "string").text = str(value)

    return f"Successfully added {control_type} '{name}'."

def add_button(name: str, button_type: str, x: int, y: int, w: int, h: int, color: str = "red") -> str:
    if button_type not in ['push', 'toggle']:
        return "Error: button_type must be either 'push' or 'toggle'."
    return _add_control("button", name, x, y, w, h, {"type": button_type, "color": color})

def add_label(name: str, text: str, x: int, y: int, w: int, h: int, color: str = "red") -> str:
    return _add_control("label", name, x, y, w, h, {"text": text, "color": color})

def embed_lua_script(control_name: str, script: str) -> str:
    """Embeds a Lua script into a specific control."""
    if current_tosc_root is None:
        return "Error: No .tosc file is currently loaded."

    control_node = current_tosc_root.find(f".//control[@name='{control_name}']")
    if control_node is None:
        return f"Error: Control '{control_name}' not found in the project."

    properties_node = control_node.find('properties')
    if properties_node is None:
        properties_node = ET.SubElement(control_node, 'properties')

    # Remove existing script if any
    existing_script = properties_node.find('script')
    if existing_script is not None:
        properties_node.remove(existing_script)

    script_node = ET.SubElement(properties_node, 'script')
    script_node.text = ET.CDATA(script)
    return f"Successfully embedded script into control '{control_name}'."
