import { useContext } from 'react'
import { FinancialDataContext } from '../context/FinancialDataContext'
import CompanyCard from '../components/CompanyCard'
import '../styles/Dashboard.css'

export default function Dashboard() {
  const { companies } = useContext(FinancialDataContext)

  return (
    <div className="dashboard">
      <h1>Company Dashboard</h1>
      <div className="company-grid">
        {companies.map(company => (
          <CompanyCard key={company.id} company={company} />
        ))}
      </div>
    </div>
  )
}
