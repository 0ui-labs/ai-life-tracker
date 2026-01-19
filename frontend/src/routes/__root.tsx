import { createRootRoute, Outlet } from "@tanstack/react-router"
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools"
import { AuthGuard } from "@/components/auth/AuthGuard"

export const Route = createRootRoute({
  component: () => (
    <AuthGuard>
      <Outlet />
      <TanStackRouterDevtools />
    </AuthGuard>
  ),
})
