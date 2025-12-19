/**
 * API Client with Authorization Bearer Header
 * 
 * Reference: @frontend/CLAUDE.md
 * Reference: @specs/api/rest-endpoints.md
 * 
 * CRITICAL: Every API request includes Authorization: Bearer <token>
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Task {
    id: number;
    user_id: string;
    title: string;
    description: string;
    completed: boolean;
    priority: "high" | "medium" | "low";
    due_date: string | null;
    created_at: string;
    updated_at: string;
    tags: { id: number; name: string; color: string }[];
}

export interface CreateTaskInput {
    title: string;
    description?: string;
    priority?: "high" | "medium" | "low";
    due_date?: string;
}

export interface UpdateTaskInput {
    title?: string;
    description?: string;
    completed?: boolean;
    priority?: "high" | "medium" | "low";
    due_date?: string;
}

/**
 * API client that automatically includes Authorization: Bearer header.
 * 
 * Per spec AC-AUTH-003.1: All API requests require Authorization: Bearer <token>
 */
class ApiClient {
    private async getToken(): Promise<string | null> {
        // In a real app, this would get the token from Better Auth
        // For now, we'll get it from localStorage or session
        if (typeof window !== "undefined") {
            return localStorage.getItem("auth_token");
        }
        return null;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const token = await this.getToken();

        const headers: HeadersInit = {
            "Content-Type": "application/json",
        };

        // CRITICAL: Add Authorization Bearer header to EVERY request
        if (token) {
            (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
        }

        // Use proxy to avoid Mixed Content (HTTPS frontend -> HTTP backend)
        const response = await fetch("/api/proxy", {
            method: "POST",
            headers,
            body: JSON.stringify({
                endpoint,
                method: options.method || "GET",
                body: options.body ? JSON.parse(options.body as string) : undefined,
            }),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || error.error || `HTTP ${response.status}`);
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return {} as T;
        }

        return response.json();
    }

    // ============================================================
    // Task CRUD Operations - Per @specs/api/rest-endpoints.md
    // ============================================================

    async getTasks(userId: string, options?: {
        completed?: boolean;
        priority?: string;
        search?: string;
    }): Promise<Task[]> {
        const params = new URLSearchParams();
        if (options?.completed !== undefined) {
            params.append("completed", String(options.completed));
        }
        if (options?.priority) {
            params.append("priority", options.priority);
        }
        if (options?.search) {
            params.append("search", options.search);
        }

        const query = params.toString() ? `?${params}` : "";
        return this.request<Task[]>(`/api/${userId}/tasks${query}`);
    }

    async createTask(userId: string, task: CreateTaskInput): Promise<Task> {
        return this.request<Task>(`/api/${userId}/tasks`, {
            method: "POST",
            body: JSON.stringify(task),
        });
    }

    async getTask(userId: string, taskId: number): Promise<Task> {
        return this.request<Task>(`/api/${userId}/tasks/${taskId}`);
    }

    async updateTask(
        userId: string,
        taskId: number,
        task: UpdateTaskInput
    ): Promise<Task> {
        return this.request<Task>(`/api/${userId}/tasks/${taskId}`, {
            method: "PUT",
            body: JSON.stringify(task),
        });
    }

    async deleteTask(userId: string, taskId: number): Promise<void> {
        await this.request<void>(`/api/${userId}/tasks/${taskId}`, {
            method: "DELETE",
        });
    }

    async toggleComplete(userId: string, taskId: number): Promise<Task> {
        return this.request<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
            method: "PATCH",
        });
    }

    async getStats(userId: string): Promise<{
        total: number;
        complete: number;
        pending: number;
    }> {
        return this.request(`/api/${userId}/stats`);
    }

    // ============================================================
    // Chat Operations - Phase III
    // Per @specs/api/rest-endpoints.md POST /api/{user_id}/chat
    // ============================================================

    async chat(userId: string, request: ChatRequest): Promise<ChatResponse> {
        return this.request<ChatResponse>(`/api/${userId}/chat`, {
            method: "POST",
            body: JSON.stringify(request),
        });
    }
}

// ============================================================
// Phase III: Chat Types
// ============================================================

export interface ChatRequest {
    conversation_id?: number;
    message: string;
}

export interface ChatResponse {
    conversation_id: number;
    response: string;
    tool_calls: string[];
}

export const api = new ApiClient();
