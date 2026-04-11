import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCompetitor } from '../services/api'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import RecommendationCard from '../components/RecommendationCard'
import { formatMoney, formatPercent } from '../utils/formatters'

function Competitor() {
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
        const result = await getCompetitor()
        setData(result)
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
        <p className="hud-label mb-5">Competitor view</p>
        <h1 className="section-title text-white">Market position</h1>
        <p className="section-subtitle mt-4">{productName} benchmarked against the average competitor price in {currency.code}.</p>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <RecommendationCard
          title="Your Avg Price"
          value={formatMoney(data.your_avg_price, currency)}
          subtitle="Your average price"
          icon="YP"
          color="blue"
        />
        <RecommendationCard
          title="Competitor Price"
          value={formatMoney(data.competitor_avg_price, currency)}
          subtitle="Market average price"
          icon="CP"
          color="yellow"
        />
        <RecommendationCard
          title="Price Difference"
          value={formatPercent(data.price_difference_pct)}
          subtitle={data.interpretation}
          icon="DF"
          color={data.price_difference > 0 ? 'red' : 'green'}
        />
      </section>

      <section className="panel rounded-[1.75rem] p-6">
        <h2 className="text-xl font-semibold text-white mb-3">Positioning guidance</h2>
        <p className="text-slate-300">{data.suggestion}</p>
      </section>

      <section className="panel rounded-[2rem] p-6">
        <h2 className="text-xl font-semibold text-white mb-6">
          Your Price vs Competitor Price Over Time
        </h2>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={data.chart_data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="date"
              stroke="#9CA3AF"
              tick={{ fontSize: 11 }}
            />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{ backgroundColor: '#08101d', border: '1px solid rgba(148,163,184,0.16)', borderRadius: '16px' }}
              labelStyle={{ color: '#F9FAFB' }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="your_price"
              stroke="#67e8f9"
              dot={false}
              strokeWidth={2.5}
              name="Your Price"
            />
            <Line
              type="monotone"
              dataKey="competitor_price"
              stroke="#fbbf24"
              dot={false}
              strokeWidth={2.5}
              name="Competitor Price"
            />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </div>
  )
}

export default Competitor
