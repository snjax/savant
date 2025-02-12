<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate, Link } from 'svelte-routing';
  import { user } from '../lib/auth';
  import type { Request, RequestStatus } from '../lib/api';
  import { getAllRequests, createRequest } from '../lib/api';
  import StatusDropdown from '../lib/components/StatusDropdown.svelte';
  import NewRequestButton from '../lib/components/NewRequestButton.svelte';

  let requests: Request[] = [];
  let isLoading = true;
  let error: string | null = null;
  let selectedStatus: RequestStatus | '' = '';
  
  // Simplified pagination state
  let offset = 0;
  let hasMore = true;
  let isLoadingMore = false;
  const LIMIT = 20;
  let isMobileView = false;

  function checkMobileView() {
    isMobileView = window.innerWidth < 768;
  }

  onMount(() => {
    loadRequests();
    checkMobileView();

    // Add scroll event listener only for mobile view
    const handleScroll = () => {
      if (!isMobileView) return;
      
      const scrollPosition = window.scrollY + window.innerHeight;
      const threshold = document.documentElement.scrollHeight - 100; // Load when 100px from bottom
      
      if (scrollPosition >= threshold && !isLoadingMore && hasMore) {
        loadMore();
      }
    };

    const handleResize = () => {
      checkMobileView();
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleResize);
    };
  });

  async function loadRequests() {
    try {
      offset = 0;
      isLoading = true;
      const newRequests = await getAllRequests({ 
        limit: LIMIT,
        offset: 0,
        status: selectedStatus || undefined 
      });
      requests = newRequests;
      hasMore = newRequests.length === LIMIT;
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
        limit: LIMIT,
        offset: nextOffset,
        status: selectedStatus || undefined 
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

  $: if (selectedStatus !== undefined) {
    loadRequests();
  }

  async function handleFileUpload(event: Event) {
    if (!$user) {
      navigate('/login');
      return;
    }

    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    try {
      const newRequest = await createRequest($user.id, file);
      requests = [newRequest, ...requests];
      navigate(`/request/${newRequest.id}`, { replace: true });
      input.value = '';
    } catch (e) {
      console.error('Failed to create request:', e);
      alert('Failed to upload file');
    }
  }
</script>

<div class="space-y-6">
  <div class="flex justify-end items-center">
    <div class="flex items-center space-x-4">
      <StatusDropdown
        bind:value={selectedStatus}
        onChange={(value) => selectedStatus = value}
      />
      {#if $user}
        <NewRequestButton
          onRequestCreated={(newRequest) => {
            requests = [newRequest, ...requests];
            navigate(`/request/${newRequest.id}`, { replace: true });
          }}
        />
      {:else}
        <Link
          to="/login"
          class="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-md"
        >
          New Request
        </Link>
      {/if}
    </div>
  </div>

  {#if isLoading}
    <div class="flex justify-center">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
    </div>
  {:else if error}
    <div class="text-red-600 text-center">{error}</div>
  {:else if requests.length === 0}
    <div class="text-gray-500 text-center">No requests yet</div>
  {:else}
    <div class="space-y-4">
      {#each requests as request}
        <Link to={`/request/${request.id}`} class="block">
          <div class="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-medium text-secondary">{request.fileName}</h3>
                <p class="text-sm text-gray-500">
                  Created {new Date(request.createdAt).toLocaleString()}
                </p>
              </div>
              <span
                class={`px-2 py-1 text-sm rounded-full ${
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
            </div>
          </div>
        </Link>
      {/each}

      {#if isLoadingMore}
        <div class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
        </div>
      {:else if hasMore}
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
      {:else if requests.length > 0}
        <div class="text-gray-500 text-center py-4">
          No more requests to load
        </div>
      {/if}
    </div>
  {/if}
</div> 
