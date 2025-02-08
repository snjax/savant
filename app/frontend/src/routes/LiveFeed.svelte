<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { user } from '../lib/auth';
  import type { Request } from '../lib/api';
  import { getAllRequests, createRequest } from '../lib/api';

  let requests: Request[] = [];
  let isLoading = true;
  let error: string | null = null;

  onMount(async () => {
    if (!$user) {
      navigate('/login', { replace: true });
      return;
    }

    try {
      requests = await getAllRequests({ limit: 50 });
    } catch (e) {
      error = 'Failed to load requests';
      console.error(e);
    } finally {
      isLoading = false;
    }

    // Poll for updates every 5 seconds
    const interval = setInterval(async () => {
      try {
        requests = await getAllRequests({ limit: 50 });
      } catch (e) {
        console.error('Failed to update requests:', e);
      }
    }, 5000);

    return () => clearInterval(interval);
  });

  async function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !$user) return;

    try {
      const newRequest = await createRequest($user.id, file);
      requests = [newRequest, ...requests];
      input.value = '';
    } catch (e) {
      console.error('Failed to create request:', e);
      alert('Failed to upload file');
    }
  }
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold text-gray-900">Live Feed</h1>
    <div>
      <label
        for="file-upload"
        class="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
      >
        New Request
      </label>
      <input
        id="file-upload"
        type="file"
        accept=".sol"
        class="hidden"
        on:change={handleFileUpload}
      />
    </div>
  </div>

  {#if isLoading}
    <div class="flex justify-center">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  {:else if error}
    <div class="text-red-600 text-center">{error}</div>
  {:else if requests.length === 0}
    <div class="text-gray-500 text-center">No requests yet</div>
  {:else}
    <div class="space-y-4">
      {#each requests as request}
        <div class="bg-white shadow rounded-lg p-4">
          <div class="flex justify-between items-start">
            <div>
              <h3 class="text-lg font-medium text-gray-900">{request.fileName}</h3>
              <p class="text-sm text-gray-500">
                Created {new Date(request.createdAt).toLocaleString()}
              </p>
            </div>
            <span
              class="px-2 py-1 text-sm rounded-full"
              class:bg-yellow-100={request.status === 'pending'}
              class:text-yellow-800={request.status === 'pending'}
              class:bg-blue-100={request.status === 'processing'}
              class:text-blue-800={request.status === 'processing'}
              class:bg-green-100={request.status === 'completed'}
              class:text-green-800={request.status === 'completed'}
              class:bg-red-100={request.status === 'failed'}
              class:text-red-800={request.status === 'failed'}
            >
              {request.status}
            </span>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div> 
