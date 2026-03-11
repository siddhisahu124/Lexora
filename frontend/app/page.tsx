export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center">
      <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
        AETHER
      </h1>
      <p className="text-gray-300 mt-3">
        Autonomous Document Intelligence Platform
      </p>

      <div className="mt-10 flex gap-6">
        <a
          href="/upload"
          className="px-6 py-3 rounded-xl bg-glass backdrop-blur border border-white/10 hover:bg-white/10 transition"
        >
          Upload Documents
        </a>
        <a
          href="/chat"
          className="px-6 py-3 rounded-xl bg-accent hover:opacity-90 transition"
        >
          Start Chat
        </a>
      </div>
    </div>
  );
}
