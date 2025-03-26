"""Models package for StudyHub application."""

from .base import BaseModel
from .user import User
from .course import Course, CourseEnrollment
from .course_content import Week, Lecture, LectureProgress
from .assignment import Assignment, AssignmentSubmission, AssignmentQuestion
from .question import Question
from .resource import Resource
from .personal_resource import PersonalResource, ResourceFile

__all__ = [
    'BaseModel',
    'User',
    'Course',
    'CourseEnrollment',
    'Week',
    'Lecture',
    'LectureProgress',
    'Assignment',
    'AssignmentSubmission',
    'AssignmentQuestion',
    'Question',
    'Resource',
    'PersonalResource',
    'ResourceFile'
] 