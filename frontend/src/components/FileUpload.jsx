import { useState } from 'react'
import { uploadFile } from '../services/api'

function FileUpload({ onUploadSuccess }) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFile = async (file) => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const result = await uploadFile(file)
      onUploadSuccess(result)
    } catch (err) {
      setError('Failed to upload file. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleChange = (e) => {
    const file = e.target.files[0]
    handleFile(file)
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`panel panel-grid rounded-[2rem] border border-dashed p-10 text-center transition-all duration-200 sm:p-14 ${
        dragging
          ? 'border-cyan-300/50 bg-cyan-400/10'
          : 'border-white/10 hover:border-cyan-300/30'
      }`}
    >
      <div className="flex flex-col items-center gap-5">
        <div className="flex h-16 w-16 items-center justify-center rounded-[1.5rem] border border-cyan-300/20 bg-cyan-400/10 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-100">
          Data
        </div>
        <div className="space-y-2">
          <p className="text-2xl font-semibold text-white">
            Drop your CSV or Excel file here
          </p>
          <p className="section-subtitle mx-auto">
            Import pricing, sales, and competitor data to unlock the analysis workspace.
          </p>
        </div>

        <input
          type="file"
          accept=".csv,.xlsx"
          onChange={handleChange}
          className="hidden"
          id="file-input"
        />
        <label
          htmlFor="file-input"
          className="primary-button cursor-pointer"
        >
          Select file
        </label>

        <p className="micro-copy">
          Supported formats: CSV, XLSX
        </p>

        {loading && (
          <div className="flex items-center gap-2 text-cyan-200">
            <div className="h-5 w-5 animate-spin rounded-full border-b-2 border-cyan-300"></div>
            <span>Uploading...</span>
          </div>
        )}

        {error && (
          <p className="text-sm text-rose-300">{error}</p>
        )}
      </div>
    </div>
  )
}

export default FileUpload
