<script lang="ts">
  import type { Request } from '../api';
  import { getRequestLogs, getRequestSource, downloadReport } from '../api';

  export let request: Request;
  export let logs: string = '';
  export let isLoading: boolean = false;
  export let onLogsChange: ((logs: string) => void) | null = null;
  
  let error: string | null = null;
  let isSourceVisible = false;
  let isDownloading = false;

  async function toggleSource() {
    try {
      isSourceVisible = !isSourceVisible;
      const newLogs = isSourceVisible 
        ? await getRequestSource(request.id)
        : await getRequestLogs(request.id);
      
      if (onLogsChange) {
        onLogsChange(newLogs);
      } else {
        logs = newLogs;
      }
    } catch (e) {
      console.error('Failed to fetch source:', e);
      const errorMessage = 'Failed to load source code';
      if (onLogsChange) {
        onLogsChange(errorMessage);
      } else {
        logs = errorMessage;
      }
    }
  }

  async function handleDownload() {
    try {
      isDownloading = true;
      await downloadReport(request.id);
    } catch (e) {
      console.error('Failed to download report:', e);
      error = 'Failed to download report';
    } finally {
      isDownloading = false;
    }
  }
</script>

<div class="space-y-6 p-6 bg-white rounded-xl shadow-sm">
  <div class="flex justify-between items-center">
    <h2 class="text-2xl font-bold text-gray-800 tracking-tight">
      Request Details
    </h2>
    <div class="space-x-4 flex items-center">
      <button
        class="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200 flex items-center gap-2 border border-blue-200 rounded-md hover:border-blue-300"
        on:click={toggleSource}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={isSourceVisible ? 'M4 6h16M4 12h16M4 18h16' : 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4'} />
        </svg>
        {isSourceVisible ? 'Show Logs' : 'Show Source'}
      </button>
      {#if request?.status === 'completed'}
        <button
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2 shadow-sm"
          on:click={handleDownload}
          disabled={isDownloading}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          {isDownloading ? 'Downloading...' : 'Download Report'}
        </button>
      {/if}
    </div>
  </div>
  
  <div class="bg-gray-50 rounded-xl p-6 grid grid-cols-2 gap-4 border border-gray-100">
    <div class="space-y-1">
      <p class="text-sm text-gray-500">ID</p>
      <p class="font-medium text-gray-900">{request.id}</p>
    </div>
    <div class="space-y-1">
      <p class="text-sm text-gray-500">Status</p>
      <p class="font-medium">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium
          {request.status === 'completed' ? 'bg-green-100 text-green-800' : 
          request.status === 'failed' ? 'bg-red-100 text-red-800' : 
          request.status === 'processing' ? 'bg-blue-100 text-blue-800' : 
          'bg-gray-100 text-gray-800'}">
          {request.status}
        </span>
      </p>
    </div>
    <div class="space-y-1">
      <p class="text-sm text-gray-500">File</p>
      <p class="font-medium text-gray-900 truncate" title={request.fileName}>{request.fileName}</p>
    </div>
    <div class="space-y-1">
      <p class="text-sm text-gray-500">Created</p>
      <p class="font-medium text-gray-900">{new Date(request.createdAt).toLocaleString()}</p>
    </div>
  </div>

  {#if isLoading}
    <div class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  {:else}
    <div class="bg-gray-900 rounded-xl p-6 h-[32rem] overflow-auto border border-gray-800 shadow-inner">
      <pre class="text-green-400 font-mono text-sm whitespace-pre-wrap leading-relaxed">{logs}</pre>
    </div>
  {/if}

  {#if error}
    <div class="bg-red-50 border-l-4 border-red-400 p-4 rounded-md">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="ml-3 text-sm text-red-700">{error}</p>
      </div>
    </div>
  {/if}
</div> 
