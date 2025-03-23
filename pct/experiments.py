# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/20_experiments.ipynb.

# %% auto 0
__all__ = ['CometExperimentManager']

# %% ../nbs/20_experiments.ipynb 3
import os, json, csv
from comet_ml import API, APIExperiment, start
from .hierarchy import PCTHierarchy  
from comet_ml.query import Metric

# %% ../nbs/20_experiments.ipynb 4
class CometExperimentManager:
    def __init__(self, api_key: str = None, workspace: str = None):
        self.api = API(api_key)
        self.workspace = workspace

    def get_all_artifacts_indexed(self):
        """Retrieve all artifacts and sort them by source experiment key."""
        filename = '/tmp/artifacts/artifacts_results.json'
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
            
        artifacts = self.api.get_artifact_list(workspace=self.workspace)
        experiment = start(workspace=self.workspace)
        results = {}
        for artifact_dict in artifacts['artifacts']:
            id = artifact_dict['name']
            try:
                logged_artifact = experiment.get_artifact(id)
                print(logged_artifact.source_experiment_key, id)
                results[logged_artifact.source_experiment_key] = id
            except Exception as e:
                print(f"Error retrieving artifact {id}: {e}")

        # Save results to a file
        with open(filename, "w") as file:
            json.dump(results, file, indent=4)
        experiment.end()
        return results

    def get_experiments_by_metrics(self, project_name: str = None, score_threshold: float = None, reward_threshold: float = None):
        """
        Retrieve experiments for a project where the metric 'score' is less than
        score_threshold and 'reward' is greater than or equal to reward_threshold.
        """
        # experiments = self.api.query(self.workspace, project_name, Metric("score") < score_threshold & Metric("reward") >= reward_threshold)
        experiments = self.api.query(self.workspace, project_name, Metric("score") < score_threshold )
 
        return experiments

    def get_artifact_name(self, experiment: APIExperiment = None):
        """Retrieve the name of an artifact from an experiment."""
        artifacts = experiment.get_artifacts()
        return artifacts[0]['artifact_name'] if artifacts else None

    def download_and_run_artifact(self, artifact_name: str = None, seeds: list[int] = None):
        """
        Download an artifact to '/tmp/artifacts/' and run PCTHierarchy.run_from_file
        with the artifact filename, returning the score value for each run.
        """
        download_path = f"/tmp/artifacts/"
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
 
        full_path = os.path.join(download_path, artifact_name)
        if os.path.exists(full_path):
            pass
        else:
            experiment = start(workspace=self.workspace)
            logged_artifact  = experiment.get_artifact(artifact_name)
            # print(logged_artifact.source_experiment_key)
            # local_artifact = logged_artifact.download(download_path)
            logged_artifact.download(download_path)
            # filename = f"{local_artifact.download_local_path}{artifact_name}"
            experiment.end()
    
        rewards = []
        for seed in seeds:
            hierarchy, score = PCTHierarchy.run_from_file(full_path, seed=seed)
            metrics = hierarchy.get_environment().get_metrics()
            # print(f'Score={score:0.3f} {metrics}')
            rewards.append(metrics['reward'])



        return rewards

    def get_original_metrics(self, experiment: APIExperiment = None):
        """Retrieve the metrics for an experiment."""
        metrics = {}
        metrics['score'] = eval(experiment.get_metrics("score")[0]['metricValue'])
        hyperparameters = experiment.get_parameters_summary()

        for param in hyperparameters:
            if param['name'] == 'mode':
                metrics['mode'] = param['valueCurrent']
                break

        metrics['name'] = experiment.name
        return metrics

    def run_experiments_and_record_results(self, project_name: str = None, experiments: list[APIExperiment] = None, artifact_results: dict = None, num_runs: int = 0, output_csv: str = None):
        """
        Run each experiment for a given project a specified number of times and record the score and the
        number of times the reward is 100, -100, or something else. Save results to a CSV file.
        """
        results = []
        for experiment in experiments:
            artifact_name = artifact_results[experiment.id]

            metrics = self.get_original_metrics(experiment)

            print(f"Running experiment {experiment.id} in project {project_name} with artifact {artifact_name}")
            if not artifact_name:
                continue

            rewards = self.download_and_run_artifact(artifact_name, seeds=range(num_runs))
            reward_counts = {'100': 0, '-100': 0, 'other': 0}

            for reward in rewards:
                if reward == 100:
                    reward_counts['100'] += 1
                elif reward == -100:
                    reward_counts['-100'] += 1
                else:
                    reward_counts['other'] += 1
            print(f"Rewards: {reward_counts}")
            results.append({
                'name': metrics['name'],
                'score': round(metrics['score'], 5),
                'mode': metrics['mode'],
                'reward_100': reward_counts['100'],
                'reward_-100': reward_counts['-100'],
                'reward_other': reward_counts['other'],
                'experiment_key': '/'.join(("https://www.comet.com", self.workspace, project_name, experiment.id)),
                'artifact_name': artifact_name
            })
        # Sort results by 'reward_100' in descending order, then by 'reward_other' in descending order
        results.sort(key=lambda x: (-x['reward_100'], -x['reward_other']))
        # Save results to CSV
        with open(output_csv, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['name', 'score', 'mode', 'reward_100', 'reward_-100', 'reward_other', 'experiment_key', 'artifact_name'])
            writer.writeheader()
            writer.writerows(results)
