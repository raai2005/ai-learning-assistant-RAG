"use client";

import { useState } from "react";
import { processVideo } from "@/lib/api";

interface YouTubeInputProps {
  onToast: (message: string, type: "success" | "error") => void;
  onSuccess: (contentId: string) => void;
}

const YOUTUBE_REGEX =
  /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)[a-zA-Z0-9_-]{11}/;

export default function YouTubeInput({ onToast, onSuccess }: YouTubeInputProps) {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      onToast("Please enter a YouTube URL", "error");
      return;
    }

    if (!YOUTUBE_REGEX.test(url.trim())) {
      onToast("Please enter a valid YouTube URL", "error");
      return;
    }

    setIsLoading(true);

    try {
      // Store source info for the learn page viewer
      sessionStorage.setItem("sourceType", "video");
      sessionStorage.setItem("sourceUrl", url.trim());
      sessionStorage.setItem("sourceTitle", "YouTube Video");

      const result = await processVideo(url.trim());
      onToast(`Video processed! ${result.chunks_count} chunks created.`, "success");
      setUrl("");
      onSuccess(result.content_id);
    } catch (err) {
      onToast(err instanceof Error ? err.message : "Failed to process video", "error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-card p-8 animate-fade-in-up animate-pulse-glow">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-red-500/15 flex items-center justify-center">
          <svg
            width="26"
            height="26"
            viewBox="0 0 24 24"
            fill="none"
            className="text-red-400"
          >
            <rect
              x="2"
              y="4"
              width="20"
              height="16"
              rx="4"
              stroke="currentColor"
              strokeWidth="1.8"
            />
            <polygon
              points="10,8.5 16,12 10,15.5"
              fill="currentColor"
            />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">YouTube URL</h2>
          <p className="text-sm text-gray-400 mt-0.5">
            Paste a YouTube video link to process
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full px-5 py-3.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300 text-sm"
            disabled={isLoading}
          />
          {url && (
            <button
              type="button"
              onClick={() => setUrl("")}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors cursor-pointer"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="gradient-btn w-full py-3.5 text-sm flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="3"
                  className="opacity-25"
                />
                <path
                  d="M4 12a8 8 0 018-8"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  className="opacity-75"
                />
              </svg>
              Processing...
            </>
          ) : (
            <>
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
              Submit URL
            </>
          )}
        </button>
      </form>
    </div>
  );
}
