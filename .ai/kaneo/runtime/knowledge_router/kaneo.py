"""Small, idempotent Kaneo client used by repository agents.

Kaneo is the work-state plane.  This module deliberately knows nothing about
research truth: descriptions contain stable repository references, while code,
tests, ledgers, and artifacts remain canonical.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import threading
import time
from contextlib import contextmanager, nullcontext
from email.utils import parsedate_to_datetime
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


PRIORITIES = {"no-priority", "low", "medium", "high", "urgent"}
MANAGED_MARKER = re.compile(r"<!-- kaneo-managed:(\{.*?\}) -->")
MANAGED_MARKER_TOKEN = "<!-- kaneo-managed:"
COMPLETION_EVIDENCE_PREFIX = "Result: completed\n\nChanged:\n"
DEFAULT_ACCEPTANCE_CRITERIA = (
    "Canonical output and validation evidence are recorded before completion."
)
TLS_CERTIFICATE_RETRY_DELAYS = (0.25, 0.5)
READ_RETRY_DELAYS = (0.25, 0.5)
# HTTP statuses that may succeed on replay.  429/503 carry Retry-After; 502/530
# are Cloudflare edge/origin failures.  401/403 are never retried.
RETRYABLE_HTTP_STATUSES = frozenset({429, 502, 503, 530})
RETRY_AFTER_STATUSES = frozenset({429, 503})
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})
# Without an operation deadline a server-requested wait longer than this fails.
MAX_RETRY_AFTER_SECONDS = 30.0
CAPABILITIES_PATH = "/task/agent/capabilities"
EXPORT_PAGE_LIMIT = 100
# Legacy list pages hold 250 tasks; paged exports hold 100.  Page bounds stay in
# task units so ``--max-pages`` keeps the same coverage on both routes.
LEGACY_TASK_PAGE_SIZE = 250
CONTEXT_PAGE_LIMIT = 100
CONTEXT_MAX_PAGES = 16
CAPABILITY_FALLBACKS = {
    "managedPreview": "dry-run start scans the project task list",
    "taskRevisions": "task edits use legacy field endpoints without a caller version",
    "relationIdempotency": "comment and relation creation is sent without an idempotency key",
    "pagedExports": "snapshot lists tasks through legacy board pages",
    "projectRelationExports": "snapshot reads relations once per task",
    "taskContext": "task context reads relations once per hierarchy level",
}


class KaneoError(RuntimeError):
    """Raised when Kaneo configuration or read-back validation fails."""


class KaneoHTTPError(KaneoError):
    """Kaneo answered with an HTTP error status."""

    def __init__(self, message: str, *, status: int, body: str = "") -> None:
        super().__init__(message)
        self.status = status
        self.body = body


def retry_after_seconds(value: str | None, *, now: datetime | None = None) -> float | None:
    """Parse numeric or HTTP-date Retry-After into non-negative seconds."""
    if value is None or not value.strip():
        return None
    text = value.strip()
    try:
        seconds = float(text)
    except ValueError:
        try:
            moment = parsedate_to_datetime(text)
        except (TypeError, ValueError, IndexError):
            return None
        if moment is None:
            return None
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        seconds = (moment - (now or datetime.now(timezone.utc))).total_seconds()
    if seconds != seconds:  # NaN
        return None
    return max(0.0, seconds)


def _policy_text(value: str | None, fallback: str, label: str) -> str:
    """Normalize required task-policy fields before a remote write."""
    result = (value if value is not None else fallback).strip()
    if not result:
        raise KaneoError(f"{label} must not be empty")
    if "\n" in result or "\r" in result:
        raise KaneoError(f"{label} must be one non-empty line")
    return result

def _is_transient_expired_tls_certificate(error: BaseException) -> bool:
    """Return whether a Cloudflare edge may have served an expired TLS chain."""
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    return (
        isinstance(reason, ssl.SSLCertVerificationError)
        and "certificate has expired" in str(reason).lower()
    )


def _is_transient_read_failure(error: BaseException) -> bool:
    """Return whether an idempotent Kaneo read lost its TCP connection."""
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    return isinstance(reason, (ConnectionResetError, TimeoutError))


@dataclass(frozen=True)
class RepoBinding:
    """Structured repository-to-Kaneo binding."""

    space_id: str
    workspace_id: str
    project_id: str
    project_name: str
    api_endpoint: str
    default_area: str
    epic_key: str | None = None
    epic_title: str | None = None

    @classmethod
    def load(cls, repo_root: Path) -> "RepoBinding":
        path = repo_root / ".ai" / "kaneo" / "config.json"
        if not path.is_file():
            raise KaneoError(f"Missing structured Kaneo binding: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        required = ("space_id", "workspace_id", "project_id", "project_name", "api_endpoint")
        missing = [name for name in required if not data.get(name)]
        if missing:
            raise KaneoError(f"Incomplete Kaneo binding {path}: {', '.join(missing)}")
        return cls(
            space_id=data["space_id"],
            workspace_id=data["workspace_id"],
            project_id=data["project_id"],
            project_name=data["project_name"],
            api_endpoint=data["api_endpoint"].rstrip("/"),
            default_area=data.get("default_area", "delivery"),
            epic_key=data.get("epic_key"),
            epic_title=data.get("epic_title"),
        )


class KaneoClient:
    """Authenticated JSON client with explicit read-back helpers."""

    def __init__(
        self, api_endpoint: str, *, timeout: int = 30,
        notice: Callable[[str], None] | None = None,
    ) -> None:
        names = ("KANEO_API_KEY", "CF_ACCESS_CLIENT_ID", "CF_ACCESS_CLIENT_SECRET")
        missing = [name for name in names if not os.getenv(name)]
        if missing:
            raise KaneoError(f"Missing Kaneo environment variables: {', '.join(missing)}")
        self.api_endpoint = api_endpoint.rstrip("/")
        self.timeout = timeout
        self._deadline_at: float | None = None
        self._capabilities: dict[str, Any] | None = None
        self._capability_lock = threading.Lock()
        self._notice = notice
        self.notices: list[str] = []
        self.headers = {
            "Authorization": f"Bearer {os.environ['KANEO_API_KEY']}",
            "CF-Access-Client-Id": os.environ["CF_ACCESS_CLIENT_ID"],
            "CF-Access-Client-Secret": os.environ["CF_ACCESS_CLIENT_SECRET"],
            "Accept": "application/json",
            "User-Agent": "Global-Knowledge-Kaneo/1.0",
        }

    @contextmanager
    def deadline(self, seconds: int):
        """Bound all nested requests, including concurrent snapshot hydration."""
        previous = self._deadline_at
        requested = time.monotonic() + seconds
        self._deadline_at = min(previous, requested) if previous is not None else requested
        try:
            yield
        finally:
            self._deadline_at = previous

    def _http_retry_wait(
        self, method: str, keyed: bool, status: int, retry_after: str | None,
        delay: float | None,
    ) -> float | None:
        """Return the wait before replaying an HTTP failure, or None to fail now.

        Only idempotent methods and requests carrying an Idempotency-Key are
        replayed; an unkeyed POST/PATCH is never sent twice.  A server
        Retry-After that does not fit inside the operation deadline fails fast.
        """
        if delay is None or status not in RETRYABLE_HTTP_STATUSES:
            return None
        if method not in IDEMPOTENT_METHODS and not keyed:
            return None
        wait = delay
        if status in RETRY_AFTER_STATUSES:
            requested = retry_after_seconds(retry_after)
            if requested is not None:
                wait = requested
        limit = MAX_RETRY_AFTER_SECONDS
        if self._deadline_at is not None:
            # Keep at least one second for the replayed request itself.
            limit = min(limit, self._deadline_at - time.monotonic() - 1)
        if wait > limit:
            return None
        return wait

    def request(
        self, method: str, path: str, body: dict[str, Any] | None = None, *,
        idempotency_key: str | None = None,
    ) -> Any:
        headers = dict(self.headers)
        payload = None
        if body is not None:
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key
        request = urllib.request.Request(
            f"{self.api_endpoint}{path}", data=payload, headers=headers, method=method
        )
        for delay in (*READ_RETRY_DELAYS, None):
            try:
                timeout = self.timeout
                if self._deadline_at is not None:
                    remaining = self._deadline_at - time.monotonic()
                    if remaining <= 0:
                        raise KaneoError("Kaneo operation deadline exceeded")
                    timeout = min(timeout, max(1, int(remaining)))
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    raw = response.read()
                    return json.loads(raw.decode("utf-8")) if raw else None
            except urllib.error.HTTPError as exc:
                detail = exc.read(1000).decode("utf-8", errors="replace")
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                wait = self._http_retry_wait(
                    method, idempotency_key is not None, exc.code, retry_after, delay,
                )
                if wait is not None:
                    time.sleep(wait)
                    continue
                raise KaneoHTTPError(
                    f"Kaneo {method} {path} failed: HTTP {exc.code}: {detail}",
                    status=exc.code, body=detail,
                ) from exc
            except (urllib.error.URLError, ssl.SSLCertVerificationError) as exc:
                retryable = _is_transient_expired_tls_certificate(exc) or (
                    method == "GET" and _is_transient_read_failure(exc)
                )
                if delay is not None and retryable:
                    time.sleep(delay)
                    continue
                raise KaneoError(f"Kaneo {method} {path} failed: {exc}") from exc
            except (OSError, ValueError) as exc:
                raise KaneoError(f"Kaneo {method} {path} failed: {exc}") from exc

    def capabilities(self) -> dict[str, Any]:
        """Read ``/task/agent/capabilities`` once per client.

        A server without the agent router (legacy fork) answers 404; that is
        cached as an empty capability set so every feature takes its fallback.
        """
        with self._capability_lock:
            if self._capabilities is None:
                try:
                    payload = self.request("GET", CAPABILITIES_PATH)
                except KaneoHTTPError as exc:
                    if exc.status != 404:
                        raise
                    payload = {}
                self._capabilities = payload if isinstance(payload, dict) else {}
            return self._capabilities

    def supports(self, feature: str) -> bool:
        """Return whether the server advertises one capability as true."""
        return self.capabilities().get(feature) is True

    def require(self, feature: str) -> bool:
        """Return support; on absence record one visible fallback notice.

        The notice names the feature, the fallback and the endpoint only; it
        never contains request headers or credentials.
        """
        if self.supports(feature):
            return True
        fallback = CAPABILITY_FALLBACKS.get(feature, "legacy behaviour is used")
        message = (
            f"Kaneo capability {feature!r} is not advertised by {self.api_endpoint}; "
            f"fallback: {fallback}"
        )
        self.note(message)
        return False

    def note(self, message: str) -> None:
        """Record one fallback notice and show it through the notice callback once."""
        with self._capability_lock:
            if message in self.notices:
                return
            self.notices.append(message)
        if self._notice is not None:
            self._notice(message)

    def export_task_pages(
        self, project_id: str, *, max_tasks: int | None = None,
        max_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        """Read every project task identity through cursor-paged export.

        Requires ``pagedExports``.  ``max_pages`` counts legacy 250-task pages
        and ``max_tasks`` caps the result; both fail closed before returning a
        partial list.  Rows carry id, version, number, title, status, workItemType,
        projectId, goal, acceptanceCriteria and completionSummary, among others.
        """
        task_limit = None if max_pages is None else max_pages * LEGACY_TASK_PAGE_SIZE
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        cursor: str | None = None
        while True:
            query = {"limit": EXPORT_PAGE_LIMIT}
            if cursor:
                query["cursor"] = cursor
            payload = self.request(
                "GET",
                f"/task/agent/export/{urllib.parse.quote(project_id, safe='')}?"
                f"{urllib.parse.urlencode(query)}",
            )
            page = payload.get("tasks") if isinstance(payload, dict) else None
            if not isinstance(page, list):
                raise KaneoError(f"Invalid Kaneo task export response: {project_id}")
            for row in page:
                if not isinstance(row, dict) or not row.get("id"):
                    raise KaneoError(f"Kaneo task export row lacks id: {project_id}")
                if row["id"] not in seen:
                    seen.add(row["id"])
                    rows.append(row)
            if task_limit is not None and len(rows) > task_limit:
                raise KaneoError(
                    f"Kaneo task pagination limit exceeded for {project_id}: {max_pages} pages"
                )
            if max_tasks is not None and len(rows) > max_tasks:
                raise KaneoError(
                    f"Kaneo export task limit exceeded for {project_id}: {len(rows)} > {max_tasks}"
                )
            next_cursor = (payload.get("pagination") or {}).get("nextCursor")
            if not next_cursor:
                return rows
            if next_cursor == cursor:
                raise KaneoError(f"Kaneo task export cursor did not advance: {project_id}")
            cursor = str(next_cursor)

    def export_relations(
        self, project_id: str, *, max_relations: int | None = None,
    ) -> list[dict[str, Any]]:
        """Read every relation touching one project once, cursor-paged.

        Requires ``projectRelationExports``.  Rows carry id, sourceTaskId,
        targetTaskId, relationType and createdAt; both endpoints are in the
        caller's workspace.
        """
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        cursor: str | None = None
        while True:
            query = {"limit": EXPORT_PAGE_LIMIT}
            if cursor:
                query["cursor"] = cursor
            payload = self.request(
                "GET",
                f"/task/agent/relation-export/{urllib.parse.quote(project_id, safe='')}?"
                f"{urllib.parse.urlencode(query)}",
            )
            page = payload.get("relations") if isinstance(payload, dict) else None
            if not isinstance(page, list):
                raise KaneoError(f"Invalid Kaneo relation export response: {project_id}")
            for row in page:
                if not isinstance(row, dict) or not row.get("id"):
                    raise KaneoError(f"Kaneo relation export row lacks id: {project_id}")
                if row["id"] not in seen:
                    seen.add(row["id"])
                    rows.append(row)
            if max_relations is not None and len(rows) > max_relations:
                raise KaneoError(
                    f"Kaneo relation export limit exceeded for {project_id}: "
                    f"{len(rows)} > {max_relations}"
                )
            next_cursor = (payload.get("pagination") or {}).get("nextCursor")
            if not next_cursor:
                return rows
            if next_cursor == cursor:
                raise KaneoError(f"Kaneo relation export cursor did not advance: {project_id}")
            cursor = str(next_cursor)

    def task_context_relations(
        self, task_id: str, *, max_pages: int = CONTEXT_MAX_PAGES,
    ) -> dict[str, Any]:
        """Read one task's relations and ancestor chain through ``/task/agent/context``.

        Requires ``taskContext``.  Relation pages are followed up to ``max_pages``;
        a longer list fails closed instead of returning a partial context.
        """
        relations: list[dict[str, Any]] = []
        ancestors: list[str] | None = None
        page = 1
        while True:
            if page > max_pages:
                raise KaneoError(f"Kaneo task context page limit exceeded for {task_id}: {max_pages}")
            payload = self.request(
                "GET",
                f"/task/agent/context/{urllib.parse.quote(task_id, safe='')}?"
                f"{urllib.parse.urlencode({'page': page, 'limit': CONTEXT_PAGE_LIMIT})}",
            )
            if not isinstance(payload, dict) or not isinstance(payload.get("relations"), list):
                raise KaneoError(f"Invalid Kaneo task context response: {task_id}")
            relations.extend(payload["relations"])
            if ancestors is None:
                ancestors = list(payload.get("ancestor_ids") or [])
            if not (payload.get("pagination") or {}).get("hasMore"):
                return {"relations": relations, "ancestor_ids": ancestors}
            page += 1

    def _revisioned_update(
        self, task_id: str, fields: dict[str, Any], version: int | None,
    ) -> bool:
        """Send one versioned field patch when the server supports revisions.

        Returns False when ``taskRevisions`` is not advertised so the caller uses
        the legacy endpoint.  A 409 means the remote task changed after the
        caller read it: the error is raised as is, without re-reading or
        re-sending, so newer remote fields are never overwritten.
        """
        if not self.require("taskRevisions"):
            return False
        expected = version
        if expected is None:
            expected = self.get_task(task_id).get("version")
        if type(expected) is not int or expected < 1:
            raise KaneoError(f"Task revision unavailable for {task_id}; cannot send a versioned edit")
        body = {"expectedVersion": expected, **fields}
        digest = hashlib.sha256(
            json.dumps([task_id, body], sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:48]
        try:
            self.request(
                "PATCH", f"/task/agent/{urllib.parse.quote(task_id, safe='')}", body,
                idempotency_key=f"edit:{digest}",
            )
        except KaneoHTTPError as exc:
            if exc.status != 409:
                raise
            current = None
            try:
                current = json.loads(exc.body).get("currentVersion")
            except (ValueError, AttributeError):
                pass
            raise KaneoError(
                f"Stale task revision for {task_id}: sent version {expected}, "
                f"server has {current if current is not None else 'a newer version'}; "
                "re-read the task before editing"
            ) from exc
        return True

    def list_projects(self, workspace_id: str, *, include_archived: bool = True) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {"workspaceId": workspace_id, "includeArchived": str(include_archived).lower()}
        )
        result = self.request("GET", f"/project?{query}")
        return result.get("data", result) if isinstance(result, dict) else result

    def list_tasks(self, project_id: str, *, max_pages: int | None = None) -> list[dict[str, Any]]:
        tasks: dict[str, dict[str, Any]] = {}
        page = 1
        while True:
            if max_pages is not None and page > max_pages:
                raise KaneoError(
                    f"Kaneo task pagination limit exceeded for {project_id}: {max_pages} pages"
                )
            query = urllib.parse.urlencode(
                {"page": page, "limit": 250, "sortBy": "number", "sortOrder": "asc"}
            )
            payload = self.request(
                "GET", f"/task/tasks/{urllib.parse.quote(project_id, safe='')}?{query}"
            )
            data = payload.get("data", payload)
            for column in data.get("columns", []):
                for task in column.get("tasks", []):
                    tasks[task["id"]] = {**task, "status": task.get("status") or column.get("slug")}
            for status, field in (
                ("archived", "archivedTasks"),
                ("planned", "plannedTasks"),
                ("blocked", "blockedTasks"),
            ):
                for task in data.get(field, []):
                    tasks[task["id"]] = {**task, "status": task.get("status") or status}
            pagination = payload.get("pagination", {})
            if page >= int(pagination.get("totalPages", 1)):
                break
            page += 1
        return list(tasks.values())

    def find_task_by_number(
        self, project_id: str, number: int, *, max_pages: int | None = None,
    ) -> dict[str, Any]:
        """Find one project task by visible number without hydrating project backlog."""
        if number < 1:
            raise KaneoError("Task number must be positive")
        page = 1
        while True:
            if max_pages is not None and page > max_pages:
                raise KaneoError(
                    f"Kaneo task-number pagination limit exceeded for {project_id}: {max_pages} pages"
                )
            query = urllib.parse.urlencode(
                {"page": page, "limit": 250, "sortBy": "number", "sortOrder": "asc"}
            )
            payload = self.request(
                "GET", f"/task/tasks/{urllib.parse.quote(project_id, safe='')}?{query}"
            )
            data = payload.get("data", payload)
            rows = [
                task
                for column in data.get("columns", [])
                for task in column.get("tasks", [])
            ]
            rows.extend(data.get("archivedTasks", []))
            rows.extend(data.get("plannedTasks", []))
            rows.extend(data.get("blockedTasks", []))
            matches = [task for task in rows if task.get("number") == number]
            if len(matches) > 1:
                raise KaneoError(f"Ambiguous task number {number} in project {project_id}")
            if matches:
                return matches[0]
            if page >= int(payload.get("pagination", {}).get("totalPages", 1)):
                break
            page += 1
        raise KaneoError(f"Task number not found in project {project_id}: {number}")

    def get_task(self, task_id: str) -> dict[str, Any]:
        return self.request("GET", f"/task/{urllib.parse.quote(task_id, safe='')}")

    def create_task(
        self, project_id: str, title: str, description: str, *, status: str = "to-do",
        priority: str = "medium", work_item_type: str = "task",
        goal: str | None = None, acceptance_criteria: str | None = None,
    ) -> dict[str, Any]:
        if priority not in PRIORITIES:
            raise KaneoError(f"Invalid priority: {priority}")
        if work_item_type not in {"task", "epic", "sub_epic"}:
            raise KaneoError(f"Invalid work item type: {work_item_type}")
        task_goal = _policy_text(goal, title, "Goal")
        task_acceptance = _policy_text(
            acceptance_criteria, DEFAULT_ACCEPTANCE_CRITERIA, "Acceptance criteria"
        )
        created = self.request(
            "POST", f"/task/{urllib.parse.quote(project_id, safe='')}",
            {"title": title, "description": description, "priority": priority, "status": status,
             "workItemType": work_item_type, "goal": task_goal,
             "acceptanceCriteria": task_acceptance},
        )
        read_back = self.get_task(created["id"])
        if (read_back.get("title") != title or read_back.get("projectId") != project_id
                or read_back.get("workItemType") != work_item_type
                or read_back.get("goal") != task_goal
                or read_back.get("acceptanceCriteria") != task_acceptance):
            raise KaneoError(f"Task create read-back mismatch: {created.get('id')}")
        return read_back

    def update_status(
        self, task_id: str, status: str, *, completion_summary: str | None = None,
        goal: str | None = None, acceptance_criteria: str | None = None,
        version: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"status": status}
        if goal is not None:
            payload["goal"] = _policy_text(goal, "", "Goal")
        if acceptance_criteria is not None:
            payload["acceptanceCriteria"] = _policy_text(acceptance_criteria, "", "Acceptance criteria")
        if status == "done":
            payload["completionSummary"] = _policy_text(
                completion_summary, "Completion evidence is recorded.", "Completion summary"
            )
        if not self._revisioned_update(task_id, payload, version):
            self.request(
                "PUT", f"/task/status/{urllib.parse.quote(task_id, safe='')}", payload
            )
        read_back = self.get_task(task_id)
        if read_back.get("status") != status:
            raise KaneoError(f"Task status read-back mismatch: {task_id}")
        if status == "done" and read_back.get("completionSummary") != payload["completionSummary"]:
            raise KaneoError(f"Task completion summary read-back mismatch: {task_id}")
        return read_back

    def update_description(
        self, task_id: str, description: str, *, version: int | None = None,
    ) -> dict[str, Any]:
        """Update task description and verify exact persisted content."""
        if not self._revisioned_update(task_id, {"description": description}, version):
            self.request(
                "PUT", f"/task/description/{urllib.parse.quote(task_id, safe='')}",
                {"description": description},
            )
        read_back = self.get_task(task_id)
        if read_back.get("description") != description:
            raise KaneoError(f"Task description read-back mismatch: {task_id}")
        return read_back

    def update_title(
        self, task_id: str, title: str, *, version: int | None = None,
    ) -> dict[str, Any]:
        """Update task title and verify exact persisted content."""
        if not self._revisioned_update(task_id, {"title": title}, version):
            self.request(
                "PUT", f"/task/title/{urllib.parse.quote(task_id, safe='')}",
                {"title": title},
            )
        read_back = self.get_task(task_id)
        if read_back.get("title") != title:
            raise KaneoError(f"Task title read-back mismatch: {task_id}")
        return read_back

    def update_assignee(
        self, task_id: str, user_id: str | None, *, version: int | None = None,
    ) -> dict[str, Any]:
        """Assign a task and verify the exact persisted assignee."""
        if not self._revisioned_update(task_id, {"userId": user_id}, version):
            self.request(
                "PUT", f"/task/assignee/{urllib.parse.quote(task_id, safe='')}",
                {"userId": user_id},
            )
        read_back = self.get_task(task_id)
        if read_back.get("userId") != user_id:
            raise KaneoError(f"Task assignee read-back mismatch: {task_id}")
        return read_back

    def _operation_key(self, prefix: str, *parts: str) -> dict[str, str]:
        """Deterministic Idempotency-Key argument when ``relationIdempotency`` is advertised."""
        if not self.require("relationIdempotency"):
            return {}
        digest = hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()[:48]
        return {"idempotency_key": f"{prefix}:{digest}"}

    def create_comment(self, task_id: str, content: str) -> dict[str, Any]:
        # The key is derived from task and exact content: a replay after a lost
        # response returns the first comment instead of writing a duplicate.
        created = self.request(
            "POST", f"/comment/{urllib.parse.quote(task_id, safe='')}", {"content": content},
            **self._operation_key("comment", task_id, content),
        )
        rows = self.list_comments(task_id)
        if not any(item.get("id") == created.get("id") for item in rows):
            raise KaneoError(f"Task comment read-back mismatch: {task_id}")
        return created

    def list_comments(self, task_id: str) -> list[dict[str, Any]]:
        """Return task comments for idempotent evidence writes."""
        comments = self.request("GET", f"/comment/{urllib.parse.quote(task_id, safe='')}")
        rows = comments.get("data") if isinstance(comments, dict) else comments
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise KaneoError(f"Invalid Kaneo comments response: {task_id}")
        return rows

    def ensure_comment(self, task_id: str, content: str) -> dict[str, Any]:
        """Create one exact evidence comment or reuse its prior successful write."""
        matches = [
            comment for comment in self.list_comments(task_id)
            if comment.get("content") == content
        ]
        if len(matches) > 1:
            raise KaneoError(f"Duplicate exact task comments: {task_id}")
        return matches[0] if matches else self.create_comment(task_id, content)

    def completion_comment(self, task_id: str, content: str) -> dict[str, Any] | None:
        """Return one matching completion record and reject conflicting records."""
        completion = [
            comment for comment in self.list_comments(task_id)
            if isinstance(comment.get("content"), str)
            and comment["content"].startswith(COMPLETION_EVIDENCE_PREFIX)
        ]
        if len(completion) > 1:
            raise KaneoError(f"Multiple completion evidence comments: {task_id}")
        if completion and completion[0].get("content") != content:
            raise KaneoError(f"Completion evidence conflict: {task_id}")
        return completion[0] if completion else None

    def ensure_completion_comment(self, task_id: str, content: str) -> dict[str, Any]:
        """Persist exactly one immutable completion evidence record."""
        existing = self.completion_comment(task_id, content)
        if existing:
            return existing
        created = self.create_comment(task_id, content)
        read_back = self.completion_comment(task_id, content)
        if read_back is None or read_back.get("id") != created.get("id"):
            raise KaneoError(f"Completion evidence read-back mismatch: {task_id}")
        return read_back

    def relations(self, task_id: str) -> list[dict[str, Any]]:
        result = self.request("GET", f"/task-relation/{urllib.parse.quote(task_id, safe='')}")
        return result.get("data", result) if isinstance(result, dict) else result

    def ensure_relation(
        self, source_id: str, target_id: str, relation_type: str = "subtask",
    ) -> dict[str, Any]:
        """Create one typed relation and verify it from source endpoint."""
        if relation_type not in {"subtask", "related"}:
            raise KaneoError(f"Unsupported task relation type: {relation_type}")
        for relation in self.relations(target_id):
            if (
                relation.get("relationType") == relation_type
                and relation.get("sourceTaskId") == source_id
                and relation.get("targetTaskId") == target_id
            ):
                return relation
        created = self.request(
            "POST", "/task-relation",
            {"sourceTaskId": source_id, "targetTaskId": target_id,
             "relationType": relation_type},
            **self._operation_key("relation", source_id, target_id, relation_type),
        )
        if not any(item.get("id") == created.get("id") for item in self.relations(target_id)):
            raise KaneoError(f"Task relation read-back mismatch: {source_id} -> {target_id}")
        return created

    def delete_relation(self, relation_id: str) -> dict[str, Any]:
        """Delete one relation and verify it is absent from both endpoints."""
        result = self.request("DELETE", f"/task-relation/{urllib.parse.quote(relation_id, safe='')}")
        source_id = result.get("sourceTaskId")
        if source_id and any(item.get("id") == relation_id for item in self.relations(source_id)):
            raise KaneoError(f"Task relation delete read-back mismatch: {relation_id}")
        return result

    def archive_project(self, project_id: str) -> dict[str, Any]:
        result = self.request("PUT", f"/project/{urllib.parse.quote(project_id, safe='')}/archive")
        read_back = self.request("GET", f"/project/{urllib.parse.quote(project_id, safe='')}")
        if not read_back.get("archivedAt"):
            raise KaneoError(f"Project archive read-back mismatch: {project_id}")
        return result

    def get_project(self, project_id: str) -> dict[str, Any]:
        return self.request("GET", f"/project/{urllib.parse.quote(project_id, safe='')}")


def _expected_task(client: KaneoClient, task_id: str, project_id: str, title: str) -> dict[str, Any]:
    task = client.get_task(task_id)
    if task.get("projectId") != project_id or task.get("title") != title:
        raise KaneoError(
            f"Task identity mismatch for {task_id}: expected {project_id!r}/{title!r}, "
            f"got {task.get('projectId')!r}/{task.get('title')!r}"
        )
    return task


def reconcile(client: KaneoClient, plan: dict[str, Any], *, apply: bool = False) -> dict[str, Any]:
    """Apply exact, reversible cleanup and hierarchy plan.

    Every destructive target is checked by both stable ID and human-readable
    identity.  This prevents an old plan from touching a reused or moved item.
    """
    archive_items = plan.get("archive_tasks", [])
    archive_workers = plan.get("archive_workers", 1)
    if type(archive_workers) is not int or not 1 <= archive_workers <= 16:
        raise KaneoError("Archive workers must be integer between 1 and 16")
    archive_ids = [item["id"] for item in archive_items]
    if len(set(archive_ids)) != len(archive_ids):
        raise KaneoError("Archive plan contains duplicate task IDs")
    actions: list[dict[str, Any]] = []
    for relation in plan.get("delete_relations", []):
        rows = client.relations(relation["source_task_id"])
        current = next((row for row in rows if row.get("id") == relation["id"]), None)
        if current is None:
            actions.append({"action": "delete_relation", "id": relation["id"], "state": "already_absent"})
            continue
        for field in ("sourceTaskId", "targetTaskId"):
            expected = relation["source_task_id" if field == "sourceTaskId" else "target_task_id"]
            if current.get(field) != expected:
                raise KaneoError(f"Relation identity mismatch for {relation['id']}: {field}")
        if apply:
            client.delete_relation(relation["id"])
        actions.append({"action": "delete_relation", "id": relation["id"], "applied": apply})

    for item in plan.get("rename_tasks", []):
        task = client.get_task(item["id"])
        if task.get("projectId") != item["project_id"]:
            raise KaneoError(f"Task project mismatch for rename: {item['id']}")
        if task.get("title") == item["new_title"]:
            state = "already_renamed"
        elif task.get("title") != item["old_title"]:
            raise KaneoError(
                f"Task title mismatch for rename {item['id']}: expected "
                f"{item['old_title']!r}, got {task.get('title')!r}"
            )
        else:
            if apply:
                client.update_title(item["id"], item["new_title"], version=task.get("version"))
            state = "renamed" if apply else "would_rename"
        actions.append({"action": "rename_task", "id": item["id"], "state": state,
                        "old_title": item["old_title"], "new_title": item["new_title"],
                        "reason": item["reason"]})

    def archive_task(item: dict[str, Any]) -> dict[str, Any]:
        task = _expected_task(client, item["id"], item["project_id"], item["title"])
        if task.get("status") == "archived":
            state = "already_archived"
        else:
            if "expected_status" in item and task.get("status") != item["expected_status"]:
                raise KaneoError(f"Task status changed since archive capture: {item['id']}")
            if "expected_version" in item and task.get("version") != item["expected_version"]:
                raise KaneoError(f"Task version changed since archive capture: {item['id']}")
            if apply:
                preserved = {field: task.get(field) for field in (
                    "id", "projectId", "number", "title", "description", "goal", "acceptanceCriteria",
                    "completionSummary", "workItemType", "priority", "userId",
                )}
                policy_fields = {}
                for argument, field in (("goal", "goal"), ("acceptance_criteria", "acceptanceCriteria")):
                    if argument not in item:
                        continue
                    value = _policy_text(item[argument], "", field)
                    if str(task.get(field) or "").strip() and task[field] != value:
                        raise KaneoError(f"Archive cannot replace existing policy field: {item['id']}/{field}")
                    policy_fields[argument] = value
                    preserved[field] = value
                archived = client.update_status(
                    item["id"], "archived", version=task.get("version"), **policy_fields,
                )
                if not isinstance(archived, dict) or any(archived.get(k) != v for k, v in preserved.items()):
                    raise KaneoError(f"Task archive content read-back mismatch: {item['id']}")
            state = "archived" if apply else "would_archive"
        return {"action": "archive_task", "id": item["id"], "state": state,
                "reason": item["reason"]}

    if archive_workers == 1:
        actions.extend(archive_task(item) for item in archive_items)
    elif archive_items:
        with ThreadPoolExecutor(max_workers=archive_workers) as executor:
            actions.extend(executor.map(archive_task, archive_items))

    for batch in plan.get("ensure_task_batches", []):
        project = client.get_project(batch["project_id"])
        if project.get("name") != batch["project_name"]:
            raise KaneoError(f"Project identity mismatch: {batch['project_id']}")
        max_workers = int(batch.get("max_workers", 8))
        if not 1 <= max_workers <= 16:
            raise KaneoError("Task batch workers must be between 1 and 16")
        existing_tasks = client.list_tasks(batch["project_id"])
        active_tasks = [
            task for task in existing_tasks if task.get("status") != "archived"
        ]
        malformed = sorted(
            str(task.get("id", "<unknown>"))
            for task in active_tasks
            if MANAGED_MARKER_TOKEN in str(task.get("description") or "")
            and managed_metadata(task) is None
        )
        if malformed:
            raise KaneoError(f"Malformed or multiple managed markers: {', '.join(malformed)}")
        existing_by_key: dict[str, dict[str, Any]] = {}
        for task in active_tasks:
            key = managed_key(task)
            if key is None:
                continue
            if key in existing_by_key:
                raise KaneoError(
                    f"Duplicate managed key {key}: "
                    f"{existing_by_key[key]['id']}, {task['id']}"
                )
            existing_by_key[key] = task
        specs = batch.get("tasks", [])
        plan_keys = [item["key"] for item in specs]
        if len(plan_keys) != len(set(plan_keys)):
            raise KaneoError("Duplicate managed key in ensure task batch")
        plan_titles = [item["title"] for item in specs]
        if len(plan_titles) != len(set(plan_titles)):
            raise KaneoError("Duplicate title in ensure task batch")
        parent_specs: dict[str, str] = {}
        related_specs: dict[str, str] = {}
        for item in specs:
            parent_id = item.get("parent_task_id")
            parent_key = item.get("parent_task_key")
            if parent_id and parent_key:
                raise KaneoError(f"Batch task has both parent ID and key: {item['key']}")
            if parent_id:
                parent_specs[parent_id] = item["parent_task_title"]
            elif parent_key:
                parent = existing_by_key.get(parent_key)
                if parent is None:
                    raise KaneoError(
                        f"Managed batch parent key is missing: {parent_key}"
                    )
                if parent.get("title") != item["parent_task_title"]:
                    raise KaneoError(
                        f"Managed batch parent title mismatch: {parent_key}"
                    )
            for related in item.get("related_tasks", []):
                related_specs[related["id"]] = related["title"]
        for task_id, title in {**parent_specs, **related_specs}.items():
            _expected_task(client, task_id, batch["project_id"], title)

        def ensure_batch_task(item: dict[str, Any]) -> dict[str, Any]:
            if MANAGED_MARKER_TOKEN in item["description"]:
                raise KaneoError(f"Batch description already has managed marker: {item['key']}")
            work_item_type = item.get("work_item_type", "task")
            level = {"task": "task", "sub_epic": "sub-epic", "epic": "epic"}.get(
                work_item_type
            )
            if level is None:
                raise KaneoError(f"Invalid batch work item type: {work_item_type}")
            expected_description = (
                f"{item['description'].rstrip()}\n\n"
                f"{marker(item['key'], level, batch['space_id'])}"
            )
            task = existing_by_key.get(item["key"])
            if task is not None:
                validate_managed_identity(
                    task,
                    RepoBinding(
                        batch["space_id"], batch["workspace_id"], batch["project_id"],
                        batch["project_name"], client.api_endpoint, "registry",
                    ),
                    key=item["key"], level=level, work_item_type=work_item_type,
                )
                for field, expected in (
                    ("title", item["title"]), ("description", expected_description),
                ):
                    if task.get(field) != expected:
                        raise KaneoError(
                            f"Managed batch task {field} mismatch for {task['id']}"
                        )
                state = "already_present"
            elif not apply:
                return {
                    "action": "ensure_task", "key": item["key"],
                    "title": item["title"], "state": "would_create",
                }
            else:
                task = client.create_task(
                    batch["project_id"], item["title"], expected_description,
                    status=item.get("status", "to-do"),
                    priority=item.get("priority", "medium"),
                    work_item_type=work_item_type,
                    goal=item.get("goal"),
                    acceptance_criteria=item.get("acceptance_criteria"),
                )
                state = "created"
            assignee_id = item.get("assignee_id", batch.get("assignee_id"))
            if apply and assignee_id and task.get("userId") != assignee_id:
                task = client.update_assignee(task["id"], assignee_id, version=task.get("version"))
            parent_id = item.get("parent_task_id")
            if parent_id is None and item.get("parent_task_key"):
                parent_id = existing_by_key[item["parent_task_key"]]["id"]
            if apply and parent_id:
                client.ensure_relation(parent_id, task["id"], "subtask")
            if apply:
                for related in item.get("related_tasks", []):
                    client.ensure_relation(task["id"], related["id"], "related")
            return {
                "action": "ensure_task", "id": task["id"], "key": item["key"],
                "title": item["title"], "state": state,
                "parent": parent_id, "related": [row["id"] for row in item.get("related_tasks", [])],
            }

        if apply and len(specs) > 1:
            with ThreadPoolExecutor(max_workers=min(max_workers, len(specs))) as executor:
                batch_actions = list(executor.map(ensure_batch_task, specs))
        else:
            batch_actions = [ensure_batch_task(item) for item in specs]
        actions.extend(batch_actions)

    for project_plan in plan.get("hierarchies", []):
        project = client.get_project(project_plan["project_id"])
        if project.get("name") != project_plan["project_name"]:
            raise KaneoError(f"Project identity mismatch: {project_plan['project_id']}")
        binding = RepoBinding(
            project_plan["space_id"], project_plan["workspace_id"], project_plan["project_id"],
            project_plan["project_name"], client.api_endpoint, project_plan.get("default_area", "delivery"),
        )
        epic_spec = project_plan["epic"]
        epic_result = ensure_managed_task(
            client, binding, key=epic_spec["key"], level="epic", title=epic_spec["title"],
            area="portfolio", status=epic_spec.get("status", "to-do"), priority="high", apply=apply,
        )
        epic = epic_result["task"]
        actions.append({"action": epic_result["action"], "kind": "epic", "title": epic_spec["title"],
                        "id": epic.get("id"), "applied": apply})
        for group in project_plan.get("groups", []):
            if group.get("existing_task_id"):
                parent = _expected_task(
                    client, group["existing_task_id"], project_plan["project_id"], group["title"]
                )
            else:
                group_result = ensure_managed_task(
                    client, binding, key=group["key"], level="sub-epic", title=group["title"],
                    area=group.get("area", "delivery"), status=group.get("status", "to-do"),
                    priority="medium", apply=apply,
                )
                parent = group_result["task"]
                actions.append({"action": group_result["action"], "kind": "sub-epic",
                                "title": group["title"], "id": parent.get("id"), "applied": apply})
            if apply:
                client.ensure_relation(epic["id"], parent["id"])
            for child in group["children"]:
                leaf = _expected_task(client, child["id"], project_plan["project_id"], child["title"])
                if apply:
                    client.ensure_relation(parent["id"], leaf["id"])
                actions.append({"action": "ensure_relation", "parent": parent.get("id"),
                                "child": leaf["id"], "applied": apply})
        for child in project_plan.get("direct_children", []):
            leaf = _expected_task(client, child["id"], project_plan["project_id"], child["title"])
            if apply:
                client.ensure_relation(epic["id"], leaf["id"])
            actions.append({"action": "ensure_relation", "parent": epic.get("id"),
                            "child": leaf["id"], "applied": apply})

    for item in plan.get("archive_projects", []):
        project = client.get_project(item["id"])
        if project.get("name") != item["name"]:
            raise KaneoError(f"Project identity mismatch for archive: {item['id']}")
        if project.get("archivedAt"):
            state = "already_archived"
        else:
            if apply:
                client.archive_project(item["id"])
            state = "archived" if apply else "would_archive"
        actions.append({"action": "archive_project", "id": item["id"], "state": state,
                        "reason": item["reason"]})
    return {"applied": apply, "actions": actions}


def marker(key: str, level: str, space_id: str) -> str:
    """Build machine-readable marker without storing mutable Kaneo IDs."""
    payload = json.dumps(
        {"key": key, "level": level, "space_id": space_id},
        sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    )
    return f"<!-- kaneo-managed:{payload} -->"


def managed_metadata(task: dict[str, Any]) -> dict[str, str] | None:
    """Return validated managed marker metadata from task description."""
    description = task.get("description") or ""
    if not isinstance(description, str) or description.count(MANAGED_MARKER_TOKEN) != 1:
        return None
    matches = MANAGED_MARKER.findall(description)
    if len(matches) != 1:
        return None
    try:
        data = json.loads(matches[0])
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    required = ("key", "level", "space_id")
    if set(data) != set(required) or any(
        not isinstance(data.get(field), str) or not data[field] for field in required
    ):
        return None
    return {field: data[field] for field in required}


def managed_key(task: dict[str, Any]) -> str | None:
    """Return stable managed key from task description."""
    metadata = managed_metadata(task)
    return metadata["key"] if metadata else None


def leaf_key(space_id: str, outcome: str) -> str:
    """Create stable, compact idempotency key for repository outcome."""
    normalized = " ".join(outcome.casefold().split())
    digest = hashlib.sha256(f"{space_id}\0{normalized}".encode("utf-8")).hexdigest()[:16]
    return f"leaf:{space_id}:{digest}"


def normalized_title(title: str) -> str:
    """Normalize a title for safe exact-match task reuse."""
    return " ".join(title.casefold().split())


def normalized_area(area: str) -> str:
    """Normalize human area input into stable lowercase slug form."""
    return re.sub(r"-+", "-", re.sub(r"[\s_]+", "-", area.strip().casefold())).strip("-")


def task_work_item_type(task: dict[str, Any]) -> str:
    """Read Kaneo API and test-double work item type spellings."""
    return str(task.get("workItemType") or task.get("work_item_type") or "task")


def validate_managed_identity(
    task: dict[str, Any], binding: RepoBinding, *, key: str, level: str,
    work_item_type: str,
) -> None:
    """Fail closed when persisted marker identity or task type has drifted."""
    metadata = managed_metadata(task)
    if (
        metadata is None
        or metadata["key"] != key
        or metadata["level"] != level
        or metadata["space_id"] != binding.space_id
        or task.get("projectId") != binding.project_id
        or task_work_item_type(task) != work_item_type
    ):
        raise KaneoError(f"Managed task identity mismatch: {task.get('id', '<unknown>')}")


def unique_managed_task(
    tasks: list[dict[str, Any]], key: str,
) -> dict[str, Any] | None:
    """Return one managed-key match and fail closed on duplicate identity."""
    malformed = sorted(
        str(task.get("id", "<unknown>"))
        for task in tasks
        if MANAGED_MARKER_TOKEN in str(task.get("description") or "")
        and managed_metadata(task) is None
    )
    if malformed:
        raise KaneoError(f"Malformed or multiple managed markers: {', '.join(malformed)}")
    matches = [task for task in tasks if managed_key(task) == key]
    if len(matches) > 1:
        raise KaneoError(
            f"Duplicate managed key {key}: {', '.join(sorted(task['id'] for task in matches))}"
        )
    return matches[0] if matches else None


def ensure_managed_task(
    client: KaneoClient, binding: RepoBinding, *, key: str, level: str, title: str,
    area: str, existing_tasks: list[dict[str, Any]] | None = None,
    parent_id: str | None = None, parent_required: bool = False,
    status: str = "to-do", priority: str = "medium", goal: str | None = None,
    acceptance_criteria: str | None = None, apply: bool = False,
) -> dict[str, Any]:
    """Find or create one task by marker, then exact compatible title."""
    if existing_tasks is None:
        existing_tasks = client.list_tasks(binding.project_id)
    work_item_type = {"epic": "epic", "sub-epic": "sub_epic", "task": "task"}[level]
    existing = unique_managed_task(existing_tasks, key)
    if existing:
        validate_managed_identity(
            existing, binding, key=key, level=level, work_item_type=work_item_type,
        )
        return {"action": "reuse", "task": existing}
    description = (
        f"## Outcome\n{title}\n\n"
        f"## Context references\n- Space: `{binding.space_id}`\n- Area: `{area}`\n\n"
        f"{marker(key, level, binding.space_id)}"
    )
    task_goal = _policy_text(goal, title, "Goal")
    task_acceptance = _policy_text(
        acceptance_criteria, DEFAULT_ACCEPTANCE_CRITERIA, "Acceptance criteria"
    )
    title_matches = [
        task for task in existing_tasks
        if normalized_title(str(task.get("title") or "")) == normalized_title(title)
        and task_work_item_type(task) == work_item_type
        and MANAGED_MARKER.search(str(task.get("description") or "")) is None
        and task.get("status") != "archived"
        and (
            not parent_required
            or not any(
                relation.get("relationType") == "subtask"
                and relation.get("targetTaskId") == task.get("id")
                and relation.get("sourceTaskId") != parent_id
                for relation in client.relations(task["id"])
            )
        )
    ]
    if len(title_matches) > 1:
        raise KaneoError(
            f"Ambiguous exact title reuse {title!r}: "
            f"{', '.join(sorted(task['id'] for task in title_matches))}"
        )
    existing = title_matches[0] if title_matches else None
    if existing:
        adoption_marker = marker(key, level, binding.space_id)
        current_description = str(existing.get("description") or "").rstrip()
        adopted_description = "\n\n".join(
            item for item in (current_description, adoption_marker) if item
        )
        adopted = {**existing, "description": adopted_description}
        if apply:
            adopted = client.update_description(
                existing["id"], adopted_description, version=existing.get("version"),
            )
        return {"action": "adopt_title", "task": adopted, "dry_run": not apply}
    if not apply:
        return {"action": "create", "dry_run": True,
                "task": {"title": title, "description": description, "workItemType": work_item_type,
                         "goal": task_goal, "acceptanceCriteria": task_acceptance}}
    task = client.create_task(
        binding.project_id, title, description, status=status, priority=priority,
        work_item_type=work_item_type, goal=task_goal, acceptance_criteria=task_acceptance,
    )
    return {"action": "create", "task": task}


RELATION_SUMMARY_FIELDS = (
    "id", "version", "title", "status", "priority", "workItemType", "number",
    "projectId", "userId", "assigneeName",
)


def _capable(client: Any, feature: str) -> bool:
    """Capability check that leaves test doubles without discovery on legacy paths."""
    return hasattr(client, "require") and client.require(feature)


def _attach_relation_summaries(
    client: Any, known_rows: list[dict[str, Any]], relations: list[dict[str, Any]],
) -> None:
    """Add ``sourceTask``/``targetTask`` summaries that legacy relation reads carry.

    Export and context routes return bare relation rows.  Summaries are built
    from already-read task rows; an endpoint outside them (cross-project) is
    read once with ``GET /task/{id}``.
    """
    by_id = {row["id"]: row for row in known_rows if row.get("id")}
    for relation in relations:
        for field, endpoint in (("sourceTask", "sourceTaskId"), ("targetTask", "targetTaskId")):
            task_id = relation.get(endpoint)
            if field in relation or not task_id:
                continue
            if task_id not in by_id:
                by_id[task_id] = client.get_task(task_id)
            row = by_id[task_id]
            relation[field] = {name: row.get(name) for name in RELATION_SUMMARY_FIELDS}


def direct_task_context(
    client: KaneoClient, task: dict[str, Any], known_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return direct relations plus full parent chain for agent context.

    With ``taskContext`` one paged ``/task/agent/context`` read returns the
    relations and the whole ancestor chain (the server rejects multiple parents
    and cycles); otherwise relations are read once per hierarchy level.
    """
    task_id = task["id"]
    by_id = {item["id"]: item for item in known_tasks}
    if _capable(client, "taskContext"):
        try:
            context = client.task_context_relations(task_id)
        except KaneoHTTPError as exc:
            if exc.status == 409 and "multiple hierarchy parents" in exc.body:
                raise KaneoError(f"Task has multiple hierarchy parents: {exc.body[:200]}") from exc
            if exc.status == 409 and "cyclic" in exc.body:
                raise KaneoError(f"Hierarchy cycle detected at task: {task_id}") from exc
            raise
        relations = context["relations"]
        return _task_context_result(
            client, task_id, relations, context["ancestor_ids"], by_id, summarize=True,
        )
    relations = client.relations(task_id)
    ancestor_ids: list[str] = []
    current_id = task_id
    seen = {task_id}
    while True:
        parent_relations = [
            relation for relation in client.relations(current_id)
            if relation.get("relationType") == "subtask"
            and relation.get("targetTaskId") == current_id
        ]
        if not parent_relations:
            break
        if len(parent_relations) > 1:
            raise KaneoError(f"Task has multiple hierarchy parents: {current_id}")
        parent_id = parent_relations[0]["sourceTaskId"]
        if parent_id in seen:
            raise KaneoError(f"Hierarchy cycle detected at task: {parent_id}")
        seen.add(parent_id)
        ancestor_ids.append(parent_id)
        current_id = parent_id
    return _task_context_result(client, task_id, relations, ancestor_ids, by_id)


