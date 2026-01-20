#!/usr/bin/env python3
"""
qdrant-update-task-status.py - Update task status in implementation plans

Updates task status in Qdrant without re-embedding vectors.
Uses Qdrant's set_payload API for efficient metadata updates.

Usage:
  python qdrant-update-task-status.py --collection "project" --point-id "uuid" --phase 1 --task 1 --status "completed"
  python qdrant-update-task-status.py --collection "project" --point-id "uuid" --phase 1 --task 1 --status "in_progress"
  python qdrant-update-task-status.py --collection "project" --list-pending

Status values: pending | in_progress | completed | blocked
"""

import argparse
import json
import sys
import requests

QDRANT_URL = "http://localhost:6333"


def get_point(collection, point_id):
    """Retrieve a point by ID."""
    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points",
        json={"ids": [point_id], "with_payload": True}
    )
    if response.status_code != 200:
        return None
    result = response.json().get("result", [])
    return result[0] if result else None


def update_payload(collection, point_id, payload_update):
    """Update payload fields without re-embedding."""
    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/payload",
        json={
            "points": [point_id],
            "payload": payload_update
        }
    )
    return response.status_code == 200


def update_task_status(collection, point_id, phase_num, task_order, new_status):
    """Update a specific task's status in an implementation plan."""
    point = get_point(collection, point_id)
    if not point:
        return {"error": f"Point {point_id} not found in {collection}"}

    payload = point.get("payload", {})
    plan = payload.get("implementation_plan")

    if not plan:
        return {"error": "No implementation_plan found in this point"}

    # Find and update the task
    updated = False
    for phase in plan.get("phases", []):
        if phase.get("phase") == phase_num:
            for task in phase.get("tasks", []):
                if task.get("order") == task_order:
                    old_status = task.get("status", "pending")
                    task["status"] = new_status
                    updated = True
                    break
            break

    if not updated:
        return {"error": f"Task not found: phase {phase_num}, task {task_order}"}

    # Update the payload
    success = update_payload(collection, point_id, {"implementation_plan": plan})

    if success:
        return {
            "success": True,
            "point_id": point_id,
            "phase": phase_num,
            "task": task_order,
            "old_status": old_status,
            "new_status": new_status
        }
    else:
        return {"error": "Failed to update payload"}


def list_pending_tasks(collection):
    """List all pending tasks across implementation plans."""
    # Search for consultation research with implementation plans
    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/scroll",
        json={
            "filter": {
                "must": [
                    {"key": "research_type", "match": {"value": "expert_consultation"}}
                ]
            },
            "limit": 100,
            "with_payload": True
        }
    )

    if response.status_code != 200:
        return {"error": "Failed to query collection"}

    points = response.json().get("result", {}).get("points", [])
    pending_tasks = []

    for point in points:
        payload = point.get("payload", {})
        plan = payload.get("implementation_plan")
        topic = payload.get("topic", "Unknown")

        if not plan:
            continue

        for phase in plan.get("phases", []):
            for task in phase.get("tasks", []):
                if task.get("status") in ["pending", "in_progress"]:
                    pending_tasks.append({
                        "point_id": point["id"],
                        "topic": topic,
                        "phase": phase.get("phase"),
                        "phase_title": phase.get("title"),
                        "task_order": task.get("order"),
                        "task": task.get("task"),
                        "status": task.get("status"),
                        "rationale": task.get("rationale")
                    })

    return {
        "collection": collection,
        "pending_count": len(pending_tasks),
        "tasks": pending_tasks
    }


def main():
    parser = argparse.ArgumentParser(description="Update task status in implementation plans")
    parser.add_argument("--collection", required=True, help="Qdrant collection name")
    parser.add_argument("--point-id", help="Point ID containing the implementation plan")
    parser.add_argument("--phase", type=int, help="Phase number (1-indexed)")
    parser.add_argument("--task", type=int, help="Task order within phase")
    parser.add_argument("--status", choices=["pending", "in_progress", "completed", "blocked"],
                        help="New status for the task")
    parser.add_argument("--list-pending", action="store_true",
                        help="List all pending/in_progress tasks in collection")

    args = parser.parse_args()

    if args.list_pending:
        result = list_pending_tasks(args.collection)
    elif args.point_id and args.phase and args.task and args.status:
        result = update_task_status(
            args.collection, args.point_id, args.phase, args.task, args.status
        )
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
