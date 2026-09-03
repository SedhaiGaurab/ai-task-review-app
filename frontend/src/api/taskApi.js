const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, { headers: { 'Content-Type': 'application/json', ...options.headers }, ...options })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed with status ${response.status}`)
  }
  if (response.status === 204) return null
  return response.json()
}

export function getTasks(status = 'ALL') { return request(`/tasks/${status === 'ALL' ? '' : `?status=${status}`}`) }
export function createTask(task) { return request('/tasks/', { method: 'POST', body: JSON.stringify(task) }) }
export function updateTaskStatus(taskId, status) { return request(`/tasks/${taskId}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }) }
export function analyseTask(taskId) { return request(`/tasks/${taskId}/analyse`, { method: 'POST' }) }
export function deleteTask(taskId) { return request(`/tasks/${taskId}`, { method: 'DELETE' }) }