def _task_context_result(
    client: Any, task_id: str, relations: list[dict[str, Any]], ancestor_ids: list[str],
    by_id: dict[str, dict[str, Any]], *, summarize: bool = False,
) -> dict[str, Any]:
    """Shape direct task context identically for legacy and context-route reads."""
    linked_ids = sorted({
        relation["targetTaskId"] if relation.get("sourceTaskId") == task_id
        else relation["sourceTaskId"]
        for relation in relations
        if task_id in {relation.get("sourceTaskId"), relation.get("targetTaskId")}
    })
    linked = []
    for item_id in sorted(set(linked_ids + ancestor_ids)):
        # list_tasks is scoped to the current project, while a ``related``
        # relation may deliberately point into another project.  Read that
        # visible relation target so callers receive usable context, not only
        # an opaque cross-project ID.
        linked.append(by_id.get(item_id) or client.get_task(item_id))
    current = client.get_task(task_id)
    if summarize:
        _attach_relation_summaries(client, [current, *linked, *by_id.values()], relations)
    return {
        "task": current,
        "relations": relations,
        "parent_ids": sorted({
            relation["sourceTaskId"] for relation in relations
            if relation.get("relationType") == "subtask" and relation.get("targetTaskId") == task_id
        }),
        "child_ids": sorted({
            relation["targetTaskId"] for relation in relations
            if relation.get("relationType") == "subtask" and relation.get("sourceTaskId") == task_id
        }),
        "ancestor_ids": ancestor_ids,
        "related_ids": sorted({
            relation["targetTaskId"] if relation.get("sourceTaskId") == task_id else relation["sourceTaskId"]
            for relation in relations if relation.get("relationType") == "related"
        }),
        "linked_tasks": linked,
    }


