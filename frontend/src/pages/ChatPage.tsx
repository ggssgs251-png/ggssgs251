import { useEffect, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Brain,
  ArrowLeft,
  Send,
  Trash2,
  Loader2,
  Database,
  Code2,
  Bot,
  User,
} from "lucide-react";
import { useAuth } from "../lib/auth-context";
import { sendMessage, resetConversation, queryKnowledgeBase } from "../lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: string;
  routingPath?: string[];
}

export function ChatPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant" as const,
      content:
        "Hello! I'm your AI agent team. Ask me anything about data analysis, statistics, coding, or your uploaded documents. I'll route your question to the right specialist — Data Tutor or Code Advisor.",
      agent: "orchestrator",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [ragQuery, setRagQuery] = useState("");
  const [ragResults, setRagResults] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput("");

    // Add user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await sendMessage(text);
      const assistantMsg: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: res.reply,
        agent: res.agent,
        routingPath: res.routing_path,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: `❌ Error: ${err.message || "Something went wrong. Is the backend running?"}`,
          agent: "system",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  async function handleReset() {
    try {
      await resetConversation();
      setMessages([
        {
          id: `welcome-${Date.now()}`,
          role: "assistant" as const,
          content: "Conversation reset. How can I help you?",
          agent: "orchestrator",
        },
      ]);
    } catch {
      // ignore
    }
  }

  async function handleRagQuery() {
    const q = ragQuery.trim();
    if (!q) return;
    setRagResults(null);
    try {
      const res = await queryKnowledgeBase(q);
      if (res.sources.length === 0) {
        setRagResults("No relevant documents found.");
      } else {
        setRagResults(
          `Found ${res.sources.length} relevant passages:\n\n${res.sources
            .map(
              (s, i) =>
                `[${i + 1}] From: ${s.source}\n   Relevance: ${(s.score * 100).toFixed(0)}%\n   ${s.content.slice(0, 300)}...`
            )
            .join("\n\n")}`
        );
      }
    } catch (err: any) {
      setRagResults(`Error: ${err.message}`);
    }
  }

  function getAgentIcon(agent: string | undefined) {
    switch (agent) {
      case "data_tutor":
        return <Database className="w-4 h-4" />;
      case "code_advisor":
        return <Code2 className="w-4 h-4" />;
      default:
        return <Brain className="w-4 h-4" />;
    }
  }

  function getAgentColor(agent: string | undefined) {
    switch (agent) {
      case "data_tutor":
        return "from-blue-500 to-cyan-500";
      case "code_advisor":
        return "from-emerald-500 to-teal-500";
      default:
        return "from-primary to-accent";
    }
  }

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-b from-background via-background to-muted/30">
      {/* Header */}
      <header className="glass border-b shrink-0">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/dashboard")}
              className="p-2 rounded-lg hover:bg-muted transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Brain className="w-3.5 h-3.5 text-white" />
            </div>
            <div>
              <span className="font-bold text-sm">ggssgs251</span>
              <span className="text-xs text-muted-foreground ml-2">Chat</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border text-xs font-medium hover:bg-muted transition-all"
            >
              <Trash2 className="w-3.5 h-3.5" />
              New Chat
            </button>
            <button
              onClick={handleLogout}
              className="text-xs text-muted-foreground hover:text-foreground px-2 py-1"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden max-w-5xl mx-auto w-full">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {/* Assistant avatar */}
                {msg.role === "assistant" && (
                  <div
                    className={`w-8 h-8 rounded-xl bg-gradient-to-br ${getAgentColor(msg.agent)} flex items-center justify-center shrink-0 mt-1`}
                  >
                    {getAgentIcon(msg.agent)}
                  </div>
                )}

                <div
                  className={`max-w-[80%] ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-2xl rounded-tr-md px-4 py-2.5"
                      : "bg-card border rounded-2xl rounded-tl-md px-4 py-2.5"
                  }`}
                >
                  {msg.role === "assistant" && msg.agent && msg.agent !== "system" && (
                    <div className="text-xs font-medium text-muted-foreground mb-1.5 flex items-center gap-1.5">
                      {getAgentIcon(msg.agent)}
                      <span className="capitalize">{msg.agent.replace("_", " ")}</span>
                    </div>
                  )}
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>
                  {msg.routingPath && msg.routingPath.length > 1 && (
                    <div className="mt-2 pt-2 border-t text-xs text-muted-foreground flex items-center gap-1">
                      <span>Path:</span>
                      {msg.routingPath.map((p, i) => (
                        <span key={p} className="capitalize">
                          {i > 0 && " → "}
                          {p.replace("_", " ")}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* User avatar */}
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-xl bg-muted flex items-center justify-center shrink-0 mt-1 border">
                    <User className="w-4 h-4 text-muted-foreground" />
                  </div>
                )}
              </motion.div>
            ))}

            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shrink-0">
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                </div>
                <div className="bg-card border rounded-2xl rounded-tl-md px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="shrink-0 border-t bg-background/80 backdrop-blur-xl px-4 py-3">
            <form onSubmit={handleSubmit} className="flex gap-2 max-w-3xl mx-auto">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask your AI team anything..."
                className="flex-1 px-4 py-2.5 rounded-xl border bg-card focus:outline-none focus:ring-2 focus:ring-ring transition-all text-sm"
                disabled={loading}
                autoFocus
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-4 py-2.5 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-all disabled:opacity-50 flex items-center gap-1.5 text-sm"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Sidebar: RAG Query Tool */}
        <aside className="hidden lg:flex w-72 border-l flex-col bg-card/50">
          <div className="p-4 border-b">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Database className="w-4 h-4 text-primary" />
              Knowledge Base
            </h3>
            <p className="text-xs text-muted-foreground mt-1">
              Search your indexed documents
            </p>
          </div>
          <div className="p-4 flex-1 flex flex-col gap-3">
            <textarea
              value={ragQuery}
              onChange={(e) => setRagQuery(e.target.value)}
              placeholder="Search your documents..."
              className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none h-20"
            />
            <button
              onClick={handleRagQuery}
              disabled={!ragQuery.trim()}
              className="w-full px-3 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all disabled:opacity-50"
            >
              Search Documents
            </button>
            {ragResults && (
              <div className="flex-1 overflow-y-auto">
                <div className="p-3 rounded-lg bg-muted/50 border text-xs leading-relaxed whitespace-pre-wrap">
                  {ragResults}
                </div>
              </div>
            )}
            <div className="mt-auto text-center">
              <button
                onClick={() => navigate("/dashboard")}
                className="text-xs text-muted-foreground hover:text-primary transition-colors"
              >
                Manage documents →
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
