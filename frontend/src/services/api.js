import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:5000'
const UPLOAD_TOKEN_KEY = 'uploadToken'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const getStoredUploadToken = () => localStorage.getItem(UPLOAD_TOKEN_KEY)

const withUploadToken = (config = {}) => {
  const uploadToken = getStoredUploadToken()

  return {
    ...config,
    headers: {
      ...(config.headers || {}),
      ...(uploadToken ? { 'X-Upload-Token': uploadToken } : {}),
    },
  }
}

export const uploadFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post(`${BASE_URL}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  if (response.data?.upload_token) {
    localStorage.setItem(UPLOAD_TOKEN_KEY, response.data.upload_token)
  }

  return response.data
}

export const analyzeData = async (mapping) => {
  const response = await api.post(
    '/analyze',
    {
      ...mapping,
      upload_token: getStoredUploadToken(),
    },
    withUploadToken(),
  )
  return response.data
}

export const getElasticity = async () => {
  const response = await api.get('/elasticity', withUploadToken())
  return response.data
}

export const getOptimalPrice = async () => {
  const response = await api.get('/optimal-price', withUploadToken())
  return response.data
}

export const getCompetitor = async () => {
  const response = await api.get('/competitor', withUploadToken())
  return response.data
}

export const simulateDiscount = async (discountPct, elasticity) => {
  const response = await api.post(
    '/simulate',
    {
      type: 'discount',
      discount_pct: discountPct,
      elasticity,
      upload_token: getStoredUploadToken(),
    },
    withUploadToken(),
  )
  return response.data
}

export const simulateBundling = async (bundleDiscountPct) => {
  const response = await api.post(
    '/simulate',
    {
      type: 'bundling',
      bundle_discount_pct: bundleDiscountPct,
      upload_token: getStoredUploadToken(),
    },
    withUploadToken(),
  )
  return response.data
}

export const getHistory = async () => {
  const response = await api.get('/history')
  return response.data
}

export const clearUploadSession = () => {
  localStorage.removeItem(UPLOAD_TOKEN_KEY)
}
