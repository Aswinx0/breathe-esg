import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'

function Upload() {
  const [sourceType, setSourceType] = useState('SAP')
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file) return setMessage({ type: 'error', text: 'Please select a file' })
    const formData = new FormData()
    formData.append('source_type', sourceType)
    formData.append('file', file)
    setLoading(true)
    try {
      await axios.post(`${API}/upload/`, formData)
      setMessage({ type: 'success', text: 'File uploaded successfully!' })
      setFile(null)
    } catch (err) {
      setMessage({ type: 'error', text: 'Upload failed. Try again.' })
    }
    setLoading(false)
  }

  return (
    <div className="card">
      <h2>Upload Data</h2>
      <p style={{ marginBottom: 16, color: '#666' }}>
        Upload CSV files from SAP, utility portals, or travel platforms.
      </p>
      <div style={{ marginTop: 16 }}>
        <select value={sourceType} onChange={e => setSourceType(e.target.value)}>
          <option value="SAP">SAP - Fuel & Procurement</option>
          <option value="UTILITY">Utility - Electricity</option>
          <option value="TRAVEL">Corporate Travel</option>
        </select>
        <input
          type="file"
          accept=".csv"
          onChange={e => setFile(e.target.files[0])}
        />
        <button className="btn-upload" onClick={handleUpload} disabled={loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      {message && (
        <div className={`message message-${message.type}`}>
          {message.text}
        </div>
      )}
    </div>
  )
}

function Dashboard() {
  const [records, setRecords] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  const fetchRecords = async () => {
    try {
      const res = await axios.get(`${API}/records/`)
      setRecords(res.data)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchRecords()
  }, [])

  const handleReview = async (id, action) => {
    try {
      await axios.post(`${API}/records/${id}/review/`, { action })
      fetchRecords()
    } catch (err) {
      console.error(err)
    }
  }

  const filtered = filter === 'all' ? records : records.filter(r => r.status === filter)

  const counts = {
    all: records.length,
    pending: records.filter(r => r.status === 'pending').length,
    approved: records.filter(r => r.status === 'approved').length,
    rejected: records.filter(r => r.status === 'rejected').length,
  }

  return (
    <div className="card">
      <h2>Review Dashboard</h2>
      <div style={{ display: 'flex', gap: 12, margin: '16px 0' }}>
        {['all', 'pending', 'approved', 'rejected'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              background: filter === f ? '#1a1a2e' : '#eee',
              color: filter === f ? 'white' : '#333',
              padding: '6px 14px',
              border: 'none',
              borderRadius: 4,
              cursor: 'pointer'
            }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)} ({counts[f]})
          </button>
        ))}
        <button
          onClick={fetchRecords}
          style={{ marginLeft: 'auto', background: '#eee', color: '#333' }}
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : filtered.length === 0 ? (
        <p style={{ color: '#666' }}>No records found. Upload a file first.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Scope</th>
                <th>Category</th>
                <th>Activity</th>
                <th>CO2e (kg)</th>
                <th>EF Source</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(r => (
                <tr key={r.id}>
                  <td>{r.source_type}</td>
                  <td>Scope {r.scope}</td>
                  <td>{r.category}</td>
                  <td>{r.activity_value} {r.activity_unit}</td>
                  <td>{r.normalized_value}</td>
                  <td>{r.emission_factor_source}</td>
                  <td>
                    <span className={`badge badge-${r.status}`}>
                      {r.status}
                    </span>
                  </td>
                  <td>
                    {r.status === 'pending' && (
                      <>
                        <button className="btn-approve" onClick={() => handleReview(r.id, 'approved')}>
                          Approve
                        </button>
                        <button className="btn-reject" onClick={() => handleReview(r.id, 'rejected')}>
                          Reject
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [page, setPage] = useState('upload')

  return (
    <>
      <nav>
        <span>Breathe ESG</span>
        <span style={{ marginLeft: 32, fontSize: 14, fontWeight: 'normal' }}>
          <span
            onClick={() => setPage('upload')}
            style={{ cursor: 'pointer', marginRight: 20, opacity: page === 'upload' ? 1 : 0.6 }}
          >
            Upload
          </span>
          <span
            onClick={() => setPage('dashboard')}
            style={{ cursor: 'pointer', opacity: page === 'dashboard' ? 1 : 0.6 }}
          >
            Dashboard
          </span>
        </span>
      </nav>
      <div className="container">
        {page === 'upload' ? <Upload /> : <Dashboard />}
      </div>
    </>
  )
}