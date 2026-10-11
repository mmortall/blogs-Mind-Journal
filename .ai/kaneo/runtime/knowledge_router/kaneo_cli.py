"""CLI for safe, repository-scoped Kaneo work management."""

from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import nullcontext
from pathlib import Path

from .kaneo import (
    KaneoClient,
    KaneoError,
    RepoBinding,
    direct_child_completion_audit,
    finish_managed_parent,
    finish_repo_work,
    project_health,
    reconcile,
    snapshot,
    start_repo_work,
    validate_snapshot,
)


def resolve_workspace_config(repo_root: Path, explicit: Path | None = None) -> Path:
    """Find central workspace map from any managed repository."""
    if explicit is not None:
        if explicit.is_file():
            return explicit.resolve()
        raise KaneoError(f"Workspace config not found: {explicit}")

    candidates = [
        repo_root.resolve() / "config" / "kaneo-workspaces.yaml",
        Path(__file__).resolve().parent.parent / "config" / "kaneo-workspaces.yaml",
    ]
    configured_root = os.getenv("KNOWLEDGE_ROOT_PLATFORM")
    if configured_root:
        candidates.append(
            Path(configured_root).resolve() / "config" / "kaneo-workspaces.yaml"
        )
    candidates.extend(
        [
            Path(sys.executable).resolve().parent.parent
            / "config"
            / "kaneo-workspaces.yaml",
            Path(__file__).resolve().parents[3]
            / "config"
            / "kaneo-workspaces.yaml",
        ]
    )
    checked: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in checked:
            continue
        checked.append(resolved)
        if resolved.is_file():
            return resolved
    raise KaneoError(
        "Workspace config not found; checked: " + ", ".join(str(path) for path in checked)
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="kaneo-workflow")
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    commands = result.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--outcome", required=True)
    start.add_argument("--area")
    start.add_argument("--goal", help="Explicit task goal; defaults to --outcome")
    start.add_argument(
        "--acceptance-criteria",
        help="Explicit non-empty acceptance criteria; defaults to canonical evidence rule",
    )
    start.add_argument("--apply", action="store_true")
    finish = commands.add_parser("finish")
    finish.add_argument("--task-id", required=True)
    finish.add_argument("--changed", action="append", default=[])
    finish.add_argument("--validation", action="append", default=[])
    finish.add_argument("--remaining", default="none")
    finish.add_argument(
        "--completion-summary",
        help="Explicit one-line completion summary; defaults to changed/validation evidence",
    )
    finish.add_argument("--apply", action="store_true")
    assign = commands.add_parser("assign")
    assign.add_argument("--task-id", required=True)
    assign.add_argument("--user-id", required=True)
    assign.add_argument("--apply", action="store_true")
    commands.add_parser("health")
    hierarchy = commands.add_parser("task-hierarchy")
    hierarchy_target = hierarchy.add_mutually_exclusive_group(required=True)
    hierarchy_target.add_argument("--task-id")
    hierarchy_target.add_argument("--task-number", type=int)
    hierarchy.add_argument("--max-children", type=int, default=100)
    hierarchy.add_argument("--max-pages", type=int, default=16)
    hierarchy.add_argument("--deadline-seconds", type=int, default=60)
    finish_parent = commands.add_parser("finish-parent")
    finish_parent.add_argument("--task-id", required=True)
    finish_parent.add_argument("--completion-summary")
    finish_parent.add_argument("--apply", action="store_true")
    capture = commands.add_parser("snapshot")
    capture.add_argument("--workspace-config", type=Path)
    capture.add_argument("--output", type=Path)
    capture.add_argument("--all-workspaces", action="store_true")
    capture.add_argument("--workers", type=int, default=8)
    capture.add_argument("--max-pages", type=int, default=8)
    capture.add_argument("--max-tasks", type=int, default=2000)
    capture.add_argument("--deadline-seconds", type=int, default=120)
    reconcile_command = commands.add_parser("reconcile")
    reconcile_command.add_argument("--workspace-config", type=Path)
    reconcile_command.add_argument("--plan", type=Path, required=True)
    reconcile_command.add_argument("--apply", action="store_true")
    validate = commands.add_parser("validate-snapshot")
    validate.add_argument("--input", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    try:
        if args.command == "validate-snapshot":
            output = validate_snapshot(json.loads(args.input.read_text(encoding="utf-8")))
            code = 0 if output["valid"] else 1
        elif args.command in {"snapshot", "reconcile"}:
            config = resolve_workspace_config(
                args.repo_root, getattr(args, "workspace_config", None),
            )
            endpoint = json.loads(config.read_text(encoding="utf-8"))["api_endpoint"]
            client = KaneoClient(endpoint)
            if args.command == "reconcile":
                plan = json.loads(args.plan.read_text(encoding="utf-8"))
                output = reconcile(client, plan, apply=args.apply)
            else:
                binding = None if args.all_workspaces else RepoBinding.load(
                    args.repo_root.resolve()
                )
                output = snapshot(
                    client, config, binding=binding, max_workers=args.workers,
                    max_pages=args.max_pages, max_tasks=args.max_tasks,
                    deadline_seconds=args.deadline_seconds,
                    progress=lambda message: print(f"snapshot: {message}", file=sys.stderr),
                )
            if args.command == "snapshot" and args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                output = {
                    "captured_at": output["captured_at"], "scope": output["scope"],
                    "output": str(args.output.resolve()),
                }
            code = 0
        else:
            binding = RepoBinding.load(args.repo_root.resolve())
            client = KaneoClient(binding.api_endpoint)
            if args.command == "health":
                output = project_health(client, binding)
            elif args.command == "task-hierarchy":
                lookup_deadline = (
                    client.deadline(args.deadline_seconds)
                    if args.task_number is not None and hasattr(client, "deadline")
                    else nullcontext()
                )
                with lookup_deadline:
                    task_id = args.task_id
                    if args.task_number is not None:
                        task_id = client.find_task_by_number(
                            binding.project_id, args.task_number, max_pages=args.max_pages,
                        )["id"]
                    output = direct_child_completion_audit(
                        client, binding, task_id, max_children=args.max_children,
                        deadline_seconds=args.deadline_seconds,
                    )
            elif args.command == "finish-parent":
                output = finish_managed_parent(
                    client, binding, args.task_id,
                    completion_summary=args.completion_summary, apply=args.apply,
                )
            elif args.command == "start":
                output = start_repo_work(
                    client, binding, outcome=args.outcome, area=args.area, goal=args.goal,
                    acceptance_criteria=args.acceptance_criteria, apply=args.apply,
                )
            elif args.command == "assign":
                if not args.apply:
                    output = {
                        "applied": False,
                        "task_id": args.task_id,
                        "user_id": args.user_id,
                    }
                else:
                    task = client.update_assignee(args.task_id, args.user_id)
                    output = {
                        "applied": True,
                        "task_id": task["id"],
                        "user_id": task.get("userId"),
                        "assignee_name": task.get("assigneeName"),
                    }
            else:
                output = finish_repo_work(
                    client, binding, args.task_id, changed=args.changed, validation=args.validation,
                    remaining=args.remaining, completion_summary=args.completion_summary,
                    apply=args.apply,
                )
            code = 0
    except (KaneoError, OSError, ValueError, KeyError) as exc:
        output, code = {"error": type(exc).__name__, "message": str(exc)}, 2
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
