<script lang="ts">
  import { Router, Link, Route } from "svelte-routing";
  import { onMount } from "svelte";
  import { user, initializeAuth, logout } from "./lib/auth";
  import Login from "./routes/Login.svelte";
  import LiveFeed from "./routes/LiveFeed.svelte";
  import UserRequests from "./routes/UserRequests.svelte";
  import RequestDetailsPage from "./routes/RequestDetailsPage.svelte";
  import Profile from "./routes/Profile.svelte";
  import Pricing from "./routes/Pricing.svelte";

  let initialized = false;
  let isMenuOpen = false;

  $: currentPath = window.location.pathname;

  // TODO: How to make useLocation work in App.svelte?
  // Update path on navigation
  const handleNavigate = (event: MouseEvent) => {
    // Small delay to ensure the pathname is updated
    setTimeout(() => {
      currentPath = window.location.pathname;
    }, 0);
  };

  onMount(() => {
    const init = async () => {
      await initializeAuth();
      initialized = true;
    };
    
    init();
  });

  async function handleLogout() {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }

  $: isHome = currentPath === "/";
  $: isUserRequests = $user && currentPath === `/user/${$user.id}`;
</script>

{#if !initialized}
  <div class="flex h-screen items-center justify-center">
    <div class="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
  </div>
{:else}
  <Router>
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <Link to="/" class="flex-shrink-0 flex items-center" on:click={handleNavigate}>
              <h1 class="text-xl font-bold text-secondary">Savant</h1>
            </Link>
            <div class="ml-6 flex space-x-4">
              <Link
                to="/"
                on:click={handleNavigate}
                class="inline-flex items-center px-1 pt-1 text-sm font-medium {isHome ? 'text-secondary border-b-2 border-secondary' : 'text-gray-900 hover:text-secondary'}"
              >
                All Requests
              </Link>
              {#if $user}
                <Link
                  to={`/user/${$user.id}`}
                  on:click={handleNavigate}
                  class="inline-flex items-center px-1 pt-1 text-sm font-medium {isUserRequests ? 'text-secondary border-b-2 border-secondary' : 'text-gray-900 hover:text-secondary'}"
                >
                  My Requests
                </Link>
              {/if}
              <Link
                to="/pricing"
                on:click={handleNavigate}
                class="inline-flex items-center px-1 pt-1 text-sm font-medium {currentPath === '/pricing' ? 'text-secondary border-b-2 border-secondary' : 'text-gray-900 hover:text-secondary'}"
              >
                Pricing
              </Link>
            </div>
          </div>
          <div class="flex items-center">
            {#if $user}
              <div class="flex items-center mr-4">
                <Link
                  to="/profile"
                  class="flex items-center hover:opacity-75 transition-opacity"
                  on:click={handleNavigate}
                >
                  <div class="text-right mr-4">
                    <p class="text-sm font-medium text-gray-900">$0.00</p>
                    <p class="text-xs text-gray-500">Basic Tier</p>
                  </div>
                </Link>
              </div>
              <div class="relative">
                <button
                  on:click={() => isMenuOpen = !isMenuOpen}
                  class="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary"
                >
                  <img
                    class="h-8 w-8 rounded-full"
                    src={$user.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent($user.name)}`}
                    alt={$user.name}
                  />
                </button>
                {#if isMenuOpen}
                  <div
                    class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 z-50"
                    role="menu"
                  >
                    <Link
                      to="/profile"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-secondary/10"
                      role="menuitem"
                      on:click={(e) => {
                        isMenuOpen = false;
                        handleNavigate(e);
                      }}
                    >
                      Profile
                    </Link>
                    <Link
                      to={`/user/${$user.id}`}
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-secondary/10"
                      role="menuitem"
                      on:click={(e) => {
                        isMenuOpen = false;
                        handleNavigate(e);
                      }}
                    >
                      My Requests
                    </Link>
                    <button
                      on:click={handleLogout}
                      class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-secondary/10"
                      role="menuitem"
                    >
                      Sign out
                    </button>
                  </div>
                {/if}
              </div>
            {:else}
              <Link
                to="/login"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-hover"
              >
                Sign In
              </Link>
            {/if}
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Route path="/login" component={Login} />
      <Route path="/" component={LiveFeed} />
      <Route path="/user/:userId" component={UserRequests} />
      <Route path="/request/:requestId" component={RequestDetailsPage} />
      <Route path="/profile" component={Profile} />
      <Route path="/pricing" component={Pricing} />
    </main>

    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-auto">
      <p class="text-center text-gray-600">
        Want to work together or have questions? Feel free to reach out to 
        <a href="https://t.me/AlexandraGulamova" class="text-secondary hover:text-secondary-hover underline" target="_blank" rel="noopener noreferrer">Alexandra Gulamova</a>
      </p>
    </footer>
  </Router>
{/if} 
