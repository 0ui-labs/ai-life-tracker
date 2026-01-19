const API_BASE = "/api"

let getTokenFn: (() => Promise<string | null>) | null = null

/**
 * Set the token getter function (called from React context).
 */
export function setTokenGetter(fn: () => Promise<string | null>) {
  getTokenFn = fn
}

export async function apiClient<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }

  // Merge existing headers
  if (options?.headers) {
    const existingHeaders = new Headers(options.headers)
    existingHeaders.forEach((value, key) => {
      headers[key] = value
    })
  }

  // Add auth token if available
  if (getTokenFn) {
    const token = await getTokenFn()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers,
    ...options,
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Unauthorized - please sign in")
    }
    throw new Error(`API Error: ${response.status}`)
  }

  return response.json()
}
