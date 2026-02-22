#!/usr/bin/env python3
"""
Main application for running PCT Examples
This script demonstrates how to use PCTExamples.run_example() to run PCT hierarchies.
"""

import argparse
import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pct.pctexamples import PCTExamples


def main():
    """Main function to run PCT examples"""
    
    parser = argparse.ArgumentParser(
        description='Run PCT hierarchy examples from configuration files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic run
  python pct/applications/pct_example.py 'testfiles/MountainCar/MountainCar-cdf7cc.properties'
  
  # Run with rendering and verbose output
  python pct/applications/pct_example.py 'testfiles/MountainCar/MountainCar-cdf7cc.properties' --render --verbose
  python pct/applications/pct_example.py 'testfiles/LunarLander/LunarLander-4905d2.properties' --render --verbose
  python pct/applications/pct_example.py 'testfiles/CartPole/CartPole-6fb461.properties' --render --verbose

  # Run with image output
  python pct/applications/pct_example.py 'testfiles/MountainCar/MountainCar-cdf7cc.properties' --image --image-size 16 10
  
  # Run with video output
  python pct/applications/pct_example.py 'testfiles/LunarLander/LunarLander-4905d2.properties' --render --video --video-file output.mp4 --fps 60
  
  # Save configuration to JSON
  python pct/applications/pct_example.py 'testfiles/CartPole/CartPole-6fb461.properties' --save-json
  python pct/applications/pct_example.py 'testfiles/CartPole/CartPole-6fb461.properties' --save-json --json-file my_config.json
  
  # Full featured run with all options
  python pct/applications/pct_example.py 'testfiles/MountainCar/MountainCar-cdf7cc.properties' --run --render --steps 5000 --image --verbose
        """
    )
    
    # Required arguments
    parser.add_argument('config_file', 
                        help='Path to the PCT hierarchy configuration file (.properties)')
    
    # Optional arguments
    parser.add_argument('--run', '--run-hierarchy', 
                        action='store_true',
                        dest='run_hierarchy',
                        help='Run the hierarchy simulation (default: True)')
    
    parser.add_argument('--no-run',
                        action='store_false',
                        dest='run_hierarchy',
                        help='Do not run the hierarchy, only create outputs')
    
    parser.add_argument('--render',
                        action='store_true',
                        help='Render the environment during simulation')
    
    parser.add_argument('--early-termination',
                        action='store_true',
                        help='Enable early termination when goal is reached')
    
    parser.add_argument('--steps',
                        type=int,
                        default=None,
                        help='Number of simulation steps (overrides config default)')
    
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Enable verbose output')
    
    parser.add_argument('--summary',
                        action='store_true',
                        help='Print hierarchy summary')
    
    parser.add_argument('--usage',
                        action='store_true',
                        help='Display detailed usage information')
    
    # Image output options
    parser.add_argument('--image',
                        action='store_true',
                        help='Create hierarchy diagram image')
    
    parser.add_argument('--image-size',
                        nargs=2,
                        type=int,
                        default=[16, 10],
                        metavar=('WIDTH', 'HEIGHT'),
                        help='Image size in inches (default: 16 10)')
    
    parser.add_argument('--image-file',
                        type=str,
                        default=None,
                        help='Output file for hierarchy image (default: auto-generated)')
    
    # Video output options
    parser.add_argument('--video',
                        action='store_true',
                        help='Create video of the simulation')
    
    parser.add_argument('--video-file',
                        type=str,
                        default=None,
                        help='Output file for video (default: auto-generated)')
    
    parser.add_argument('--fps',
                        type=int,
                        default=60,
                        help='Video frames per second (default: 60)')
    
    # JSON output options
    parser.add_argument('--save-json',
                        action='store_true',
                        help='Save the configuration as a JSON file')
    
    parser.add_argument('--json-file',
                        type=str,
                        default=None,
                        help='Output file for JSON configuration (default: auto-generated from config file name)')
    
    # Set default for run_hierarchy to True
    parser.set_defaults(run_hierarchy=True)
    
    args = parser.parse_args()
    
    # Display usage if requested
    if args.usage:
        PCTExamples.run_example('', display_usage=True)
        return 0
    
    # Validate config file
    if not os.path.exists(args.config_file):
        print(f"Error: Configuration file not found: {args.config_file}")
        return 1
    
    # Build parameters for run_example
    run_params = {
        'config_file': args.config_file,
        'run_hierarchy': args.run_hierarchy,
        'render': args.render,
        'early_termination': args.early_termination,
        'verbose': args.verbose,
        'print_summary': args.summary,
        'return_config': args.save_json,  # Request config if saving to JSON
    }
    
    # Add steps if specified
    if args.steps is not None:
        run_params['steps'] = args.steps
    
    # Add image parameters if requested
    if args.image:
        image_params = {
            'figsize': tuple(args.image_size),
            'with_labels': True,
        }
        if args.image_file:
            image_params['file'] = args.image_file
        run_params['image_params'] = image_params
    
    # Add video parameters if requested
    if args.video:
        video_params = {
            'fps': args.fps,
        }
        if args.video_file:
            video_params['filename'] = args.video_file
        run_params['video_params'] = video_params
    
    # Run the example
    if args.verbose:
        print(f"Running PCT example from: {args.config_file}")
        print(f"Parameters: {run_params}")
        print("-" * 60)
    
    try:
        results = PCTExamples.run_example(**run_params)
        
        # Display results
        if args.verbose:
            print("-" * 60)
            print("Results:")
            for key, value in results.items():
                if key == 'figure':
                    print(f"  {key}: <matplotlib.figure.Figure>")
                elif key == 'config':
                    print(f"  {key}: <configuration dict>")
                elif key == 'run_result':
                    print(f"  {key}: <run result object>")
                else:
                    print(f"  {key}: {value}")
        
        # Check for success
        if results.get('success', False):
            if args.verbose:
                print("\nExecution completed successfully!")
            
            # Save JSON configuration if requested
            if args.save_json and 'config' in results:
                # Generate default filename if not specified
                if args.json_file:
                    json_output_file = args.json_file
                else:
                    # Auto-generate from config file name
                    base_name = os.path.splitext(os.path.basename(args.config_file))[0]
                    json_output_file = f"{base_name}.json"
                
                try:
                    with open(json_output_file, 'w') as f:
                        json.dump(results['config'], f, indent=2)
                    print(f"JSON configuration saved: {json_output_file}")
                except Exception as e:
                    print(f"Warning: Failed to save JSON configuration: {e}")
            
            # Report output files
            if 'image_file' in results:
                print(f"Hierarchy image saved: {results['image_file']}")
            if 'video_file' in results:
                print(f"Video saved: {results['video_file']}")
            if 'steps_completed' in results:
                print(f"Simulation completed: {results['steps_completed']} steps")
            
            return 0
        else:
            print(f"Error: {results.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"Error running example: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
