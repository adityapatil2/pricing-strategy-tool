import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getElasticity } from '../services/api'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import RecommendationCard from '../components/RecommendationCard'

function Elasticity() {
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
        const result = await getElasticity()
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
        <p className="hud-label mb-5">Elasticity view</p>
        <h1 className="section-title text-white">Demand sensitivity</h1>
        <p className="section-subtitle mt-4">
          {productName} in {currency.symbol} {currency.code}. This view compares price levels to units sold so you can see whether demand is reacting sharply or staying stable.
        </p>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <RecommendationCard
          title="Elasticity Score"
          value={data.elasticity}
          subtitle={data.interpretation}
          icon="EL"
          color="blue"
        />
        <div className="panel rounded-[1.75rem] p-6">
          <h3 className="text-white font-semibold mb-3">
            What does this mean?
          </h3>
          <div className="flex flex-col gap-2 text-sm text-slate-400">
            <p>
              <span className="text-rose-300 font-medium">Below -1: </span>
              Demand is more sensitive to price changes.
            </p>
            <p>
              <span className="text-amber-200 font-medium">Equal to -1: </span>
              Revenue tends to stay balanced when price shifts.
            </p>
            <p>
              <span className="text-emerald-200 font-medium">Above -1: </span>
              Demand is less reactive, which may create room for price increases.
            </p>
          </div>
        </div>
      </section>

      <section className="panel rounded-[2rem] p-6">
        <h2 className="text-xl font-semibold text-white mb-6">
          Price vs Units Sold
        </h2>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={data.chart_data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="price"
              stroke="#9CA3AF"
              label={{ value: `Price (${currency.symbol})`, position: 'insideBottom', offset: -5, fill: '#9CA3AF' }}
            />
            <YAxis
              stroke="#9CA3AF"
              label={{ value: 'Units Sold', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#08101d', border: '1px solid rgba(148,163,184,0.16)', borderRadius: '16px' }}
              labelStyle={{ color: '#F9FAFB' }}
              formatter={(value, name) => [value, name === 'units_sold' ? 'Units Sold' : name]}
              labelFormatter={(label) => `Price: ${currency.symbol}${label}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="units_sold"
              stroke="#67e8f9"
              dot={{ r: 2, strokeWidth: 0, fill: '#67e8f9' }}
              strokeWidth={2.5}
              name="Units Sold"
            />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </div>
  )
}

export default Elasticity
