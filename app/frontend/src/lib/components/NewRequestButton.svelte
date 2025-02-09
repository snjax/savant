<script lang="ts">
  import { navigate } from 'svelte-routing';
  import { user } from '../auth';
  import { createRequest } from '../api';
  import Modal from './Modal.svelte';

  export let onRequestCreated: (request: any) => void;

  let isModalOpen = false;
  let fileInput: HTMLInputElement;

  const disclaimer = `This AI code audit tool is a hackathon project for educational purposes only. All submitted code and reports are publicly accessible. The automated analysis may not detect all issues and should not replace human review. Provided "as is" without warranties. We are not liable for any damages from tool usage. Do not upload sensitive code.`;

  function openModal() {
    if (!$user) {
      navigate('/login');
      return;
    }
    isModalOpen = true;
  }

  function closeModal() {
    isModalOpen = false;
  }

  async function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !$user) return;

    try {
      const newRequest = await createRequest($user.id, file);
      onRequestCreated(newRequest);
      closeModal();
      input.value = '';
    } catch (e) {
      console.error('Failed to create request:', e);
      alert('Failed to upload file');
    }
  }
</script>

<button
  class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
  on:click={openModal}
>
  New Request
</button>

<Modal
  isOpen={isModalOpen}
  onClose={closeModal}
  title="New Code Analysis Request"
>
  <div class="space-y-6">
    <div class="text-gray-700 bg-gray-50 p-4 rounded-lg text-sm">
      {disclaimer}
    </div>

    <div class="flex justify-end space-x-4">
      <button
        class="text-gray-600 hover:text-gray-800"
        on:click={closeModal}
      >
        Cancel
      </button>
      
      <label
        for="file-upload-modal"
        class="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
      >
        Upload Solidity File
      </label>
      <input
        bind:this={fileInput}
        id="file-upload-modal"
        type="file"
        accept=".sol"
        class="hidden"
        on:change={handleFileUpload}
      />
    </div>
  </div>
</Modal> 
