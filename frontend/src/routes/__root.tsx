import { createRootRoute, Outlet } from "@tanstack/react-router"
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { ErrorBoundary } from "@/components/error/ErrorBoundary"

export const Route = createRootRoute({
  component: () => (
    <ErrorBoundary>
      <AuthGuard>
        <Outlet />
        <TanStackRouterDevtools />
      </AuthGuard>
    </ErrorBoundary>
  ),
})
