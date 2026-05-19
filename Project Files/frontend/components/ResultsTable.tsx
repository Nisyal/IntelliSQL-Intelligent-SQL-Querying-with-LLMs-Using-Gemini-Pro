"use client"

import { Download } from "lucide-react"
import { Button } from "./ui/button"

interface ResultsTableProps {
  columns: string[]
  rows: any[][]
}

export function ResultsTable({ columns, rows }: ResultsTableProps) {
  if (!columns || !rows || columns.length === 0) return null

  const exportCSV = () => {
    const csvContent = [
      columns.join(","),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(","))
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.setAttribute("href", url)
    link.setAttribute("download", "intellisql_results.csv")
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium tracking-tight">Query Results ({rows.length} rows)</h3>
        <Button variant="outline" size="sm" onClick={exportCSV}>
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>
      
      <div className="rounded-md border border-border overflow-hidden bg-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-secondary/50 border-b border-border">
              <tr>
                <th className="px-4 py-3 w-12 text-center font-medium">#</th>
                {columns.map((col, i) => (
                  <th key={i} className="px-4 py-3 font-medium whitespace-nowrap">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b border-border/50 hover:bg-secondary/20 transition-colors last:border-0">
                  <td className="px-4 py-3 text-center text-muted-foreground font-mono text-xs">
                    {rowIndex + 1}
                  </td>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex} className="px-4 py-3 whitespace-nowrap">
                      {cell !== null ? String(cell) : <span className="text-muted-foreground italic">null</span>}
                    </td>
                  ))}
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={columns.length + 1} className="px-4 py-8 text-center text-muted-foreground">
                    No results found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
