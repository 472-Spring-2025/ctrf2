import json
import logging
import requests
import time
from datetime import datetime

from flask import request, Blueprint, abort
from CTFd.models import Users
from CTFd.utils.decorators import authed_only

from ..models import DojoChallenges, DojoStudents, DojoStudents
from .course import grade
from ..utils.dojo import dojo_route

canvas = Blueprint("canvas", __name__)

logger = logging.getLogger(__name__)


def canvas_request(endpoint, method="GET", *, dojo, **kwargs):
    missing = [attr for attr in ["canvas_token", "canvas_api_host", "canvas_course_id"] if not (dojo.course or {}).get(attr)]
    if missing:
        raise RuntimeError(f"Canvas not configured: missing {', '.join(missing)}")
    canvas_token = dojo.course["canvas_token"]
    canvas_api_host = dojo.course["canvas_api_host"]
    canvas_course_id = dojo.course["canvas_course_id"]

    headers = {"Authorization": f"Bearer {canvas_token}"}
    canvas_course_endpoint = f"https://{canvas_api_host}/api/v1/courses/{canvas_course_id}"
    response = requests.request(method, f"{canvas_course_endpoint}{endpoint}", headers=headers, **kwargs)
    response.raise_for_status()
    if "application/json" in response.headers.get("Content-Type", ""):
        return response.json()
    else:
        return response.content


@canvas.route("/dojo/<dojo>/admin/canvas/sync")
@dojo_route
@authed_only
def canvas_sync(dojo):
    if not (dojo.course and dojo.course.get("canvas_token")):
        abort(404)

    if not dojo.is_admin():
        abort(403)

    ignore_pending = request.args.get("ignore_pending") is not None
    posting_results = sync_canvas(dojo, ignore_pending=ignore_pending)
    return json.dumps(posting_results, indent=2)


@canvas.route("/dojo/<dojo>/admin/canvas/progress/<int:progress_id>")
@dojo_route
@authed_only
def canvas_progress(dojo, progress_id):
    if not (dojo.course and dojo.course.get("canvas_token")):
        abort(404)

    if not dojo.is_admin():
        abort(403)

    response = canvas_request(f"/progress/{progress_id}", dojo=dojo)
    return json.dumps(response, indent=2)


def sync_canvas_user(user_id, challenge_id):
    for dojo_challenge in DojoChallenges.query.filter(DojoChallenges.challenge_id == challenge_id):
        dojo = dojo_challenge.dojo
        if not (dojo.course and dojo.course.get("canvas_token")):
            continue
        posting_results = sync_canvas(dojo, module_id=dojo_challenge.module.id, user_id=user_id)
        student_id = posting_results.get("student_id")
        assignment_id = posting_results.get("json", {}).get("assignment_id")
        score = posting_results.get("json", {}).get("score")
        logger.info(f"Canvas synced: user={user_id}, challenge={challenge_id}, student={student_id}, assignment={assignment_id}, score={score}")


def sync_canvas(dojo, module_id=None, user_id=None, ignore_pending=False):
    course_students = dojo.course.get("students", [])
    users = (
        Users.query
        .join(DojoStudents, DojoStudents.user_id == Users.id)
        .filter(DojoStudents.dojo == dojo, DojoStudents.token.in_(course_students))
    )
    if user_id is not None:
        users = users.filter(DojoStudents.user_id == user_id)

    assessments = dojo.course.get("assessments", [])
    canvas_assignments = {
        assignment["id"]: dict(
            id=assignment["id"],
            name=assignment["name"],
            due_date=datetime.strptime(assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ") if assignment["due_at"] else None,
        )
        for assignment in canvas_request("/assignments", dojo=dojo)
    }

    assignment_submissions = {}

    grades = grade(dojo, users, ignore_pending=ignore_pending)
    for user_grades in grades:
        for assessment, assessment_grade in zip(assessments, user_grades["assessment_grades"]):
            canvas_assignment = canvas_assignments.get(assessment.get("canvas_assignment_id"))

            if not canvas_assignment:
                continue
            if module_id and module_id != assessment["module_id"]:
                continue
            if not assessment_grade["credit"] and canvas_assignment["due_date"] and canvas_assignment["due_date"] > datetime.now():
                continue

            student_submissions = assignment_submissions.setdefault(canvas_assignment["id"], {})
            grade_data = student_submissions.setdefault("grade_data", {})
            student_user_id = f"sis_user_id:{user_grades['user_id']}"
            grade_credit = f"{assessment_grade['credit'] * 100:.2f}%"
            grade_data[student_user_id] = {"posted_grade": grade_credit}

    progress_info = {}
    for assignment_id, grade_data in assignment_submissions.items():
        response = canvas_request(f"/assignments/{assignment_id}/submissions/update_grades", method="POST", dojo=dojo, json=grade_data)
        progress_info[assignment_id] = response

    return progress_info
