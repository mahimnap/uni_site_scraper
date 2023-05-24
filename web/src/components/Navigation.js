import React from "react";
import { NavLink } from "react-router-dom";

function Navigation() {
  return (
    <div className="navigation">
      <nav className="navbar navbar-expand navbar-dark bg-dark">
        <div className="container">
          <NavLink className="navbar-brand" to="/">
            Home
          </NavLink>
          <div>
            <ul className="navbar-nav ml-auto">
            <li className="nav-item">
                <NavLink className="nav-link" to="/searchform">
                  Search for Courses
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/guelphsubjectgraph">
                  Graph Guelph Subjects
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/carletonsubjectgraph">
                  Graph Carleton Subjects
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/majorgraph">
                  Graph Majors
                </NavLink>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </div>
  );
}

export default Navigation;
