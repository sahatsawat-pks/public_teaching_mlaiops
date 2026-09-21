"""Lab 5 — compile pipeline/pipeline.yaml into your provider's pipeline service.

This module is Layer 3, so provider SDKs are allowed here and nowhere else. The DAG stays
in YAML; only the translation lives here. That separation is what you argue for or against
in Lab 5 Task 4.

Implement ONE compile function, for your provider.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

SPEC = Path(__file__).resolve().parents[1] / "pipeline" / "pipeline.yaml"


def load_spec(path: Path = SPEC) -> dict[str, Any]:
    """Read the neutral DAG and expand ${VAR} references from the environment."""
    raw = path.read_text()
    for key, value in os.environ.items():
        raw = raw.replace(f"${{{key}}}", value)
    return yaml.safe_load(raw)


def compile_aws(spec: dict[str, Any]):
    """SageMaker Pipelines.

    Each step becomes a ProcessingStep or TrainingStep; `condition` becomes a
    ConditionStep. Note that SageMaker's condition steps branch rather than abort, so
    `on_failure: abort` needs a FailStep on the else branch — an asymmetry worth
    mentioning in your Lab 5 write-up.
    """
    raise NotImplementedError("TODO Lab 5: build a sagemaker.workflow.pipeline.Pipeline")


def compile_azure(spec: dict[str, Any]):
    """Azure ML Pipelines.

    Each step becomes a command component; the DAG is expressed as a @pipeline function.
    Conditions use azure.ai.ml.dsl.condition, which is closer to this YAML than the other
    two providers' equivalents.
    """
    raise NotImplementedError("TODO Lab 5: build an azure.ai.ml pipeline job")


def compile_gcp(spec: dict[str, Any]) -> Path:
    """Vertex AI Pipelines.

    Translates the neutral YAML DAG into a Vertex AI Pipelines (Kubeflow Pipelines v2)
    JSON specification. Each step becomes a containerised task executor, and condition
    expressions gate model registration.
    """
    import json
    from src import config

    cfg = config.load(strict=False)

    # 1. Expand environment/config variables
    defaults = {
        "CONTAINER_REGISTRY": cfg.container_registry,
        "IMAGE_TAG": getattr(cfg, "git_commit", "latest") or "latest",
        "TRAIN_INSTANCE": "n1-standard-4",
        "PROJECT_ID": cfg.project_id,
    }

    pipeline_name = spec.get("name", "itcs355-training-pipeline")
    schedule = spec.get("schedule", "0 2 * * 0")
    steps = spec.get("steps", [])

    # 2. Build Vertex AI / KFP v2 Pipeline Specification
    executors: dict[str, Any] = {}
    components: dict[str, Any] = {}
    tasks: dict[str, Any] = {}

    for step in steps:
        name = step["name"]
        raw_image = step.get("image", "")
        for k, v in defaults.items():
            raw_image = raw_image.replace(f"${{{k}}}", str(v))

        command = step.get("command", [])
        depends_on = step.get("depends_on", [])
        condition = step.get("condition")
        instance = step.get("instance", "")
        for k, v in defaults.items():
            instance = instance.replace(f"${{{k}}}", str(v))

        # Executor specification
        exec_id = f"exec-{name}"
        exec_def: dict[str, Any] = {
            "container": {
                "image": raw_image,
                "command": command,
            }
        }
        if instance:
            exec_def["container"]["resources"] = {
                "machineType": instance,
            }
        executors[exec_id] = exec_def

        # Component specification
        comp_id = f"comp-{name}"
        components[comp_id] = {
            "executorLabel": exec_id,
        }

        # DAG Task specification
        task_def: dict[str, Any] = {
            "taskInfo": {"name": name},
            "componentRef": {"name": comp_id},
        }
        if depends_on:
            task_def["dependentTasks"] = [f"task-{d}" for d in depends_on]
        if condition:
            task_def["triggerPolicy"] = {
                "condition": condition,
                "strategy": "TRIGGER_WHEN_ALL_PREDICATES_MET",
            }
        tasks[f"task-{name}"] = task_def

    pipeline_spec = {
        "pipelineSpec": {
            "pipelineInfo": {
                "name": pipeline_name,
                "description": "ITCS355 managed training and evaluation pipeline",
            },
            "root": {
                "dag": {
                    "tasks": tasks,
                }
            },
            "components": components,
            "deploymentSpec": {
                "executors": executors,
            },
        },
        "labels": {
            "course": "itcs355",
            "student": cfg.project_id,
            "lab": "5",
        },
        "schedule": schedule,
    }

    # 3. Write compiled artifact
    out_dir = Path(SPEC).parent
    out_path = out_dir / "pipeline-gcp.json"
    out_path.write_text(json.dumps(pipeline_spec, indent=2))

    # Also write to reports/ for artifact submission
    reports_path = Path(__file__).resolve().parents[1] / "reports" / "pipeline-gcp.json"
    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text(json.dumps(pipeline_spec, indent=2))

    print(f"Compiled Vertex AI Pipeline: {out_path}")
    print(f"  Pipeline:   {pipeline_name}")
    print(f"  Schedule:   {schedule}")
    print(f"  Steps ({len(steps)}): {', '.join(s['name'] for s in steps)}")
    print('  Condition:  register step gated on condition "gate_decision == \'pass\'"')

    return out_path


COMPILERS = {"aws": compile_aws, "azure": compile_azure, "gcp": compile_gcp}


def compile_for(provider: str, spec: dict[str, Any] | None = None):
    spec = spec or load_spec()
    try:
        return COMPILERS[provider.lower()](spec)
    except KeyError:
        raise ValueError(f"No pipeline compiler for {provider!r}") from None
