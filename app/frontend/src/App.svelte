<script lang="ts">
  import { Router, Link, Route } from "svelte-routing";
  import { onMount } from "svelte";
  import { user, initializeAuth, logout } from "./lib/auth";
  import Login from "./routes/Login.svelte";
  import LiveFeed from "./routes/LiveFeed.svelte";
  import UserRequests from "./routes/UserRequests.svelte";

  let initialized = false;
  let isMenuOpen = false;

  onMount(async () => {
    await initializeAuth();
    initialized = true;
  });

  async function handleLogout() {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }
</script>

{#if !initialized}
  <div class="flex h-screen items-center justify-center">
    <div class="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
  </div>
{:else}
  <Router>
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <Link to="/" class="flex-shrink-0 flex items-center">
              <h1 class="text-xl font-bold text-gray-900">Savant</h1>
            </Link>
          </div>
          {#if $user}
            <div class="flex items-center">
              <div class="relative">
                <button
                  on:click={() => isMenuOpen = !isMenuOpen}
                  class="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <img
                    class="h-8 w-8 rounded-full"
                    src={$user.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent($user.name)}`}
                    alt={$user.name}
                  />
                </button>
                {#if isMenuOpen}
                  <div
                    class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5"
                    role="menu"
                  >
                    <Link
                      to={`/user/${$user.id}`}
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      role="menuitem"
                      on:click={() => isMenuOpen = false}
                    >
                      My Requests
                    </Link>
                    <button
                      on:click={handleLogout}
                      class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      role="menuitem"
                    >
                      Sign out
                    </button>
                  </div>
                {/if}
              </div>
            </div>
          {/if}
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Route path="/login" component={Login} />
      <Route path="/" component={LiveFeed} />
      <Route path="/user/:userId" component={UserRequests} />
    </main>
  </Router>
{/if} 
