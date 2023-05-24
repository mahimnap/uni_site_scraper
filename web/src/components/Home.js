import React from "react";
import "./App.css";

function Home() {
  return (
    <div className="App-body">
      <h1>Welcome to the CIS3760 Team One Website!</h1>
      <br></br>
      <img class = "img-fluid" src="/api/homeuog" alt="UOG Image"/>
      <p>
        Please Select an Option in the Navigation Bar to Continue
        <ul>
          <li><b>Search for Courses: </b> Search through Guelph or Carleton Courses</li>
          <li><b>Graph Guelph Subjects: </b> Graph the prerequisite path for an individual course at Guelph</li>
          <li><b>Graph Carleton Subjects: </b> Graph the prerequisite path for an individual course at Carleton</li>
          <li><b>Graph Majors: </b> Graph the full path for a major at Guelph</li>
        </ul>
      </p>
    </div>
  );
}

export default Home;
