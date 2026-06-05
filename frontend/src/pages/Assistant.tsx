import { useState, useRef, useEffect } from "react";
import { useChat } from "@/hooks/useAssistant";
import { Bot, Send, User, Sparkles } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Assistant() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Olá! Sou seu assistente financeiro. Como posso ajudar hoje?" },
  ]);
  const [input, setInput] = useState("");
  const chatMutation = useChat();
  const [convId, setConvId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    const res = await chatMutation.mutateAsync({ message: input, conversation_id: convId });
    setConvId(res.conversation_id);
    setMessages((prev) => [...prev, { role: "assistant", content: res.message }]);
  };

  return (
    <div className="animate-fade-in flex h-[calc(100vh-8rem)] flex-col">
      <div className="flex items-center gap-3 pb-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-600">
          <Bot className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight">Assistente IA</h1>
          <p className="text-xs text-muted-foreground">Inteligência artificial para suas finanças</p>
        </div>
      </div>

      <div className="glass-card flex-1 overflow-y-auto rounded-xl p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`flex max-w-[80%] items-start gap-3 rounded-xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-accent/30"
              }`}
            >
              {msg.role === "assistant" && (
                <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
              )}
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.role === "user" && (
                <User className="mt-0.5 h-4 w-4 shrink-0" />
              )}
            </div>
          </div>
        ))}
        {chatMutation.isPending && (
          <div className="flex justify-start">
            <div className="flex items-center gap-3 rounded-xl bg-accent/30 px-4 py-3">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              <p className="text-sm text-muted-foreground">Pensando...</p>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="mt-4 flex items-center gap-3">
        <div className="glass-input flex flex-1 items-center gap-2 rounded-lg px-4 py-2.5">
          <input
            placeholder="Digite sua mensagem..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>
        <button
          type="submit"
          disabled={!input.trim() || chatMutation.isPending}
          className="glass-button flex h-10 w-10 items-center justify-center rounded-lg disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
