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
      <div className="fixed left-0 top-0 h-full w-64 border-r bg-white p-6">
        <h1 className="mb-8 text-2xl font-bold">Vineyard</h1>
        <nav className="space-y-6">
          <div className="space-y-2">
            <p className="text-lg">Search</p>
          </div>
          <div className="space-y-2">
            <p className="text-lg font-semibold">Dashboard</p>
          </div>
          <div className="fixed bottom-6 space-y-2">
            <h3 className="text-lg font-semibold">View Pricing &amp; Plans</h3>
            <p className="text-sm text-muted-foreground">Check out which plans...</p>
          </div>
        </nav>
      </div>

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
          <div>
            <Image
              // Use the productImage from API response or fallback to a placeholder.
              src={productImage || "/placeholder.png"}
              alt="Product Image"
              width={600}
              height={600}
              className="rounded-lg border bg-white"
            />
          </div>

          <div className="space-y-6">
            <div>
              <h1 className="text-4xl font-bold">{searchTerm}</h1>
            </div>

            <div className="flex items-center gap-4">
              <Button onClick={toggleAlerts} className="bg-black hover:bg-black/90">
                <Bell className="mr-2 h-4 w-4" />
                {alertsOn ? "Alerts On" : "Alerts Off"}
              </Button>
            </div>

            {/* Price Comparisons in 2 columns */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Shopee */}
              <Link href={`/search/${searchTerm}/shopee`} className="block">
                <Card className="p-3 cursor-pointer hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    {/* Retailer info */}
                    <div className="flex items-center gap-2">
                      <div className="flex h-6 w-6 items-center justify-center rounded bg-orange-100">
                        <span className="text-orange-500 text-xs">S</span>
                      </div>
                      <span className="font-medium text-sm">Shopee</span>
                    </div>
                    {/* Price info */}
                    <div className="flex flex-col items-end">
                      <span className="text-xs text-green-500">Lowest in 30 days</span>
                      <span className="text-base font-bold">$15.84</span>
                    </div>
                  </div>
                  {/* Chart below */}
                  <div className="mt-4 flex items-center justify-center">
                    {isClient ? (
                      <PriceGraph data={shopeeData} color="#ff5722" />
                    ) : (
                      <div className="h-[50px] bg-gray-100 flex items-center justify-center text-xs">
                        Loading chart...
                      </div>
                    )}
                  </div>
                </Card>
              </Link>

              {/* Lazada */}
              <Link href={`/search/${searchTerm}/lazada`} className="block">
                <Card className="p-3 cursor-pointer hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    {/* Retailer info */}
                    <div className="flex items-center gap-2">
                      <div className="flex h-6 w-6 items-center justify-center rounded bg-orange-100">
                        <span className="text-orange-500 text-xs">L</span>
                      </div>
                      <span className="font-medium text-sm">Lazada</span>
                    </div>
                    {/* Price info */}
                    <div className="flex flex-col items-end">
                      <span className="text-xs text-red-500">Was $15.35 2 days ago</span>
                      <span className="text-base font-bold">$17.01</span>
                    </div>
                  </div>
                  {/* Chart below */}
                  <div className="mt-4 flex items-center justify-center">
                    {isClient ? (
                      <PriceGraph data={lazadaData} color="#ff5722" />
                    ) : (
                      <div className="h-[50px] bg-gray-100 flex items-center justify-center text-xs">
                        Loading chart...
                      </div>
                    )}
                  </div>
                </Card>
              </Link>

              {/* Carousell */}
              <Link href={`/search/${searchTerm}/carousell`} className="block">
                <Card className="p-3 cursor-pointer hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    {/* Retailer info */}
                    <div className="flex items-center gap-2">
                      <div className="flex h-6 w-6 items-center justify-center rounded bg-orange-100">
                        <span className="text-orange-500 text-xs">C</span>
                      </div>
                      <span className="font-medium text-sm">Carousell</span>
                    </div>
                    {/* Price info */}
                    <div className="flex flex-col items-end">
                      <span className="text-xs text-red-500">Was $17.78 17 days ago</span>
                      <span className="text-base font-bold">$21.43</span>
                    </div>
                  </div>
                  {/* Chart below */}
                  <div className="mt-4 flex items-center justify-center">
                    {isClient ? (
                      <PriceGraph data={carousellData} color="#ff5722" />
                    ) : (
                      <div className="h-[50px] bg-gray-100 flex items-center justify-center text-xs">
                        Loading chart...
                      </div>
                    )}
                  </div>
                </Card>
              </Link>
            </div>

            {/* AI Insights */}
            <Card className="p-6">
              <h2 className="mb-4 text-xl font-bold">Vineyard AI Insights</h2>
              <p className="text-muted-foreground">
                Birch Moisturizing Sunscreen is a <span className="font-medium">dual-function skincare product</span>{" "}
                designed to provide broad-spectrum sun protection while delivering{" "}
                <span className="font-medium">deep hydration</span>. Infused with{" "}
                <span className="font-medium">natural birch sap extract</span>, it offers a{" "}
                <span className="font-medium">lightweight, non-greasy</span> formula suitable for daily use.
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

