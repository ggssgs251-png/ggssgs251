import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Brain,
  MessageSquare,
  Upload,
  FileText,
  Trash2,
  LogOut,
  Database,
  Code2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { useAuth } from "../lib/auth-context";
import {
  uploadDocument,
  listDocuments,
  deleteDocument,
  type DocumentList,
} from "../lib/api";

export function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [docs, setDocs] = useState<DocumentList | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [loadingDocs, setLoadingDocs] = useState(true);

  async function fetchDocs() {
    try {
      const data = await listDocuments();
      setDocs(data);
    } catch {
      // ignore
    } finally {
      setLoadingDocs(false);
    }
  }

  useEffect(() => {
    fetchDocs();
  }, []);

  async function handleUpload(file: File) {
    setUploading(true);
    setUploadMsg(null);
    try {
      const res = await uploadDocument(file);
      setUploadMsg({ type: "success", text: res.message });
      await fetchDocs();
    } catch (err: any) {
      setUploadMsg({ type: "error", text: err.message || "Upload failed" });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDelete(filename: string) {
    try {
      await deleteDocument(filename);
      await fetchDocs();
    } catch {
      // ignore
    }
  }

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      {/* Header */}
      <header className="glass border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg">ggssgs251</span>
            <span className="hidden sm:inline text-sm text-muted-foreground ml-2">
              Dashboard
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/chat")}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all"
            >
              <MessageSquare className="w-4 h-4" />
              Open Chat
            </button>
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border text-sm text-muted-foreground hover:text-foreground transition-all"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Welcome */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-2xl sm:text-3xl font-bold">
            Welcome, {user?.username}
          </h1>
          <p className="text-muted-foreground mt-1">
            Your AI agent team is ready. Upload documents to build your knowledge
            base, then chat with your agents.
          </p>
        </motion.div>

        {/* Quick Actions */}
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            {
              icon: MessageSquare,
              title: "Chat with Agents",
              desc: "Talk to your AI team",
              onClick: () => navigate("/chat"),
              gradient: "from-primary to-accent",
            },
            {
              icon: Upload,
              title: "Upload Documents",
              desc: "Build your knowledge base",
              onClick: () => fileInputRef.current?.click(),
              gradient: "from-blue-500 to-cyan-500",
            },
            {
              icon: RefreshCw,
              title: "Refresh Documents",
              desc: "Update document list",
              onClick: fetchDocs,
              gradient: "from-emerald-500 to-teal-500",
            },
          ].map((action) => (
            <motion.button
              key={action.title}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={action.onClick}
              className="p-6 rounded-2xl border bg-card text-left hover:shadow-lg transition-all"
            >
              <div
                className={`w-10 h-10 rounded-xl bg-gradient-to-br ${action.gradient} flex items-center justify-center mb-3`}
              >
                <action.icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-semibold">{action.title}</h3>
              <p className="text-sm text-muted-foreground mt-1">{action.desc}</p>
            </motion.button>
          ))}
        </div>

        {/* Agent Info Cards */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Your AI Team</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {[
              {
                icon: Database,
                name: "Data Tutor",
                desc: "Data science, statistics, analysis, visualizations",
                gradient: "from-blue-500 to-cyan-500",
              },
              {
                icon: Code2,
                name: "Code Advisor",
                desc: "Code reviews, explanations, best practices",
                gradient: "from-emerald-500 to-teal-500",
              },
            ].map((agent) => (
              <div
                key={agent.name}
                className="p-6 rounded-2xl border bg-card hover:shadow-md transition-all"
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.gradient} flex items-center justify-center shrink-0`}
                  >
                    <agent.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{agent.name}</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {agent.desc}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Knowledge Base */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Knowledge Base</h2>
            <label className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium cursor-pointer hover:opacity-90 transition-all">
              <Upload className="w-4 h-4" />
              Upload Document
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.md,.pdf,.docx"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleUpload(file);
                }}
              />
            </label>
          </div>

          {/* Upload status */}
          {uploading && (
            <div className="mb-4 p-4 rounded-xl border bg-card flex items-center gap-3 text-sm">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              Indexing document...
            </div>
          )}

          {uploadMsg && (
            <div
              className={`mb-4 p-4 rounded-xl border flex items-start gap-3 text-sm ${
                uploadMsg.type === "success"
                  ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                  : "bg-destructive/10 border-destructive/20 text-destructive"
              }`}
            >
              {uploadMsg.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              )}
              {uploadMsg.text}
            </div>
          )}

          {/* Document List */}
          <div className="rounded-2xl border bg-card overflow-hidden">
            {loadingDocs ? (
              <div className="p-8 text-center text-muted-foreground animate-pulse">
                Loading documents...
              </div>
            ) : !docs || docs.count === 0 ? (
              <div className="p-8 text-center">
                <FileText className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
                <p className="text-muted-foreground">No documents indexed yet</p>
                <p className="text-sm text-muted-foreground/60 mt-1">
                  Upload a PDF, DOCX, TXT, or Markdown file to get started
                </p>
              </div>
            ) : (
              <div className="divide-y">
                {docs.documents.map((doc) => (
                  <div
                    key={doc.filename}
                    className="flex items-center justify-between px-6 py-4 hover:bg-muted/30 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-muted-foreground" />
                      <span className="text-sm font-medium">{doc.filename}</span>
                    </div>
                    <button
                      onClick={() => handleDelete(doc.filename)}
                      className="p-2 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
