<script lang="ts">
  import { user } from "../lib/auth";
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { navigate } from "svelte-routing";

  let showTopUpModal = false;
  let loading = false;

  // Placeholder data
  let transactions = [
    { date: "2024-03-15", description: "PLACEHOLDER: Monthly credit", amount: 100 },
    { date: "2024-03-14", description: "PLACEHOLDER: Service usage", amount: -25 },
    { date: "2024-03-10", description: "PLACEHOLDER: Bonus credit", amount: 50 },
  ];

  onMount(() => {
    if (!$user) {
      navigate('/login', { replace: true });
      return;
    }
  });

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
</script>

{#if $user}
  <div class="space-y-8" in:fade>
    <!-- Profile Header -->
    <div class="bg-gradient-to-r from-secondary to-secondary/80 rounded-lg shadow-xl p-6 text-white">
      <div class="flex items-center space-x-6">
        <img
          src={$user.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent($user.name)}`}
          alt={$user.name}
          class="w-24 h-24 rounded-full border-4 border-white shadow-lg"
        />
        <div>
          <h1 class="text-3xl font-bold">{$user.name}</h1>
          <p class="text-white/80">{$user.email}</p>
          {#if $user.isAdmin}
            <span class="inline-flex items-center px-3 py-1 mt-2 rounded-full text-sm font-medium bg-primary text-white">
              Admin
            </span>
          {/if}
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Balance Card -->
      <div class="bg-white rounded-lg shadow-lg p-6" in:fly="{{ y: 50, duration: 500 }}">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold text-secondary">Balance</h2>
          <div class="text-3xl font-bold text-primary">$0.00</div>
        </div>
        <button
          class="w-full py-3 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed"
          disabled
        >
          Top Up Balance (Coming Soon)
        </button>
        <p class="text-sm text-gray-500 mt-2 text-center">Balance top-up feature will be available soon</p>
      </div>

      <!-- Usage Stats -->
      <div class="bg-white rounded-lg shadow-lg p-6" in:fly="{{ y: 50, duration: 500, delay: 200 }}">
        <h2 class="text-xl font-semibold text-secondary mb-6">Usage Statistics</h2>
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-600">Active Requests</span>
            <span class="font-semibold">{$user.activeRequests}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div
              class="bg-primary h-2.5 rounded-full"
              style="width: {($user.activeRequests / $user.maxRequests) * 100}%"
            ></div>
          </div>
          <div class="flex justify-between text-sm text-gray-500">
            <span>0</span>
            <span>{$user.maxRequests} max</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Account Tiers -->
    <div class="bg-white rounded-lg shadow-lg p-6" in:fly="{{ y: 50, duration: 500, delay: 300 }}">
      <h2 class="text-xl font-semibold text-secondary mb-6">Account Tier</h2>
      <div class="relative mb-8">
        <div class="flex items-center justify-between p-6 rounded-lg border-2 border-primary bg-gradient-to-r from-primary/5 to-white">
          <div class="flex items-center space-x-4">
            <div class="bg-primary/10 rounded-full p-3">
              <svg class="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-secondary">Basic Tier</h3>
              <p class="text-sm text-gray-600">Current active tier</p>
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-600">Monthly Limit</div>
            <div class="text-2xl font-bold text-secondary">$500</div>
          </div>
        </div>

        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-4 rounded-lg bg-gray-50">
            <h4 class="font-medium text-secondary mb-2">Tier Features</h4>
            <ul class="space-y-2">
              <li class="flex items-center text-gray-600">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Up to 3 concurrent requests
              </li>
              <li class="flex items-center text-gray-600">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                ~50 lines per request
              </li>
              <li class="flex items-center text-gray-600">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                No KYC required
              </li>
            </ul>
          </div>
          <div class="p-4 rounded-lg bg-gray-50">
            <h4 class="font-medium text-secondary mb-2">Available Upgrades</h4>
            <div class="space-y-3">
              <button class="w-full flex items-center justify-between p-3 rounded-lg border-2 border-secondary/20 hover:border-secondary bg-white transition-colors cursor-not-allowed" disabled>
                <span class="text-secondary font-medium">Pro Tier</span>
                <div class="text-right">
                  <div class="text-sm text-gray-600">Coming Soon</div>
                  <div class="text-xs text-secondary">Requires KYC</div>
                </div>
              </button>
              <button class="w-full flex items-center justify-between p-3 rounded-lg border-2 border-gray-200 hover:border-gray-900 bg-white transition-colors cursor-not-allowed" disabled>
                <span class="text-gray-900 font-medium">Enterprise Tier</span>
                <div class="text-right">
                  <div class="text-sm text-gray-600">Coming Soon</div>
                  <div class="text-xs text-gray-600">Contact us</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Subscription Options -->
      <div class="mt-8">
        <h2 class="text-xl font-semibold text-secondary mb-6">Subscription Options</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Basic Tier Subscription -->
          <div class="rounded-lg border-2 border-gray-200 p-6 bg-white hover:border-primary transition-colors flex flex-col h-full">
            <div class="text-center mb-4">
              <span class="inline-block px-3 py-1 rounded-full text-sm bg-primary/10 text-primary mb-2">Basic Tier</span>
              <div class="mt-2">
                <span class="text-3xl font-bold text-secondary">$350</span>
              </div>
              <p class="text-sm text-gray-500 mt-2">Get $500 worth of requests</p>
            </div>
            <div class="mt-4 space-y-2 text-sm text-gray-600 flex-grow">
              <p class="flex items-center">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                30% savings on requests
              </p>
              <p class="flex items-center">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Monthly subscription
              </p>
            </div>
            <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
              Coming Soon
            </button>
          </div>

          <!-- Pro Tier Subscription -->
          <div class="rounded-lg border-2 border-gray-200 p-6 bg-white hover:border-secondary transition-colors flex flex-col h-full">
            <div class="text-center mb-4">
              <span class="inline-block px-3 py-1 rounded-full text-sm bg-secondary/10 text-secondary mb-2">Pro Tier</span>
              <div class="mt-2">
                <span class="text-3xl font-bold text-secondary">$3,500</span>
              </div>
              <p class="text-sm text-gray-500 mt-2">Get $5,000 worth of requests</p>
            </div>
            <div class="mt-4 space-y-2 text-sm text-gray-600 flex-grow">
              <p class="flex items-center">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                30% savings on requests
              </p>
              <p class="flex items-center">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Monthly subscription
              </p>
            </div>
            <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
              Coming Soon
            </button>
          </div>

          <!-- Enterprise Subscription -->
          <div class="rounded-lg border-2 border-gray-200 p-6 bg-white hover:border-gray-900 transition-colors flex flex-col h-full">
            <div class="text-center mb-4">
              <span class="inline-block px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800 mb-2">Enterprise</span>
              <div class="mt-2">
                <span class="text-3xl font-bold text-secondary">Custom</span>
              </div>
              <p class="text-sm text-gray-500 mt-2">Tailored subscription plans</p>
            </div>
            <div class="mt-4 space-y-2 text-sm text-gray-600 flex-grow">
              <p class="flex items-center">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Volume discounts
              </p>
              <p class="flex items-center">
                <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Flexible terms
              </p>
            </div>
            <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="bg-white rounded-lg shadow-lg p-6" in:fly="{{ y: 50, duration: 500, delay: 400 }}">
      <h2 class="text-xl font-semibold text-gray-800 mb-6">Recent Transactions</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="text-left py-3 px-4 text-gray-600">Date</th>
              <th class="text-left py-3 px-4 text-gray-600">Description</th>
              <th class="text-right py-3 px-4 text-gray-600">Amount</th>
            </tr>
          </thead>
          <tbody>
            {#each transactions as transaction}
              <tr class="border-b border-gray-100 hover:bg-gray-50">
                <td class="py-3 px-4 text-gray-800">{formatDate(transaction.date)}</td>
                <td class="py-3 px-4 text-gray-800">{transaction.description}</td>
                <td class="py-3 px-4 text-right">
                  <span class={transaction.amount > 0 ? "text-green-600" : "text-red-600"}>
                    {transaction.amount > 0 ? "+" : ""}{transaction.amount.toFixed(2)}
                  </span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  </div>
{:else}
  <div class="text-center py-12">
    <p class="text-gray-600">Please log in to view your profile.</p>
  </div>
{/if}

<style>
  /* Add any custom styles here if needed */
</style> 
