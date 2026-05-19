import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { cn } from "@/lib/utils"
import AppLayout from "./AppLayout"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
})

export const metadata: Metadata = {
  title: "IntelliSQL | Natural Language Database Querying",
  description: "Query your PostgreSQL database using plain English with advanced LLMs.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={cn(inter.variable, "font-sans antialiased min-h-screen bg-background")}>
        <AppLayout>
          {children}
        </AppLayout>
      </body>
    </html>
  )
}
