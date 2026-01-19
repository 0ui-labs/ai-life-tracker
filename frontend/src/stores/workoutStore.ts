import { create } from "zustand"

interface WorkoutState {
  isActive: boolean
  currentExercise: string | null
  currentSet: number
  lastWeight: number | null

  // Actions
  startWorkout: (exercise: string) => void
  endWorkout: () => void
  nextSet: () => void
  setExercise: (exercise: string) => void
  setWeight: (weight: number) => void
}

export const useWorkoutStore = create<WorkoutState>((set) => ({
  isActive: false,
  currentExercise: null,
  currentSet: 1,
  lastWeight: null,

  startWorkout: (exercise) =>
    set({
      isActive: true,
      currentExercise: exercise,
      currentSet: 1,
    }),

  endWorkout: () =>
    set({
      isActive: false,
      currentExercise: null,
      currentSet: 1,
      lastWeight: null,
    }),

  nextSet: () => set((state) => ({ currentSet: state.currentSet + 1 })),

  setExercise: (exercise) => set({ currentExercise: exercise, currentSet: 1 }),

  setWeight: (weight) => set({ lastWeight: weight }),
}))
