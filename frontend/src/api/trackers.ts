import { apiClient } from "./client"

// =============================================================================
// Types
// =============================================================================

export interface Tracker {
  id: string
  name: string
  category: string
  schema: Record<string, unknown>
  icon: string | null
  color: string | null
  created_at: string
}

export interface TrackerCreate {
  name: string
  category: string
  schema?: Record<string, unknown>
  icon?: string | null
  color?: string | null
}

export interface TrackerUpdate {
  name?: string
  category?: string
  schema?: Record<string, unknown>
  icon?: string | null
  color?: string | null
}

export interface Entry {
  id: string
  tracker_id: string
  data: Record<string, unknown>
  notes: string | null
  timestamp: string
  created_at: string
}

export interface EntryCreate {
  data: Record<string, unknown>
  notes?: string | null
  timestamp?: string
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Get all trackers for the current user.
 */
export async function getTrackers(): Promise<Tracker[]> {
  return apiClient<Tracker[]>("/trackers")
}

/**
 * Get a single tracker by ID.
 */
export async function getTracker(trackerId: string): Promise<Tracker> {
  return apiClient<Tracker>(`/trackers/${trackerId}`)
}

/**
 * Create a new tracker.
 */
export async function createTracker(data: TrackerCreate): Promise<Tracker> {
  return apiClient<Tracker>("/trackers", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

/**
 * Update an existing tracker.
 */
export async function updateTracker(trackerId: string, data: TrackerUpdate): Promise<Tracker> {
  return apiClient<Tracker>(`/trackers/${trackerId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  })
}

/**
 * Delete a tracker.
 */
export async function deleteTracker(trackerId: string): Promise<{ message: string }> {
  return apiClient<{ message: string }>(`/trackers/${trackerId}`, {
    method: "DELETE",
  })
}

/**
 * Get entries for a tracker.
 */
export async function getTrackerEntries(trackerId: string, limit = 50): Promise<Entry[]> {
  return apiClient<Entry[]>(`/trackers/${trackerId}/entries?limit=${limit}`)
}

/**
 * Create a new entry for a tracker.
 */
export async function createEntry(trackerId: string, data: EntryCreate): Promise<Entry> {
  return apiClient<Entry>(`/trackers/${trackerId}/entries`, {
    method: "POST",
    body: JSON.stringify(data),
  })
}
