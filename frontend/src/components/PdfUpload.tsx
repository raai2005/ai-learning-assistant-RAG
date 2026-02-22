"use client";

import { useCallback, useRef, useState } from "react";
import { processPdf } from "@/lib/api";

interface PdfUploadProps {
  onToast: (message: string, type: "success" | "error") => void;
  onSuccess: (contentId: string) => void;
}

const MAX_FILE_SIZE_MB = 25;

export default function PdfUpload({ onToast, onSuccess }: PdfUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    if (file.type !== "application/pdf") {
      onToast("Only PDF files are accepted", "error");
      return false;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      onToast(`File size must be under ${MAX_FILE_SIZE_MB}MB`, "error");
      return false;
    }
    return true;
  };

  const handleFile = useCallback(
    (file: File) => {
      if (validateFile(file)) {
        setSelectedFile(file);
        onToast(`"${file.name}" ready to upload`, "success");
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [onToast]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);

    try {
      // Store the PDF blob URL for the learn page viewer
      const blobUrl = URL.createObjectURL(selectedFile);
      sessionStorage.setItem("pdfBlobUrl", blobUrl);
      sessionStorage.setItem("sourceType", "pdf");
      sessionStorage.setItem("sourceTitle", selectedFile.name);

      const result = await processPdf(selectedFile);
      onToast(
        `"${result.filename}" processed! ${result.chunks_count} chunks from ${result.pages_count} pages.`,
        "success"
      );
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      onSuccess(result.content_id);
    } catch (err) {
      onToast(err instanceof Error ? err.message : "Upload failed", "error");
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div
      className="glass-card p-8 animate-fade-in-up animate-pulse-glow"
      style={{ animationDelay: "0.15s" }}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-blue-500/15 flex items-center justify-center">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" className="text-blue-400">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            <line x1="12" y1="18" x2="12" y2="12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            <polyline points="9 15 12 12 15 15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Upload PDF</h2>
          <p className="text-sm text-gray-400 mt-0.5">Drag & drop or browse to upload</p>
        </div>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`drop-zone flex flex-col items-center justify-center py-12 px-6 cursor-pointer ${isDragOver ? "drag-over" : ""}`}
      >
        <input ref={fileInputRef} type="file" accept=".pdf" onChange={handleFileSelect} className="hidden" />
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300 ${isDragOver ? "bg-purple-500/20 scale-110" : "bg-white/5"}`}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className={`transition-colors duration-300 ${isDragOver ? "text-purple-400" : "text-gray-500"}`}>
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points="17 8 12 3 7 8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
        </div>
        <p className="text-sm text-gray-400 text-center">
          <span className="text-purple-400 font-medium">Click to browse</span> or drag and drop
        </p>
        <p className="text-xs text-gray-600 mt-1.5">PDF only • Max {MAX_FILE_SIZE_MB}MB</p>
      </div>

      {/* Selected File */}
      {selectedFile && (
        <div className="mt-4 flex items-center gap-3 p-3.5 bg-white/5 rounded-xl border border-white/8 animate-fade-in">
          <div className="w-10 h-10 rounded-lg bg-red-500/15 flex items-center justify-center flex-shrink-0">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-red-400">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="currentColor" strokeWidth="1.8" />
              <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="1.8" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{selectedFile.name}</p>
            <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
          </div>
          {!isUploading && (
            <button
              onClick={(e) => { e.stopPropagation(); removeFile(); }}
              className="text-gray-500 hover:text-red-400 transition-colors flex-shrink-0 cursor-pointer"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          )}
        </div>
      )}

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={!selectedFile || isUploading}
        className="gradient-btn w-full py-3.5 text-sm mt-4 flex items-center justify-center gap-2"
      >
        {isUploading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
              <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" className="opacity-75" />
            </svg>
            Processing...
          </>
        ) : (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload PDF
          </>
        )}
      </button>
    </div>
  );
}
