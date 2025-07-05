import { useState } from 'react'
export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")

  const sendMessage = async () => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    })
    const data = await res.json()
    setMessages([...messages, { user: input, bot: data.response }])
    setInput("")
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">AI Financial Agent</h1>
      <div className="my-4">
        {messages.map((m, i) => (
          <div key={i}>
            <p><strong>You:</strong> {m.user}</p>
            <p><strong>Agent:</strong> {m.bot}</p>
          </div>
        ))}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} className="border p-2" />
      <button onClick={sendMessage} className="bg-blue-500 text-white px-4 py-2 ml-2">Send</button>
    </div>
  )
}