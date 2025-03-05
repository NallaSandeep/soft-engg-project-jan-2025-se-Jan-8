import React, { useEffect, useState } from 'react';
import apiService from '../services/apiService';
import { useParams } from 'react-router-dom';

const CourseDetails = () => {
    const { courseId } = useParams();
    const [lectures, setLectures] = useState([]);
    const [assignments, setAssignments] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchCourseDetails = async () => {
            try {
                const lecturesResponse = await apiService.getLectures(courseId);
                setLectures(lecturesResponse.data);

                const assignmentsResponse = await apiService.getAssignments(courseId);
                setAssignments(assignmentsResponse.data);
            } catch (err) {
                setError('Failed to fetch course details');
            }
        };

        fetchCourseDetails();
    }, [courseId]);

    return (
        <div className="course-details">
            <h2>Course Details</h2>
            {error && <p className="error">{error}</p>}
            <h3>Lectures</h3>
            <ul>
                {lectures.map((lecture) => (
                    <li key={lecture.id}>{lecture.title}</li>
                ))}
            </ul>
            <h3>Assignments</h3>
            <ul>
                {assignments.map((assignment) => (
                    <li key={assignment.id}>{assignment.title}</li>
                ))}
            </ul>
        </div>
    );
};

export default CourseDetails; 