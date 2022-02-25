# MLFLOW & JFrog Artifactory Plugin (Under construction)

Send artifacts into JFrog Generic Repository

## Setup

Expects environment variables below:  
`JFROG_ENDPOINT_URL` like `"http://<IP>:<PORT>/artifactory/<REPO>`  
Credentials:  
`JFROG_ARTIFACTORY_TOKEN` or  
`JFROG_ARTIFACTORY_APIKEY` or  
`JFROG_ARTIFACTORY_USERNAME` and `JFROG_ARTIFACTORY_PASSWORD`  
PS: `JFROG_ARTIFACTORY_APIKEY` can be used as `JFROG_ARTIFACTORY_PASSWORD`

## MLFlow

```python
import mlflow
import mlflow.pyfunc

class Mod(mlflow.pyfunc.PythonModel):
    def predict(self, ctx, inp):
        return 7

project_name = "project"
exp_name = "experiment1"
mlflow.create_experiment(exp_name, artifact_location=f"artifactory://{project_name}/{exp_name}")
mlflow.set_experiment(exp_name)
mlflow.log_artifact(artifact_path='python_files', #folder inside experiment
                    local_path='file.txt')
```