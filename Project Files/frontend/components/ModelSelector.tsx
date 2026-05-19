"use client"

import { Check, ChevronsUpDown } from "lucide-react"
import { Button } from "./ui/button"
import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import { useState } from "react"

const models = [
  {
    id: "qwen-2.5-coder-32b",
    name: "Qwen 2.5 Coder 32B",
    description: "Optimized for code and SQL generation",
  },
  {
    id: "llama-3.3-70b",
    name: "Llama 3.3 70B",
    description: "General-purpose powerhouse",
  },
]

export function ModelSelector({ value, onChange }: { value: string, onChange: (v: string) => void }) {
  const [open, setOpen] = useState(false)
  const selected = models.find((m) => m.id === value) || models[0]

  return (
    <DropdownMenu.Root open={open} onOpenChange={setOpen}>
      <DropdownMenu.Trigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[280px] justify-between bg-card"
        >
          {selected.name}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="start"
          className="w-[280px] rounded-md border bg-popover text-popover-foreground shadow-md p-1 z-50"
        >
          {models.map((model) => (
            <DropdownMenu.Item
              key={model.id}
              onClick={() => onChange(model.id)}
              className="relative flex cursor-pointer select-none flex-col rounded-sm px-2 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
            >
              <div className="flex items-center w-full">
                <span className="font-medium">{model.name}</span>
                {value === model.id && (
                  <Check className="ml-auto h-4 w-4 text-primary" />
                )}
              </div>
              <span className="text-xs text-muted-foreground mt-1">
                {model.description}
              </span>
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
