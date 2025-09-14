import os
from typing import Optional

from lxml import etree
from tosclib import ElementTOSC, createTemplate, write
from tosclib.controls import Label, Button

current_tosc: Optional[etree.Element] = None
current_tosc_path: Optional[str] = None
PROJECT_ROOT: str = os.path.dirname(os.path.abspath(__file__))

def create_new_tosc_file(file_path: str) -> str:
    global current_tosc, current_tosc_path, PROJECT_ROOT
    abs_path = os.path.join(PROJECT_ROOT, file_path)
    
    current_tosc = createTemplate()
    write(current_tosc, abs_path)
    current_tosc_path = abs_path
    
    return f"Successfully created '{abs_path}' and loaded it for editing."

def load_tosc_file(file_path: str) -> str:
    global current_tosc, current_tosc_path, PROJECT_ROOT
    abs_path = os.path.join(PROJECT_ROOT, file_path)
    
    if not os.path.exists(abs_path):
        return f"Error: File not found at '{abs_path}'"
        
    # From the wrapper, get the raw element via the .node attribute
    current_tosc = ElementTOSC(abs_path).node
    current_tosc_path = abs_path
    
    return f"Successfully loaded '{abs_path}' for editing."

def write_tosc_file(file_path: str = None) -> str:
    global current_tosc, current_tosc_path
    if not current_tosc:
        return "Error: No .tosc file is currently loaded."
        
    if file_path:
        abs_path = os.path.join(PROJECT_ROOT, file_path)
    elif current_tosc_path:
        abs_path = current_tosc_path
    else:
        return "Error: No output path specified. Please provide a 'file_path'."

    # Pass the raw element directly
    write(current_tosc, abs_path)
    current_tosc_path = abs_path
    
    return f"Successfully wrote project to '{abs_path}'."

def add_label(name: str, text: str, x: int, y: int, w: int, h: int, color: str = "red") -> str:
    global current_tosc
    if not current_tosc:
        return "Error: No .tosc file is currently loaded."

    root = current_tosc
    
    if root.find(f".//control[@name='{name}']") is not None:
        return f"Error: A control with the name '{name}' already exists."

    # The constructor is (parent, id, **properties)
    Label(root, name, text=text, x=x, y=y, w=w, h=h, color=color)
    return f"Successfully added label '{name}'."

def add_button(name: str, button_type: str, x: int, y: int, w: int, h: int, color: str = "red") -> str:
    global current_tosc
    if not current_tosc:
        return "Error: No .tosc file is currently loaded."

    if button_type not in ['push', 'toggle']:
        return "Error: button_type must be either 'push' or 'toggle'."

    root = current_tosc

    if root.find(f".//control[@name='{name}']") is not None:
        return f"Error: A control with the name '{name}' already exists."

    # The constructor is (parent, id, **properties), and the arg is 'type'
    Button(root, name, type=button_type, x=x, y=y, w=w, h=h, color=color)
    return f"Successfully added {button_type} button '{name}'."

def embed_lua_script(control_name: str, script: str) -> str:
    global current_tosc
    if not current_tosc:
        return "Error: No .tosc file is currently loaded."

    root = current_tosc
    control_node = root.find(f".//control[@name='{control_name}']")

    if control_node is None:
        return f"Error: Control '{control_name}' not found in the project."

    properties_node = control_node.find('properties')
    if properties_node is None:
        properties_node = etree.SubElement(control_node, 'properties')

    script_node = properties_node.find('script')
    if script_node is None:
        script_node = etree.SubElement(properties_node, 'script')
    
    script_node.text = etree.CDATA(script)
    return f"Successfully embedded script into control '{control_name}'."