def task_record(
    client: KaneoClient, binding: RepoBinding, task_id: str, *, deadline_seconds: int = 60,
) -> dict[str, Any]:
    """Read one task, its comments, relations and direct relation targets in any project.

    Read-only by design: no project gate, so a close-out reader can load a task
    owned by another repository's binding on the same Kaneo endpoint.
    """
    if not 1 <= deadline_seconds <= 3600:
        raise KaneoError("Task record deadline must be between 1 and 3600 seconds")
    deadline = client.deadline(deadline_seconds) if hasattr(client, "deadline") else nullcontext()
    with deadline:
        task = client.get_task(task_id)
        relations = client.relations(task_id)
        comments = client.list_comments(task_id)
        linked = []
        for relation in relations:
            other_id = (
                relation.get("targetTaskId") if relation.get("sourceTaskId") == task_id
                else relation.get("sourceTaskId")
            )
            other = client.get_task(other_id)
            linked.append({
                "relation_type": relation.get("relationType"),
                "direction": "outgoing" if relation.get("sourceTaskId") == task_id else "incoming",
                "id": other_id, "number": other.get("number"), "title": other.get("title"),
                "status": other.get("status"), "project_id": other.get("projectId"),
            })
    linked.sort(key=lambda row: (str(row["relation_type"]), row["number"] is None, row["number"] or 0))
    return {
        "task": task,
        "project_id": task.get("projectId"),
        "in_bound_project": task.get("projectId") == binding.project_id,
        "comments": comments,
        "relations": relations,
        "linked_tasks": linked,
    }


