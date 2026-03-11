"use client";

import { useEffect, useState } from "react";
import { FileText, Trash2, RotateCcw, Bot, Pencil } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function ChatPage() {
  const [docs, setDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [chatMessages, setChatMessages] = useState({});
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);

  /* ---------------- Load documents ---------------- */
  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("docs") || "[]");
    const normalized = stored.map((d) =>
      typeof d === "string"
        ? { id: d, title: `Chat ${d.slice(0, 6)}` }
        : d
    );
    setDocs(normalized);
    setSelectedDoc(normalized[0] || null);
  }, []);

  /* ---------------- Load history ---------------- */
  useEffect(() => {
    if (!selectedDoc) return;
    loadHistory(selectedDoc.id);
  }, [selectedDoc]);

  /* ---------------- Poll document status ---------------- */
  useEffect(() => {
    if (!selectedDoc || !processing) return;

    const interval = setInterval(async () => {
      const res = await fetch(
        `http://127.0.0.1:8000/document-status/${selectedDoc.id}`
      );
      const data = await res.json();

      if (data.status === "ready") {
        setProcessing(false);
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [selectedDoc, processing]);

  function loadHistory(docId) {
    fetch(`http://127.0.0.1:8000/history/${docId}`)
      .then((res) => res.json())
      .then((data) => {
        const formatted = data.map((m) => ({
          role: m.role,
          text: m.content,
        }));
        setChatMessages((prev) => ({
          ...prev,
          [docId]: formatted,
        }));
      })
      .catch(() => {});
  }

  const messages = selectedDoc
    ? chatMessages[selectedDoc.id] || []
    : [];

  /* ---------------- Upload document ---------------- */
  async function uploadFile(e) {
    const file = e.target.files[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: form,
    });

    const data = await res.json();

    console.log("UPLOAD RESPONSE:", data);

    if (data.doc_id) {
      const newDoc = {
        id: data.doc_id,
        title: file.name,
      };

      setDocs((prev) => {
        const updated = [...prev, newDoc];
        localStorage.setItem("docs", JSON.stringify(updated));
        return updated;
      });

      setSelectedDoc(newDoc);
      localStorage.setItem("active_doc", data.doc_id);

      // Start polling
      setProcessing(true);

      loadHistory(data.doc_id);
    }
  }

  /* ---------------- Send message ---------------- */
  async function sendMessage() {
    if (!input.trim() || !selectedDoc || loading || processing) return;

    const text = input.trim();
    setInput("");
    setLoading(true);

    setChatMessages((prev) => ({
      ...prev,
      [selectedDoc.id]: [...(prev[selectedDoc.id] || []), { role: "user", text }],
    }));

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          doc_id: selectedDoc.id,
          question: text,
        }),
      });

      const data = await res.json();

      setChatMessages((prev) => ({
        ...prev,
        [selectedDoc.id]: [
          ...(prev[selectedDoc.id] || []),
          { role: "assistant", text: data.answer },
        ],
      }));
    } catch {
      setChatMessages((prev) => ({
        ...prev,
        [selectedDoc.id]: [
          ...(prev[selectedDoc.id] || []),
          { role: "assistant", text: "⚠️ Something went wrong." },
        ],
      }));
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function renameChat(doc) {
    const name = prompt("Rename chat:", doc.title);
    if (!name) return;

    const updated = docs.map((d) =>
      d.id === doc.id ? { ...d, title: name } : d
    );

    setDocs(updated);
    localStorage.setItem("docs", JSON.stringify(updated));
    setSelectedDoc({ ...doc, title: name });
  }

  async function newChat() {
    if (!selectedDoc) return;
    await fetch(`http://127.0.0.1:8000/new-chat/${selectedDoc.id}`, {
      method: "POST",
    });
    setChatMessages((prev) => ({ ...prev, [selectedDoc.id]: [] }));
  }

  async function deleteDoc() {
    if (!selectedDoc) return;
    if (!confirm("Delete document permanently?")) return;

    await fetch(`http://127.0.0.1:8000/document/${selectedDoc.id}`, {
      method: "DELETE",
    });

    const updatedDocs = docs.filter((d) => d.id !== selectedDoc.id);
    setDocs(updatedDocs);
    localStorage.setItem("docs", JSON.stringify(updatedDocs));

    setChatMessages((prev) => {
      const copy = { ...prev };
      delete copy[selectedDoc.id];
      return copy;
    });

    setSelectedDoc(updatedDocs[0] || null);
  }

  /* ===================== UI ===================== */
  return (
    <div className="flex h-screen bg-zinc-100 text-zinc-900 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-4 border-b font-semibold flex items-center gap-2">
          <FileText size={18} /> Chats
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {docs.map((doc) => (
            <div
              key={doc.id}
              className={`flex items-center justify-between px-3 py-2 rounded-md text-sm cursor-pointer
                transition-colors duration-200
                ${
                  selectedDoc?.id === doc.id
                    ? "bg-zinc-200"
                    : "hover:bg-zinc-100"
                }`}
            >
              <span onClick={() => setSelectedDoc(doc)} className="truncate">
                {doc.title}
              </span>
              <button onClick={() => renameChat(doc)}>
                <Pencil size={14} />
              </button>
            </div>
          ))}
        </div>

        <div className="p-4 border-t space-y-2">
          <button onClick={newChat} className="w-full flex gap-2 text-sm">
            <RotateCcw size={14} /> New Chat
          </button>
          <button
            onClick={deleteDoc}
            className="w-full flex gap-2 text-sm text-red-600"
          >
            <Trash2 size={14} /> Delete Document
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col bg-white">
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          <div className="text-xs text-gray-500 mb-2">
            Active document: {selectedDoc?.title}
            {processing && (
              <span className="ml-2 text-yellow-500 animate-pulse">
                ⏳ Processing...
              </span>
            )}
          </div>

          {processing && (
            <div className="p-3 border border-yellow-300 rounded text-sm text-yellow-700 bg-yellow-50">
              ⏳ Document is still being processed. Chat will enable automatically.
            </div>
          )}

          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`
                  max-w-[75%] rounded-xl px-4 py-3 text-sm border
                  animate-slideUp
                `}
              >
                {m.role === "assistant" && (
                  <Bot size={16} className="mb-2" />
                )}
                <ReactMarkdown>{m.text}</ReactMarkdown>

                {/* Revenue chart */}
                {m.role === "assistant" &&
                  m.text?.includes("Revenue chart generated at:") &&
                  selectedDoc && (
                    <div className="mt-3">
                      <img
                        src={`http://127.0.0.1:8000/chart/${selectedDoc.id}`}
                        alt="Revenue Chart"
                        className="rounded-lg border w-full max-w-md"
                        onError={(e) => (e.target.style.display = "none")}
                      />
                    </div>
                  )}

                {/* Revenue metrics table */}
                {m.role === "assistant" &&
                  m.text?.includes("Revenue mentions found:") && (
                    <div className="mt-3 border rounded-lg overflow-hidden text-xs">
                      <div className="bg-zinc-100 px-3 py-2 font-semibold text-zinc-700">
                        📊 Extracted Revenue Figures
                      </div>
                      <table className="w-full">
                        <thead className="bg-zinc-50">
                          <tr>
                            <th className="px-3 py-2 text-left text-zinc-500">#</th>
                            <th className="px-3 py-2 text-left text-zinc-500">Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {m.text
                            .split("\n")
                            .filter((line) => line.match(/\$[\d,\.]+/))
                            .map((line, i) => (
                              <tr key={i} className="border-t">
                                <td className="px-3 py-2 text-zinc-400">{i + 1}</td>
                                <td className="px-3 py-2 font-medium text-zinc-800">
                                  {line.trim()}
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  )}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="max-w-[75%] rounded-xl px-4 py-3 text-sm border text-gray-500">
                <Bot size={16} className="inline mr-2" />
                Assistant is thinking...
              </div>
            </div>
          )}
        </div>

        {/* Fixed input */}
        <div className="border-t px-6 py-4 bg-white flex items-center gap-2">
          {/* Upload Button */}
          <input
            type="file"
            accept=".pdf"
            onChange={uploadFile}
            className="hidden"
            id="upload"
          />
          <label
            htmlFor="upload"
            className="px-3 py-2 bg-gray-200 rounded cursor-pointer"
          >
            Upload
          </label>

          {/* Text Input */}
          <textarea
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={processing}
            className={`flex-1 border rounded px-3 py-2 ${
              processing ? "opacity-50 cursor-not-allowed" : ""
            }`}
            placeholder={
              processing
                ? "Waiting for document to finish processing..."
                : "Enter to send, Shift+Enter for new line"
            }
          />

          {/* Send Button */}
          <button
            onClick={sendMessage}
            disabled={processing}
            className={`bg-black text-white px-4 py-2 rounded transition ${
              processing
                ? "opacity-50 cursor-not-allowed"
                : "hover:scale-105"
            }`}
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
}