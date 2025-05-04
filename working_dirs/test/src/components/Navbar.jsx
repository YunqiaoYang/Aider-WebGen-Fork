import { Link } from 'react-router-dom'
import '../styles/Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">Financial Dashboard</Link>
      <div className="navbar-links">
        <Link to="/" className="nav-link">Dashboard</Link>
        <Link to="/consolidated" className="nav-link">Consolidated Report</Link>
        <Link to="/compare" className="nav-link">Comparison Tool</Link>
      </div>
    </nav>
  )
}
