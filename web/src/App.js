import Nav from 'react-bootstrap/Nav';
import './App.css';
import jQuery from 'jquery';

function App() {
  return (
    <div className="App">
      <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
        integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3"
        crossorigin="anonymous"
      />

      <body className="App-body">
        <Nav
          className="App-nav"
          activeKey="/home"

          /* Function that occurs when a navbar item is clicked */
          onSelect={(selectedKey) =>
            selectedKey !=="Home" ? alert(`selected ${selectedKey}`) : null
          }
        >
          <Nav.Item>
            <Nav.Link className="App-nav-item" href="/" eventKey="Home">Home</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link className="App-nav-item" href="./graph.html">3DJS Graph</Nav.Link>
          </Nav.Item>
        </Nav>

        <img src="./website_logo.jpg" className="App-logo" alt="logo" />
        <h1 className="App-main-title">Welcome to CIS3760 - Group 1's website!</h1>
        <h2>All University of Guelph and University of Carleton Majors</h2>
        <div className="App-pdf-section">

          <div>
            <div className="App-pdf-subsection">
              <h3>Guelph Majors</h3>
              <a className="App-link" href="./graph_multimajor.pdf" target="_blank">View in a new tab</a>
              <iframe className="App-pdf-section-iframe" src="./graph_multimajor.pdf" frameborder="0" scrolling="auto" title="Guelph Graph">
                <p>Here are the graphs for all Guelph majors</p>
                <a href="./graph_multimajor.pdf">Download PDF</a>
              </iframe>
            </div>

            <div className="App-pdf-subsection">
              <h3>Carleton Majors</h3>
              <a className="App-link" href="./graph_carleton.pdf" target="_blank">View in a new tab</a>
              <iframe className="App-pdf-section-iframe" src="./graph_carleton.pdf" frameborder="0" scrolling="auto" title="Carleton Graph">
                <p>Here are the graphs for all Carleton majors</p>
                <a href="./graph_carleton.pdf">Download PDF</a>
              </iframe>
            </div>
          </div>

        </div>

        <>
           <button onClick={() =>
             jQuery.ajax ({
               type: 'get',
               dataType: 'json',
               url: '/api/search',
               data : {
                 prereqs: "false",
                 credits: "0.5",
                 terms: "F",
                 levels: "2000",
                 subjects: "CIS"
               },
               success: function (data) {
                 alert (data["results"]);
               },
               fail: function (error) {
                 alert (error);
               }
             })
           }>Endpoint Test</button>
        </>

      </body>

    </div>
  );
}

export default App;
