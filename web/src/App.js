import Nav from 'react-bootstrap/Nav';
import './App.css';

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
            <Nav.Link className="App-nav-item" eventKey="D3 Graph" href="./graph.html">D3JS Graph</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link className="App-nav-item" eventKey="PDF Graphs" href="./pdfgraph.html">PDF Graphs</Nav.Link>
          </Nav.Item>
        </Nav>

        <img src="./website_logo.jpg" className="App-logo" alt="logo" />
        <h1 className="App-main-title">Welcome to CIS3760 - Group 1's website!</h1>
    </body>

  </div>
  );
}

export default App;
