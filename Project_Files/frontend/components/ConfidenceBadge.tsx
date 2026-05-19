"use client"

import { Badge } from "./ui/badge"
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from "lucide-react"

export function ConfidenceBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return null

  let variant: "default" | "secondary" | "destructive" | "outline" = "default"
  let colorClass = ""
  let Icon = HelpCircle

  if (score >= 85) {
    colorClass = "bg-green-500/15 text-green-500 border-green-500/20 hover:bg-green-500/25"
    Icon = CheckCircle2
  } else if (score >= 60) {
    colorClass = "bg-yellow-500/15 text-yellow-500 border-yellow-500/20 hover:bg-yellow-500/25"
    Icon = AlertTriangle
  } else {
    variant = "destructive"
    Icon = XCircle
  }

  return (
    <Badge variant={variant} className={`px-3 py-1 text-sm font-medium ${variant === "default" ? colorClass : ""}`}>
      <Icon className="w-4 h-4 mr-1.5" />
      Confidence: {score}%
    </Badge>
  )
}
