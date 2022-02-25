from setuptools import setup
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mflow-artifactory-plugin",
    version='0.0.1',
    description='Plugin that provides Artifact Store functionality between MLFlow and JFrog',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lucas A. Bonini',
    author_email='lucasamorimbonini@gmail.com',
    url="https://github.com/lbonini94/mflow-artifactory-plugin",
    # Require MLflow as a dependency of the plugin, so that plugin users can simply install
    # the plugin and then immediately use it with MLflow
    install_requires=[
        "mlflow",
        "dohq-artifactory",
    ],
    packages=find_packages(),
    entry_points={
        # Define a ArtifactRepository plugin for artifact URIs with scheme 'file-plugin'
        "mlflow.artifact_repository":
            "artifactory=mlflowartifactoryplugin.store.artifact.jfrog_artifactory:JfrogArtifactoryRepository",
    },
)