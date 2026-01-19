/// <reference types="@testing-library/jest-dom/vitest" />
import { cleanup, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { ErrorBoundary } from "./ErrorBoundary"

// Component that throws an error for testing
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error("Test error message")
  }
  return <div>No error</div>
}

// Suppress console.error during tests since we expect errors
const originalError = console.error

beforeEach(() => {
  console.error = vi.fn()
})

afterEach(() => {
  console.error = originalError
  cleanup()
})

describe("ErrorBoundary", () => {
  describe("when no error occurs", () => {
    it("renders_children_normally_when_no_error", () => {
      render(
        <ErrorBoundary>
          <div>Child content</div>
        </ErrorBoundary>,
      )

      expect(screen.getByText("Child content")).toBeInTheDocument()
    })
  })

  describe("when an error occurs", () => {
    it("renders_fallback_ui_when_child_throws_error", () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>,
      )

      expect(screen.getByText(/etwas ist schiefgelaufen/i)).toBeInTheDocument()
    })

    it("displays_error_message_in_fallback_ui", () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>,
      )

      expect(screen.getByText("Test error message")).toBeInTheDocument()
    })

    it("renders_retry_button_in_fallback_ui", () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>,
      )

      expect(screen.getByRole("button", { name: /erneut versuchen/i })).toBeInTheDocument()
    })

    it("resets_error_state_when_retry_button_clicked", async () => {
      const user = userEvent.setup()
      let shouldThrow = true

      function ControlledThrow() {
        if (shouldThrow) {
          throw new Error("Controlled error")
        }
        return <div>Recovered content</div>
      }

      const { rerender } = render(
        <ErrorBoundary>
          <ControlledThrow />
        </ErrorBoundary>,
      )

      // Error state should be shown
      expect(screen.getByText(/etwas ist schiefgelaufen/i)).toBeInTheDocument()

      // Fix the error condition
      shouldThrow = false

      // Click retry button
      await user.click(screen.getByRole("button", { name: /erneut versuchen/i }))

      // Rerender to trigger the reset
      rerender(
        <ErrorBoundary>
          <ControlledThrow />
        </ErrorBoundary>,
      )

      // Should show recovered content
      expect(screen.getByText("Recovered content")).toBeInTheDocument()
    })
  })

  describe("custom fallback", () => {
    it("renders_custom_fallback_when_provided", () => {
      const customFallback = <div>Custom error view</div>

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>,
      )

      expect(screen.getByText("Custom error view")).toBeInTheDocument()
    })
  })

  describe("onError callback", () => {
    it("calls_onError_callback_when_error_occurs", () => {
      const onError = vi.fn()

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>,
      )

      expect(onError).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledWith(
        expect.objectContaining({ message: "Test error message" }),
        expect.objectContaining({ componentStack: expect.any(String) }),
      )
    })
  })
})