def direct_child_completion_audit(
    client: KaneoClient, binding: RepoBinding, task_id: str, *,
    max_children: int = 100, deadline_seconds: int = 60,
) -> dict[str, Any]:
    """Audit one parent and its direct subtasks without listing its project."""
    if max_children < 1:
        raise KaneoError("Task hierarchy max children must be positive")
    if not 1 <= deadline_seconds <= 3600:
        raise KaneoError("Task hierarchy deadline must be between 1 and 3600 seconds")

    deadline = client.deadline(deadline_seconds) if hasattr(client, "deadline") else nullcontext()
    with deadline:
        parent = client.get_task(task_id)
        if parent.get("projectId") != binding.project_id:
            raise KaneoError(
                f"Task project mismatch: expected {binding.project_id!r}, got {parent.get('projectId')!r}"
            )
        relation_rows = None
        if _capable(client, "taskContext"):
            # Paged relation read; pages beyond the child bound fail closed.
            try:
                relation_rows = client.task_context_relations(
                    task_id, max_pages=max_children // CONTEXT_PAGE_LIMIT + 2,
                )["relations"]
            except KaneoHTTPError as exc:
                # The context route also validates the parent's own ancestor
                # chain; the audit only needs direct children, so a 409 there
                # falls back to the single legacy relation read.
                if exc.status != 409:
                    raise
        if relation_rows is None:
            relation_rows = client.relations(task_id)
        child_ids = sorted({
            relation["targetTaskId"]
            for relation in relation_rows
            if relation.get("relationType") == "subtask"
            and relation.get("sourceTaskId") == task_id
        })
        if len(child_ids) > max_children:
            raise KaneoError(
                f"Task hierarchy child limit exceeded for {task_id}: "
                f"{len(child_ids)} > {max_children}"
            )

        children: list[dict[str, Any]] = []
        for child_id in child_ids:
            child = client.get_task(child_id)
            if child.get("projectId") != binding.project_id:
                raise KaneoError(
                    f"Direct subtask project mismatch: {child_id} -> {child.get('projectId')!r}"
                )
            children.append({
                "id": child_id,
                "number": child.get("number"),
                "title": child.get("title"),
                "status": child.get("status"),
                "completion_summary": child.get("completionSummary"),
                "terminal_with_evidence": (
                    child.get("status") in ("done", "archived")
                    and bool(child.get("completionSummary"))
                ),
            })

    children.sort(key=lambda child: (child["number"] is None, child["number"], child["id"]))
    return {
        "task": {
            "id": parent["id"], "number": parent.get("number"), "title": parent.get("title"),
            "status": parent.get("status"), "project_id": parent.get("projectId"),
            "goal": parent.get("goal"), "acceptance_criteria": parent.get("acceptanceCriteria"),
            "completion_summary": parent.get("completionSummary"),
        },
        "direct_children": children,
        "has_direct_children": bool(children),
        "all_direct_children_terminal_with_evidence": bool(children) and all(
            child["terminal_with_evidence"] for child in children
        ),
    }


