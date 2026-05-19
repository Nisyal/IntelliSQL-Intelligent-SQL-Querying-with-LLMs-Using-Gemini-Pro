"use client"

import { Card } from "./ui/card"
import { Copy, Terminal } from "lucide-react"
import { Button } from "./ui/button"

export function SQLPreview({ sql }: { sql: string }) {
  if (!sql) return null

  const handleCopy = () => {
    navigator.clipboard.writeText(sql)
  }

  // Very basic syntax highlighting for demo purposes
  const highlightSQL = (text: string) => {
    const keywords = ["SELECT", "FROM", "WHERE", "AND", "OR", "GROUP BY", "ORDER BY", "LIMIT", "COUNT", "SUM", "AVG", "JOIN", "ON", "ILIKE", "AS"]
    let highlighted = text
    keywords.forEach(kw => {
      const regex = new RegExp(`\\b${kw}\\b`, 'gi')
      highlighted = highlighted.replace(regex, `<span class="text-primary font-bold">$&</span>`)
    })
    return highlighted
  }

  return (
    <Card className="overflow-hidden border-border bg-[#0a0a0a]">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card">
        <div className="flex items-center text-sm font-medium text-muted-foreground">
          <Terminal className="w-4 h-4 mr-2" />
          Generated SQL Preview
        </div>
        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleCopy} title="Copy SQL">
          <Copy className="w-4 h-4 text-muted-foreground" />
        </Button>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="text-sm font-mono text-foreground">
          <code dangerouslySetInnerHTML={{ __html: highlightSQL(sql) }} />
        </pre>
      </div>
    </Card>
  )
}
