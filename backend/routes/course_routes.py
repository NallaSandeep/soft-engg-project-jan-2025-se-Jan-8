from flask import Blueprint, request, jsonify, abort
from backend.services import course_service

course_bp = Blueprint('course', __name__, url_prefix='/api/courses')

@course_bp.post('/<courseId>/upload')
def upload_material(courseId):
    file = request.files.get('file')
    metadata = request.form.to_dict()
    if not file:
        abort(400, description="File is required")
    result = course_service.upload_material(courseId, file, metadata)
    return jsonify(result), 201

@course_bp.get('/<courseId>/materials')
def get_materials(courseId):
    materials = course_service.get_materials(courseId)
    return jsonify({"courseId": courseId, "materials": materials}), 200

@course_bp.delete('/<courseId>/materials/<fileId>')
def delete_material(courseId, fileId):
    success = course_service.delete_material(courseId, fileId)
    if not success:
        abort(404, description="Material not found")
    return jsonify({"message": "Material deleted successfully"}), 200

@course_bp.get('')
def list_courses():
    courses = course_service.list_courses()
    return jsonify({"courses": courses}), 200

@course_bp.post('/enroll')
def enroll_course():
    data = request.get_json()
    success = course_service.enroll_in_course(data)
    if not success:
        abort(400, description="Enrollment failed")
    return jsonify({"message": "Enrollment successful"}), 200

@course_bp.get('/<courseId>/students')
def list_students(courseId):
    students = course_service.list_students(courseId)  # returns list of students
    return jsonify({"courseId": courseId, "students": students}), 200
