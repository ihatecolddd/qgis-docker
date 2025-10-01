#!/usr/bin/env python3
import sys
import argparse

def quick_check():
    try:
        import qgis.core
        import numpy
        import pandas
        print("[OK] Quick validation passed")
        return True
    except ImportError as e:
        print(f"[ERROR] Quick validation failed: {e}")
        return False

def full_check():
    print("Running full validation...")
    quick_check()
    
    # Check directories
    import os
    from pathlib import Path
    
    dirs = ["/workspace", "/logs", "/config"]
    for d in dirs:
        if Path(d).exists():
            print(f"[OK] Directory exists: {d}")
        else:
            print(f"[ERROR] Directory missing: {d}")
    
    # Check Python packages
    packages = ["numpy", "scipy", "pandas", "rasterio", "geopandas"]
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"[OK] Package {pkg} installed")
        except ImportError:
            print(f"[ERROR] Package {pkg} not found")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    
    if args.quick:
        sys.exit(0 if quick_check() else 1)
    else:
        sys.exit(0 if full_check() else 1)
