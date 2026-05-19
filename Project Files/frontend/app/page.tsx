import Link from "next/link"
import { ArrowRight, Database, Terminal, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-2rem)] items-center justify-center p-8 text-center">
      {/* Hero Section */}
      <div className="max-w-4xl space-y-8 animate-in slide-in-from-bottom-8 duration-700 fade-in zoom-in-95">
        
        <div className="inline-flex items-center rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-sm font-medium text-primary mb-4">
          <Zap className="mr-2 h-4 w-4" />
          Powered by Llama 3.3 & Qwen 2.5 Coder
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-foreground">
          Talk to your database in <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-cyan-400">
            plain English.
          </span>
        </h1>
        
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          IntelliSQL transforms your natural language questions into highly accurate PostgreSQL queries instantly. No SQL expertise required.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link href="/console">
            <Button size="lg" className="h-14 px-8 text-lg font-medium group">
              Start Querying
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
          <Link href="/history">
            <Button size="lg" variant="outline" className="h-14 px-8 text-lg font-medium bg-card">
              View History
            </Button>
          </Link>
        </div>
      </div>

      {/* Decorative Mockup */}
      <div className="mt-20 w-full max-w-5xl mx-auto animate-in slide-in-from-bottom-12 duration-1000 fade-in delay-200 fill-mode-both">
        <div className="rounded-xl border border-border bg-[#0a0a0a] shadow-2xl overflow-hidden relative">
          
          {/* Mockup Header */}
          <div className="flex items-center px-4 py-3 border-b border-border bg-card">
            <div className="flex space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            <div className="mx-auto text-xs text-muted-foreground font-mono flex items-center">
              <Database className="w-3 h-3 mr-2" />
              intellisql-demo
            </div>
          </div>

          {/* Mockup Body */}
          <div className="p-6 md:p-8 grid md:grid-cols-2 gap-8 text-left">
            <div className="space-y-4">
              <div className="text-sm font-medium text-muted-foreground">User Ask:</div>
              <div className="p-4 rounded-md border border-border bg-card font-mono text-sm">
                Show me the top 5 students who scored above 80 in BTech.
              </div>
            </div>
            <div className="space-y-4">
              <div className="text-sm font-medium text-muted-foreground flex items-center justify-between">
                <span>Generated SQL:</span>
                <span className="text-xs px-2 py-1 bg-green-500/15 text-green-500 rounded-full border border-green-500/20">Confidence: 98%</span>
              </div>
              <div className="p-4 rounded-md border border-border bg-[#0a0a0a] font-mono text-sm text-foreground">
                <span className="text-primary font-bold">SELECT</span> * <span className="text-primary font-bold">FROM</span> students
                <br />
                <span className="text-primary font-bold">WHERE</span> class <span className="text-primary font-bold">ILIKE</span> 'BTech' <span className="text-primary font-bold">AND</span> marks {'>'} 80
                <br />
                <span className="text-primary font-bold">ORDER BY</span> marks <span className="text-primary font-bold">DESC</span>
                <br />
                <span className="text-primary font-bold">LIMIT</span> 5;
              </div>
            </div>
          </div>
          
          {/* Subtle glow effect behind mockup */}
          <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/20 to-cyan-400/20 blur-2xl -z-10 rounded-xl opacity-50"></div>
        </div>
      </div>
    </div>
  )
}
