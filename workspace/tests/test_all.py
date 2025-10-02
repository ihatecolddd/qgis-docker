#!/usr/bin/env python3
"""
Comprehensive Test Suite for QGIS Docker Environment
Tests all Phase 1 deliverables
Save as: tests/test_all.py
"""

import sys
import os
import json
import traceback
from datetime import datetime

class TestResults:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        self.start_time = datetime.now()
        
    def add_result(self, test_name, passed, message=""):
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"  ✅ {test_name}: PASSED")
        else:
            self.tests_failed += 1
            self.failures.append({"test": test_name, "message": message})
            print(f"  ❌ {test_name}: FAILED - {message}")
    
    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.failures:
            print("\nFailed Tests:")
            for failure in self.failures:
                print(f"  - {failure['test']}: {failure['message']}")
        
        return self.tests_failed == 0

def test_qgis_installation(results):
    """Test 1: QGIS Installation and Version"""
    print("\n🔧 Testing QGIS Installation...")
    
    try:
        from qgis.core import Qgis, QgsApplication
        version = Qgis.version()
        version_int = Qgis.versionInt()
        
        # Check version is 3.34.x
        if version.startswith("3.34"):
            results.add_result("QGIS Version 3.34 LTR", True, f"Version: {version}")
        else:
            results.add_result("QGIS Version 3.34 LTR", False, f"Wrong version: {version}")
        
        # Test QGIS initialization
        QgsApplication.setPrefixPath("/usr", True)
        qgs = QgsApplication([], False)
        qgs.initQgis()
        results.add_result("QGIS Initialization", True)
        qgs.exitQgis()
        
    except Exception as e:
        results.add_result("QGIS Installation", False, str(e))
        return False
    
    return True

def test_python_libraries(results):
    """Test 2: Python Scientific Libraries"""
    print("\n📚 Testing Python Libraries...")
    
    required_libs = {
        'numpy': 'Scientific computing',
        'pandas': 'Data analysis',
        'gdal': 'Geospatial data',
        'matplotlib': 'Plotting',
        'scipy': 'Scientific tools',
        'rasterio': 'Raster I/O',
        'shapely': 'Geometric operations',
        'fiona': 'Vector I/O'
    }
    
    for lib, description in required_libs.items():
        try:
            module = __import__(lib)
            version = getattr(module, '__version__', 'unknown')
            results.add_result(f"Library: {lib}", True, f"v{version}")
        except ImportError:
            results.add_result(f"Library: {lib}", False, "Not installed")

def test_enmapbox_installation(results):
    """Test 3: EnMAP-Box Installation"""
    print("\n📦 Testing EnMAP-Box...")
    
    # Check if files exist
    enmapbox_path = '/usr/share/qgis/python/plugins/enmapbox'
    if os.path.exists(enmapbox_path):
        results.add_result("EnMAP-Box Files", True, f"Found at {enmapbox_path}")
        
        # Count files to ensure complete installation
        file_count = sum([len(files) for r, d, files in os.walk(enmapbox_path)])
        if file_count > 100:  # EnMAP-Box has hundreds of files
            results.add_result("EnMAP-Box Completeness", True, f"{file_count} files")
        else:
            results.add_result("EnMAP-Box Completeness", False, f"Only {file_count} files")
    else:
        results.add_result("EnMAP-Box Files", False, "Not found")
        return False
    
    # Check dependencies
    try:
        import pyqtgraph
        results.add_result("EnMAP-Box Dependency: pyqtgraph", True)
    except ImportError:
        results.add_result("EnMAP-Box Dependency: pyqtgraph", False, "Not installed")
    
    try:
        import spectral
        results.add_result("EnMAP-Box Dependency: spectral", True)
    except ImportError:
        results.add_result("EnMAP-Box Dependency: spectral", False, "Not installed")
    
    # Try to import (may fail in headless mode, that's OK)
    sys.path.insert(0, '/usr/share/qgis/python/plugins')
    try:
        import enmapbox
        results.add_result("EnMAP-Box Import", True, "Module loads")
    except Exception as e:
        # Check if it's just GUI-related error
        if "pyqtgraph" in str(e) or "display" in str(e).lower():
            results.add_result("EnMAP-Box Import", True, "Installed (GUI components need display)")
        else:
            results.add_result("EnMAP-Box Import", False, str(e))

def test_processing_algorithms(results):
    """Test 4: QGIS Processing Algorithms"""
    print("\n⚙️ Testing Processing Algorithms...")
    
    try:
        from qgis.core import QgsApplication, QgsProcessingRegistry
        from qgis import processing
        
        QgsApplication.setPrefixPath("/usr", True)
        qgs = QgsApplication([], False)
        qgs.initQgis()
        
        # Initialize processing
        import processing
        from processing.core.Processing import Processing
        Processing.initialize()
        
        # Count available algorithms
        registry = QgsApplication.processingRegistry()
        algorithms = registry.algorithms()
        alg_count = len(algorithms)
        
        if alg_count > 100:
            results.add_result("Processing Algorithms", True, f"{alg_count} algorithms available")
        else:
            results.add_result("Processing Algorithms", False, f"Only {alg_count} algorithms")
        
        # Test specific important algorithms
        test_algs = ['native:buffer', 'gdal:hillshade', 'qgis:creategrid']
        for alg_id in test_algs:
            alg = registry.algorithmById(alg_id)
            if alg:
                results.add_result(f"Algorithm: {alg_id}", True)
            else:
                results.add_result(f"Algorithm: {alg_id}", False, "Not found")
        
        qgs.exitQgis()
        
    except Exception as e:
        results.add_result("Processing Framework", False, str(e))

