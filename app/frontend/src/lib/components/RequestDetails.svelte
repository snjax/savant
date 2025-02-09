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

<div class="space-y-4">
  <div class="flex justify-between items-center">
    <h2 class="text-xl font-bold text-gray-900">
      Request Details
    </h2>
    <div class="space-x-4">
      <button
        class="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500"
        on:click={toggleSource}
      >
        {isSourceVisible ? 'Show Logs' : 'Show Source'}
      </button>
      {#if request?.status === 'completed'}
        <button
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
          on:click={handleDownload}
          disabled={isDownloading}
        >
          {isDownloading ? 'Downloading...' : 'Download Report'}
        </button>
      {/if}
    </div>
  </div>
  
  <div class="bg-gray-50 rounded-lg p-4">
    <p><strong>ID:</strong> {request.id}</p>
    <p><strong>Status:</strong> {request.status}</p>
    <p><strong>File:</strong> {request.fileName}</p>
    <p><strong>Created:</strong> {new Date(request.createdAt).toLocaleString()}</p>
  </div>

  {#if isLoading}
    <div class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  {:else}
    <div class="bg-black rounded-lg p-4 h-96 overflow-auto">
      <pre class="text-green-400 font-mono text-sm whitespace-pre-wrap">{logs}</pre>
    </div>
  {/if}
</div> 
