"use client"

import { useState } from "react"
import { Play, Sparkles, AlertCircle, DatabaseZap, Bot } from "lucide-react"
import { Button } from "@/components/ui/button"
import { QueryEditor } from "@/components/QueryEditor"
import { ConfidenceBadge } from "@/components/ConfidenceBadge"
import { SQLPreview } from "@/components/SQLPreview"
import { ResultsTable } from "@/components/ResultsTable"
import axios from "axios"

interface PipelineResult {
  plan: string
  sql: string
  planner_model: string
  coder_model: string
  confidence: { score: number, explanation: string }
  query_id: number
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

export default function ConsolePage() {
  const [question, setQuestion] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  
  const [pipelineResult, setPipelineResult] = useState<PipelineResult | null>(null)
  const [results, setResults] = useState<{ columns: string[], rows: any[][] } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!question.trim()) return
    setIsGenerating(true)
    setError(null)
    setResults(null)
    setPipelineResult(null)

    try {
      const res = await axios.post(`${API_BASE}/api/generate`, {
        question
      })
      setPipelineResult(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to run pipeline.")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleExecute = async () => {
    if (!pipelineResult?.sql.trim() || isExecuting) return
    
    setIsExecuting(true)
    setError(null)

    try {
      const res = await axios.post(`${API_BASE}/api/execute`, {
        sql: pipelineResult.sql,
        query_id: pipelineResult.query_id
      })
      setResults({ columns: res.data.columns, rows: res.data.rows })
    } catch (err: any) {
      setError(err.response?.data?.detail || "Execution failed.")
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center">
          <DatabaseZap className="w-8 h-8 mr-3 text-primary" />
          Multi-Agent Console
        </h1>
        <p className="text-muted-foreground mt-2">
          Work is split: <strong>Llama 3.3 70B</strong> acts as the Query Planner, and <strong>Qwen 2.5 Coder 32B</strong> writes the SQL.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Column: Input */}
        <div className="xl:col-span-1 space-y-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block text-foreground">
                Natural Language Query
              </label>
              <QueryEditor 
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={isGenerating || isExecuting}
              />
            </div>
            <Button 
              className="w-full h-12 text-md font-medium" 
              onClick={handleGenerate}
              disabled={!question.trim() || isGenerating}
            >
              {isGenerating ? (
                <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
              ) : (
                <Sparkles className="w-5 h-5 mr-2" />
              )}
              Run Multi-Agent Pipeline
            </Button>
          </div>
        </div>

        {/* Right Column: Preview and Results */}
        <div className="xl:col-span-2 space-y-6">
          
          {/* Error Alert */}
          {error && (
            <div className="p-4 rounded-md bg-destructive/10 border border-destructive/20 text-destructive flex items-start animate-in fade-in">
              <AlertCircle className="w-5 h-5 mr-3 mt-0.5 shrink-0" />
              <div className="text-sm font-medium">{error}</div>
            </div>
          )}

          {/* Loading State */}
          {isGenerating && !pipelineResult && (
            <div className="h-64 rounded-lg border border-border bg-card animate-pulse flex flex-col items-center justify-center text-muted-foreground space-y-4">
               <Bot className="w-10 h-10 text-primary animate-bounce" />
               <p className="font-medium text-lg">Agents are working...</p>
               <div className="text-sm space-y-1 text-center">
                 <p>1. Llama is planning the query structure</p>
                 <p>2. Qwen is translating the plan to SQL</p>
               </div>
            </div>
          )}

          {/* Pipeline Results */}
          {pipelineResult && !isGenerating && (
            <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
              
              {/* Llama's Plan */}
              <div className="border border-border rounded-lg overflow-hidden bg-card">
                <div className="flex items-center px-4 py-2 border-b border-border bg-secondary/30">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mr-3">Phase 1</span>
                  <h3 className="text-sm font-medium">Query Plan</h3>
                  <span className="ml-auto text-xs px-2 py-1 bg-primary/10 text-primary rounded-full border border-primary/20">
                    {pipelineResult.planner_model}
                  </span>
                </div>
                <div className="p-4 text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                  {pipelineResult.plan}
                </div>
              </div>

              {/* Qwen's SQL */}
              <div className="border border-border rounded-lg overflow-hidden bg-card">
                 <div className="flex items-center px-4 py-2 border-b border-border bg-secondary/30">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mr-3">Phase 2</span>
                  <h3 className="text-sm font-medium">Final SQL</h3>
                  <span className="ml-auto text-xs px-2 py-1 bg-primary/10 text-primary rounded-full border border-primary/20">
                    {pipelineResult.coder_model}
                  </span>
                </div>
                <div className="p-4 space-y-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Generated Query</span>
                    <ConfidenceBadge score={pipelineResult.confidence.score} />
                  </div>

                  <SQLPreview sql={pipelineResult.sql} />
                  
                  {pipelineResult.confidence.explanation && (
                    <p className="text-sm text-muted-foreground italic">
                      <span className="font-semibold not-italic">Scoring Note:</span> {pipelineResult.confidence.explanation}
                    </p>
                  )}

                  <div className="flex justify-end pt-2">
                    <Button 
                      variant="secondary" 
                      onClick={handleExecute}
                      disabled={isExecuting}
                      className="bg-primary text-primary-foreground hover:bg-primary/90"
                    >
                      {isExecuting ? (
                        <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                      ) : (
                        <Play className="w-4 h-4 mr-2" />
                      )}
                      Execute Query
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Results Table */}
          {results && (
            <div className="pt-6 border-t border-border animate-in fade-in slide-in-from-bottom-4">
              <ResultsTable columns={results.columns} rows={results.rows} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
