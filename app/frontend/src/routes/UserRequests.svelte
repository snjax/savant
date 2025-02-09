<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { user } from '../lib/auth';
  import type { Request, RequestStatus } from '../lib/api';
  import { getUserRequests, getRequestLogs, createRequest } from '../lib/api';
  import StatusDropdown from '../lib/components/StatusDropdown.svelte';
  import RequestDetails from '../lib/components/RequestDetails.svelte';

  export let userId: string;
  
  let requests: Request[] = [];
  let selectedRequest: Request | null = null;
  let isLoading = true;
  let isDetailsLoading = false;
  let error: string | null = null;
  let selectedStatus: RequestStatus | '' = '';
  let logs: string = '';
  let interval: number;

  onMount(() => {
    if (!$user) {
      navigate('/login', { replace: true });
      return;
    }

    if ($user.id !== userId) {
      navigate(`/user/${$user.id}`, { replace: true });
      return;
    }

    loadInitialRequests().then(() => {
      // Only set up polling if there are any non-completed requests
      if (requests.some(r => r.status !== 'completed')) {
        interval = setInterval(updateRequests, 5000);
      }
    });

    return () => {
      if (interval) clearInterval(interval);
    };
  });

  async function loadInitialRequests() {
    try {
      requests = await getUserRequests(userId, selectedStatus ? { status: selectedStatus } : {});
      if (requests.length > 0 && !selectedRequest) {
        await selectRequest(requests[0]);
      }
    } catch (e) {
      error = 'Failed to load requests';
      console.error(e);
    } finally {
      isLoading = false;
    }
  }

  async function updateRequests() {
    try {
      const updatedRequests = await getUserRequests(userId, selectedStatus ? { status: selectedStatus } : {});
      requests = updatedRequests;

      if (selectedRequest) {
        // Find the updated version of the selected request
        const updatedRequest = updatedRequests.find(r => r.id === selectedRequest!.id);
        if (updatedRequest && updatedRequest.status !== 'completed') {
          try {
            logs = await getRequestLogs(updatedRequest.id);
          } catch (e) {
            console.error('Failed to fetch logs:', e);
          }
          selectedRequest = updatedRequest;
        }
      }
    } catch (e) {
      console.error('Failed to update requests:', e);
    }
  }

  async function selectRequest(request: Request) {
    selectedRequest = request;
    isDetailsLoading = true;
    try {
      logs = await getRequestLogs(request.id);
    } catch (e) {
      console.error('Failed to fetch logs:', e);
      logs = 'Failed to load logs';
    } finally {
      isDetailsLoading = false;
    }
  }

  // TODO: Already have a file upload button in the LiveFeed.svelte, should probably refactor this.
  async function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !$user) return;

    try {
      const newRequest = await createRequest($user.id, file);
      requests = [newRequest, ...requests];
      await selectRequest(newRequest);
      input.value = '';
    } catch (e) {
      console.error('Failed to create request:', e);
      alert('Failed to upload file');
    }
  }

  $: if (selectedStatus !== undefined) {
    loadInitialRequests();
  }
</script>

<div class="flex h-full">
  <!-- Requests List -->
  <div class="w-1/3 border-r pr-4 space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-900">Your Requests</h2>
      <div class="flex items-center space-x-4">
        <StatusDropdown
          bind:value={selectedStatus}
          onChange={(value) => selectedStatus = value}
        />
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
      <div class="text-red-600">{error}</div>
    {:else if requests.length === 0}
      <div class="text-gray-500">No requests yet</div>
    {:else}
      <div class="space-y-4">
        {#each requests as request}
          <button 
            class="block w-full text-left"
            on:click={() => selectRequest(request)}
          >
            <div class="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow" class:ring-2={selectedRequest?.id === request.id} class:ring-blue-500={selectedRequest?.id === request.id}>
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
            </div>
          </button>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Request Details -->
  <div class="w-2/3 pl-4">
    {#if selectedRequest}
      <RequestDetails 
        request={selectedRequest}
        logs={logs}
        isLoading={isDetailsLoading}
      />
    {:else}
      <div class="text-gray-500 text-center mt-8">
        Select a request to view details
      </div>
    {/if}
  </div>
</div> 
