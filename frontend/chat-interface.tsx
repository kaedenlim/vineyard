"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Mic, ArrowRight } from "lucide-react"
import { useState } from "react"
import { Progress } from "@/components/ui/progress"

export default function Component() {
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const mockApiCall = async () => {
    setIsLoading(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 3000))
    // You would typically make your actual API call here
    setIsLoading(false)
  }

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!inputValue) return
    await mockApiCall()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit()
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-zinc-900 text-white flex flex-col items-center justify-center">
        <div className="w-full max-w-md space-y-8">
          <h2 className="text-2xl font-semibold text-center mb-8">Scraping data for "{inputValue}"</h2>
          <Progress value={33} className="w-full" />
          <p className="text-center text-zinc-400 mt-4">This might take a few moments...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-900 text-white">
      <div className="container mx-auto px-4">
        {/* Header with auth buttons */}
        <div className="flex justify-end gap-2 py-4">
          <Button variant="ghost" className="text-white hover:text-white/90">
            Log in
          </Button>
          <Button className="bg-white text-black hover:bg-white/90">Sign up</Button>
        </div>

        {/* Main content */}
        <div className="mx-auto max-w-3xl py-32">
          <h1 className="mb-8 text-center text-4xl font-semibold">Get insights on a product</h1>

          <div className="relative">
            <Input
              placeholder="Enter the product name"
              className="h-14 rounded-2xl bg-zinc-800 px-4 text-lg text-white placeholder:text-zinc-400 pr-12"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2">
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8 rounded-full bg-white"
                onClick={() => handleSubmit()}
                disabled={!inputValue}
              >
                {inputValue ? <ArrowRight className="h-4 w-4 text-black" /> : <Mic className="h-4 w-4 text-black" />}
                <span className="sr-only">{inputValue ? "Submit" : "Voice input"}</span>
              </Button>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

