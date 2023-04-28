import mlflow
from dotenv import load_dotenv
from mlflow.sklearn import load_model
import os
load_dotenv()

MLFLOW_TRACKING_URI= os.environ["MLFLOW_TRACKING_URI"]
os.environ["MLFLOW_TRACKING_USERNAME"]
os.environ["MLFLOW_TRACKING_PASSWORD"]
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

class MLFlowManager:
    def __init__(self):
        if mlflow.tracking.is_tracking_uri_set():
            self.client = mlflow.MlflowClient()
        else:
            raise Exception("Tracking URI not set")
    
    def get_or_create_an_experiment(self, experiment_name):
        exp = mlflow.get_experiment_by_name(experiment_name)
        if exp is None:
            exp_id = mlflow.create_experiment(experiment_name)
            return exp_id
        return exp.experiment_id
    
    def latest_model_version(self, model_name) -> int:
        return self.client.get_latest_versions(model_name)[0].version
    
    @property
    def get_latest_version_model_uri(self, model_name) -> str:
        model_uri = f"models:/{model_name}/{self.latest_model_version(model_name)}"
        return model_uri
    
    def load_latest_model_version(self, model_name):
        return load_model(self.get_latest_version_model_uri(model_name))

    def get_best_run_id_and_model_uri(self, experiment_id: str, metric_name: str="metrics.mae", ascending = True ):
        runs = mlflow.search_runs(f"{experiment_id}")
        runs = runs.dropna(subset=['tags.mlflow.log-model.history'])
        runs.sort_values(by=[metric_name], ascending = ascending, inplace = True)
        runs.to_csv('mlflow.csv', index=False)
        runs.reset_index(inplace= True, drop = True)
        best_run_id = runs['run_id'][0]

        best_run = runs[runs["run_id"]==best_run_id]
        artifact_uri = best_run['artifact_uri'][0]

        logged_model_dir = best_run['tags.mlflow.log-model.history'][0].split(',')[1:2]
        logged_model_dir = logged_model_dir[0].strip().split(':')[1].replace('"', '').strip()

        model_uri = str(artifact_uri)+"/"+str(logged_model_dir)

        return best_run_id, model_uri
    
    def print_registered_model(self, model_name):
        for model in self.client.search_registered_models(filter_string = f"name LIKE {model_name}"):
            for model_version in model.latest_versions:
                print(f"name : {model_version.name} run_id : {model_version.run_id} version : {model_version.version} stage : {model_version.current_stage}")

    def rename_a_registered_model(self ,current_name, new_name):
        self.client.rename_registered_model(
            name = current_name,
            new_name = new_name,
        )

    def transition_model_version_stage(self, model_name, model_version, stage):
        self.client.transition_model_version_stage(
            name = model_name,
            version = model_version,
            stage = stage
        )
