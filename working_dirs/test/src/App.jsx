import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CompanyDetail from './pages/CompanyDetail'
import ConsolidatedReport from './pages/ConsolidatedReport'
import ComparisonTool from './pages/ComparisonTool'
import AddCompany from './pages/AddCompany'
import NotFound from './pages/NotFound'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { FinancialDataProvider } from './context/FinancialDataContext'
import './App.css'

function App() {
  return (
    <FinancialDataProvider>
      <BrowserRouter>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/company/:id" element={<CompanyDetail />} />
              <Route path="/consolidated" element={<ConsolidatedReport />} />
              <Route path="/compare" element={<ComparisonTool />} />
              <Route path="/add-company" element={<AddCompany />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </FinancialDataProvider>
  )
}

export default App
