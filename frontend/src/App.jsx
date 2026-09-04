import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

const PROJECT_TYPE_LABELS = {
  web_application: 'Web application',
  mobile_app: 'Mobile app',
  landing_page: 'Landing page',
}
const DETAIL_LEVEL_LABELS = {
  summary: 'Summary',
  medium: 'Medium',
  detailed: 'Detailed',
}
const OUTPUT_FORMAT_LABELS = {
  phases_table: 'Phases table',
  narrative: 'Narrative',
}

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

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.transcription.trim().length < 50) {
      setError('The transcription has to be more than 50 characters')
      return
    }
    setError(null)
    setLoading(true)

    try {
      const res = await fetch('/api/v1/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error(`Error ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900">
      <aside className="hidden w-72 flex-col gap-6 border-r border-slate-200 bg-white p-6 sm:flex">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Estimador de Proyectos</h1>
          <p className="mt-1 text-sm text-slate-500">
            Genera una estimación estructurada a partir de la transcripción de una reunión.
          </p>
        </div>

        <div className="space-y-3">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Modelo</p>
            <p className="mt-1 truncate font-mono text-sm text-slate-700">{result?.model ?? '—'}</p>
            {result?.provider && (
              <span className="mt-2 inline-block rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">
                {result.provider}
              </span>
            )}
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Tokens</p>
            {result?.usage ? (
              <dl className="mt-2 space-y-1 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-500">Input</dt>
                  <dd className="font-mono">{result.usage.input_tokens}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Output</dt>
                  <dd className="font-mono">{result.usage.output_tokens}</dd>
                </div>
                <div className="flex justify-between border-t border-slate-200 pt-1 font-medium">
                  <dt>Total</dt>
                  <dd className="font-mono">{result.usage.total_tokens}</dd>
                </div>
              </dl>
            ) : (
              <p className="mt-2 text-sm text-slate-400">Sin datos aún</p>
            )}
          </div>

          {result?.prompt_version && (
            <p className="px-1 text-xs text-slate-400">prompt v{result.prompt_version}</p>
          )}
        </div>
      </aside>

      <main className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          {!result && !error && (
            <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center text-slate-400">
              <p className="text-sm">Pega la transcripción de una reunión abajo para generar una estimación.</p>
            </div>
          )}

          {error && (
            <div className="mx-auto mt-6 max-w-3xl rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {result?.data && (
            <div className="mx-auto max-w-3xl px-6 py-8">
              <h2 className="text-2xl font-semibold tracking-tight">{result.data.title}</h2>

              <div className="mt-4 grid grid-cols-3 gap-3">
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <p className="text-xs font-medium uppercase text-slate-400">Horas</p>
                  <p className="mt-1 text-xl font-semibold">{result.data.total_hours}</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <p className="text-xs font-medium uppercase text-slate-400">Coste</p>
                  <p className="mt-1 text-xl font-semibold">{result.data.total_cost_eur.toLocaleString()} €</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <p className="text-xs font-medium uppercase text-slate-400">Duración</p>
                  <p className="mt-1 text-xl font-semibold">{result.data.duration_weeks} sem</p>
                </div>
              </div>

              <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-4 py-2 font-medium">Fase</th>
                      <th className="px-4 py-2 text-right font-medium">Horas</th>
                      <th className="px-4 py-2 text-right font-medium">Coste</th>
                      <th className="px-4 py-2 text-right font-medium">Confianza</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {result.data.phases.map((p) => (
                      <tr key={p.name} className="odd:bg-white even:bg-slate-50/50">
                        <td className="px-4 py-2">{p.name}</td>
                        <td className="px-4 py-2 text-right font-mono">{p.hours}h</td>
                        <td className="px-4 py-2 text-right font-mono">{p.cost_eur.toLocaleString()} €</td>
                        <td className="px-4 py-2 text-right">
                          {p.confidence_pct != null ? (
                            <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
                              {p.confidence_pct}%
                            </span>
                          ) : (
                            '—'
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {result.data.narrative && (
                <div className="mt-6 text-sm leading-relaxed text-slate-700 [&_h1]:mb-2 [&_h1]:mt-4 [&_h1]:text-lg [&_h1]:font-semibold [&_h2]:mb-2 [&_h2]:mt-4 [&_h2]:text-base [&_h2]:font-semibold [&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-5 [&_p]:mb-3 [&_strong]:font-semibold [&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-5">
                  <ReactMarkdown>{result.data.narrative}</ReactMarkdown>
                </div>
              )}

              <div className="mt-6">
                <p className="text-xs font-medium uppercase text-slate-400">Equipo</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.data.team.map((member) => (
                    <span
                      key={member}
                      className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-600"
                    >
                      {member}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-white p-4">
          <div className="mx-auto flex max-w-3xl flex-col gap-3">
            <div className="flex flex-wrap gap-2">
              <select
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none"
                value={form.project_type}
                onChange={updateField('project_type')}
              >
                {Object.entries(PROJECT_TYPE_LABELS).map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>

              <select
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none"
                value={form.detail_level}
                onChange={updateField('detail_level')}
              >
                {Object.entries(DETAIL_LEVEL_LABELS).map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>

              <select
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none"
                value={form.output_format}
                onChange={updateField('output_format')}
              >
                {Object.entries(OUTPUT_FORMAT_LABELS).map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-3">
              <textarea
                value={form.transcription}
                onChange={updateField('transcription')}
                placeholder="Pega aquí la transcripción de la reunión..."
                className="flex-1 resize-none rounded-lg border border-slate-300 p-3 text-sm focus:border-indigo-500 focus:outline-none"
                rows={4}
              />
              <button
                type="submit"
                disabled={loading}
                className="shrink-0 self-end rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? 'Generando…' : 'Estimar'}
              </button>
            </div>
          </div>
        </form>
      </main>
    </div>
  )
}

export default App