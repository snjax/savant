<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate, Link } from 'svelte-routing';
  import { user } from '../lib/auth';
  import type { Request, RequestStatus } from '../lib/api';
  import { getAllRequests, getRequestLogs, createRequest } from '../lib/api';
  import StatusDropdown from '../lib/components/StatusDropdown.svelte';
  import RequestDetails from '../lib/components/RequestDetails.svelte';
  import NewRequestButton from '../lib/components/NewRequestButton.svelte';

  export let userId: string;
  
  let requests: Request[] = [];
  let selectedRequest: Request | null = null;
  let isLoading = true;
  let isLoadingMore = false;
  let isDetailsLoading = false;
  let error: string | null = null;
  let selectedStatus: RequestStatus | '' = '';
  let logs: string = '';
  let interval: number;
  let offset = 0;
  let hasMore = true;
  const LIMIT = 20;
  let requestDetailsComponent: any;

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
      offset = 0;
      const newRequests = await getAllRequests({
        userId,
        status: selectedStatus || undefined,
        limit: LIMIT,
        offset: 0
      });
      requests = newRequests;
      hasMore = newRequests.length === LIMIT;
      
      if (requests.length > 0 && !selectedRequest && window.innerWidth >= 768) {
        await selectRequest(requests[0]);
      }
    } catch (e) {
      error = 'Failed to load requests';
      console.error(e);
    } finally {
      isLoading = false;
    }
  }

  async function loadMore() {
    if (isLoadingMore || !hasMore) return;
    
    try {
      isLoadingMore = true;
      const nextOffset = offset + LIMIT;
      const newRequests = await getAllRequests({
        userId,
        status: selectedStatus || undefined,
        limit: LIMIT,
        offset: nextOffset
      });
      
      if (newRequests.length > 0) {
        requests = [...requests, ...newRequests];
        offset = nextOffset;
        hasMore = newRequests.length === LIMIT;
      } else {
        hasMore = false;
      }
    } catch (e) {
      console.error('Failed to load more requests:', e);
    } finally {
      isLoadingMore = false;
    }
  }

  async function updateRequests() {
    try {
      const updatedRequests = await getAllRequests({
        userId,
        status: selectedStatus || undefined,
        limit: offset + LIMIT,
        offset: 0
      });
      requests = updatedRequests;

      if (selectedRequest) {
        // Find the updated version of the selected request
        const updatedRequest = updatedRequests.find(r => r.id === selectedRequest!.id);
        if (updatedRequest) {
          try {
            selectedRequest = updatedRequest;
            if (requestDetailsComponent) {
              await requestDetailsComponent.updateContent();
            }
          } catch (e) {
            console.error('Failed to fetch content:', e);
          }
        }
      }
    } catch (e) {
      console.error('Failed to update requests:', e);
    }
  }

  async function selectRequest(request: Request) {
    if (window.innerWidth < 768) {
      navigate(`/request/${request.id}`);
      return;
    }

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

<div class="flex flex-col md:flex-row h-full">
  <!-- Requests List -->
  <div class="w-full md:w-1/3 border-r pr-4 space-y-4">
    <div class="flex justify-end items-center">
      <div class="flex items-center space-x-4">
        <StatusDropdown
          bind:value={selectedStatus}
          onChange={(value) => selectedStatus = value}
        />
        <NewRequestButton
          onRequestCreated={(newRequest) => {
            requests = [newRequest, ...requests];
            selectRequest(newRequest);
          }}
        />
      </div>
    </div>
    
    {#if isLoading}
      <div class="flex justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
      </div>
    {:else if error}
      <div class="text-red-600">{error}</div>
    {:else if requests.length === 0}
      <div class="text-gray-500">No requests yet</div>
    {:else}
      <div class="space-y-4">
        {#each requests as request}
          <div class="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow relative" class:ring-2={selectedRequest?.id === request.id} class:ring-secondary={selectedRequest?.id === request.id}>
            <button 
              class="block w-full text-left"
              on:click={() => selectRequest(request)}
            >
              <h3 class="font-medium text-secondary">{request.fileName}</h3>
              <p class="text-sm text-gray-500">
                Created {new Date(request.createdAt).toLocaleString()}
              </p>
              <span
                class={`inline-block mt-2 px-2 py-1 text-sm rounded-full ${
                  request.status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : request.status === 'processing'
                    ? 'bg-primary/10 text-primary'
                    : request.status === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {request.status}
              </span>
            </button>
            <Link
              to={`/request/${request.id}`}
              class="absolute top-4 right-4 p-2 text-gray-500 hover:text-secondary hover:bg-secondary/5 rounded-full md:block"
              title="Open request details"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
              </svg>
            </Link>
          </div>
        {/each}
        
        {#if hasMore}
          <div class="flex justify-center py-4">
            <button
              class="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              on:click={loadMore}
              disabled={isLoadingMore}
            >
              {#if isLoadingMore}
                <div class="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                Loading...
              {:else}
                Load More
              {/if}
            </button>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Request Details -->
  <div class="w-full md:w-2/3 pl-4 hidden md:block">
    {#if selectedRequest}
      <RequestDetails
        bind:this={requestDetailsComponent}
        request={selectedRequest}
        logs={logs}
        isLoading={isDetailsLoading}
      />
    {:else}
      <div class="flex items-center justify-center h-full text-gray-500">
        Select a request to view details
      </div>
    {/if}
  </div>
</div> 
