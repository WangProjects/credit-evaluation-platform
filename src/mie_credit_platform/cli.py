from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from mie_credit_platform.governance.registry import approve_model, list_models
from mie_credit_platform.modeling.train import TrainConfig, train_baseline_logreg
from mie_credit_platform.settings import get_settings


app = typer.Typer(help="MIE Credit Platform CLI (training, registry, governance).")


@app.command()
def train(
    out: str = typer.Option("models", help="Model registry output directory."),
    version: str = typer.Option("v0.1.0", help="Model version string."),
    n: int = typer.Option(8000, help="Number of synthetic rows (demo only)."),
    seed: int = typer.Option(7, help="Random seed."),
) -> None:
    """
    Train a demo baseline model on synthetic data and write a versioned model package.
    """

    res = train_baseline_logreg(TrainConfig(version=version, registry_dir=out, n_synth=n, seed=seed))
    typer.echo(json.dumps(res, indent=2))


@app.command("list-models")
def list_models_cmd(registry_dir: Optional[str] = typer.Option(None, help="Registry directory.")) -> None:
    settings = get_settings()
    d = registry_dir or settings.model_registry_dir
    models = list_models(d)
    typer.echo(json.dumps([m.__dict__ for m in models], indent=2))


@app.command("approve-model")
def approve_model_cmd(
    version: str = typer.Argument(..., help="Model version to approve."),
    registry_dir: Optional[str] = typer.Option(None, help="Registry directory."),
    approved: bool = typer.Option(True, help="Set approved true/false."),
) -> None:
    settings = get_settings()
    d = registry_dir or settings.model_registry_dir
    approve_model(d, version, approved=approved)
    typer.echo(json.dumps({"version": version, "approved": approved, "registry_dir": d}, indent=2))


@app.command("show-model-card")
def show_model_card(
    version: str = typer.Argument(..., help="Model version."),
    registry_dir: Optional[str] = typer.Option(None, help="Registry directory."),
) -> None:
    settings = get_settings()
    d = Path(registry_dir or settings.model_registry_dir) / version / "model_card.md"
    if not d.exists():
        raise typer.Exit(code=2)
    typer.echo(d.read_text(encoding="utf-8"))


