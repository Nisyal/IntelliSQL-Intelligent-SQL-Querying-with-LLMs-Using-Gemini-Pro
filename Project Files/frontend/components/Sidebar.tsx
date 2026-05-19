"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Terminal, History, Settings, LogOut, Database } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "./ui/button"

const navItems = [
  { name: "Home", href: "/", icon: LayoutDashboard },
  { name: "Query Console", href: "/console", icon: Terminal },
  { name: "History", href: "/history", icon: History },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 flex flex-col bg-card border-r border-border min-h-screen">
      {/* Brand */}
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-border">
        <Database className="h-6 w-6 text-primary mr-2" />
        <span className="text-xl font-bold tracking-tight">IntelliSQL</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-6">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon
                className={cn(
                  "mr-3 flex-shrink-0 h-5 w-5 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )}
                aria-hidden="true"
              />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* User Section (Placeholder for now) */}
      <div className="p-4 border-t border-border">
        <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground">
          <LogOut className="mr-3 h-5 w-5" />
          Logout
        </Button>
      </div>
    </aside>
  )
}
