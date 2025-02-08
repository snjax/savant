<script lang="ts">
  import { onMount } from 'svelte';

  let buttonContainer: HTMLDivElement;

  onMount(() => {
    window.google.accounts.id.renderButton(buttonContainer, {
      theme: 'outline',
      size: 'large',
    });
  });
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Sign in to your account
      </h2>
    </div>
    <div bind:this={buttonContainer} class="flex justify-center"></div>
  </div>
</div> 
