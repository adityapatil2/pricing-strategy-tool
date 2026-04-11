import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import { analyzeData, clearUploadSession } from '../services/api'

function Home() {
  const navigate = useNavigate()
  const [columns, setColumns] = useState([])
  const [mapping, setMapping] = useState({
    price: '',
    units_sold: '',
    competitor_price: '',
    date: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [uploadDone, setUploadDone] = useState(false)
  const [autoDetected, setAutoDetected] = useState({})
  const [productName, setProductName] = useState('')
  const [currency, setCurrency] = useState({ symbol: '$', code: 'USD', name: 'US Dollar' })

  const requiredFields = [
    { key: 'price', label: 'Price Column', required: true },
    { key: 'units_sold', label: 'Units Sold Column', required: true },
    { key: 'competitor_price', label: 'Competitor Price Column', required: true },
    { key: 'date', label: 'Date Column', required: false },
  ]

  const handleUploadSuccess = (result) => {
    setColumns(result.columns)
    setAutoDetected(result.auto_mapping)
    setCurrency(result.currency)
    setMapping({
      price: result.auto_mapping.price || '',
      units_sold: result.auto_mapping.units_sold || '',
      competitor_price: result.auto_mapping.competitor_price || '',
      date: result.auto_mapping.date || '',
    })
    setUploadDone(true)
  }

  const handleMappingChange = (field, value) => {
    setMapping((prev) => ({ ...prev, [field]: value }))
  }

  const handleAnalyze = async () => {
    if (!mapping.price || !mapping.units_sold || !mapping.competitor_price) {
      setError('Please map all required columns')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const result = await analyzeData({ ...mapping, product_name: productName || 'Your Product' })
      if (result.upload_token) {
        localStorage.setItem('uploadToken', result.upload_token)
      }
      localStorage.setItem('currency', JSON.stringify(currency))
      localStorage.setItem('productName', productName || 'Your Product')
      navigate('/dashboard')
    } catch (err) {
      setError('Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const allAutoDetected = mapping.price && mapping.units_sold && mapping.competitor_price

  return (
    <div className="surface mx-auto flex max-w-5xl flex-col gap-8">
      <section className="hero-panel rounded-[2rem] px-6 py-8 sm:px-10 sm:py-12">
        <div className="hud-label mb-6">Minimal pricing intelligence</div>
        <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr] lg:items-end">
          <div>
            <h1 className="section-title text-white">
              Build pricing decisions from live demand signals.
            </h1>
            <p className="section-subtitle mt-5">
              Upload a raw sales file, map the key columns, and move straight into elasticity,
              optimal price, competitor positioning, and simulation views with a calmer, faster workflow.
            </p>
          </div>
          <div className="panel rounded-[1.75rem] p-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Workspace outputs</p>
            <div className="mt-4 grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              <div>
                <p className="text-3xl font-semibold text-white">03</p>
                <p className="micro-copy mt-1">Core analyses</p>
              </div>
              <div>
                <p className="text-3xl font-semibold text-white">01</p>
                <p className="micro-copy mt-1">Simulation studio</p>
              </div>
              <div>
                <p className="text-3xl font-semibold text-white">16MB</p>
                <p className="micro-copy mt-1">Max upload size</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
        <div className="space-y-6">
          {!uploadDone ? (
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          ) : (
            <div className="panel rounded-[2rem] p-6 sm:p-8">
              <div className="mb-6 flex flex-wrap items-center gap-3">
                <span className="hud-label status-ok">Upload synced</span>
                <span className="micro-copy">Review the detected schema before running the analysis.</span>
              </div>

              <div className={`mb-6 rounded-2xl border px-4 py-4 text-sm ${
                allAutoDetected
                  ? 'border-cyan-300/20 bg-cyan-400/10 text-cyan-100'
                  : 'border-amber-200/20 bg-amber-300/10 text-amber-100'
              }`}>
                {allAutoDetected
                  ? 'Most required fields were detected automatically. You can still override them below.'
                  : 'Some fields still need manual mapping before the analysis can run.'}
              </div>

              <div className="mb-6">
                <h2 className="text-xl font-semibold text-white">Column mapping</h2>
                <p className="micro-copy mt-2">Match each analysis input to the correct source column.</p>
              </div>

              <div className="mb-5 grid gap-4 md:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-slate-300">
                    Product name
                    <span className="ml-2 text-xs text-slate-500">(optional)</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Premium Headphones"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    className="field"
                  />
                </div>

                <div className="panel rounded-[1.25rem] p-4">
                  <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Detected currency</p>
                  <p className="mt-3 text-2xl font-semibold text-white">{currency.symbol}</p>
                  <p className="micro-copy mt-1">{currency.name} - {currency.code}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {requiredFields.map((field) => (
                  <div key={field.key} className="flex flex-col gap-2">
                    <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
                      {field.label}
                      {field.required && <span className="text-rose-300">*</span>}
                      {autoDetected[field.key] && (
                        <span className="rounded-full border border-cyan-300/20 bg-cyan-400/10 px-2 py-0.5 text-[0.65rem] uppercase tracking-[0.2em] text-cyan-100">
                          Auto
                        </span>
                      )}
                    </label>
                    <select
                      value={mapping[field.key]}
                      onChange={(e) => handleMappingChange(field.key, e.target.value)}
                      className="field"
                    >
                      <option value="">Select column</option>
                      {columns.map((col) => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>

              {error && (
                <p className="mt-4 text-sm text-rose-300">{error}</p>
              )}

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <button
                  onClick={() => {
                    clearUploadSession()
                    setUploadDone(false)
                    setMapping({ price: '', units_sold: '', competitor_price: '', date: '' })
                  }}
                  className="secondary-button"
                >
                  Reset upload
                </button>
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="primary-button flex-1 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? 'Analyzing...' : 'Launch analysis'}
                </button>
              </div>
            </div>
          )}
        </div>

        <aside className="panel panel-grid rounded-[2rem] p-6">
          <p className="text-xs uppercase tracking-[0.32em] text-slate-500">Pipeline</p>
          <div className="mt-6 space-y-5">
            {[
              ['01', 'Upload dataset', 'Import sales, price, competitor, and optional time-series fields.'],
              ['02', 'Map schema', 'Confirm which columns represent price, units sold, competitor price, and date.'],
              ['03', 'Explore outcomes', 'Open the dashboard, elasticity view, competitor view, and simulator.'],
            ].map(([step, title, copy]) => (
              <div key={step} className="rounded-[1.25rem] border border-white/5 bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-[0.28em] text-cyan-200">{step}</p>
                <p className="mt-2 text-lg font-medium text-white">{title}</p>
                <p className="micro-copy mt-2">{copy}</p>
              </div>
            ))}
          </div>
        </aside>
      </section>
    </div>
  )
}

export default Home
