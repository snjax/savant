<script lang="ts">
  export let isOpen = false;
  export let onClose: () => void;
  export let title: string;

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }
</script>

{#if isOpen}
  <div
    class="fixed top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50 flex items-center justify-center [&:not(:first-child)]:!ml-0 z-[9999]"
    on:click={handleBackdropClick}
  >
    <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 relative">
      <button
        class="absolute top-4 right-4 text-gray-500 hover:text-secondary"
        on:click={onClose}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      
      <h2 class="text-xl font-semibold mb-4 text-secondary">{title}</h2>
      
      <div class="mt-2">
        <slot />
      </div>
    </div>
  </div>
{/if} 
