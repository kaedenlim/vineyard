"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, Bell, User } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { PriceGraph } from "@/components/price-graph"

// Sample pricing data
const shopeeData = [
  { date: "2023-01-01", price: 18.5 },
  { date: "2023-01-15", price: 17.2 },
  { date: "2023-02-01", price: 16.8 },
  { date: "2023-02-15", price: 16.0 },
  { date: "2023-03-01", price: 15.84 },
]

const lazadaData = [
  { date: "2023-01-01", price: 15.7 },
  { date: "2023-01-15", price: 16.03 },
  { date: "2023-02-01", price: 17.8 },
  { date: "2023-02-15", price: 15.35 },
  { date: "2023-03-01", price: 17.01 },
]

const carousellData = [
  { date: "2023-01-01", price: 17.78 },
  { date: "2023-01-15", price: 20.5 },
  { date: "2023-02-01", price: 21.65 },
  { date: "2023-02-15", price: 23.98 },
  { date: "2023-03-01", price: 21.43 },
]

export default function SearchProduct() {
  const searchParams = useSearchParams()
  // Retrieve the query parameter "q"; if not provided, fall back to "sunscreen"
  const initialSearchTerm = searchParams.get("q") || "sunscreen"
  const [isClient, setIsClient] = useState(false)
  const [searchTerm, setSearchTerm] = useState(initialSearchTerm)
  const [productImage, setProductImage] = useState(
    "https://img.lazcdn.com/g/p/303c7d35af6fefd40c2cee2309a50886.jpg_200x200q80.jpg_.webp",
  )
  const [alertsOn, setAlertsOn] = useState(false)

  useEffect(() => {
    setIsClient(true)
    // Inject the search term into the endpoint URL
    const fetchData = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/scrape/${encodeURIComponent(searchTerm)}`)
        const data = await res.json()

        // Get the first image URL from the scraped_data array provided by the endpoint.
        if (data?.lazada_results?.scraped_data?.length && data.lazada_results.scraped_data[0].image) {
          setProductImage(data.lazada_results.scraped_data[0].image)
        } else {
          // Fallback: use product_type_image if scraped_data is empty or no image exists.
          setProductImage(data.lazada_results.product_type_image)
        }
      } catch (error) {
        console.error("Error fetching search results:", error)
      }
    }
    fetchData()
  }, [searchTerm])

  // Toggle alerts on/off
  const toggleAlerts = () => {
    setAlertsOn((prev) => !prev)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}

      {/* Main Content */}
      <div className="ml-64 p-6">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2 text-lg">
              <ArrowLeft className="h-5 w-5" />
              Back to Dashboard
            </Link>
          </div>
          <Button variant="ghost" size="icon">
            <User className="h-6 w-6" />
          </Button>
        </div>

        {/* Product Details */}
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="lg:sticky lg:top-6">
            <Image
              src={productImage || "/placeholder.png"}
              alt="Product Image"
              width={600}
              height={600}
              className="rounded-lg border bg-white w-full object-cover"
            />
          </div>

          <div className="space-y-6">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold">{searchTerm}</h1>
            </div>

            <div className="flex items-center gap-4">
              <Button onClick={toggleAlerts} className="bg-black hover:bg-black/90">
                <Bell className="mr-2 h-4 w-4" />
                {alertsOn ? "Alerts On" : "Alerts Off"}
              </Button>
            </div>

            {/* Price Comparisons */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Shopee */}
              <Card className="p-4">
                <div className="flex items-center justify-between mb-3">
                  {/* Retailer info */}

                  <Link href={`/search/${searchTerm}/results/shopee`}>
                    <div className="flex items-center gap-2">
                      <div className="flex h-6 w-6 items-center justify-center rounded bg-orange-100">
                        <span className="text-orange-500 text-xs">S</span>
                      </div>
                      <span className="font-medium text-sm">Shopee</span>
                    </div>
                  </Link>
                  {/* Price info */}
                  <div className="text-right">
                    <span className="text-base font-bold">$15.84</span>
                    <span className="block text-xs text-green-500">Lowest in 30 days</span>
                  </div>
                </div>
                {/* Chart */}
                <div className="h-[120px]">
                  {isClient ? (
                    <PriceGraph data={shopeeData} color="#ff5722" />
                  ) : (
                    <div className="h-full bg-gray-100 flex items-center justify-center text-xs">Loading chart...</div>
                  )}
                </div>
              </Card>

              {/* Lazada */}
              <Card className="p-4">
                <div className="flex items-center justify-between mb-3">
                  {/* Retailer info */}
                  <Link href={`/search/${searchTerm}/results/lazada`}>
                  <div className="flex items-center gap-2">
                    <div className="flex h-6 w-6 items-center justify-center rounded bg-orange-100">
                      <span className="text-orange-500 text-xs">L</span>
                    </div>
                    <span className="font-medium">Lazada</span>
                  </div>
                  </Link>
                  {/* Price info */}
                  <div className="text-right">
                    <span className="text-base font-bold">$17.01</span>
                    <span className="block text-xs text-red-500">Was $15.35 2 days ago</span>
                  </div>
                </div>
                {/* Chart */}
                <div className="h-[120px]">
                  {isClient ? (
                    <PriceGraph data={lazadaData} color="#ff5722" />
                  ) : (
                    <div className="h-full bg-gray-100 flex items-center justify-center text-xs">Loading chart...</div>
                  )}
                </div>
              </Card>

              {/* Carousell */}
              <Card className="p-4">
                <div className="flex items-center justify-between mb-3">
                  {/* Retailer info */}
                  <Link href={`/search/${searchTerm}/results/carousell`}>
                    <div className="flex items-center gap-2">
                      <div className="flex h-6 w-6 items-center justify-center rounded bg-orange-100">
                        <span className="text-orange-500 text-xs">C</span>
                      </div>
                      <span className="font-medium text-sm">Carousell</span>
                    </div>
                  </Link>
                  {/* Price info */}
                  <div className="text-right">
                    <span className="text-base font-bold">$21.43</span>
                    <span className="block text-xs text-red-500">Was $17.78 17 days ago</span>
                  </div>
                </div>
                {/* Chart */}
                <div className="h-[120px]">
                  {isClient ? (
                    <PriceGraph data={carousellData} color="#ff5722" />
                  ) : (
                    <div className="h-full bg-gray-100 flex items-center justify-center text-xs">Loading chart...</div>
                  )}
                </div>
              </Card>
            </div>

            {/* AI Insights */}
            <Card className="p-6">
              <h2 className="text-xl font-bold mb-4">Vineyard AI Insights</h2>
              <p className="text-muted-foreground leading-relaxed">
                The e-commerce sunscreen market is highly competitive, with major brands like Supergoop!, La
                Roche-Posay, and Neutrogena dominating through strong SEO, influencer marketing, and retail
                partnerships. Consumer demand is shifting towards daily SPF use, reef-safe formulas, and
                multi-functional sunscreens that combine skincare benefits with sun protection. Emerging opportunities
                lie in niche targeting (e.g., acne-prone or tinted SPF), sustainable packaging, and AI-driven
                personalization to differentiate from market leaders.
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

