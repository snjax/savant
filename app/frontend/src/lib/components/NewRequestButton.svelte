<script lang="ts">
  import { navigate } from 'svelte-routing';
  import { user } from '../auth';
  import { createRequest } from '../api';
  import Modal from './Modal.svelte';

  export let onRequestCreated: (request: any) => void;

  let isModalOpen = false;
  let fileInput: HTMLInputElement;
  let isUploading = false;
  let errorMessage: string | null = null;

  const disclaimer = `This AI code audit tool is a hackathon project for educational purposes only. All submitted code and reports are publicly accessible. The automated analysis may not detect all issues and should not replace human review. Provided "as is" without warranties. We are not liable for any damages from tool usage. Do not upload sensitive code.`;

  function openModal() {
    if (!$user) {
      navigate('/login');
      return;
    }
    isModalOpen = true;
    errorMessage = null;
  }

  function closeModal() {
    isModalOpen = false;
    errorMessage = null;
  }

  async function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !$user) return;

    // Validate file type
    if (!file.name.endsWith('.sol')) {
      errorMessage = 'Please upload a Solidity (.sol) file';
      input.value = '';
      return;
    }

    if (file.size > 3000) {
      errorMessage = 'File size exceeds the limit of 3000 characters';
      input.value = '';
      return;
    }

    try {
      isUploading = true;
      errorMessage = null;
      const newRequest = await createRequest($user.id, file);
      onRequestCreated(newRequest);
      closeModal();
      input.value = '';
    } catch (e) {
      console.error('Failed to create request:', e);
      errorMessage = e instanceof Error ? e.message : 'Failed to upload file. Please try again.';
    } finally {
      isUploading = false;
    }
  }
</script>

<button
  class="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-md flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
  on:click={openModal}
  disabled={!$user?.isAdmin && ($user?.remainingRequests ?? 0) <= 0}
>
  <span>New Request</span>
  {#if $user}
    {#if $user.isAdmin}
      <span class="text-sm opacity-75">(∞)</span>
    {:else}
      <span class="text-sm opacity-75">({Math.max(0, $user.remainingRequests)}/{$user.maxRequests})</span>
    {/if}
  {/if}
</button>

<Modal
  isOpen={isModalOpen}
  onClose={closeModal}
  title="New Code Analysis Request"
>
  <div class="space-y-6">
    {#if ($user?.remainingRequests ?? 0) <= 0 && !$user?.isAdmin}
      <div class="text-red-600 bg-red-50 p-4 rounded-lg text-sm">
        You have reached the maximum number of active requests ({$user?.maxRequests}). Please wait for some of your existing requests to complete before creating new ones.
      </div>
    {:else}
      <div class="text-gray-700 bg-gray-50 p-4 rounded-lg text-sm">
        {disclaimer}
      </div>
    {/if}

    {#if errorMessage}
      <div class="text-red-600 bg-red-50 p-4 rounded-lg text-sm">
        {errorMessage}
      </div>
    {/if}

    <div class="flex justify-end space-x-4">
      <button
        class="text-gray-600 hover:text-gray-800"
        on:click={closeModal}
        disabled={isUploading}
      >
        Cancel
      </button>
      
      <label
        for="file-upload-modal"
        class="cursor-pointer bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-md flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        class:opacity-50={isUploading}
        class:cursor-not-allowed={isUploading}
      >
        {#if isUploading}
          <div class="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
          <span>Uploading...</span>
        {:else}
          <span>Upload Solidity File</span>
        {/if}
      </label>
      <input
        bind:this={fileInput}
        id="file-upload-modal"
        type="file"
        accept=".sol"
        class="hidden"
        on:change={handleFileUpload}
        disabled={isUploading}
      />
    </div>
  </div>
</Modal> 
