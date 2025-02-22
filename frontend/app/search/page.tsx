"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Mic, ArrowRight, ImagePlus, X } from "lucide-react"
import { useState, useRef } from "react"
import { Progress } from "@/components/ui/progress"
import Image from "next/image"
import { useRouter } from "next/navigation";

import { scrape } from "@/services/scrapeAPI"

export default function Search() {
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter();

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue) return;
  
    setIsLoading(true);
    try {
      const response = await scrape(inputValue); // Call the imported `scrape` function
      
      router.push("/search/${inputValue}/results");
      // need push router here
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setIsLoading(false);
    }
  };

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
        <div className="flex justify-between items-center py-4">
          {/* Brand logo */}
          <div className="flex items-center gap-2">
            <span className="text-xl font-semibold tracking-tight bg-gradient-to-r from-zinc-100 to-white-900 bg-clip-text text-transparent">
              Vineyard
            </span>
          </div>

          {/* Auth buttons */}
          <div className="flex gap-2">
            <Button variant="ghost" className="text-white hover:text-white/90">
              Log in
            </Button>
            <Button className="bg-white text-black hover:bg-white/90">Sign up</Button>
          </div>
        </div>

        {/* Main content */}
        <div className="mx-auto max-w-3xl py-32">
          <h1 className="mb-8 text-center text-4xl font-semibold">Get insights on a product</h1>

          <div className="space-y-2">
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

            <div className="flex flex-col items-start space-y-4">
              <input type="file" ref={fileInputRef} onChange={handleImageChange} accept="image/*" className="hidden" />

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
                  className="h-10 px-4 rounded-lg text-zinc-400 hover:text-zinc-300 hover:bg-zinc-800"
                >
                  <ImagePlus className="mr-2 h-4 w-4" />
                  Add image
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

