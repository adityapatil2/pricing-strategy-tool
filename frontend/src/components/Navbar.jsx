import { Link, useLocation } from 'react-router-dom'

function Navbar() {
  const location = useLocation()

  const links = [
    { path: '/', label: 'Home' },
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/elasticity', label: 'Elasticity' },
    { path: '/competitor', label: 'Competitor' },
    { path: '/simulator', label: 'Simulator' },
  ]

  return (
    <nav className="surface sticky top-0 z-20 border-b border-white/5 bg-slate-950/65 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-xs font-semibold uppercase tracking-[0.35em] text-cyan-200">
              PI
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Pricing System</p>
              <p className="text-lg font-semibold text-white">PricingIQ</p>
            </div>
          </Link>
          <span className="hud-label hidden sm:inline-flex">Realtime strategy lab</span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {links.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`rounded-full px-4 py-2 text-sm font-medium transition-all duration-200 ${
                location.pathname === link.path
                  ? 'border border-cyan-400/30 bg-cyan-400/10 text-cyan-100 shadow-[0_0_0_1px_rgba(34,211,238,0.06)]'
                  : 'border border-transparent text-slate-400 hover:border-white/10 hover:bg-white/5 hover:text-white'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
