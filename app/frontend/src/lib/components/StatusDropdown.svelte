<script lang="ts">
  import { slide } from 'svelte/transition';
  import { clickOutside } from '../utils';
  import type { RequestStatus } from '../api';

  export let value: RequestStatus | '' = '';
  export let onChange: (value: RequestStatus | '') => void;

  let isOpen = false;
  let selectedValue = value;

  $: if (value !== selectedValue) {
    selectedValue = value;
  }

  const options: { value: RequestStatus | '', label: string, icon: string }[] = [
    { 
      value: '', 
      label: 'All',
      icon: '🔍'
    },
    { 
      value: 'pending', 
      label: 'Pending',
      icon: '⏳'
    },
    { 
      value: 'processing', 
      label: 'Processing',
      icon: '⚙️'
    },
    { 
      value: 'completed', 
      label: 'Completed',
      icon: '✅'
    },
    { 
      value: 'failed', 
      label: 'Failed',
      icon: '❌'
    }
  ];

  function handleSelect(option: typeof options[0]) {
    selectedValue = option.value;
    value = option.value;
    onChange(option.value);
    isOpen = false;
  }

  $: currentOption = options.find(opt => opt.value === selectedValue) || options[0];
</script>

<div 
  class="relative"
  use:clickOutside={() => isOpen = false}
>
  <button
    type="button"
    class="inline-flex items-center gap-x-2 bg-white px-3 py-2 text-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 
           rounded-md shadow-sm font-semibold text-gray-900 focus:outline-none focus:ring-2 focus:ring-secondary"
    on:click={() => isOpen = !isOpen}
  >
    <span class="flex items-center gap-x-2">
      <span class="text-lg">{currentOption.icon}</span>
      <span>{currentOption.label}</span>
    </span>
    <span class="text-gray-400 transition-transform duration-200" class:rotate-180={isOpen}>
      ▼
    </span>
  </button>

  {#if isOpen}
    <div
      class="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 
             focus:outline-none divide-y divide-gray-100"
      transition:slide={{ duration: 200 }}
    >
      <div class="py-1">
        {#each options as option}
          <button
            class="flex w-full items-center gap-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-secondary/10 
                   {selectedValue === option.value ? 'bg-secondary/5 text-secondary' : ''}"
            on:click={() => handleSelect(option)}
          >
            <span class="text-lg">{option.icon}</span>
            {option.label}
            {#if selectedValue === option.value}
              <span class="ml-auto text-secondary">✓</span>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div> 
