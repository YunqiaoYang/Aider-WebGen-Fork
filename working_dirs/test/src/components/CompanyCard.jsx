import { Link } from 'react-router-dom'
import '../styles/CompanyCard.css'

export default function CompanyCard({ company }) {
  return (
    <Link to={`/company/${company.id}`} className="company-card">
      <h3>{company.name}</h3>
      <div className="metrics">
        <div className="metric">
          <span>Revenue</span>
          <span>${company.revenue.toLocaleString()}</span>
        </div>
        <div className="metric">
          <span>Profit</span>
          <span>${company.profit.toLocaleString()}</span>
        </div>
        <div className="metric">
          <span>Employees</span>
          <span>{company.employees}</span>
        </div>
      </div>
    </Link>
  )
}
