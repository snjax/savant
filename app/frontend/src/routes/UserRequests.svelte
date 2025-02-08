<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { user } from '../lib/auth';
  import type { Request } from '../lib/api';
  import { getUserRequests, getRequestLogs } from '../lib/api';

  export let userId: string;
  
  let requests: Request[] = [];
  let selectedRequest: Request | null = null;
  let logs: string = '';
  let isLoading = true;
  let error: string | null = null;
  let isSourceVisible = false;

  $: if (selectedRequest) {
    updateLogs();
  }

  onMount(async () => {
    if (!$user) {
      navigate('/login', { replace: true });
      return;
    }

    if ($user.id !== userId) {
      navigate(`/user/${$user.id}`, { replace: true });
      return;
    }

    try {
      requests = await getUserRequests(userId);
      if (requests.length > 0) {
        selectedRequest = requests[0];
      }
    } catch (e) {
      error = 'Failed to load requests';
      console.error(e);
    } finally {
      isLoading = false;
    }

    // Poll for updates every 5 seconds
    const interval = setInterval(async () => {
      try {
        const updatedRequests = await getUserRequests(userId);
        requests = updatedRequests;
        
        if (selectedRequest) {
          const updatedRequest = updatedRequests.find((r: Request) => r.id === selectedRequest.id);
          if (updatedRequest) {
            selectedRequest = updatedRequest;
          }
        }
      } catch (e) {
        console.error('Failed to update requests:', e);
      }
    }, 5000);

    return () => clearInterval(interval);
  });

  async function updateLogs() {
    if (!selectedRequest) return;
    
    try {
      logs = await getRequestLogs(selectedRequest.id);
    } catch (e) {
      console.error('Failed to fetch logs:', e);
    }
  }

  async function toggleSource() {
    if (!selectedRequest) return;
    
    isSourceVisible = !isSourceVisible;
    if (isSourceVisible) {
      try {
        const response = await fetch(`/requests/${selectedRequest.id}/source.sol`);
        if (response.ok) {
          const sourceCode = await response.text();
          logs = sourceCode;
        } else {
          logs = 'Failed to load source code';
        }
      } catch (e) {
        console.error('Failed to fetch source:', e);
        logs = 'Failed to load source code';
      }
    } else {
      updateLogs();
    }
  }
</script>

<div class="flex h-full">
  <!-- Requests List -->
  <div class="w-1/3 border-r pr-4 space-y-4">
    <h2 class="text-xl font-bold text-gray-900">Your Requests</h2>
    
    {#if isLoading}
      <div class="flex justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    {:else if error}
      <div class="text-red-600">{error}</div>
    {:else if requests.length === 0}
      <div class="text-gray-500">No requests yet</div>
    {:else}
      {#each requests as request}
        <button
          class="w-full text-left p-4 rounded-lg transition-colors"
          class:bg-blue-50={selectedRequest?.id === request.id}
          class:hover:bg-gray-50={selectedRequest?.id !== request.id}
          on:click={() => selectedRequest = request}
        >
          <h3 class="font-medium text-gray-900">{request.fileName}</h3>
          <p class="text-sm text-gray-500">
            Created {new Date(request.createdAt).toLocaleString()}
          </p>
          <span
            class="inline-block mt-2 px-2 py-1 text-sm rounded-full"
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
        </button>
      {/each}
    {/if}
  </div>

  <!-- Request Details -->
  <div class="w-2/3 pl-4 space-y-4">
    {#if selectedRequest}
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900">
          Request Details
        </h2>
        <button
          class="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500"
          on:click={toggleSource}
        >
          {isSourceVisible ? 'Show Logs' : 'Show Source'}
        </button>
      </div>
      
      <div class="bg-gray-50 rounded-lg p-4">
        <p><strong>ID:</strong> {selectedRequest.id}</p>
        <p><strong>Status:</strong> {selectedRequest.status}</p>
        <p><strong>File:</strong> {selectedRequest.fileName}</p>
        <p><strong>Created:</strong> {new Date(selectedRequest.createdAt).toLocaleString()}</p>
      </div>

      <div class="bg-black rounded-lg p-4 h-96 overflow-auto">
        <pre class="text-green-400 font-mono text-sm whitespace-pre-wrap">{logs}</pre>
      </div>
    {:else}
      <div class="text-gray-500 text-center mt-8">
        Select a request to view details
      </div>
    {/if}
  </div>
</div> 
