import React, { createContext, useState } from 'react'

export const FinancialDataContext = createContext()

export function FinancialDataProvider({ children }) {
  const [companies, setCompanies] = useState([
    {
      id: 1,
      name: 'TechCorp',
      revenue: 1200000,
      expenses: 800000,
      profit: 400000,
      assets: 2500000,
      liabilities: 1500000,
      employees: 120
    },
    {
      id: 2,
      name: 'FinanceCo',
      revenue: 1800000,
      expenses: 1200000,
      profit: 600000,
      assets: 3500000,
      liabilities: 2000000,
      employees: 85
    },
    {
      id: 3,
      name: 'RetailGroup',
      revenue: 900000,
      expenses: 700000,
      profit: 200000,
      assets: 1800000,
      liabilities: 1200000,
      employees: 210
    }
  ])

  const addCompany = (company) => {
    setCompanies([...companies, company])
  }

  const updateCompany = (id, updatedData) => {
    setCompanies(companies.map(company => 
      company.id === id ? { ...company, ...updatedData } : company
    ))
  }

  return (
    <FinancialDataContext.Provider value={{ companies, addCompany, updateCompany }}>
      {children}
    </FinancialDataContext.Provider>
  )
}
