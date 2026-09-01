import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

const PROJECT_TYPE = ["web_application", "mobile_app", "landing_page"]
const DETAILS_LEVEL = ["summary","medium", "detailed"]
const OUTPUT_FORMAT = ["phases_table", "narrative"]

function App() {
  const [form, setForm] = useState({
    transcription: '',
    project_type: 'web_application',
    detail_level: 'detailed',
    output_format: 'phases_table',
  })

const [result, setResult] = useState(null)
const [loading, setLoading] = useState(false)
const [error, setError] = useState(null)

const updateField = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

const handleSubmit = async(e) => {
  e.preventDefault()
  if (form.transcription.trim().length < 50 ){
    setError('The transcription has to be more the 50 characters')
    return
  }
  setError(null)
  setLoading(true)

  try{
    const res = await fetch('api/v1/estimate', {
      method:'POST',
      headers: {'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    if (!res.ok) throw new Error(`Error ${res.status}`)
    const data = await res.json()
    setResult(data)
  }catch(error){
    setError(error.message)
  }finally{
    setLoading(false)
  }
}
  return (
    <div className="flex h-screen">
      <aside className="w-64 border-r p-4 flex flex-col gap-4">
        <h2 className="font-semibold">Modelo</h2>
        <p className="text-sm">{result?.model ?? 'No hay datos aún'}</p>

        <h2 className="font-semibold">Tokens</h2>
        {result?.usage ? (
          <ul className="text-sm space-y-1">
            <li>Input: {result.usage.input_tokens}</li>
            <li>Output: {result.usage.output_tokens}</li>
            <li>Total: {result.usage.total_tokens}</li>
          </ul>
        ) : (
          <p className="text-sm">No hay datos aún</p>
        )}
      </aside>

      <main className='flex flex-col flex-1 overflow-hidden' >
        <div className='flex-1 overflow-y-auto p-4'>
          {error && <p className='text-red-600'>{error}</p>}
          {result && <ReactMarkdown>{result.estimation}</ReactMarkdown>}
        </div>

        <form onSubmit={handleSubmit} className='border-t p-4 flex flex-col gap-3'>
          <div className='flex gap-3'>
            <select className='border rounded-lg p-2' value={form.project_type} onChange={updateField('project_type')}>
               {PROJECT_TYPE.map((v) => <option key={v} value={v}> {v} </option>)}
            </select>

            <select className='border rounded-lg p-2' value={form.detail_level} onChange={updateField('detail_level')}>
              {DETAILS_LEVEL.map((v) => <option key={v} value={v}> {v} </option>)}
            </select>

            <select className='border rounded-lg p-2' value={form.output_format} onChange={updateField('output_format')}>
              {OUTPUT_FORMAT.map((v) => <option key={v} value={v}> {v} </option>)}
            </select>
          </div>

          <div className='flex gap-3'>
            <textarea
              value={form.transcription}
              onChange={updateField('transcription')}
              placeholder='Paste the transcription here'
              className=' flex-1 resize-none border rounded-lg p-3 focus:outline-none'
              rows={6}
            />
            <button
              type="submit"
              disabled={loading}
              className='bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50'
            >
              {loading ? 'Loading...': 'Send'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}

export default App
