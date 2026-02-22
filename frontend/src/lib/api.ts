const API_BASE = "http://localhost:8000/api";

export interface ProcessVideoResponse {
  content_id: string;
  title: string;
  duration: string | null;
  chunks_count: number;
  status: string;
  created_at: string;
}

export interface ProcessPdfResponse {
  content_id: string;
  filename: string;
  pages_count: number;
  chunks_count: number;
  status: string;
  created_at: string;
}

export interface Flashcard {
  id: number;
  question: string;
  answer: string;
}

export interface FlashcardsResponse {
  content_id: string;
  flashcards: Flashcard[];
  total: number;
}

export interface QuizOption {
  label: string;
  text: string;
}

export interface QuizQuestion {
  id: number;
  question: string;
  options: QuizOption[];
  correct_answer: string;
}

export interface QuizResponse {
  content_id: string;
  questions: QuizQuestion[];
  total: number;
}

export interface ChatResponse {
  content_id: string;
  reply: string;
  sources: string[];
}

export async function processVideo(youtubeUrl: string): Promise<ProcessVideoResponse> {
  const res = await fetch(`${API_BASE}/process-video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ youtube_url: youtubeUrl }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

export async function processPdf(file: File): Promise<ProcessPdfResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/process-pdf`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

export async function generateFlashcards(
  contentId: string,
  numCards: number = 10
): Promise<FlashcardsResponse> {
  const res = await fetch(`${API_BASE}/generate-flashcards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content_id: contentId, num_cards: numCards }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

export async function generateQuiz(
  contentId: string,
  numQuestions: number = 5
): Promise<QuizResponse> {
  const res = await fetch(`${API_BASE}/generate-quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content_id: contentId, num_questions: numQuestions }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

export async function chat(
  contentId: string,
  message: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content_id: contentId, message }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}
