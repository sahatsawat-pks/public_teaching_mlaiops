"""GCP adapter. Implement upload/download/push_image for Lab 1.

SDK:  pip install google-cloud-storage google-cloud-aiplatform
Docs: storage.Client for GCS; Artifact Registry push goes through `docker push` after
      `gcloud auth configure-docker <region>-docker.pkg.dev`.

Hints for Lab 1:
  * BLOB_URI looks like gs://bucket/prefix — parse it here, never in src/.
  * Artifact Registry paths are region-scoped:
        <region>-docker.pkg.dev/<project>/<repo>/<image>
    A common first failure is pushing to gcr.io out of habit; it is a different service.
  * push_image must return the digest reference, not the tag.
  * GCP calls them labels, not tags, and they must be lowercase with no spaces.
    cfg.tags(1) already satisfies that constraint — do not "improve" the values.
"""
from __future__ import annotations

from typing import Any

from cloudlayer.base import CloudAdapter


class GcpAdapter(CloudAdapter):
    def upload(self, local_path: str, key: str) -> str:
        from urllib.parse import urlparse
        from google.cloud import storage

        parsed = urlparse(self.cfg.blob_uri)
        bucket_name = parsed.netloc
        prefix = parsed.path.strip("/")
        blob_name = f"{prefix}/{key.lstrip('/')}" if prefix else key.lstrip("/")

        client = storage.Client(project=self.cfg.project_id if self.cfg.project_id != "unset" else None)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        return f"gs://{bucket_name}/{blob_name}"

    def download(self, uri: str, local_path: str) -> None:
        from pathlib import Path
        from urllib.parse import urlparse
        from google.cloud import storage

        parsed = urlparse(uri)
        bucket_name = parsed.netloc
        blob_name = parsed.path.lstrip("/")

        dest = Path(local_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        client = storage.Client(project=self.cfg.project_id if self.cfg.project_id != "unset" else None)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(str(dest))

    def push_image(self, local_tag: str) -> str:
        import json
        import subprocess

        registry = self.cfg.container_registry.rstrip("/")
        remote_tag = f"{registry}/{local_tag}"

        # Configure Docker authentication for Artifact Registry
        registry_host = registry.split("/")[0]
        if registry_host:
            subprocess.run(
                ["gcloud", "auth", "configure-docker", registry_host, "--quiet"],
                check=False,
            )

        # Tag and push the container image
        subprocess.run(["docker", "tag", local_tag, remote_tag], check=True)
        subprocess.run(["docker", "push", remote_tag], check=True)

        # Retrieve the digest reference (repo@sha256:...)
        res = subprocess.run(
            ["docker", "inspect", "--format={{index .RepoDigests 0}}", remote_tag],
            capture_output=True,
            text=True,
            check=True,
        )
        digest = res.stdout.strip()
        if not digest:
            res = subprocess.run(
                ["docker", "inspect", "--format={{json .RepoDigests}}", remote_tag],
                capture_output=True,
                text=True,
                check=True,
            )
            digests = json.loads(res.stdout.strip() or "[]")
            for d in digests:
                if d.startswith(remote_tag.split(":")[0]):
                    digest = d
                    break
            if not digest and digests:
                digest = digests[0]

        return digest

    # submit_training / register_model  -> Lab 2 (Vertex custom training + Model Registry)
    # deploy / invoke                   -> Lab 3 (Vertex Endpoint)
    # emit_metric                       -> Lab 4 (Cloud Monitoring time series)
    # generate                          -> Lab 5 (managed LLM endpoint; read usageMetadata for tokens)
    # teardown                          -> Lab 5 (filter resources by label)
