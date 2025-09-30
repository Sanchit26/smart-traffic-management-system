import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Components/Auth/Login';
// Registration removed
import UserDetails from './Components/Auth/UserDetails';

function App() {
  const handleFilter = (e) => {
    const value = e.target.value;
    console.log('Search input:', value); // You can handle filtering logic here
  };

  return (
    <Router>
      <div>

        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          {/* register route removed */}
          <Route path="/userDetails" element={<UserDetails />} />
          {/* Add more routes here if needed */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