def finish_managed_parent(
    client: KaneoClient, binding: RepoBinding, task_id: str, *,
    completion_summary: str | None = None, apply: bool = False,
) -> dict[str, Any]:
    """Close one managed epic/sub-epic only after all direct children prove completion."""
    parent = client.get_task(task_id)
    metadata = managed_metadata(parent)
    expected_type = {"epic": "epic", "sub-epic": "sub_epic"}
    if (
        metadata is None
        or metadata["level"] not in expected_type
        or task_work_item_type(parent) != expected_type[metadata["level"]]
        or parent.get("projectId") != binding.project_id
        or metadata["space_id"] != binding.space_id
    ):
        raise KaneoError(f"Refusing to auto-complete non-managed parent: {task_id}")

    audit = direct_child_completion_audit(client, binding, task_id)
    if not audit["all_direct_children_terminal_with_evidence"]:
        raise KaneoError(f"Refusing to complete parent with unfinished direct children: {task_id}")
    children = audit["direct_children"]
    canonical_summary = _policy_text(
        completion_summary,
        f"Verified {len(children)} direct subtasks are done with persisted completion summaries.",
        "Completion summary",
    )
    child_numbers = ", ".join(
        f"#{child['number']}" if child["number"] is not None else child["id"]
        for child in children
    )
    evidence = (
        "Result: completed parent\n\n"
        f"Validation:\n- Direct-child audit verified terminal evidence for: {child_numbers}\n\n"
        "Remaining:\n- none"
    )
    if not apply:
        return {
            "applied": False, "task": parent, "audit": audit,
            "completion_summary": canonical_summary, "comment": evidence,
        }
    if parent.get("status") == "done" and parent.get("completionSummary") not in (None, canonical_summary):
        raise KaneoError(f"Parent completion summary conflict: {task_id}")
    comment = client.ensure_comment(task_id, evidence)
    completed = (
        parent
        if parent.get("status") == "done" and parent.get("completionSummary") == canonical_summary
        else client.update_status(
            task_id, "done", completion_summary=canonical_summary,
            version=parent.get("version"),
        )
    )
    return {"applied": True, "task": completed, "audit": audit, "comment": comment}


