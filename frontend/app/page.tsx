"use client"

import Link from "next/link"
import { ArrowRight, Grape } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="px-4 lg:px-6 h-16 flex items-center justify-center">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <Grape className="h-6 w-6" />
          <span>Vineyard</span>
        </Link>
      </header>
      <main className="flex-1 flex items-center justify-center">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
          <div className="container mx-auto px-4 md:px-6 flex justify-center">
            <div className="flex flex-col items-center text-center">
              <div className="flex flex-col justify-center items-center space-y-4 max-w-[800px]">
                <div className="space-y-2">
                  <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                    <span className="animate-fade-in-up">Monitor Competitors.{" "}</span>
                    <span className="relative inline-block">
                      <span className="relative z-10 animate-fade-in-up">Outsmart the Market.</span>
                      <span 
                        className="absolute inset-0 bg-gradient-to-r from-purple-500/40 to-blue-500/20 rounded-md animate-highlight-pan" 
                        style={{ padding: '0.1em 0.05em' }}
                      ></span>
                    </span>
                  </h1>
                  <p
                    className="text-muted-foreground md:text-xl animate-fade-in-up"
                    style={{ animationDelay: "200ms" }}
                  >
                    Track competitor products and identify key market trends in real-time to make data-driven decisions
                    that boost your ecommerce business performance.
                  </p>
                </div>
                <div
                  className="flex flex-col gap-2 min-[400px]:flex-row justify-center animate-fade-in-up"
                  style={{ animationDelay: "400ms" }}
                >
                  <Link href="/signup">
                    <Button size="lg" className="gap-1">
                      <b>Try Vinesweeper</b> <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                  <Link href="/login">
                    <Button size="lg" variant="outline">
                      Sign back in
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

