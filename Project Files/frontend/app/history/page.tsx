"use client"

import { useEffect, useState } from "react"
import { History as HistoryIcon, Search, Trash2, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ConfidenceBadge } from "@/components/ConfidenceBadge"
import axios from "axios"
import { useRouter } from "next/navigation"
import { formatDistanceToNow } from "date-fns"

interface HistoryItem {
  id: number
  natural_query: string
  generated_sql: string
  model_used: string
  confidence_score: number | null
  created_at: string
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const router = useRouter()

  const fetchHistory = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/history?page_size=50")
      setHistory(res.data.items)
    } catch (err) {
      console.error("Failed to fetch history:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/history/${id}`)
      setHistory(history.filter(item => item.id !== id))
    } catch (err) {
      console.error("Failed to delete history item:", err)
    }
  }

  const handleLoadQuery = (query: string) => {
    // In a real app we might pass this via context or state manager,
    // but a simple query param works for jumping to the console.
    router.push(`/console?q=${encodeURIComponent(query)}`)
  }

  const filteredHistory = history.filter(item => 
    item.natural_query.toLowerCase().includes(search.toLowerCase()) || 
    item.generated_sql.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center">
            <HistoryIcon className="w-8 h-8 mr-3 text-primary" />
            Query History
          </h1>
          <p className="text-muted-foreground mt-2">
            Review and reuse your past database queries.
          </p>
        </div>
        
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Search queries..." 
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* History Feed */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12 text-muted-foreground animate-pulse">
            Loading history...
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-border rounded-lg bg-card/50">
            <p className="text-muted-foreground">No queries found in history.</p>
          </div>
        ) : (
          filteredHistory.map((item) => (
            <div key={item.id} className="group flex flex-col md:flex-row gap-4 p-5 rounded-lg border border-border bg-card hover:bg-secondary/20 transition-colors">
              <div className="flex-1 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-foreground">
                    "{item.natural_query}"
                  </h3>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">
                      {item.created_at ? formatDistanceToNow(new Date(item.created_at), { addSuffix: true }) : "Unknown time"}
                    </span>
                    <ConfidenceBadge score={item.confidence_score} />
                  </div>
                </div>
                
                <div className="p-3 bg-[#0a0a0a] rounded-md overflow-x-auto border border-border">
                  <code className="text-sm font-mono text-muted-foreground">
                    {item.generated_sql}
                  </code>
                </div>

                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="px-2 py-1 bg-secondary rounded">Model: {item.model_used}</span>
                </div>
              </div>

              <div className="flex flex-row md:flex-col justify-end gap-2 shrink-0 border-t md:border-t-0 md:border-l border-border pt-4 md:pt-0 md:pl-4">
                <Button 
                  variant="default" 
                  className="w-full md:w-auto"
                  onClick={() => handleLoadQuery(item.natural_query)}
                >
                  Load in Console
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full md:w-auto text-destructive hover:bg-destructive/10 hover:text-destructive border-transparent md:border-border"
                  onClick={() => handleDelete(item.id)}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
