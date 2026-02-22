"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import YouTubeInput from "@/components/YouTubeInput";
import PdfUpload from "@/components/PdfUpload";
import Toast, { ToastType } from "@/components/Toast";

interface ToastData {
  id: number;
  message: string;
  type: ToastType;
}

let toastId = 0;

export default function Home() {
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const router = useRouter();

  const showToast = useCallback((message: string, type: ToastType) => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const handleSuccess = useCallback(
    (contentId: string) => {
      router.push(`/learn/${contentId}`);
    },
    [router]
  );

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center px-4 py-16 overflow-hidden">
      {/* Ambient background blobs */}
      <div
        className="ambient-blob w-[500px] h-[500px] bg-purple-600 -top-40 -left-40"
        aria-hidden
      />
      <div
        className="ambient-blob w-[400px] h-[400px] bg-blue-600 -bottom-32 -right-32"
        aria-hidden
      />
      <div
        className="ambient-blob w-[300px] h-[300px] bg-indigo-600 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
        aria-hidden
      />

      {/* Hero */}
      <div className="text-center mb-14 animate-fade-in-up">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-6 rounded-full bg-white/5 border border-white/10 text-xs text-gray-400 tracking-wide uppercase">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          AI-Powered Learning
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight">
          <span className="text-white">Learn from </span>
          <span className="gradient-text">any source</span>
        </h1>
        <p className="mt-4 text-gray-400 text-base sm:text-lg max-w-xl mx-auto leading-relaxed">
          Paste a YouTube URL or upload a PDF document and let our AI transform
          it into structured learning material.
        </p>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-3xl">
        <YouTubeInput onToast={showToast} onSuccess={handleSuccess} />
        <PdfUpload onToast={showToast} onSuccess={handleSuccess} />
      </div>

      {/* Footer */}
      <p className="mt-16 text-xs text-gray-600 animate-fade-in">
        Built with Next.js • AI Learning Assistant
      </p>

      {/* Toasts */}
      <div className="fixed top-6 right-6 z-50 flex flex-col gap-3">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </main>
  );
}
