import React from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Create from "../pages/Create/Create";
import Login from "../pages/Login/Login";
import Notes from "../pages/Notes/Notes";
import Edit from "../pages/Edit/Edit";

function AppRoutes() {

    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/create" element={<Create />} />
                <Route path="/notes" element={<Notes />} />
                <Route path="/edit" element={<Edit />} />
            </Routes>
        </Router>
    );
}

export default AppRoutes;