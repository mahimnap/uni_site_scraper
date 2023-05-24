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
      <header className="App-header">
        <Nav
          className="App-nav"
          activeKey="/home"
          onSelect={(selectedKey) => alert(`selected ${selectedKey}`)}
        >
          <Nav.Item>
            <Nav.Link className="App-nav-item" eventKey="Home">Home</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link className="App-nav-item" eventKey="Course Scraper">Course Scraper</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link className="App-nav-item" eventKey="Major Scraper">Major Scraper</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link className="App-nav-item" eventKey="Carleton Scraper">Carleton Scraper</Nav.Link>
          </Nav.Item>
        </Nav>

        <img src="https://st2.depositphotos.com/17253970/46802/v/380/depositphotos_468021592-stock-illustration-internet-bot-isolated-vector-icon.jpg?forcejpeg=true" className="App-logo" alt="logo" />
        <p>
          Welcome to CIS3760 - Group 1's website!
        </p>

      </header>
    </div>
  );
}

export default App;
