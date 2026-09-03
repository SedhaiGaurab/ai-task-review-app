import { useEffect, useState } from 'react'
import { analyseTask, createTask, deleteTask, getTasks, updateTaskStatus } from './api/taskApi'
import './App.css'

const statuses = ['ALL', 'NEW', 'IN_PROGRESS', 'COMPLETED']

function App() {
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ title: '', description: '', priority: 'MEDIUM' })
  const [creating, setCreating] = useState(false)
  const [analysingId, setAnalysingId] = useState(null)
  const [analysis, setAnalysis] = useState(null)

  async function loadTasks(selectedFilter = filter) {
    setLoading(true)
    setError('')
    try { setTasks(await getTasks(selectedFilter)) } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }

  useEffect(() => {
    let active = true
    getTasks().then((loadedTasks) => {
      if (active) setTasks(loadedTasks)
    }).catch((requestError) => {
      if (active) setError(requestError.message)
    }).finally(() => {
      if (active) setLoading(false)
    })
    return () => { active = false }
  }, [])

  async function handleCreate(event) {
    event.preventDefault()
    setCreating(true)
    setError('')
    try {
      const newTask = await createTask(form)
      setTasks((currentTasks) => [newTask, ...currentTasks])
      setForm({ title: '', description: '', priority: 'MEDIUM' })
    } catch (requestError) { setError(requestError.message) } finally { setCreating(false) }
  }

  async function handleStatusChange(taskId, status) {
    setError('')
    try {
      const updatedTask = await updateTaskStatus(taskId, status)
      setTasks((currentTasks) => currentTasks.map((task) => task.id === taskId ? updatedTask : task))
    } catch (requestError) { setError(requestError.message) }
  }

  async function handleAnalysis(task) {
    setAnalysingId(task.id)
    setAnalysis(null)
    setError('')
    try { setAnalysis({ task, result: await analyseTask(task.id) }) } catch (requestError) { setError(requestError.message) } finally { setAnalysingId(null) }
  }

  async function handleDelete(task) {
    if (!window.confirm(`Delete "${task.title}"? This cannot be undone.`)) return
    setError('')
    try {
      await deleteTask(task.id)
      setTasks((currentTasks) => currentTasks.filter((currentTask) => currentTask.id !== task.id))
      if (analysis?.task.id === task.id) setAnalysis(null)
    } catch (requestError) { setError(requestError.message) }
  }

  function chooseFilter(nextFilter) { setFilter(nextFilter); loadTasks(nextFilter) }

  const completedCount = tasks.filter((task) => task.status === 'COMPLETED').length
  const visibleTasks = filter === 'ALL' ? tasks : tasks.filter((task) => task.status === filter)

  return (
    <main className="app-shell">
      <header className="topbar"><div className="brand-mark">TR</div><div><p className="eyebrow">Personal operations desk</p><h1>Task Review</h1></div><div className="api-status"><span /> API connected</div></header>
      <section className="intro"><div><p className="eyebrow">Today&apos;s workspace</p><h2>Make progress visible.</h2><p className="intro-copy">Capture the next thing, keep its status honest, and ask AI for a second opinion when a task needs more thought.</p></div><div className="stats"><div><strong>{tasks.length}</strong><span>total tasks</span></div><div><strong>{completedCount}</strong><span>completed</span></div></div></section>
      {error && <div className="error-banner" role="alert">{error}</div>}
      <section className="workspace">
        <div className="task-panel"><div className="panel-heading"><div><p className="eyebrow">Your queue</p><h2>Tasks</h2></div><button className="refresh-button" type="button" onClick={() => loadTasks()} title="Refresh tasks" aria-label="Refresh tasks">↻</button></div>
          <nav className="filters" aria-label="Filter tasks">{statuses.map((status) => <button key={status} className={filter === status ? 'active' : ''} type="button" onClick={() => chooseFilter(status)}>{status.replace('_', ' ')}</button>)}</nav>
          <div className="task-list">{loading ? <p className="empty-state">Loading your tasks...</p> : visibleTasks.length === 0 ? <p className="empty-state">Nothing here yet. Add a task to get moving.</p> : visibleTasks.map((task) => <article className={`task-card ${task.status === 'COMPLETED' ? 'is-complete' : ''}`} key={task.id}><div className="task-card-top"><span className={`priority priority-${task.priority.toLowerCase()}`}>{task.priority}</span><time>{new Date(task.createdAt).toLocaleDateString()}</time></div><h3>{task.title}</h3><p>{task.description}</p><div className="task-actions"><select value={task.status} onChange={(event) => handleStatusChange(task.id, event.target.value)} aria-label={`Status for ${task.title}`}>{statuses.slice(1).map((status) => <option key={status} value={status}>{status.replace('_', ' ')}</option>)}</select><div className="task-buttons"><button className="text-button" type="button" onClick={() => handleAnalysis(task)} disabled={analysingId === task.id}>{analysingId === task.id ? 'Thinking...' : 'Analyse task'}</button><button className="delete-button" type="button" onClick={() => handleDelete(task)} aria-label={`Delete ${task.title}`} title="Delete task">Delete</button></div></div></article>)}</div>
        </div>
        <aside className="side-panel"><section className="form-section"><p className="eyebrow">Add to the queue</p><h2>New task</h2><form onSubmit={handleCreate}><label>What needs doing?<input required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} placeholder="e.g. Book a haircut" /></label><label>Details<textarea required value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Add enough context for future you..." rows="4" /></label><label>Priority<select value={form.priority} onChange={(event) => setForm({ ...form, priority: event.target.value })}>{['LOW', 'MEDIUM', 'HIGH'].map((priority) => <option key={priority}>{priority}</option>)}</select></label><button className="primary-button" type="submit" disabled={creating}>{creating ? 'Adding task...' : 'Add task'} <span>→</span></button></form></section>{analysis && <section className="analysis-section"><div className="analysis-heading"><p className="eyebrow">AI review</p><span>OpenRouter</span></div><h2>{analysis.result.category.replaceAll('_', ' ')}</h2><p className="analysis-summary">{analysis.result.summary}</p><div className="recommendation"><strong>Recommended next step</strong><p>{analysis.result.recommendedAction}</p></div><button className="close-button" type="button" onClick={() => setAnalysis(null)}>Dismiss</button></section>}</aside>
      </section>
    </main>
  )
}

export default App
