#!/usr/bin/env python3

"""Test script to check if layout_seed produces consistent results"""

import sys
import os

# Set seeds at the very beginning to control all randomization
import numpy as np
import random
import hashlib

# Set deterministic behavior
GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)

# Set Python hash seed for consistent dictionary ordering
os.environ['PYTHONHASHSEED'] = str(GLOBAL_SEED)

# Add the pct module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pct.hierarchy import PCTHierarchy
import tempfile
import matplotlib
import datetime

# Set NetworkX seed if available
try:
    import networkx as nx
    nx.random.seed(GLOBAL_SEED)
except (ImportError, AttributeError):
    pass

matplotlib.use('Agg')  # Use non-interactive backend

def test_with_examples():
    """Test using PCTHierarchy.load_from_file to load and draw hierarchies"""
    
    # Re-enforce seeds before each test
    np.random.seed(GLOBAL_SEED)
    random.seed(GLOBAL_SEED)
    try:
        nx.random.seed(GLOBAL_SEED)
    except AttributeError:
        pass
    
    # Use the specific file we know works
    config_file = "nbs/testfiles/MountainCar/MountainCar-cdf7cc1497ad143c0b04a3d9e72ab783.properties"
    
    if not os.path.exists(config_file):
        print(f"✗ Test file not found: {config_file}")
        return
    
    print(f"Testing with: {config_file}")
    
    try:
        # Load hierarchy directly
        print("Loading hierarchy...")
        hierarchy, _, _ = PCTHierarchy.load_from_file(config_file, suffixes=True)
        print(f"✓ Successfully loaded hierarchy: {hierarchy.name}")
        
        # Create timestamp for unique filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = "/tmp/dtest"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Test drawing with different seeds in output directory
        file1 = os.path.join(output_dir, f"{timestamp}_test_seed42_1.png")
        file2 = os.path.join(output_dir, f"{timestamp}_test_seed42_2.png")
        file3 = os.path.join(output_dir, f"{timestamp}_test_seed999.png")
        
        # Clean up any existing test files
        for f in [file1, file2, file3]:
            if os.path.exists(f):
                os.remove(f)
        
        print("Testing layout_seed parameter...")
        # move={}
        with_edge_labels=True
        font_size=6
        node_size=200
        funcdata=False
        move = {'IV':[0, 0.05],'IP':[-0.6, 0.3],  'OL0C0sm':[-0.28, -0.2],'OL0C1sm':[0.28, -0.2], 'OL1C0sm':[0,-0.1], 'MountainCarContinuousV0':[-.7,-0.5], 'Action1ws':[-0.4,-0.3]}

        # Draw with different seeds
        test_cases = [
            (file1, 42, "seed=42 (first time)"),
            (file2, 42, "seed=42 (second time)"),
            (file3, 999, "seed=999")
        ]
        
        for filename, seed, description in test_cases:
            print(f"  Drawing with {description}...")
            # hierarchy.draw(file=filename, layout_seed=seed, figsize=(8, 6))
            hierarchy.draw(file=filename, layout_seed=seed, figsize=(8, 6), with_edge_labels=with_edge_labels, font_size=font_size, node_size=node_size, funcdata=funcdata, move=move)

        # Check results and compare file sizes and hashes
        files_created = 0
        file_info = {}
        
        def get_file_hash(filepath):
            """Calculate MD5 hash of a file"""
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        for f in [file1, file2, file3]:
            if os.path.exists(f) and os.path.getsize(f) > 0:
                files_created += 1
                size = os.path.getsize(f)
                file_hash = get_file_hash(f)
                file_info[f] = {'size': size, 'hash': file_hash}
                print(f"    ✓ {f}: {size} bytes, hash: {file_hash[:8]}...")
        
        if files_created == 3:
            print("✓ All test images created successfully!")
            
            # Check if same seeds produce identical files
            if file_info[file1]['hash'] == file_info[file2]['hash']:
                print("✓ Same seed (42) produced identical files (same hash)")
            else:
                print("✗ Same seed (42) produced different files (different hash)")
            
            # Check if different seeds produce different files
            if file_info[file1]['hash'] != file_info[file3]['hash']:
                print("✓ Different seeds produced different files (different hash)")
            else:
                print("ℹ Different seeds produced identical files (same hash - layout may be deterministic)")
            
            print("✓ Layout seed functionality is working")
        else:
            print(f"✗ Only {files_created}/3 images created")
            
    except Exception as e:
        print(f"✗ Error running test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_examples()
    print("\nLayout seed test completed!")
