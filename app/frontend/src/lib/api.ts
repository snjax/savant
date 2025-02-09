export interface Request {
  id: string;
  userId: string;
  status: RequestStatus;
  createdAt: string;
  fileName: string;
}

export type RequestStatus = 'pending' | 'processing' | 'completed' | 'failed';

export async function getAllRequests(params: {
  userId?: string;
  limit?: number;
  offset?: number;
  status?: RequestStatus;
} = {}): Promise<Request[]> {
  const searchParams = new URLSearchParams();
  if (params.userId) searchParams.set('user_id', params.userId);
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

  const response = await fetch(`/api/v1/requests`, {
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

// TODO: Probably easier to just insert a link to the report.
export async function downloadReport(requestId: string): Promise<void> {
  const response = await fetch(`/api/v1/requests/${requestId}/report`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to download report');
  }
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'report.pdf';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
} 
