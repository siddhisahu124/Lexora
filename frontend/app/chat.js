import { useState } from "react";

export default function Chat() {
  const [msg, setMsg] = useState("");
  const [reply, setReply] = useState("");

  async function send() {
    const res = await fetch(`http://127.0.0.1:8000/ask?q=${msg}`);
    const data = await res.json();
    setReply(data.answer);
  }

  return (
    <div>
      <input onChange={e => setMsg(e.target.value)} />
      <button onClick={send}>Send</button>
      <p>{reply}</p>
    </div>
  );
}
