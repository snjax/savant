<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { user } from '../lib/auth';
  import type { Request } from '../lib/api';
  import { getRequest, getRequestLogs } from '../lib/api';
  import RequestDetails from '../lib/components/RequestDetails.svelte';

  export let requestId: string;
  
  let request: Request | null = null;
  let logs: string = '';
  let isLoading = true;
  let error: string | null = null;
  let interval: number;

  onMount(() => {
    if (!$user) {
      navigate('/login', { replace: true });
      return;
    }

    loadInitialRequest().then(() => {
      // Only set up polling if the request is not completed
      if (request?.status !== 'completed' && request?.status !== 'failed') {
        interval = setInterval(updateRequest, 5000);
      }
    });

    return () => {
      if (interval) clearInterval(interval);
    };
  });

  async function loadInitialRequest() {
    try {
      const newRequest = await getRequest(requestId);
      if (!newRequest) {
        error = 'Request not found';
        return;
      }

      try {
        logs = await getRequestLogs(newRequest.id);
      } catch (e) {
        console.error('Failed to fetch logs:', e);
        logs = 'Failed to load logs';
      }
      
      request = newRequest;
    } catch (e) {
      error = 'Failed to load request';
      console.error(e);
    } finally {
      isLoading = false;
    }
  }

  async function updateRequest() {
    try {
      const newRequest = await getRequest(requestId);
      if (!newRequest) {
        error = 'Request not found';
        return;
      }

      try {
        logs = await getRequestLogs(newRequest.id);
      } catch (e) {
        console.error('Failed to fetch logs:', e);
      }
      
      request = newRequest;
    } catch (e) {
      console.error('Failed to update request:', e);
    }
  }
</script>

<div class="container mx-auto space-y-6">
  {#if isLoading}
    <div class="flex justify-center">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  {:else if error}
    <div class="text-red-600">{error}</div>
  {:else if request}
    <RequestDetails 
      request={request}
      logs={logs}
      isLoading={false}
    />
  {:else}
    <div class="text-gray-500 text-center mt-8">
      Request not found
    </div>
  {/if}
</div> 
