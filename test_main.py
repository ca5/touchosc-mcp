import unittest
import os
import tosc_editor_lib as main
from tosclib import ElementTOSC, createTemplate, write

class TestTouchOSCEditorTools(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test."""
        main.current_tosc = None
        main.current_tosc_path = None
        self.test_file1 = "test1.tosc"
        self.test_file2 = "test2.tosc"
        self.tearDown()

    def tearDown(self):
        """Clean up after each test."""
        for f in [self.test_file1, self.test_file2]:
            if os.path.exists(f):
                os.remove(f)

    def test_create_new_tosc_file(self):
        """Test the creation of a new .tosc file."""
        result = main.create_new_tosc_file(self.test_file1)
        self.assertTrue(os.path.exists(self.test_file1))
        self.assertIsNotNone(main.current_tosc)
        self.assertIsInstance(main.current_tosc, ElementTOSC)
        self.assertIn("Successfully created", result)

    def test_load_non_existent_file(self):
        """Test loading a file that does not exist."""
        result = main.load_tosc_file("non_existent_file.tosc")
        self.assertIn("Error: File not found", result)
        self.assertIsNone(main.current_tosc)

    def test_load_and_write_file(self):
        """Test loading an existing file and writing it."""
        # Create a file to load
        tosc_obj_raw = createTemplate()
        write(tosc_obj_raw, self.test_file1)

        main.load_tosc_file(self.test_file1)
        self.assertIsNotNone(main.current_tosc)

        main.write_tosc_file(self.test_file2)
        self.assertTrue(os.path.exists(self.test_file2))

    def test_add_button(self):
        """Test adding a button to the current project."""
        main.create_new_tosc_file(self.test_file1)
        result = main.add_button("my_button", "push", 10, 10, 50, 50)
        self.assertIn("Successfully added", result)

        # Verify the button was actually added using the wrapper's method
        self.assertIsNotNone(main.current_tosc.findChildByName('my_button'))

        # Test adding a duplicate
        result_duplicate = main.add_button("my_button", "push", 20, 20, 50, 50)
        self.assertIn("Error: A control with the name 'my_button' already exists", result_duplicate)

    def test_embed_lua_script(self):
        """Test embedding a lua script into a control."""
        main.create_new_tosc_file(self.test_file1)
        main.add_button("script_button", "toggle", 0, 0, 50, 50)
        script_content = "function onValue(v) print(v) end"
        result = main.embed_lua_script("script_button", script_content)
        self.assertIn("Successfully embedded", result)

        # Verify the script was added using the wrapper's method
        script_node_wrapper = main.current_tosc.findChildByName('script_button')
        self.assertEqual(script_node_wrapper.getScript(), script_content)

if __name__ == '__main__':
    unittest.main()