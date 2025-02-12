<script lang="ts">
  import { fade, fly } from "svelte/transition";
  import { user } from "../lib/auth";
</script>

<div class="space-y-12" in:fade>
  <!-- Hero Section -->
  <div class="text-center">
    <h1 class="text-4xl font-bold text-secondary mb-4">Simple, Transparent Pricing</h1>
    <p class="text-xl text-gray-600 max-w-2xl mx-auto">
      Pay only for what you use, with flexible options for every need
    </p>
  </div>

  <!-- Per-Line Pricing -->
  <div class="bg-white rounded-lg shadow-lg p-8" in:fly="{{ y: 50, duration: 500 }}">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-secondary mb-4">Pay-As-You-Go Pricing</h2>
      <div class="flex items-center justify-center space-x-2">
        <span class="text-5xl font-bold text-primary">$1</span>
        <div class="text-left">
          <span class="text-gray-600">per</span>
          <br />
          <span class="text-gray-600">line of code</span>
        </div>
      </div>
      <p class="mt-4 text-gray-600 max-w-xl mx-auto">
        Approximately $1/line, with final pricing based on actual token count after upload.
      </p>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
      <div class="bg-gray-50 rounded-lg p-6 flex items-start">
        <div class="flex-shrink-0">
          <div class="flex items-center justify-center h-12 w-12 rounded-md bg-primary text-white">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <h3 class="text-lg font-medium text-secondary mb-2">Accelerate Your Audit Process</h3>
          <p class="text-gray-600">AI-powered analysis helps both auditors and development teams spot vulnerabilities faster and streamline their workflow</p>
        </div>
      </div>

      <div class="bg-gray-50 rounded-lg p-6 flex items-start">
        <div class="flex-shrink-0">
          <div class="flex items-center justify-center h-12 w-12 rounded-md bg-primary text-white">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <h3 class="text-lg font-medium text-secondary mb-2">Instant Results</h3>
          <p class="text-gray-600">Get comprehensive analysis in minutes, not weeks, enabling rapid iteration and deployment</p>
        </div>
      </div>

      <div class="bg-gray-50 rounded-lg p-6 flex items-start">
        <div class="flex-shrink-0">
          <div class="flex items-center justify-center h-12 w-12 rounded-md bg-primary text-white">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <h3 class="text-lg font-medium text-secondary mb-2">Transparent Pricing</h3>
          <p class="text-gray-600">See the exact price when you upload your contracts</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Account Tiers -->
  <div class="bg-white rounded-lg shadow-lg p-8" in:fly="{{ y: 50, duration: 500, delay: 100 }}">
    <h2 class="text-2xl font-bold text-secondary mb-8 text-center">Account Tiers</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Basic Tier -->
      <div class="border-2 border-gray-200 rounded-lg p-6 hover:border-primary transition-colors">
        <div class="text-center">
          <span class="inline-block px-4 py-1 rounded-full text-sm bg-primary/10 text-primary">Basic</span>
          <div class="mt-4">
            <p class="text-gray-500">Monthly Limit</p>
            <p class="text-4xl font-bold text-secondary">$500</p>
          </div>
        </div>
        <ul class="mt-6 space-y-4">
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Standard audit queue
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            150 lines welcome pack included for free
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            No KYC required
          </li>
        </ul>
        {#if !$user}
          <button class="block w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
            Coming Soon
          </button>
        {/if}
      </div>

      <!-- Pro Tier -->
      <div class="border-2 border-gray-200 rounded-lg p-6 hover:border-secondary transition-colors">
        <div class="text-center">
          <span class="inline-block px-4 py-1 rounded-full text-sm bg-secondary/10 text-secondary">Pro</span>
          <div class="mt-4">
            <p class="text-gray-500">Monthly Limit</p>
            <p class="text-4xl font-bold text-secondary">$5,000</p>
          </div>
        </div>
        <ul class="mt-6 space-y-4">
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Priority audit processing
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Unlimited lines per request
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Priority support
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            KYC required
          </li>
        </ul>
        <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
          Coming Soon
        </button>
      </div>

      <!-- Enterprise Tier -->
      <div class="border-2 border-gray-200 rounded-lg p-6 hover:border-gray-900 transition-colors">
        <div class="text-center">
          <span class="inline-block px-4 py-1 rounded-full text-sm bg-gray-100 text-gray-800">Enterprise</span>
          <div class="mt-4">
            <p class="text-gray-500">Monthly Limit</p>
            <p class="text-4xl font-bold text-secondary">Custom</p>
          </div>
        </div>
        <ul class="mt-6 space-y-4">
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Expedited audit pipeline
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Custom volume discounts
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Dedicated support
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Custom integration options
          </li>
        </ul>
        <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
          Coming Soon
        </button>
      </div>
    </div>
  </div>

  <!-- Subscription Options -->
  <div class="bg-white rounded-lg shadow-lg p-8" in:fly="{{ y: 50, duration: 500, delay: 200 }}">
    <h2 class="text-2xl font-bold text-secondary mb-8 text-center">Subscription Plans</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Basic Subscription -->
      <div class="border-2 border-gray-200 rounded-lg p-6 hover:border-primary transition-colors flex flex-col h-full">
        <div class="text-center mb-4">
          <span class="inline-block px-4 py-1 rounded-full text-sm bg-primary/10 text-primary">Basic Tier</span>
          <div class="mt-4">
            <span class="text-4xl font-bold text-secondary">$350</span>
          </div>
          <p class="text-gray-500 mt-2">Get $500 worth of requests</p>
        </div>
        <ul class="mt-6 space-y-4 flex-grow">
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            30% savings on requests
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Monthly subscription
          </li>
        </ul>
        <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
          Coming Soon
        </button>
      </div>

      <!-- Pro Subscription -->
      <div class="border-2 border-gray-200 rounded-lg p-6 hover:border-secondary transition-colors flex flex-col h-full">
        <div class="text-center mb-4">
          <span class="inline-block px-4 py-1 rounded-full text-sm bg-secondary/10 text-secondary">Pro Tier</span>
          <div class="mt-4">
            <span class="text-4xl font-bold text-secondary">$3,500</span>
          </div>
          <p class="text-gray-500 mt-2">Get $5,000 worth of requests</p>
        </div>
        <ul class="mt-6 space-y-4 flex-grow">
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            30% savings on requests
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Monthly subscription
          </li>
        </ul>
        <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
          Coming Soon
        </button>
      </div>

      <!-- Enterprise Subscription -->
      <div class="border-2 border-gray-200 rounded-lg p-6 hover:border-gray-900 transition-colors flex flex-col h-full">
        <div class="text-center mb-4">
          <span class="inline-block px-4 py-1 rounded-full text-sm bg-gray-100 text-gray-800">Enterprise</span>
          <div class="mt-4">
            <span class="text-4xl font-bold text-secondary">Custom</span>
          </div>
          <p class="text-gray-500 mt-2">Contact us for custom pricing</p>
        </div>
        <ul class="mt-6 space-y-4 flex-grow">
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Custom volume discounts
          </li>
          <li class="flex items-center text-gray-600">
            <svg class="h-5 w-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Annual billing available
          </li>
        </ul>
        <button class="w-full mt-6 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed" disabled>
          Contact Us
        </button>
      </div>
    </div>
  </div>

  <!-- FAQ Section -->
  <div class="bg-white rounded-lg shadow-lg p-8" in:fly="{{ y: 50, duration: 500, delay: 300 }}">
    <h2 class="text-2xl font-bold text-gray-900 mb-8 text-center">Frequently Asked Questions</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">How is the price calculated?</h3>
        <p class="text-gray-600">While we show approximate pricing based on lines of code, the final price is calculated based on the actual token count in your smart contracts. You'll see the exact price when you upload your files.</p>
      </div>
      <div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">What payment methods do you accept?</h3>
        <p class="text-gray-600">Currently, we're working on implementing various payment methods. Please contact us for available options.</p>
      </div>
      <div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Can I upgrade my tier later?</h3>
        <p class="text-gray-600">Yes, you can upgrade your tier at any time. Contact our support team for assistance with the upgrade process.</p>
      </div>
      <div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">What's included in the audit?</h3>
        <p class="text-gray-600">Our AI performs comprehensive security analysis of your Solidity smart contracts, focusing on identifying potential vulnerabilities and security issues.</p>
      </div>
    </div>
  </div>
</div> 