MANAGED_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9:._/-]{1,512}$")


def _managed_description(binding: RepoBinding, key: str, level: str, title: str, area: str) -> str:
    """Description written for a new managed task (same text as ensure_managed_task)."""
    return (
        f"## Outcome\n{title}\n\n"
        f"## Context references\n- Space: `{binding.space_id}`\n- Area: `{area}`\n\n"
        f"{marker(key, level, binding.space_id)}"
    )


def _managed_preview(
    client: Any, binding: RepoBinding, specs: list[tuple[str, str, str, str]],
    task_goal: str, task_acceptance: str,
) -> dict[str, Any] | None:
    """Plan a dry-run start with the server's read-only managed preview.

    Uses at most three requests (capabilities, preview, leaf context) and never
    lists the project.  Returns None when ``managedPreview`` is not advertised,
    a key does not fit the server pattern, or the server reports a hierarchy
    conflict (409); the caller then runs the legacy scan, which explains or
    reuses the existing hierarchy exactly as before.
    """
    if not hasattr(client, "require") or not client.require("managedPreview"):
        return None
    work_item_types = {"epic": "epic", "sub-epic": "sub_epic", "task": "task"}
    items = []
    for key, level, title, area in specs:
        if not MANAGED_KEY_PATTERN.match(key):
            client.note(
                f"Kaneo managed preview skipped: key {key!r} does not match the server key pattern; "
                "fallback: dry-run start scans the project task list"
            )
            return None
        leaf = level == "task"
        items.append({
            "key": key, "title": title,
            "description": _managed_description(binding, key, level, title, area),
            "goal": task_goal if leaf else title,
            "acceptanceCriteria": task_acceptance if leaf else DEFAULT_ACCEPTANCE_CRITERIA,
            "workItemType": work_item_types[level],
        })
    try:
        payload = client.request(
            "POST",
            f"/task/agent/managed/{urllib.parse.quote(binding.project_id, safe='')}/preview",
            {"items": items},
        )
    except KaneoHTTPError as exc:
        if exc.status != 409:
            raise
        client.note(
            f"Kaneo managed preview reported a conflict ({exc.body[:200]}); "
            "fallback: dry-run start scans the project task list"
        )
        return None
    tasks = payload.get("tasks") if isinstance(payload, dict) else None
    actions = payload.get("actions") if isinstance(payload, dict) else None
    if (
        not isinstance(tasks, list) or not isinstance(actions, list)
        or len(tasks) != 3 or len(actions) != 3
    ):
        raise KaneoError(f"Invalid Kaneo managed preview response: {binding.project_id}")
    results = []
    for action, task in zip(actions, tasks):
        row: dict[str, Any] = {"action": action, "task": task}
        if action != "reuse":
            row["dry_run"] = True
        results.append(row)
    leaf = tasks[-1]
    if leaf.get("id") and client.supports("taskContext"):
        context_payload = client.request(
            "GET", f"/task/agent/context/{urllib.parse.quote(leaf['id'], safe='')}?"
            f"{urllib.parse.urlencode({'page': 1, 'limit': CONTEXT_PAGE_LIMIT})}",
        )
        context = {
            field: context_payload.get(field, [])
            for field in ("relations", "parent_ids", "child_ids", "ancestor_ids",
                          "related_ids", "linked_tasks")
        }
        context["task"] = context_payload.get("task", leaf)
        if context_payload.get("truncation"):
            context["truncation"] = context_payload["truncation"]
    else:
        context = {"task": leaf, "relations": [], "parent_ids": [], "child_ids": [],
                   "ancestor_ids": [], "related_ids": [], "linked_tasks": []}
    return {
        "applied": False,
        "space_id": binding.space_id,
        "project_id": binding.project_id,
        "items": results,
        "leaf_id": leaf.get("id"),
        "context": context,
        "planner": "managed_preview",
    }


