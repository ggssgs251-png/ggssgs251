import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  Brain,
  Code2,
  Database,
  ArrowRight,
  Sparkles,
  Shield,
  BookOpen,
} from "lucide-react";

const fadeUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
};

const stagger = {
  animate: { transition: { staggerChildren: 0.1 } },
};

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg">ggssgs251</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="inline-flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-all"
            >
              Get Started
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <motion.div
          className="max-w-5xl mx-auto text-center"
          initial="initial"
          animate="animate"
          variants={stagger}
        >
          <motion.div
            variants={fadeUp}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-sm text-primary font-medium mb-8"
          >
            <Sparkles className="w-4 h-4" />
            Powered by Strands Agents + Ollama
          </motion.div>

          <motion.h1
            variants={fadeUp}
            className="text-4xl sm:text-5xl lg:text-7xl font-extrabold tracking-tight leading-tight"
          >
            Your{" "}
            <span className="gradient-text">AI Agent Team</span>
            {" "}for Data & Code
          </motion.h1>

          <motion.p
            variants={fadeUp}
            className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed"
          >
            A multi-agent AI system with a Data Tutor and Code Advisor, augmented
            with your proprietary knowledge. Chat, upload documents, and get
            intelligent answers — all running locally and privately.
          </motion.p>

          <motion.div variants={fadeUp} className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-primary text-primary-foreground font-semibold text-lg hover:opacity-90 transition-all shadow-lg shadow-primary/20"
            >
              Start Free
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl border text-lg font-medium hover:bg-muted transition-all"
            >
              Sign In
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold">
              Everything you need
            </h2>
            <p className="mt-4 text-muted-foreground text-lg max-w-2xl mx-auto">
              Three specialized agents, one seamless experience.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Brain,
                title: "Orchestrator",
                description:
                  "Intelligently routes your questions to the right specialist agent. Knows when to ask the Data Tutor vs the Code Advisor.",
                gradient: "from-violet-500 to-purple-600",
              },
              {
                icon: Database,
                title: "Data Tutor",
                description:
                  "Your data science mentor. Explains statistics, analyzes datasets, and suggests visualizations and preprocessing strategies.",
                gradient: "from-blue-500 to-cyan-500",
              },
              {
                icon: Code2,
                title: "Code Advisor",
                description:
                  "Your programming companion. Reviews code, suggests improvements, explains complex logic, and teaches best practices.",
                gradient: "from-emerald-500 to-teal-500",
              },
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                className="relative group"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="p-8 rounded-2xl border bg-card hover:shadow-xl transition-all duration-300">
                  <div
                    className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-5 shadow-lg`}
                  >
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* RAG Feature */}
      <section className="py-20 px-4 bg-gradient-to-b from-muted/20 to-background">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="grid md:grid-cols-2 gap-12 items-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium text-primary mb-4">
                <Shield className="w-3.5 h-3.5" />
                Private & Local
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Your data stays{" "}
                <span className="gradient-text">yours</span>
              </h2>
              <p className="text-muted-foreground text-lg leading-relaxed mb-6">
                Upload PDFs, Word docs, or text files to build a private knowledge
                base. The RAG engine indexes your documents using local embeddings,
                so your proprietary data never leaves your machine.
              </p>
              <ul className="space-y-3">
                {[
                  { icon: BookOpen, text: "Support for PDF, DOCX, TXT, Markdown" },
                  { icon: Database, text: "Semantic search across all your documents" },
                  { icon: Shield, text: "100% local — no data sent to external APIs" },
                ].map((item) => (
                  <li key={item.text} className="flex items-start gap-3">
                    <div className="mt-0.5 w-5 h-5 rounded bg-primary/10 flex items-center justify-center shrink-0">
                      <item.icon className="w-3 h-3 text-primary" />
                    </div>
                    <span className="text-muted-foreground">{item.text}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative">
              <div className="rounded-2xl border bg-card p-8 shadow-xl">
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="ml-2 font-mono">knowledge-base</span>
                  </div>
                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-muted/50 border text-sm">
                      <span className="text-primary font-medium">Q:</span> What does our Q3 report say about customer churn?
                    </div>
                    <div className="p-3 rounded-lg bg-primary/5 border border-primary/20 text-sm">
                      <span className="text-primary font-medium">A:</span> Based on your Q3 report, customer churn decreased by 12% due to the new onboarding flow...
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Database className="w-3 h-3" />
                      Retrieved from: Q3_Analysis_Report.pdf
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <motion.div
          className="max-w-3xl mx-auto text-center"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to meet your AI team?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">
            No cloud costs. No data sharing. Just you, your documents, and
            three intelligent assistants working together.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-primary text-primary-foreground font-semibold text-lg hover:opacity-90 transition-all shadow-lg shadow-primary/20"
          >
            Create Your Account
            <ArrowRight className="w-5 h-5" />
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t">
        <div className="max-w-6xl mx-auto text-center text-sm text-muted-foreground">
          ggssgs251 — Powered by Strands Agents SDK &middot; Ollama &middot; FastAPI &middot; React
        </div>
      </footer>
    </div>
  );
}
