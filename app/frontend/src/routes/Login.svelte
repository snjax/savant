<script lang="ts">
  import { onMount } from 'svelte';
  import { user, isInitialized } from '../lib/auth';
  import { navigate } from 'svelte-routing';

  let buttonContainer: HTMLDivElement;
  let error: string | null = null;

  onMount(() => {
    // If user is already logged in, redirect to home
    if ($user) {
      navigate('/');
      return;
    }

    // Wait for auth to be initialized before rendering the button
    if ($isInitialized) {
      window.google.accounts.id.renderButton(buttonContainer, {
        theme: 'outline',
        size: 'large',
        type: 'standard',
        shape: 'rectangular',
        text: 'continue_with',
        logo_alignment: 'left'
      });
    }
  });

  $: if ($user) {
    navigate('/');
  }
</script>

<div class="flex h-full items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-secondary">
        Sign in to your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Please sign in with your Google account to continue
      </p>
    </div>

    {#if error}
      <div class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              Error signing in
            </h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    {/if}

    {#if !$isInitialized}
      <div class="flex justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
      </div>
    {:else}
      <div bind:this={buttonContainer} class="flex justify-center"></div>
    {/if}
  </div>
</div> 
