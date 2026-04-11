function RecommendationCard({ title, value, subtitle, icon, color }) {
  const colorMap = {
    blue: 'from-cyan-400/16 to-cyan-400/5 border-cyan-300/16 text-cyan-200',
    green: 'from-emerald-400/16 to-emerald-400/5 border-emerald-300/16 text-emerald-200',
    red: 'from-rose-400/16 to-rose-400/5 border-rose-300/16 text-rose-200',
    yellow: 'from-amber-300/16 to-amber-300/5 border-amber-200/16 text-amber-100',
    purple: 'from-sky-400/16 to-indigo-400/5 border-sky-300/16 text-sky-100',
  }

  const colorClass = colorMap[color] || colorMap.blue

  return (
    <div className={`panel panel-grid rounded-[1.75rem] border bg-gradient-to-br p-6 ${colorClass}`}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-sm font-semibold uppercase tracking-[0.2em] text-white/80">
          {icon}
        </div>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.22em] text-slate-300">
          {title}
        </span>
      </div>
      <p className="metric-value mt-2 font-semibold text-white">{value}</p>
      {subtitle && (
        <p className="micro-copy mt-3">{subtitle}</p>
      )}
    </div>
  )
}

export default RecommendationCard