def start_repo_work(
    client: KaneoClient, binding: RepoBinding, *, outcome: str, area: str | None = None,
    goal: str | None = None, acceptance_criteria: str | None = None, apply: bool = False,
) -> dict[str, Any]:
    """Ensure repository epic/sub-epic/leaf and start leaf."""
    normalized_outcome = outcome.strip()
    selected_area = normalized_area(area or binding.default_area)
    if not normalized_outcome:
        raise KaneoError("Outcome must not be empty")
    if not selected_area:
        raise KaneoError("Area must not be empty")
    task_goal = _policy_text(goal, normalized_outcome, "Goal")
    task_acceptance = _policy_text(
        acceptance_criteria,
        f"Canonical output and validation evidence for {normalized_outcome} are recorded before completion.",
        "Acceptance criteria",
    )
    specs = [
        (
            binding.epic_key or f"epic:{binding.space_id}", "epic",
            binding.epic_title or f"Epic: {binding.project_name} delivery", "portfolio",
        ),
        (
            f"subepic:{binding.space_id}:{selected_area}", "sub-epic",
            f"Sub-epic: {selected_area.replace('-', ' ').title()}", selected_area,
        ),
        (leaf_key(binding.space_id, normalized_outcome), "task", normalized_outcome, selected_area),
    ]
    if not apply:
        previewed = _managed_preview(client, binding, specs, task_goal, task_acceptance)
        if previewed is not None:
            return previewed
    existing_tasks = client.list_tasks(binding.project_id)
    existing_leaf = unique_managed_task(existing_tasks, specs[-1][0])
    if existing_leaf:
        validate_managed_identity(
            existing_leaf, binding, key=specs[-1][0], level="task", work_item_type="task",
        )
        parent_ids = sorted({
            relation["sourceTaskId"] for relation in client.relations(existing_leaf["id"])
            if relation.get("relationType") == "subtask"
            and relation.get("targetTaskId") == existing_leaf["id"]
        })
        if len(parent_ids) > 1:
            raise KaneoError(f"Managed leaf has multiple hierarchy parents: {existing_leaf['id']}")
        if parent_ids:
            current_parent = client.get_task(parent_ids[0])
            parent_key_matches = managed_key(current_parent) == specs[1][0]
            if parent_key_matches:
                validate_managed_identity(
                    current_parent, binding, key=specs[1][0], level="sub-epic",
                    work_item_type="sub_epic",
                )
            requested_parent_matches = parent_key_matches or (
                normalized_title(str(current_parent.get("title") or ""))
                == normalized_title(specs[1][2])
                and task_work_item_type(current_parent) == "sub_epic"
            )
            current_epic_ids = sorted({
                relation["sourceTaskId"] for relation in client.relations(current_parent["id"])
                if relation.get("relationType") == "subtask"
                and relation.get("targetTaskId") == current_parent["id"]
            })
            if len(current_epic_ids) > 1:
                raise KaneoError(
                    f"Managed sub-epic has multiple hierarchy parents: {current_parent['id']}"
                )
            if current_epic_ids:
                current_epic = client.get_task(current_epic_ids[0])
                epic_key_matches = managed_key(current_epic) == specs[0][0]
                if epic_key_matches:
                    validate_managed_identity(
                        current_epic, binding, key=specs[0][0], level="epic",
                        work_item_type="epic",
                    )
                requested_parent_matches = requested_parent_matches and (epic_key_matches or (
                    normalized_title(str(current_epic.get("title") or ""))
                    == normalized_title(specs[0][2])
                    and task_work_item_type(current_epic) == "epic"
                ))
            if not requested_parent_matches:
                if apply and existing_leaf.get("status") != "in-progress":
                    existing_leaf = client.update_status(
                        existing_leaf["id"], "in-progress", version=existing_leaf.get("version"),
                    )
                context = direct_task_context(client, existing_leaf, existing_tasks)
                linked_by_id = {task["id"]: task for task in context["linked_tasks"]}
                hierarchy = [
                    {"action": "reuse_hierarchy", "task": linked_by_id[task_id]}
                    for task_id in reversed(context["ancestor_ids"])
                    if task_id in linked_by_id
                ]
                hierarchy.append({"action": "reuse", "task": context["task"]})
                return {
                    "applied": apply,
                    "space_id": binding.space_id,
                    "project_id": binding.project_id,
                    "items": hierarchy,
                    "leaf_id": existing_leaf["id"],
                    "context": context,
                }
    results = []
    for index, (key, level, title, task_area) in enumerate(specs):
        parent_id = results[index - 1]["task"].get("id") if index else None
        results.append(ensure_managed_task(
            client, binding, key=key, level=level, title=title, area=task_area,
            existing_tasks=existing_tasks, parent_id=parent_id, parent_required=index > 0,
            status="to-do", priority="high" if level == "epic" else "medium",
            goal=task_goal if level == "task" else title,
            acceptance_criteria=task_acceptance if level == "task" else DEFAULT_ACCEPTANCE_CRITERIA,
            apply=apply,
        ))
    if apply:
        epic, subepic, leaf = (item["task"] for item in results)
        client.ensure_relation(epic["id"], subepic["id"])
        client.ensure_relation(subepic["id"], leaf["id"])
        if leaf.get("status") != "in-progress":
            leaf = client.update_status(leaf["id"], "in-progress", version=leaf.get("version"))
            results[-1]["task"] = leaf
        context = direct_task_context(client, leaf, client.list_tasks(binding.project_id))
    else:
        leaf = results[-1]["task"]
        if leaf.get("id"):
            context = direct_task_context(client, leaf, existing_tasks)
        else:
            context = {"task": leaf, "relations": [], "parent_ids": [],
                       "child_ids": [], "ancestor_ids": [], "related_ids": [], "linked_tasks": []}
    return {
        "applied": apply,
        "space_id": binding.space_id,
        "project_id": binding.project_id,
        "items": results,
        "leaf_id": results[-1]["task"].get("id"),
        "context": context,
    }


def canonical_evidence_items(items: list[str], label: str) -> list[str]:
    """Validate and sort one-line evidence so retries produce identical content."""
    if not items:
        raise KaneoError(f"{label} evidence must not be empty")
    normalized: set[str] = set()
    for item in items:
        if not isinstance(item, str):
            raise KaneoError(f"{label} evidence entries must be strings")
        value = item.strip()
        if not value or "\n" in value or "\r" in value:
            raise KaneoError(f"{label} evidence entries must be non-empty single lines")
        normalized.add(value)
    return sorted(normalized, key=lambda value: (value.casefold(), value))


