import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Elasticity from './pages/Elasticity'
import Competitor from './pages/Competitor'
import Simulator from './pages/Simulator'

function App() {
  return (
    <Router>
      <div className="min-h-screen app-shell text-slate-100">
        <div className="ambient ambient-a" />
        <div className="ambient ambient-b" />
        <Navbar />
        <main className="mx-auto w-full max-w-7xl px-4 pb-10 pt-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/elasticity" element={<Elasticity />} />
            <Route path="/competitor" element={<Competitor />} />
            <Route path="/simulator" element={<Simulator />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
