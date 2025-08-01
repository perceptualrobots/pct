


from pct.experiments import CometExperimentManager
import os

"""


python -m pct.applications.run_experiments


"""


# Initialize the manager
workspace = 'lunarlandercontinuous-v2'

manager = CometExperimentManager(workspace=workspace)

projects = manager.get_workspace_projects()
print(f"Projects in workspace '{workspace}':", projects)

# Get all artifacts once (outside loop for better performance)
artifact_results = manager.get_all_artifacts_indexed()

num_runs=100

for project_name in projects:
    if 'test' in project_name.lower() or project_name.lower() == 'general':      
        continue
    
    # Set max and score_threshold based on project_name
    max = False
    score_threshold = 0.05  # Default for error-based projects
    
    # Reward-based projects use higher thresholds and max=True
    if 'reward' in project_name.lower():
        score_threshold = 100
        max = True
    # RMS and smooth error projects typically use lower thresholds
    elif 'inputs-rms' in project_name.lower():
        score_threshold = 1.0
        max = False
    elif 'refinputs-smooth' in project_name.lower():
        score_threshold = 0.05
        max = False
    # Referenced inputs projects
    elif 'refinputs-rms' in project_name.lower():
        score_threshold = 1.5
        max = False
    # Current error projects
    elif 'refinputs-currentrms' in project_name.lower():
        score_threshold = 0.05
        max = False
    # Variance-based projects (new for Welford)
    elif 'variance' in project_name.lower() or 'welford' in project_name.lower():
        score_threshold = 0.1
        max = False

    # Test get_experiments_by_metrics
    experiments = manager.get_experiments_by_metrics(project_name=project_name, score_threshold=score_threshold, reward_threshold=99.0, max=max)
    # print("Filtered experiments:", experiments)

    output_csv = f'/tmp/artifacts/experiment_results_{project_name}.csv'
    if os.path.exists(output_csv):
        print(f"{output_csv} already exists, skipping...")
        continue
    manager.run_experiments_and_record_results(experiments=experiments, project_name=project_name, artifact_results=artifact_results, num_runs=num_runs, output_csv=output_csv)
    print(f"Results saved to {output_csv}")




