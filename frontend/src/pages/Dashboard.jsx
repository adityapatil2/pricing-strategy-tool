import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getElasticity, getOptimalPrice, getCompetitor } from '../services/api'
import RecommendationCard from '../components/RecommendationCard'
import { formatMoney, formatPercent } from '../utils/formatters'

function Dashboard() {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currency, setCurrency] = useState({ symbol: '$', code: 'USD' })
  const [productName, setProductName] = useState('Your Product')

  useEffect(() => {
    const savedCurrency = localStorage.getItem('currency')
    const savedProduct = localStorage.getItem('productName')
    if (savedCurrency) setCurrency(JSON.parse(savedCurrency))
    if (savedProduct) setProductName(savedProduct)
  }, [])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [elasticity, optimalPrice, competitor] = await Promise.all([
          getElasticity(),
          getOptimalPrice(),
          getCompetitor(),
        ])
        setData({ elasticity, optimalPrice, competitor })
      } catch (err) {
        setError('Please upload and analyze a file first')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-300"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-rose-300 text-lg mb-4">{error}</p>
        <button
          onClick={() => navigate('/')}
          className="primary-button"
        >
          Go to upload
        </button>
      </div>
    )
  }

  return (
    <div className="surface mx-auto flex max-w-6xl flex-col gap-8">
      <section className="hero-panel rounded-[2rem] px-6 py-8 sm:px-10">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="hud-label mb-5">Analysis overview</p>
            <h1 className="section-title text-white">{productName}</h1>
            <p className="section-subtitle mt-4">
              A focused readout of demand sensitivity, revenue opportunity, and competitor position in {currency.code}.
            </p>
          </div>
          <div className="panel rounded-[1.5rem] p-5">
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Current environment</p>
            <p className="mt-3 text-2xl font-semibold text-white">{currency.symbol} - {currency.code}</p>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
        <RecommendationCard
          title="Elasticity Score"
          value={data.elasticity.elasticity}
          subtitle={data.elasticity.interpretation}
          icon="EL"
          color="blue"
        />
        <RecommendationCard
          title="Optimal Price"
          value={formatMoney(data.optimalPrice.optimal_price, currency)}
          subtitle={`Current price: ${formatMoney(data.optimalPrice.current_price, currency)}`}
          icon="OP"
          color="green"
        />
        <RecommendationCard
          title="Revenue Increase"
          value={formatMoney(data.optimalPrice.revenue_increase, currency)}
          subtitle="Potential revenue gain"
          icon="RI"
          color="purple"
        />
        <RecommendationCard
          title="Your Avg Price"
          value={formatMoney(data.competitor.your_avg_price, currency)}
          subtitle="Your average price"
          icon="YP"
          color="yellow"
        />
        <RecommendationCard
          title="Competitor Price"
          value={formatMoney(data.competitor.competitor_avg_price, currency)}
          subtitle="Market average price"
          icon="CP"
          color="red"
        />
        <RecommendationCard
          title="Price Difference"
          value={formatPercent(data.competitor.price_difference_pct)}
          subtitle={data.competitor.interpretation}
          icon="DF"
          color={data.competitor.price_difference > 0 ? 'red' : 'green'}
        />
      </section>

      <section className="panel rounded-[2rem] p-6 sm:p-8">
        <h2 className="text-xl font-semibold text-white">Recommended next move</h2>
        <div className="flex flex-col gap-3">
          <div className="mt-6 flex items-start gap-3 text-slate-300">
            <span className="status-ok mt-1">01</span>
            <p>{data.elasticity.interpretation}</p>
          </div>
          <div className="flex items-start gap-3 text-slate-300">
            <span className="status-ok mt-1">02</span>
            <p>{data.competitor.suggestion}</p>
          </div>
          <div className="flex items-start gap-3 text-slate-300">
            <span className="status-ok mt-1">03</span>
            <p>Shifting toward the modeled optimal price could add {formatMoney(data.optimalPrice.revenue_increase, currency)} in average revenue.</p>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[
          { path: '/elasticity', label: 'Elasticity view' },
          { path: '/competitor', label: 'Competitor view' },
          { path: '/simulator', label: 'Simulator' },
          { path: '/', label: 'New upload' },
        ].map((btn) => (
          <button
            key={btn.path}
            onClick={() => navigate(btn.path)}
            className="panel rounded-[1.25rem] px-4 py-4 text-left text-sm font-medium text-slate-300 transition-all duration-200 hover:border-cyan-300/30 hover:text-white"
          >
            {btn.label}
          </button>
        ))}
      </section>
    </div>
  )
}

export default Dashboard
