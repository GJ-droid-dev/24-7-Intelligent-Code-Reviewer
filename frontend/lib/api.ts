import { Review, ReviewSubmission, HistoricalRule } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  token?: string | null;
}

async function apiFetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { token, headers = {}, ...rest } = options;
  const requestHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };

  if (token) {
    requestHeaders["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: requestHeaders,
    ...rest,
  });

  if (!response.ok) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      // JSON parse error, use default status text
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export const api = {
  // System Health
  async getHealth(): Promise<{ status: string; service: string }> {
    return apiFetch<{ status: string; service: string }>("/health");
  },

  // Submit a new code review
  async submitReview(submission: ReviewSubmission, token: string): Promise<Review> {
    return apiFetch<Review>("/reviews", {
      method: "POST",
      token,
      body: JSON.stringify(submission),
    });
  },

  // Get a single review report by ID
  async getReview(reviewId: string, token: string): Promise<Review> {
    return apiFetch<Review>(`/reviews/${reviewId}`, {
      token,
    });
  },

  // Get paginated reviews
  async getReviews(
    token: string,
    page: number = 1,
    pageSize: number = 10
  ): Promise<{ reviews: Review[]; total: number; page: number; pageSize: number }> {
    return apiFetch<{ reviews: Review[]; total: number; page: number; pageSize: number }>(
      `/reviews?page=${page}&pageSize=${pageSize}`,
      {
        token,
      }
    );
  },

  // Get historical rules
  async getRules(token: string): Promise<{ rules: HistoricalRule[]; total: number }> {
    try {
      return await apiFetch<{ rules: HistoricalRule[]; total: number }>("/rules", { token });
    } catch {
      // Fallback for mock/local inspection
      return {
        rules: [
          { id: "1", type: "formatting", description: "Avoid single-character variable names — they hurt readability" },
          { id: "2", type: "performance", description: "Cache repeated database lookups inside the request loop" },
          { id: "3", type: "security", description: "Never interpolate raw user input directly into SQL queries" },
          { id: "4", type: "security", description: "Always verify user ownership before returning customer orders" },
          { id: "5", type: "testing", description: "All new API endpoints must include negative unauthorized tests" },
          { id: "6", type: "performance", description: "Enforce cursor or page limits on all list queries" },
        ],
        total: 6,
      };
    }
  },

  // Upload CSV rules
  async uploadRulesCsv(file: File, token: string): Promise<{ message: string; count: number }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/rules/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to upload CSV: ${response.statusText}`);
    }

    return response.json();
  },
};
