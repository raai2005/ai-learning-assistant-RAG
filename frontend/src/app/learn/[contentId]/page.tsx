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

type Tab = "flashcards" | "quiz" | "chat";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

export default function LearnPage() {
  const params = useParams();
  const router = useRouter();
  const contentId = params.contentId as string;

  const [activeTab, setActiveTab] = useState<Tab>("flashcards");

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
    { key: "flashcards", label: "Flashcards", icon: "🃏" },
    { key: "quiz", label: "Quiz", icon: "❓" },
    { key: "chat", label: "Chat", icon: "💬" },
  ];

  return (
    <main className="relative min-h-screen px-4 py-10 overflow-hidden">
      {/* Background blobs */}
      <div className="ambient-blob w-[500px] h-[500px] bg-purple-600 -top-40 -left-40" aria-hidden />
      <div className="ambient-blob w-[400px] h-[400px] bg-blue-600 -bottom-32 -right-32" aria-hidden />

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => router.push("/")}
            className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
          >
            ←
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Learning Dashboard</h1>
            <p className="text-sm text-gray-500 mt-0.5 font-mono">{contentId.slice(0, 8)}...</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => { setActiveTab(tab.key); setError(""); }}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer ${
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
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* ── Flashcards Tab ── */}
        {activeTab === "flashcards" && (
          <div className="glass-card p-8">
            {flashcards.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-400 mb-6 text-lg">Generate AI flashcards from your content</p>
                <button
                  onClick={handleGenerateFlashcards}
                  disabled={flashcardsLoading}
                  className="gradient-btn px-8 py-3 text-sm"
                >
                  {flashcardsLoading ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> Generating...
                    </span>
                  ) : (
                    "🃏 Generate Flashcards"
                  )}
                </button>
              </div>
            ) : (
              <div>
                {/* Card counter */}
                <div className="flex items-center justify-between mb-6">
                  <span className="text-sm text-gray-400">
                    Card {currentCard + 1} of {flashcards.length}
                  </span>
                  <button
                    onClick={handleGenerateFlashcards}
                    disabled={flashcardsLoading}
                    className="text-xs text-purple-400 hover:text-purple-300 transition-colors cursor-pointer"
                  >
                    {flashcardsLoading ? "Regenerating..." : "♻️ Regenerate"}
                  </button>
                </div>

                {/* Flashcard */}
                <div
                  onClick={() => setFlipped(!flipped)}
                  className="min-h-[200px] p-8 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center cursor-pointer hover:bg-white/8 transition-all"
                >
                  <div className="text-center">
                    <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">
                      {flipped ? "Answer" : "Question"}
                    </p>
                    <p className={`text-lg ${flipped ? "text-emerald-300" : "text-white"}`}>
                      {flipped
                        ? flashcards[currentCard].answer
                        : flashcards[currentCard].question}
                    </p>
                    {!flipped && (
                      <p className="text-xs text-gray-600 mt-4">Click to reveal answer</p>
                    )}
                  </div>
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between mt-6">
                  <button
                    onClick={() => { setCurrentCard(Math.max(0, currentCard - 1)); setFlipped(false); }}
                    disabled={currentCard === 0}
                    className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-gray-400 hover:text-white disabled:opacity-30 transition-all cursor-pointer disabled:cursor-not-allowed"
                  >
                    ← Previous
                  </button>
                  <div className="flex gap-1">
                    {flashcards.map((_, i) => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full transition-all ${
                          i === currentCard ? "bg-purple-400 scale-125" : "bg-white/10"
                        }`}
                      />
                    ))}
                  </div>
                  <button
                    onClick={() => { setCurrentCard(Math.min(flashcards.length - 1, currentCard + 1)); setFlipped(false); }}
                    disabled={currentCard === flashcards.length - 1}
                    className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-gray-400 hover:text-white disabled:opacity-30 transition-all cursor-pointer disabled:cursor-not-allowed"
                  >
                    Next →
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Quiz Tab ── */}
        {activeTab === "quiz" && (
          <div className="glass-card p-8">
            {questions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-400 mb-6 text-lg">Generate an AI quiz from your content</p>
                <button
                  onClick={handleGenerateQuiz}
                  disabled={quizLoading}
                  className="gradient-btn px-8 py-3 text-sm"
                >
                  {quizLoading ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> Generating...
                    </span>
                  ) : (
                    "❓ Generate Quiz"
                  )}
                </button>
              </div>
            ) : (
              <div>
                {quizSubmitted && (
                  <div className={`mb-6 p-4 rounded-xl text-center text-lg font-bold ${
                    quizScore === questions.length
                      ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
                      : quizScore >= questions.length / 2
                      ? "bg-yellow-500/10 border border-yellow-500/20 text-yellow-300"
                      : "bg-red-500/10 border border-red-500/20 text-red-300"
                  }`}>
                    Score: {quizScore} / {questions.length}
                  </div>
                )}

                <div className="space-y-6">
                  {questions.map((q) => (
                    <div key={q.id} className="p-5 rounded-xl bg-white/3 border border-white/8">
                      <p className="text-white font-medium mb-3">
                        {q.id}. {q.question}
                      </p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {q.options.map((opt) => {
                          const isSelected = selectedAnswers[q.id] === opt.label;
                          const isCorrect = quizSubmitted && opt.label === q.correct_answer;
                          const isWrong = quizSubmitted && isSelected && opt.label !== q.correct_answer;

                          return (
                            <button
                              key={opt.label}
                              onClick={() => {
                                if (quizSubmitted) return;
                                setSelectedAnswers((prev) => ({ ...prev, [q.id]: opt.label }));
                              }}
                              className={`p-3 rounded-lg text-sm text-left transition-all cursor-pointer ${
                                isCorrect
                                  ? "bg-emerald-500/15 border border-emerald-500/30 text-emerald-300"
                                  : isWrong
                                  ? "bg-red-500/15 border border-red-500/30 text-red-300"
                                  : isSelected
                                  ? "bg-purple-500/15 border border-purple-500/30 text-purple-300"
                                  : "bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10"
                              }`}
                            >
                              <span className="font-bold mr-2">{opt.label}.</span>
                              {opt.text}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex gap-3 mt-6">
                  {!quizSubmitted ? (
                    <button
                      onClick={() => setQuizSubmitted(true)}
                      disabled={Object.keys(selectedAnswers).length < questions.length}
                      className="gradient-btn px-6 py-3 text-sm disabled:opacity-40"
                    >
                      ✅ Submit Quiz
                    </button>
                  ) : (
                    <button
                      onClick={handleGenerateQuiz}
                      disabled={quizLoading}
                      className="gradient-btn px-6 py-3 text-sm"
                    >
                      {quizLoading ? "Generating..." : "🔄 New Quiz"}
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Chat Tab ── */}
        {activeTab === "chat" && (
          <div className="glass-card p-0 flex flex-col" style={{ height: "500px" }}>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-16">
                  <p className="text-3xl mb-3">💬</p>
                  <p className="text-gray-400">Ask anything about your content</p>
                  <p className="text-xs text-gray-600 mt-1">AI will answer based on the processed material</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-purple-500/20 border border-purple-500/30 text-purple-100 rounded-br-md"
                        : "bg-white/5 border border-white/10 text-gray-300 rounded-bl-md"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="px-4 py-3 rounded-2xl bg-white/5 border border-white/10 text-gray-400 text-sm rounded-bl-md">
                    <span className="animate-pulse">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-white/10">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask a question about the content..."
                  className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all"
                  disabled={chatLoading}
                />
                <button
                  type="submit"
                  disabled={chatLoading || !chatInput.trim()}
                  className="gradient-btn px-5 py-3 text-sm disabled:opacity-40"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </main>
  );
}
