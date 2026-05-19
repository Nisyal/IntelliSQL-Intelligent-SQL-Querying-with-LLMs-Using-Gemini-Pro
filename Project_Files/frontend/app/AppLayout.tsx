import { Sidebar } from "@/components/Sidebar"

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <Sidebar />
      <main className="flex-1 flex flex-col min-h-screen relative overflow-hidden">
        <div className="flex-1 w-full h-full overflow-y-auto">
          {children}
        </div>
      </main>
    </div>
  )
}
