
import posixpath
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from artifactory import ArtifactoryPath
from mlflow.exceptions import MlflowException
from mlflow.utils.file_utils import relative_path_to_artifact_path
import os
import urllib
import logging
from mlflow.entities import FileInfo
import sys

logger = logging.getLogger(__name__)


class JfrogArtifactoryRepository(ArtifactRepository):
    """Stores Artifacts on JFrog Artifactory
    """
    
    is_plugin=True
    
    def __init__(self,
                 artifact_uri: str, # "artifactory://experiment_foo",
                 ):
        super(JfrogArtifactoryRepository, self).__init__(artifact_uri)
        
        # "http://my-jfrog-server/artifactory/<main_repo>"
        self.jfrog_endpoint_url = os.environ.get("JFROG_ENDPOINT_URL")
        assert self.jfrog_endpoint_url, 'Please set JFROG_ENDPOINT_URL'
        
        self.auth: dict = self._auth()
        
        
    def _auth(self):

        if "JFROG_ARTIFACTORY_TOKEN" in os.environ:
            jfrog_artifactory_token = os.environ.get("JFROG_ARTIFACTORY_TOKEN")
            path = ArtifactoryPath(
                self.jfrog_endpoint_url,
                token=jfrog_artifactory_token
            )
            if path.exists():
                return {"token": jfrog_artifactory_token}
                
        elif "JFROG_ARTIFACTORY_APIKEY" in os.environ:
            jfrog_apikey = os.environ.get("JFROG_ARTIFACTORY_APIKEY")
            path = ArtifactoryPath(
                self.jfrog_endpoint_url,
                apikey=jfrog_apikey
            )
            if path.exists():
                return {"apikey": jfrog_apikey}
 
        else:
            try:
                jfrog_artifactory_username = os.environ["JFROG_ARTIFACTORY_USERNAME"]
                jfrog_artifactory_password = os.environ["JFROG_ARTIFACTORY_PASSWORD"]
            except KeyError:
                raise Exception("YOU NEED TO PROVIDE SOME AUTH METHOD TO JFROG\n-APIKEY\n-TOKEN\n-USER/PASS")
            path = ArtifactoryPath(
                self.jfrog_endpoint_url,
                auth=(jfrog_artifactory_username,
        # "JFROG_ARTIFACTORY_PASSWORD" can be "JFROG_ARTIFACTORY_APIKEY"
                    jfrog_artifactory_password), 
            )
            if path.exists():
                return {"auth": (jfrog_artifactory_username,
                                 jfrog_artifactory_password)}

                
    @staticmethod
    def parse_artifactory_uri(uri:str):
        """Parse an Artifactory URI, returning (repo_name, repo_path)"""
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != "artifactory":
            raise Exception("Not an artifactory URI: %s" % uri)
        path = parsed.path
        if path.startswith('/'):
            path = path[1:]
        return parsed.netloc, path
    
    def log_artifact(self, local_file, artifact_path=None):
        rname, dest_path = self.parse_artifactory_uri(self.artifact_uri)
        
        if artifact_path:
            dest_path = posixpath.join(rname, dest_path, artifact_path)
        else:
            dest_path = posixpath.join(rname, dest_path)
        path = ArtifactoryPath(
            self.jfrog_endpoint_url + '/'
            + dest_path,
            **self.auth
        )
        if not path.exists():
            path.mkdir()
        
        path.deploy_file(local_file)

    
    def log_artifacts(self, local_dir, artifact_path=None):
        rname, dest_path = self.parse_artifactory_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(rname, dest_path, artifact_path)
        local_dir = os.path.abspath(local_dir)
        for (root, _, filenames) in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                rel_path = relative_path_to_artifact_path(rel_path)
                upload_path = posixpath.join(dest_path, rel_path)
                
            for f in filenames:
                dest, local =  posixpath.join(upload_path, f), os.path.join(root, f)
                path = ArtifactoryPath( 
                self.jfrog_endpoint_url + '/'
                + dest,
                **self.auth,
                )
                path.deploy_file(local)
        
    
    def list_artifacts(self, path=None):
        rname, dest_path = self.parse_artifactory_uri(self.artifact_uri)
        if path:
            dest_path = posixpath.join(rname, dest_path, path)
        else:
            dest_path = posixpath.join(rname, dest_path)
            
        _path = ArtifactoryPath( 
                self.jfrog_endpoint_url + '/'
                + dest_path,
                **self.auth,
                )
        
        results = [FileInfo(p.as_posix(),
                            p.is_dir(),
                            sys.getsizeof(p.read_bytes()))
                            for p in _path.glob("**/*")]
        
        return results
    
    def _download_file(self, remote_file_path, local_path):
        rname, dest_path = self.parse_artifactory_uri(self.artifact_uri)
        dest_path = posixpath.join(rname, dest_path, remote_file_path)
        _path = ArtifactoryPath( 
                self.jfrog_endpoint_url + '/'
                + dest_path,
                **self.auth,
                )

        with _path.open() as fd:
            with open(local_path, "wb") as out:
                out.write(fd.read())
 
    
    def delete_artifacts(self, artifact_path=None):
        raise MlflowException('Not implemented yet')