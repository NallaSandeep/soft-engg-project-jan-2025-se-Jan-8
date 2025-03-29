"""
Models for StudyIndexerNew
"""

from .base import BaseResponse, BaseSearchQuery, BaseSearchResponse
from .course_selector import CourseInfo, CourseSelectorQuery, CourseSelectorResponse, CourseMatchResult
from .faq import FAQItem, FAQSearchQuery, FAQSearchResult, FAQSearchResponse, FAQCreateRequest, FAQUpdateRequest, JSONLImportItem, JSONLImportResponse
from .personal_resource import (
    PersonalResourceInfo, ResourceFile, PersonalResource, 
    PersonalResourceSearchQuery, PersonalResourceSearchResult, 
    PersonalResourceSearchResponse, ResourceType
)
from .integrity_check import (
    GradedAssignmentInfo, GradedAssignmentQuestion, IntegrityCheckQuery,
    AssignmentMatch, HighestMatch, IntegrityCheckResponse, MatchSegment
) 