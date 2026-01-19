import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
  useAuth,
} from "@clerk/clerk-react"
import { useEffect } from "react"
import { setTokenGetter } from "@/api/client"

/**
 * Sets up auth token for API requests and provides sign in/out UI.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth()

  // Set up token getter for API client
  useEffect(() => {
    setTokenGetter(getToken)
  }, [getToken])

  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <div className="flex h-screen flex-col items-center justify-center gap-6 bg-background">
          <div className="text-center">
            <h1 className="text-3xl font-bold">AI Life Tracker</h1>
            <p className="mt-2 text-muted-foreground">
              Voice-first AI-powered life tracking
            </p>
          </div>
          <SignInButton mode="modal">
            <button
              type="button"
              className="rounded-lg bg-primary px-6 py-3 font-medium text-primary-foreground hover:bg-primary/90"
            >
              Sign in to get started
            </button>
          </SignInButton>
        </div>
      </SignedOut>
    </>
  )
}

/**
 * User avatar button for the header.
 */
export function AuthUserButton() {
  return (
    <SignedIn>
      <UserButton
        appearance={{
          elements: {
            avatarBox: "h-8 w-8",
          },
        }}
      />
    </SignedIn>
  )
}
