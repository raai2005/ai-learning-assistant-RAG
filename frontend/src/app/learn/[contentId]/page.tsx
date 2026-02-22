"use client";

import { useState, useRef, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  generateFlashcards,
  generateQuiz,
  chat,
  Flashcard,
  QuizQuestion,
} from "@/lib/api";

type Tab = "chat" | "flashcards" | "quiz";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

function extractYouTubeId(url: string): string | null {
  const match = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
  );
  return match ? match[1] : null;
}

export default function LearnPage() {
  const params = useParams();
  const router = useRouter();
  const contentId = params.contentId as string;

  // Source info from sessionStorage
  const [sourceType, setSourceType] = useState<"pdf" | "video" | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [videoId, setVideoId] = useState<string | null>(null);
  const [sourceTitle, setSourceTitle] = useState("");

  const [activeTab, setActiveTab] = useState<Tab>("chat");

  // Flashcards state
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [flashcardsLoading, setFlashcardsLoading] = useState(false);
  const [currentCard, setCurrentCard] = useState(0);
  const [flipped, setFlipped] = useState(false);

  // Quiz state
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [error, setError] = useState("");

  useEffect(() => {
    const type = sessionStorage.getItem("sourceType") as "pdf" | "video" | null;
    setSourceType(type);
    setSourceTitle(sessionStorage.getItem("sourceTitle") || "Content");

    if (type === "pdf") {
      setPdfUrl(sessionStorage.getItem("pdfBlobUrl"));
    } else if (type === "video") {
      const url = sessionStorage.getItem("sourceUrl") || "";
      setVideoId(extractYouTubeId(url));
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Flashcards ──
  const handleGenerateFlashcards = async () => {
    setFlashcardsLoading(true);
    setError("");
    try {
      const res = await generateFlashcards(contentId, 10);
      setFlashcards(res.flashcards);
      setCurrentCard(0);
      setFlipped(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate flashcards");
    } finally {
      setFlashcardsLoading(false);
    }
  };

  // ── Quiz ──
  const handleGenerateQuiz = async () => {
    setQuizLoading(true);
    setError("");
    setQuizSubmitted(false);
    setSelectedAnswers({});
    try {
      const res = await generateQuiz(contentId, 5);
      setQuestions(res.questions);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate quiz");
    } finally {
      setQuizLoading(false);
    }
  };

  const quizScore = quizSubmitted
    ? questions.filter((q) => selectedAnswers[q.id] === q.correct_answer).length
    : 0;

  // ── Chat ──
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMsg = chatInput.trim();
    setChatInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setChatLoading(true);

    try {
      const res = await chat(contentId, userMsg);
      setMessages((prev) => [...prev, { role: "assistant", text: res.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: err instanceof Error ? err.message : "Something went wrong" },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const tabs: { key: Tab; label: string; icon: string }[] = [
    { key: "chat", label: "Chat", icon: "💬" },
    { key: "flashcards", label: "Flashcards", icon: "🃏" },
    { key: "quiz", label: "Quiz", icon: "❓" },
  ];

  return (
    <main className="relative h-screen flex flex-col overflow-hidden">
      {/* Background blobs */}
      <div className="ambient-blob w-[500px] h-[500px] bg-purple-600 -top-40 -left-40" aria-hidden />
      <div className="ambient-blob w-[400px] h-[400px] bg-blue-600 -bottom-32 -right-32" aria-hidden />

      {/* Top Bar */}
      <div className="flex items-center gap-4 px-6 py-4 border-b border-white/10 bg-black/20 backdrop-blur-md z-10 flex-shrink-0">
        <button
          onClick={() => router.push("/")}
          className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
        >
          ←
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="text-lg font-bold text-white truncate">{sourceTitle}</h1>
          <p className="text-xs text-gray-500 font-mono">{contentId.slice(0, 12)}...</p>
        </div>
      </div>

      {/* Split Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* ─── LEFT: Document Viewer ─── */}
        <div className="w-1/2 border-r border-white/10 flex flex-col bg-black/10">
          {sourceType === "pdf" && pdfUrl ? (
            <iframe
              src={pdfUrl}
              className="w-full h-full"
              title="PDF Preview"
            />
          ) : sourceType === "video" && videoId ? (
            <div className="flex-1 flex items-center justify-center p-6">
              <iframe
                src={`https://www.youtube.com/embed/${videoId}`}
                className="w-full aspect-video rounded-xl max-w-lg"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                title="YouTube Video"
              />
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-4xl mb-3">📄</p>
                <p className="text-sm">Document preview not available</p>
                <p className="text-xs text-gray-600 mt-1">Content has been processed and is ready to learn from</p>
              </div>
            </div>
          )}
        </div>

        {/* ─── RIGHT: Tabs Panel ─── */}
        <div className="w-1/2 flex flex-col overflow-hidden">
          {/* Tab Buttons */}
          <div className="flex gap-1.5 px-4 pt-4 pb-3 flex-shrink-0">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => { setActiveTab(tab.key); setError(""); }}
                className={`px-4 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                  activeTab === tab.key
                    ? "bg-purple-500/20 border border-purple-500/40 text-purple-300"
                    : "bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {error && (
            <div className="mx-4 mb-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
              {error}
            </div>
          )}

          {/* Tab content fills remaining space */}
          <div className="flex-1 overflow-hidden px-4 pb-4">
            {/* ── Chat Tab ── */}
            {activeTab === "chat" && (
              <div className="h-full flex flex-col glass-card p-0 overflow-hidden">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {messages.length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-3xl mb-2">💬</p>
                      <p className="text-gray-400 text-sm">Ask anything about your content</p>
                      <p className="text-xs text-gray-600 mt-1">AI will answer based on the processed material</p>
                    </div>
                  )}
                  {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[85%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "bg-purple-500/20 border border-purple-500/30 text-purple-100 rounded-br-md"
                          : "bg-white/5 border border-white/10 text-gray-300 rounded-bl-md"
                      }`}>
                        {msg.text}
                      </div>
                    </div>
                  ))}
                  {chatLoading && (
                    <div className="flex justify-start">
                      <div className="px-3.5 py-2.5 rounded-2xl bg-white/5 border border-white/10 text-gray-400 text-sm rounded-bl-md">
                        <span className="animate-pulse">Thinking...</span>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Input */}
                <form onSubmit={handleSendMessage} className="p-3 border-t border-white/10 flex-shrink-0">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="Ask a question..."
                      className="flex-1 px-3.5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all"
                      disabled={chatLoading}
                    />
                    <button
                      type="submit"
                      disabled={chatLoading || !chatInput.trim()}
                      className="gradient-btn px-4 py-2.5 text-sm disabled:opacity-40"
                    >
                      Send
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* ── Flashcards Tab ── */}
            {activeTab === "flashcards" && (
              <div className="h-full glass-card p-6 overflow-y-auto">
                {flashcards.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-400 mb-5">Generate AI flashcards from your content</p>
                    <button
                      onClick={handleGenerateFlashcards}
                      disabled={flashcardsLoading}
                      className="gradient-btn px-6 py-2.5 text-sm"
                    >
                      {flashcardsLoading ? "⏳ Generating..." : "🃏 Generate Flashcards"}
                    </button>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-xs text-gray-400">Card {currentCard + 1} of {flashcards.length}</span>
                      <button onClick={handleGenerateFlashcards} disabled={flashcardsLoading} className="text-xs text-purple-400 hover:text-purple-300 cursor-pointer">
                        {flashcardsLoading ? "Regenerating..." : "♻️ Regenerate"}
                      </button>
                    </div>

                    <div
                      onClick={() => setFlipped(!flipped)}
                      className="min-h-[160px] p-6 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center cursor-pointer hover:bg-white/8 transition-all"
                    >
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">
                          {flipped ? "Answer" : "Question"}
                        </p>
                        <p className={`text-base ${flipped ? "text-emerald-300" : "text-white"}`}>
                          {flipped ? flashcards[currentCard].answer : flashcards[currentCard].question}
                        </p>
                        {!flipped && <p className="text-xs text-gray-600 mt-3">Click to reveal</p>}
                      </div>
                    </div>

                    <div className="flex items-center justify-between mt-4">
                      <button
                        onClick={() => { setCurrentCard(Math.max(0, currentCard - 1)); setFlipped(false); }}
                        disabled={currentCard === 0}
                        className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-gray-400 hover:text-white disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed"
                      >← Prev</button>
                      <div className="flex gap-1">
                        {flashcards.map((_, i) => (
                          <div key={i} className={`w-1.5 h-1.5 rounded-full ${i === currentCard ? "bg-purple-400 scale-125" : "bg-white/10"}`} />
                        ))}
                      </div>
                      <button
                        onClick={() => { setCurrentCard(Math.min(flashcards.length - 1, currentCard + 1)); setFlipped(false); }}
                        disabled={currentCard === flashcards.length - 1}
                        className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-gray-400 hover:text-white disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed"
                      >Next →</button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── Quiz Tab ── */}
            {activeTab === "quiz" && (
              <div className="h-full glass-card p-6 overflow-y-auto">
                {questions.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-400 mb-5">Generate an AI quiz from your content</p>
                    <button
                      onClick={handleGenerateQuiz}
                      disabled={quizLoading}
                      className="gradient-btn px-6 py-2.5 text-sm"
                    >
                      {quizLoading ? "⏳ Generating..." : "❓ Generate Quiz"}
                    </button>
                  </div>
                ) : (
                  <div>
                    {quizSubmitted && (
                      <div className={`mb-4 p-3 rounded-lg text-center font-bold ${
                        quizScore === questions.length
                          ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
                          : quizScore >= questions.length / 2
                          ? "bg-yellow-500/10 border border-yellow-500/20 text-yellow-300"
                          : "bg-red-500/10 border border-red-500/20 text-red-300"
                      }`}>
                        Score: {quizScore} / {questions.length}
                      </div>
                    )}

                    <div className="space-y-4">
                      {questions.map((q) => (
                        <div key={q.id} className="p-4 rounded-lg bg-white/3 border border-white/8">
                          <p className="text-white text-sm font-medium mb-2">{q.id}. {q.question}</p>
                          <div className="grid grid-cols-1 gap-1.5">
                            {q.options.map((opt) => {
                              const isSelected = selectedAnswers[q.id] === opt.label;
                              const isCorrect = quizSubmitted && opt.label === q.correct_answer;
                              const isWrong = quizSubmitted && isSelected && opt.label !== q.correct_answer;
                              return (
                                <button
                                  key={opt.label}
                                  onClick={() => { if (!quizSubmitted) setSelectedAnswers((prev) => ({ ...prev, [q.id]: opt.label })); }}
                                  className={`p-2.5 rounded-lg text-xs text-left transition-all cursor-pointer ${
                                    isCorrect ? "bg-emerald-500/15 border border-emerald-500/30 text-emerald-300"
                                    : isWrong ? "bg-red-500/15 border border-red-500/30 text-red-300"
                                    : isSelected ? "bg-purple-500/15 border border-purple-500/30 text-purple-300"
                                    : "bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10"
                                  }`}
                                >
                                  <span className="font-bold mr-1.5">{opt.label}.</span>{opt.text}
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="mt-4">
                      {!quizSubmitted ? (
                        <button
                          onClick={() => setQuizSubmitted(true)}
                          disabled={Object.keys(selectedAnswers).length < questions.length}
                          className="gradient-btn px-5 py-2.5 text-sm disabled:opacity-40"
                        >✅ Submit</button>
                      ) : (
                        <button
                          onClick={handleGenerateQuiz}
                          disabled={quizLoading}
                          className="gradient-btn px-5 py-2.5 text-sm"
                        >{quizLoading ? "Generating..." : "🔄 New Quiz"}</button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
