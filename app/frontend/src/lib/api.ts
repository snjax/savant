export interface Request {
  id: string;
  userId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  createdAt: string;
  fileName: string;
}

export async function getUserRequests(userId: string): Promise<Request[]> {
  const response = await fetch(`/api/v1/user/${userId}/requests`);
  if (!response.ok) throw new Error('Failed to fetch user requests');
  return response.json();
}

export async function getAllRequests(params: {
  limit?: number;
  offset?: number;
  status?: string;
} = {}): Promise<Request[]> {
  const searchParams = new URLSearchParams();
  if (params.limit) searchParams.set('limit', params.limit.toString());
  if (params.offset) searchParams.set('offset', params.offset.toString());
  if (params.status) searchParams.set('status', params.status);

  const response = await fetch(`/api/v1/requests?${searchParams.toString()}`);
  if (!response.ok) throw new Error('Failed to fetch requests');
  return response.json();
}

export async function getRequest(requestId: string): Promise<Request> {
  const response = await fetch(`/api/v1/requests/${requestId}`);
  if (!response.ok) throw new Error('Failed to fetch request');
  return response.json();
}

export async function createRequest(userId: string, file: File): Promise<Request> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`/api/v1/user/${userId}/requests`, {
    method: 'PUT',
    body: formData,
  });

  if (!response.ok) throw new Error('Failed to create request');
  return response.json();
}

export async function getRequestLogs(requestId: string): Promise<string> {
  const response = await fetch(`/api/v1/requests/${requestId}/logs`);
  if (!response.ok) throw new Error('Failed to fetch request logs');
  return response.text();
}

export async function getRequestSource(requestId: string): Promise<string> {
  const response = await fetch(`/api/v1/requests/${requestId}/source`);
  if (!response.ok) throw new Error('Failed to fetch source code');
  return response.text();
} 
