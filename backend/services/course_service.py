def upload_material(course_id, file, metadata):
    return {"message": "File uploaded successfully", "fileId": "generated_file_id"}

def get_materials(course_id):
    return [{"fileId": "generated_file_id", "title": "SE", "description": "Software Eng.", "uploadedBy": "Some TA"}]

def delete_material(course_id, file_id):
    return True

def list_courses():
    return [{"courseId": "TEMP", "name": "IITM Course", "instructor": "Prof. ABC"}]

def enroll_in_course(data):
    if data.get("userId") and data.get("courseId"):
        return True
    return False

def list_students(course_id):
    return [{"userId": "123456", "name": "ABC", "email": "ABC@iitm.ac.in"}]
