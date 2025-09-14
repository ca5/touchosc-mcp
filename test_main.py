import unittest
import os
import xml.etree.ElementTree as ET
import tosc_editor_lib as lib

class TestTouchOSCEditor(unittest.TestCase):

    def setUp(self):
        """Set up a clean environment before each test."""
        lib.current_tosc_root = None
        lib.current_tosc_path = None
        self.test_file = "test_output.tosc"
        self.test_file2 = "test_output2.tosc"
        # Clean up any files from previous runs
        self.tearDown()

    def tearDown(self):
        """Clean up files after each test."""
        for f in [self.test_file, self.test_file2]:
            if os.path.exists(f):
                os.remove(f)

    def test_01_create_new_file(self):
        """Test creating a new .tosc file."""
        result = lib.create_new_tosc_file(self.test_file)
        self.assertIn("Successfully created", result)
        self.assertTrue(os.path.exists(self.test_file))
        self.assertIsNotNone(lib.current_tosc_root)

        # Verify the file content
        tree = ET.parse(self.test_file)
        root = tree.getroot()
        self.assertEqual(root.tag, 'lexml')
        self.assertEqual(root.get('version'), '18')

    def test_02_load_and_write_file(self):
        """Test loading a file, modifying it, and writing it out."""
        # 1. Create a base file
        lib.create_new_tosc_file(self.test_file)

        # 2. Load it back
        load_result = lib.load_tosc_file(self.test_file)
        self.assertIn("Successfully loaded", load_result)

        # 3. Add a control to the loaded file
        lib.add_label("my_label", "hello", 0, 0, 100, 50)

        # 4. Write to a new file
        write_result = lib.write_tosc_file(self.test_file2)
        self.assertIn("Successfully wrote", write_result)

        # 5. Verify the new file has the added control
        tree = ET.parse(self.test_file2)
        label_node = tree.getroot().find(".//control[@name='my_label']")
        self.assertIsNotNone(label_node)
        self.assertEqual(label_node.get('type'), 'label')

    def test_03_add_button(self):
        """Test adding a button control."""
        lib.create_new_tosc_file(self.test_file)
        result = lib.add_button("my_button", "push", 10, 20, 30, 40, "green")
        self.assertIn("Successfully added", result)

        # Verify by checking the in-memory XML root
        button_node = lib.current_tosc_root.find(".//control[@name='my_button']")
        self.assertIsNotNone(button_node)
        self.assertEqual(button_node.get('x'), '10')

        type_prop = button_node.find("properties/property[@name='type']/string")
        self.assertEqual(type_prop.text, 'push')

        color_prop = button_node.find("properties/property[@name='color']/string")
        self.assertEqual(color_prop.text, 'green')

    def test_04_add_duplicate_control(self):
        """Test that adding a control with a duplicate name fails."""
        lib.create_new_tosc_file(self.test_file)
        lib.add_button("my_button", "push", 0, 0, 0, 0)
        result = lib.add_button("my_button", "toggle", 0, 0, 0, 0)
        self.assertIn("Error: A control with the name 'my_button' already exists", result)

    def test_05_embed_lua_script(self):
        """Test embedding a Lua script into a control."""
        lib.create_new_tosc_file(self.test_file)
        lib.add_button("script_button", "toggle", 0, 0, 50, 50)

        script_content = "function onValue(v) print(v) end"
        result = lib.embed_lua_script("script_button", script_content)
        self.assertIn("Successfully embedded", result)

        # Verify by checking the in-memory XML root
        control_node = lib.current_tosc_root.find(".//control[@name='script_button']")
        script_node = control_node.find("properties/script")
        self.assertIsNotNone(script_node)
        self.assertEqual(script_node.text, script_content)

if __name__ == '__main__':
    # The 's' in tests is for 'sequential' to ensure create runs first.
    # A better approach would be to not rely on global state, but this
    # matches the original structure. Forcing alphabetical order.
    unittest.main(failfast=True)
