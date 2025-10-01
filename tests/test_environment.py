#!/usr/bin/env python3
import unittest
import sys
import platform

class TestEnvironment(unittest.TestCase):
    def test_qgis_import(self):
        """Test QGIS can be imported"""
        try:
            from qgis.core import QgsApplication, Qgis
            self.assertIsNotNone(QgsApplication)
        except ImportError as e:
            self.fail(f"Failed to import QGIS: {e}")
    
    def test_python_packages(self):
        """Test required Python packages"""
        packages = ["numpy", "scipy", "pandas", "rasterio"]
        for package in packages:
            with self.subTest(package=package):
                try:
                    __import__(package)
                except ImportError:
                    self.fail(f"Package {package} not installed")

if __name__ == "__main__":
    unittest.main(verbosity=2)