def finish_repo_work(
    client: KaneoClient, binding: RepoBinding, task_id: str, *, changed: list[str],
    validation: list[str], remaining: str = "none", completion_summary: str | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    """Record concise canonical evidence, then complete managed leaf."""
    task = client.get_task(task_id)
    metadata = managed_metadata(task)
    if (
        metadata is None
        or metadata["level"] != "task"
        or task_work_item_type(task) != "task"
    ):
        raise KaneoError(f"Refusing to auto-complete non-managed leaf: {task_id}")
    if task.get("projectId") != binding.project_id or metadata["space_id"] != binding.space_id:
        raise KaneoError(f"Refusing to auto-complete leaf outside repository binding: {task_id}")
    canonical_changed = canonical_evidence_items(changed, "Changed")
    canonical_validation = canonical_evidence_items(validation, "Validation")
    canonical_remaining = remaining.strip()
    if not canonical_remaining or "\n" in canonical_remaining or "\r" in canonical_remaining:
        raise KaneoError("Remaining must be one non-empty line")
    canonical_completion = _policy_text(
        completion_summary,
        "Completed task. "
        f"Changed: {', '.join(canonical_changed)}. "
        f"Validation: {'; '.join(canonical_validation)}. "
        f"Remaining: {canonical_remaining}.",
        "Completion summary",
    )
    content = "\n".join(
        ["Result: completed", "", "Changed:"]
        + [f"- `{item}`" for item in canonical_changed]
        + ["", "Validation:"]
        + [f"- {item}" for item in canonical_validation]
        + ["", "Canonical references:"]
        + [f"- `{item}`" for item in canonical_changed]
        + ["", "Remaining:", f"- {canonical_remaining}"]
    )
    existing_comment = client.completion_comment(task_id, content)
    if not apply:
        return {
            "applied": False, "task_id": task_id, "comment": content,
            "existing_comment": existing_comment, "status": "done",
        }
    comment = existing_comment or client.ensure_completion_comment(task_id, content)
    if task.get("status") == "done" and task.get("completionSummary") not in (None, canonical_completion):
        raise KaneoError(f"Completion summary conflict: {task_id}")
    completed = (
        task
        if task.get("status") == "done" and task.get("completionSummary") == canonical_completion
        else client.update_status(
            task_id, "done", completion_summary=canonical_completion,
            version=task.get("version"),
        )
    )
    return {"applied": True, "task": completed, "comment": comment}


def project_health(client: KaneoClient, binding: RepoBinding) -> dict[str, Any]:
    """Verify API/auth and exact repository project binding with one read."""
    project = client.get_project(binding.project_id)
    if project.get("id") != binding.project_id or project.get("name") != binding.project_name:
        raise KaneoError(
            f"Project binding mismatch: expected {binding.project_id!r}/"
            f"{binding.project_name!r}, got {project.get('id')!r}/{project.get('name')!r}"
        )
    return {
        "ok": True,
        "scope": "project",
        "workspace_id": binding.workspace_id,
        "project_id": binding.project_id,
        "project_name": binding.project_name,
    }


def _snapshot_project(
    client: KaneoClient, project: dict[str, Any], max_workers: int, *,
    max_pages: int | None, max_tasks: int, progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Capture one project while preserving deterministic task order.

    With ``pagedExports`` task identities come from cursor-paged export pages
    (ordered by number, then id); with ``projectRelationExports`` relations are
    read once per project instead of once per task.  Task rows are still
    hydrated with ``GET /task/{id}`` and comments per task, and exported
    relations get the same ``sourceTask``/``targetTask`` summaries as
    ``GET /task-relation/{id}``, so output fields do not depend on the route.
    """
    if _capable(client, "pagedExports"):
        tasks = sorted(
            client.export_task_pages(project["id"], max_pages=max_pages, max_tasks=max_tasks),
            key=lambda row: (row.get("number") is None, row.get("number") or 0, row["id"]),
        )
    else:
        tasks = client.list_tasks(project["id"], max_pages=max_pages)
    if len(tasks) > max_tasks:
        raise KaneoError(
            f"Kaneo snapshot task limit exceeded for {project['id']}: {len(tasks)} > {max_tasks}"
        )
    if progress:
        progress(f"project {project['id']}: hydrating {len(tasks)} tasks")

    exported_relations: dict[str, list[dict[str, Any]]] | None = None
    if _capable(client, "projectRelationExports"):
        exported_relations = {task["id"]: [] for task in tasks}
        for relation in client.export_relations(project["id"]):
            for endpoint in {relation.get("sourceTaskId"), relation.get("targetTaskId")}:
                if endpoint in exported_relations:
                    exported_relations[endpoint].append(relation)

    def hydrate(task: dict[str, Any]) -> dict[str, Any]:
        task_id = task["id"]
        full = client.get_task(task_id)
        full["relations"] = (
            client.relations(task_id) if exported_relations is None
            else exported_relations[task_id]
        )
        full["comments"] = client.list_comments(task_id)
        return full

    if tasks:
        with ThreadPoolExecutor(max_workers=min(max_workers, len(tasks))) as executor:
            task_rows = list(executor.map(hydrate, tasks))
    else:
        task_rows = []
    if exported_relations is not None:
        _attach_relation_summaries(client, task_rows, [
            relation for row in task_rows for relation in row["relations"]
        ])
    return {**project, "tasks": task_rows}


def snapshot(
    client: KaneoClient, workspace_config: Path, *, binding: RepoBinding | None = None,
    max_workers: int = 8, max_pages: int | None = 8, max_tasks: int = 2000,
    deadline_seconds: int = 120, progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Capture bound project by default or all configured workspaces for audits."""
    if not 1 <= max_workers <= 32:
        raise KaneoError("Snapshot workers must be between 1 and 32")
    if max_pages is not None and max_pages < 1:
        raise KaneoError("Snapshot max pages must be positive")
    if max_tasks < 1:
        raise KaneoError("Snapshot max tasks must be positive")
    if not 1 <= deadline_seconds <= 3600:
        raise KaneoError("Snapshot deadline must be between 1 and 3600 seconds")
    config = json.loads(workspace_config.read_text(encoding="utf-8"))
    result: dict[str, Any] = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "api_endpoint": client.api_endpoint,
        "scope": "project" if binding else "all_workspaces",
        "workspaces": [],
    }
    workspaces = config["workspaces"]
    if binding:
        workspace = next(
            (item for item in workspaces if item["id"] == binding.workspace_id), None
        )
        if workspace is None:
            raise KaneoError(f"Bound workspace missing from workspace map: {binding.workspace_id}")
        project = client.get_project(binding.project_id)
        if project.get("id") != binding.project_id or project.get("name") != binding.project_name:
            raise KaneoError(f"Bound project identity mismatch: {binding.project_id}")
        workspaces = [workspace]
        scoped_projects = [project]
    else:
        scoped_projects = None
    deadline = client.deadline(deadline_seconds) if hasattr(client, "deadline") else nullcontext()
    with deadline:
        for workspace in workspaces:
            projects = scoped_projects or client.list_projects(workspace["id"])
            project_rows = [
                _snapshot_project(
                    client, project, max_workers, max_pages=max_pages,
                    max_tasks=max_tasks, progress=progress,
                ) for project in projects
            ]
            result["workspaces"].append({**workspace, "projects": project_rows})
    return result


def validate_snapshot(data: dict[str, Any]) -> dict[str, Any]:
    """Validate managed-key uniqueness and Kaneo subtask forest invariants."""
    issues: list[dict[str, Any]] = []
    projects = [project for workspace in data.get("workspaces", []) for project in workspace.get("projects", [])]
    task_count = relation_count = 0
    for project in projects:
        tasks = project.get("tasks", [])
        task_count += len(tasks)
        task_ids = {task["id"] for task in tasks}
        keys: dict[str, str] = {}
        relations: dict[str, dict[str, Any]] = {}
        for task in tasks:
            if (
                MANAGED_MARKER_TOKEN in str(task.get("description") or "")
                and managed_metadata(task) is None
            ):
                issues.append({
                    "code": "MALFORMED_MANAGED_MARKER",
                    "project_id": project["id"],
                    "task_id": task["id"],
                })
            key = managed_key(task)
            if key and key in keys:
                issues.append({"code": "DUPLICATE_MANAGED_KEY", "project_id": project["id"],
                               "key": key, "task_ids": [keys[key], task["id"]]})
            elif key:
                keys[key] = task["id"]
            completion_comments = [
                comment for comment in task.get("comments", [])
                if isinstance(comment, dict)
                and isinstance(comment.get("content"), str)
                and comment["content"].startswith(COMPLETION_EVIDENCE_PREFIX)
            ]
            if len(completion_comments) > 1:
                issues.append({
                    "code": "MULTIPLE_COMPLETION_EVIDENCE",
                    "project_id": project["id"],
                    "task_id": task["id"],
                    "comment_ids": sorted(str(comment.get("id")) for comment in completion_comments),
                })
            for relation in task.get("relations", []):
                relations[relation["id"]] = relation
        relation_count += len(relations)
        parents: dict[str, list[str]] = {}
        graph: dict[str, list[str]] = {}
        for relation in relations.values():
            if relation.get("relationType") != "subtask":
                continue
            source, target = relation.get("sourceTaskId"), relation.get("targetTaskId")
            if source not in task_ids or target not in task_ids:
                continue
            parents.setdefault(target, []).append(source)
            graph.setdefault(source, []).append(target)
        for child, parent_ids in parents.items():
            if len(parent_ids) > 1:
                issues.append({"code": "MULTIPLE_SUBTASK_PARENTS", "project_id": project["id"],
                               "task_id": child, "parent_ids": sorted(parent_ids)})
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visiting:
                issues.append({"code": "SUBTASK_CYCLE", "project_id": project["id"], "task_id": node_id})
                return
            if node_id in visited:
                return
            visiting.add(node_id)
            for child_id in graph.get(node_id, []):
                visit(child_id)
            visiting.remove(node_id)
            visited.add(node_id)

        for task_id in task_ids:
            visit(task_id)
    return {
        "valid": not issues,
        "workspace_count": len(data.get("workspaces", [])),
        "project_count": len(projects),
        "task_count": task_count,
        "relation_count": relation_count,
        "issues": issues,
    }
