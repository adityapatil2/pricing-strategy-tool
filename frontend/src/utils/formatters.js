export function formatMoney(value, currency = { symbol: '$' }) {
  const numericValue = Number(value)

  if (Number.isNaN(numericValue)) {
    return `${currency.symbol ?? '$'}0.00`
  }

  return `${currency.symbol ?? '$'}${numericValue.toFixed(2)}`
}

export function formatPercent(value) {
  const numericValue = Number(value)

  if (Number.isNaN(numericValue)) {
    return '0.00%'
  }

  return `${numericValue.toFixed(2)}%`
}
