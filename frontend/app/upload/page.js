"use client";
import { useState } from "react";

export default function Upload() {
  const [docs, setDocs] = useState(
    JSON.parse(localStorage.getItem("docs") || "[]")
  );
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [loading, setLoading] = useState(false);

  async function uploadFile(e) {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    const newDoc = {
      id: data.doc_id,
      title: file.name,
    };

    const updatedDocs = [...docs, newDoc];
    setDocs(updatedDocs);
    localStorage.setItem("docs", JSON.stringify(updatedDocs));
    setSelectedDoc(newDoc);

    setLoading(false);
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div
        className="
          p-8 w-[420px] rounded-2xl
          bg-glass backdrop-blur
          border border-white/10
          shadow-2xl
          animate-fadeInScale
        "
      >
        <h2 className="text-xl font-semibold mb-6 text-center">
          Upload Document
        </h2>

        <input
          type="file"
          onChange={uploadFile}
          disabled={loading}
          className="
            mb-6 w-full text-sm
            file:mr-4 file:py-2 file:px-4
            file:rounded-lg file:border-0
            file:bg-white/10 file:text-white
            hover:file:bg-white/20
            transition
          "
        />

        {loading && (
          <p className="text-center text-sm text-white/60 animate-pulse">
            Processing...
          </p>
        )}
      </div>
    </div>
  );
}