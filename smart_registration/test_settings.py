"""
Tests for Django settings and environment variable loading.

This module tests that the settings.py file correctly loads environment
variables from a .env file using python-dotenv.
"""
import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


class SettingsEnvLoadingTestCase(TestCase):
    """Test that settings.py correctly loads .env file."""

    def test_dotenv_module_import(self):
        """Test that dotenv module can be imported."""
        try:
            import dotenv
            self.assertTrue(True, "dotenv module imported successfully")
        except ImportError:
            self.fail("dotenv module not available - python-dotenv not installed")

    def test_dotenv_loads_env_file(self):
        """Test that dotenv.load_dotenv() works with a .env file."""
        import dotenv
        
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR_1=test_value_1\n')
            f.write('TEST_VAR_2=test_value_2\n')
            temp_env_path = f.name
        
        try:
            # Clear the environment
            os.environ.pop('TEST_VAR_1', None)
            os.environ.pop('TEST_VAR_2', None)
            
            # Load the .env file
            dotenv.load_dotenv(temp_env_path)
            
            # Verify variables were loaded
            self.assertEqual(os.environ.get('TEST_VAR_1'), 'test_value_1')
            self.assertEqual(os.environ.get('TEST_VAR_2'), 'test_value_2')
        finally:
            # Cleanup
            os.environ.pop('TEST_VAR_1', None)
            os.environ.pop('TEST_VAR_2', None)
            os.unlink(temp_env_path)

    def test_dotenv_handles_missing_file_gracefully(self):
        """Test that dotenv.load_dotenv() handles missing .env file."""
        import dotenv
        
        # Try to load non-existent file - should not raise exception
        nonexistent_file = Path('/tmp/nonexistent_file_12345.env')
        result = dotenv.load_dotenv(nonexistent_file)
        
        # Should return False when file doesn't exist
        self.assertFalse(result, "load_dotenv should return False for missing file")

    def test_config_helper_with_env_vars(self):
        """Test the config() helper function with environment variables."""
        # Setup test environment variable
        os.environ['TEST_CONFIG_VAR'] = 'test_value'
        
        try:
            # Import the config function from settings
            from smart_registration.settings import config
            
            # Test basic retrieval
            value = config('TEST_CONFIG_VAR')
            self.assertEqual(value, 'test_value')
            
            # Test with default
            value = config('NON_EXISTENT_VAR', default='default_value')
            self.assertEqual(value, 'default_value')
            
            # Test bool casting
            os.environ['TEST_BOOL_TRUE'] = 'True'
            os.environ['TEST_BOOL_FALSE'] = 'false'
            
            self.assertTrue(config('TEST_BOOL_TRUE', cast=bool))
            self.assertFalse(config('TEST_BOOL_FALSE', cast=bool))
            
        finally:
            # Cleanup
            os.environ.pop('TEST_CONFIG_VAR', None)
            os.environ.pop('TEST_BOOL_TRUE', None)
            os.environ.pop('TEST_BOOL_FALSE', None)

    def test_settings_imports_without_error(self):
        """Test that settings module can be imported without errors."""
        # This test verifies that the settings.py file with dotenv.load_dotenv()
        # can be imported successfully
        try:
            import smart_registration.settings
            self.assertTrue(True, "Settings module imported successfully")
        except Exception as e:
            self.fail(f"Failed to import settings module: {e}")

    def test_debug_setting_from_env(self):
        """Test that DEBUG setting is correctly read from environment."""
        from smart_registration import settings
        
        # The DEBUG value should be loaded from .env or use default
        # This verifies the integration works
        self.assertIsNotNone(settings.DEBUG)
        self.assertIsInstance(settings.DEBUG, bool)

    def test_secret_key_setting(self):
        """Test that SECRET_KEY is available."""
        from smart_registration import settings
        
        # SECRET_KEY should be set (from .env or default)
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertIsInstance(settings.SECRET_KEY, str)
        self.assertGreater(len(settings.SECRET_KEY), 0)