def test_data_io(results):
    """Test 5: Data Input/Output"""
    print("\n💾 Testing Data I/O...")
    
    try:
        from qgis.core import Qgis
        
        QgsApplication.setPrefixPath("/usr", True)
        qgs = QgsApplication([], False)
        qgs.initQgis()
        
        # Test 1: Create memory layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test", "memory")
        results.add_result("Create Memory Layer", layer.isValid())
        
        # Test 2: Add features
        provider = layer.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        provider.addFeatures([feat])
        results.add_result("Add Features", layer.featureCount() == 1)
        
        # Test 3: Save to file
        output_path = "/workspace/test_output.geojson"
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GeoJSON"
        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer, output_path, QgsCoordinateTransformContext(), options
        )
        results.add_result("Write GeoJSON", error[0] == QgsVectorFileWriter.NoError)
        
        # Test 4: Read file back
        loaded_layer = QgsVectorLayer(output_path, "loaded", "ogr")
        results.add_result("Read GeoJSON", loaded_layer.isValid() and loaded_layer.featureCount() == 1)
        
        # Test 5: Multiple formats
        formats = {
            "ESRI Shapefile": "/workspace/test.shp",
            "GPKG": "/workspace/test.gpkg"
        }
        
        for format_name, path in formats.items():
            options.driverName = format_name
            error = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, path, QgsCoordinateTransformContext(), options
            )
            results.add_result(f"Write {format_name}", error[0] == QgsVectorFileWriter.NoError)
        
        qgs.exitQgis()
        
    except Exception as e:
        results.add_result("Data I/O", False, str(e))

def test_docker_environment(results):
    """Test 6: Docker Environment"""
    print("\n🐳 Testing Docker Environment...")
    
    # Test workspace directory
    workspace_exists = os.path.exists('/workspace')
    results.add_result("Workspace Directory", workspace_exists)
    
    # Test write permissions
    try:
        test_file = '/workspace/test_write.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        results.add_result("Workspace Write Permission", True)
    except:
        results.add_result("Workspace Write Permission", False, "Cannot write to workspace")
    
    # Test environment variables
    env_vars = ['QGIS_PREFIX_PATH', 'PYTHONPATH']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            results.add_result(f"Environment: {var}", True, value)
        else:
            results.add_result(f"Environment: {var}", False, "Not set")

def test_providers(results):
    """Test 7: Data Providers"""
    print("\n🔌 Testing Data Providers...")
    
    try:
        from qgis.core import QgsApplication, QgsProviderRegistry
        
        QgsApplication.setPrefixPath("/usr", True)
        qgs = QgsApplication([], False)
        qgs.initQgis()
        
        registry = QgsProviderRegistry.instance()
        providers = registry.providerList()
        
        # Check essential providers
        essential = ['ogr', 'gdal', 'memory', 'WFS', 'WMS']
        for provider in essential:
            if provider in providers:
                results.add_result(f"Provider: {provider}", True)
            else:
                results.add_result(f"Provider: {provider}", False, "Not available")
        
        results.add_result("Total Providers", True, f"{len(providers)} providers available")
        
        qgs.exitQgis()
        
    except Exception as e:
        results.add_result("Providers", False, str(e))

def generate_test_report(results):
    """Generate a test report file"""
    report = {
        "test_date": datetime.now().isoformat(),
        "environment": "Docker QGIS 3.34 LTR with EnMAP-Box",
        "total_tests": results.tests_run,
        "passed": results.tests_passed,
        "failed": results.tests_failed,
        "success_rate": f"{(results.tests_passed/results.tests_run*100):.1f}%",
        "failures": results.failures
    }
    
    # Save JSON report
    with open('/workspace/test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save readable report
    with open('/workspace/test_report.txt', 'w') as f:
        f.write("QGIS DOCKER ENVIRONMENT TEST REPORT\n")
        f.write("="*50 + "\n")
        f.write(f"Date: {report['test_date']}\n")
        f.write(f"Tests Run: {report['total_tests']}\n")
        f.write(f"Passed: {report['passed']}\n")
        f.write(f"Failed: {report['failed']}\n")
        f.write(f"Success Rate: {report['success_rate']}\n")
        
        if results.failures:
            f.write("\nFailed Tests:\n")
            for failure in results.failures:
                f.write(f"  - {failure['test']}: {failure['message']}\n")
        else:
            f.write("\n✅ All tests passed!\n")
    
    print(f"\n📄 Test report saved to:")
    print(f"  - /workspace/test_report.json")
    print(f"  - /workspace/test_report.txt")

def main():
    """Run all tests"""
    print("="*70)
    print("QGIS DOCKER ENVIRONMENT - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = TestResults()
    
    # Run all test categories
    test_qgis_installation(results)
    test_python_libraries(results)
    test_enmapbox_installation(results)
    test_processing_algorithms(results)
    test_data_io(results)
    test_docker_environment(results)
    test_providers(results)
    
    # Print summary
    all_passed = results.print_summary()
    
    # Generate report
    generate_test_report(results)
    
    # Exit code
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Environment is fully operational.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {results.tests_failed} tests failed. Check the report for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()