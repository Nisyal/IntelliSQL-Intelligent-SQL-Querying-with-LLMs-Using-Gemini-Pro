"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export type QueryEditorProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>

const QueryEditor = React.forwardRef<HTMLTextAreaElement, QueryEditorProps>(
  ({ className, ...props }, ref) => {
    return (
      <div className="relative w-full">
        <textarea
          className={cn(
            "flex w-full rounded-md border border-input bg-card px-4 py-4 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 min-h-[120px] resize-y font-mono",
            className
          )}
          ref={ref}
          placeholder="e.g. Show me all students who scored above 80 marks in BTech..."
          {...props}
        />
        <div className="absolute bottom-3 right-3 flex space-x-1">
          {/* Subtle decoration for the editor vibe */}
          <span className="h-2 w-2 rounded-full bg-red-500/50"></span>
          <span className="h-2 w-2 rounded-full bg-yellow-500/50"></span>
          <span className="h-2 w-2 rounded-full bg-green-500/50"></span>
        </div>
      </div>
    )
  }
)
QueryEditor.displayName = "QueryEditor"

export { QueryEditor }
