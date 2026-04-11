import { useState, useEffect } from 'react'
import { simulateDiscount, simulateBundling } from '../services/api'
import RecommendationCard from '../components/RecommendationCard'
import { formatMoney, formatPercent } from '../utils/formatters'

function Simulator() {
  const [activeTab, setActiveTab] = useState('discount')
  const [discountPct, setDiscountPct] = useState(10)
  const [elasticity, setElasticity] = useState(-1.5)
  const [bundleDiscountPct, setBundleDiscountPct] = useState(10)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currency, setCurrency] = useState({ symbol: '$', code: 'USD' })
  const [productName, setProductName] = useState('Your Product')

  useEffect(() => {
    const savedCurrency = localStorage.getItem('currency')
    const savedProduct = localStorage.getItem('productName')
    if (savedCurrency) setCurrency(JSON.parse(savedCurrency))
    if (savedProduct) setProductName(savedProduct)
  }, [])

  const handleSimulate = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      let res
      if (activeTab === 'discount') {
        res = await simulateDiscount(discountPct, elasticity)
      } else {
        res = await simulateBundling(bundleDiscountPct)
      }
      setResult(res)
    } catch (err) {
      setError('Please upload and analyze a file first')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="surface mx-auto flex max-w-5xl flex-col gap-8">
      <section className="hero-panel rounded-[2rem] px-6 py-8 sm:px-10">
        <p className="hud-label mb-5">Simulation studio</p>
        <h1 className="section-title text-white">Revenue simulator</h1>
        <p className="section-subtitle mt-4">
          Stress test discount and bundle scenarios for {productName} before you make a pricing move in market.
        </p>
      </section>

      <div className="flex gap-2">
        {['discount', 'bundling'].map((tab) => (
          <button
            key={tab}
            onClick={() => {
              setActiveTab(tab)
              setResult(null)
            }}
            className={`rounded-full px-5 py-3 font-medium capitalize transition-colors duration-200 ${
              activeTab === tab
                ? 'bg-cyan-400/15 text-cyan-100 border border-cyan-300/20'
                : 'panel border border-white/5 text-slate-400 hover:text-white'
            }`}
          >
            {tab === 'discount' ? 'Discount' : 'Bundling'}
          </button>
        ))}
      </div>

      <section className="panel rounded-[2rem] p-6 sm:p-8">
        {activeTab === 'discount' ? (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-semibold text-white">Discount Simulator</h2>

            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Discount Percentage: <span className="text-cyan-200">{discountPct}%</span>
              </label>
              <input
                type="range"
                min="1"
                max="50"
                value={discountPct}
                onChange={(e) => setDiscountPct(Number(e.target.value))}
                className="w-full accent-cyan-300"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1%</span>
                <span>50%</span>
              </div>
            </div>

            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Elasticity: <span className="text-cyan-200">{elasticity}</span>
              </label>
              <input
                type="range"
                min="-3"
                max="0"
                step="0.1"
                value={elasticity}
                onChange={(e) => setElasticity(Number(e.target.value))}
                className="w-full accent-cyan-300"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>-3 (Very Sensitive)</span>
                <span>0 (Not Sensitive)</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-semibold text-white">Bundling Simulator</h2>
            <p className="text-gray-400 text-sm">
              Simulate selling 2 products together at a discounted bundle price
            </p>

            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Bundle Discount: <span className="text-cyan-200">{bundleDiscountPct}%</span>
              </label>
              <input
                type="range"
                min="1"
                max="40"
                value={bundleDiscountPct}
                onChange={(e) => setBundleDiscountPct(Number(e.target.value))}
                className="w-full accent-cyan-300"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1%</span>
                <span>40%</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <p className="text-rose-300 text-sm mt-4">{error}</p>
        )}

        <button
          onClick={handleSimulate}
          disabled={loading}
          className="primary-button mt-6 w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Simulating...
            </span>
          ) : (
            'Run simulation'
          )}
        </button>
      </section>

      {result && (
        <section className="flex flex-col gap-6">
          <h2 className="text-xl font-semibold text-white">Simulation Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <RecommendationCard
              title="Current Revenue"
              value={formatMoney(result.current_revenue, currency)}
              subtitle="Before simulation"
              icon="CR"
              color="yellow"
            />
            <RecommendationCard
              title="Projected Revenue"
              value={formatMoney(result.new_revenue || result.bundle_revenue, currency)}
              subtitle="After simulation"
              icon="PR"
              color={result.revenue_change > 0 ? 'green' : 'red'}
            />
            <RecommendationCard
              title="Revenue Change"
              value={formatMoney(result.revenue_change, currency)}
              subtitle={`${formatPercent(result.revenue_change_pct)} change`}
              icon={result.revenue_change > 0 ? 'UP' : 'DN'}
              color={result.revenue_change > 0 ? 'green' : 'red'}
            />
            <RecommendationCard
              title="Verdict"
              value={result.interpretation}
              subtitle={activeTab === 'discount'
                ? `At ${discountPct}% discount`
                : `At ${bundleDiscountPct}% bundle discount`}
              icon="VR"
              color="purple"
            />
          </div>
        </section>
      )}
    </div>
  )
}

export default Simulator
