  "use client"

  import type React from "react"
  import { Button } from "@/components/ui/button"
  import { Input } from "@/components/ui/input"
  import { Mic, ArrowRight, ImagePlus, X } from "lucide-react"
  import { useState, useRef, useEffect } from "react"
  import { Progress } from "@/components/ui/progress"
  import Image from "next/image"
  import { useRouter } from "next/navigation";

  import { scrape } from "@/services/scrapeAPI"

  export default function Search() {
    const [inputValue, setInputValue] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [selectedImage, setSelectedImage] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const router = useRouter();

    useEffect(() => {
      if (isLoading) {
        const duration = 10000 // 2 seconds
        const interval = 10 // Update every 10ms
        const steps = duration / interval
        let currentStep = 0
  
        const timer = setInterval(() => {
          currentStep++
          setProgress(Math.min((currentStep / steps) * 100, 95)) // Max out at 95% until complete
        }, interval)
  
        return () => clearInterval(timer)
      } else {
        setProgress(100) // Complete the progress bar
        const resetTimer = setTimeout(() => setProgress(0), 300) // Reset after animation
        return () => clearTimeout(resetTimer)
      }
    }, [isLoading])
  
    const handleSubmit = async (e?: React.FormEvent) => {
      e?.preventDefault()
      if (!inputValue) return
  
      // Set loading state immediately
      setIsLoading(true)
      setProgress(0)
  
      // Small delay before starting the actual operation to ensure loading UI is shown
      await new Promise((resolve) => setTimeout(resolve, 100))
  
      try {
        // Create a promise that resolves after 2 seconds
        const minimumLoadingTime = new Promise((resolve) => setTimeout(resolve, 100000))
  
        // Run both the API call and the timer in parallel
        await Promise.all([scrape(inputValue), minimumLoadingTime])
      } catch (error) {
        console.error("Error fetching data:", error)
      } finally {
        // Add a small delay before navigation to ensure smooth transition
        await new Promise((resolve) => setTimeout(resolve, 300))
        setIsLoading(false)
        router.push(`/search/${inputValue}`)
      }
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        handleSubmit()
      }
    }

    const handleImageClick = () => {
      fileInputRef.current?.click()
    }

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        const reader = new FileReader()
        reader.onloadend = () => {
          setSelectedImage(reader.result as string)
        }
        reader.readAsDataURL(file)
      }
    }

    const removeImage = () => {
      setSelectedImage(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }

    if (isLoading) {
      return (
        <div className="min-h-screen w-full bg-zinc-900 text-white flex flex-col items-center justify-center">
          <div className="w-full max-w-md space-y-8">
            <h2 className="text-2xl font-semibold text-center mb-8">Scraping data for "{inputValue}"</h2>
            <Progress value={progress} className="w-full h-2" />
            <p className="text-center text-zinc-400 mt-4">This might take a few moments...</p>
          </div>
        </div>
      )
    }

    return (
      <div className="flex min-h-screen w-full bg-zinc-50">

  
        {/* Main Content */}
        <main className="flex-1">
          <div className="container mx-auto px-4">
            <div className="flex justify-end items-center py-4">
              {/* Auth buttons */}
              <div className="flex gap-2">
                <Button className="bg-black text-white hover:bg-black/90">Sign up</Button>
                <Button variant="ghost" className="text-gray-600 hover:text-gray-900">
                  Log in
                </Button>
              </div>
            </div>
  
            {/* Search Content */}
            <div className="mx-auto max-w-3xl py-32">
              <h1 className="mb-8 text-center text-4xl font-semibold">Get insights on a product</h1>
  
              <div className="space-y-2">
                <div className="relative">
                  <Input
                    placeholder="Enter the product name"
                    className="h-14 rounded-2xl bg-zinc-900 px-4 text-lg text-white placeholder:text-zinc-400 pr-12"
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
                      {inputValue ? (
                        <ArrowRight className="h-4 w-4 text-black" />
                      ) : (
                        <Mic className="h-4 w-4 text-black" />
                      )}
                      <span className="sr-only">{inputValue ? "Submit" : "Voice input"}</span>
                    </Button>
                  </span>
                </div>
  
                <div className="flex flex-col items-start space-y-4">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleImageChange}
                    accept="image/*"
                    className="hidden"
                  />
  
                  {selectedImage ? (
                    <div className="relative w-full max-w-xs">
                      <Image
                        src={selectedImage || "/placeholder.svg"}
                        alt="Selected product"
                        width={300}
                        height={300}
                        className="rounded-lg w-full h-auto"
                      />
                      <Button
                        variant="secondary"
                        size="icon"
                        className="absolute top-2 right-2 h-8 w-8 rounded-full bg-zinc-800/80 hover:bg-zinc-700"
                        onClick={removeImage}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <Button
                      variant="ghost"
                      onClick={handleImageClick}
                      className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
                    >
                      <ImagePlus className="h-4 w-4" />
                      Add image
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    )
  }

