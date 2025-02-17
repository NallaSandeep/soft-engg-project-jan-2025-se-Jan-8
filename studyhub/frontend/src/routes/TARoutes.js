import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import TADashboard from '../components/ta/Dashboard';
import LectureManagement from '../components/ta/LectureManagement';
import AssignmentManagement from '../components/ta/AssignmentManagement';
import QuestionBank from '../components/ta/QuestionBank';
import SystemLogs from '../components/ta/SystemLogs';

const TARoutes = () => {
    return (
        <Routes>
            <Route path="dashboard" element={<TADashboard />} />
            <Route path="lectures" element={<LectureManagement />} />
            <Route path="assignments" element={<AssignmentManagement />} />
            <Route path="question-bank" element={<QuestionBank />} />
            <Route path="system-logs" element={<SystemLogs />} />
            <Route path="" element={<Navigate to="dashboard" replace />} />
        </Routes>
    );
};

export default TARoutes; 