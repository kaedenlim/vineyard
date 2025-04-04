// app/page.tsx
import React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function OnboardFormPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8 w-full">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Let's get you set up</h1>
          <p className="mt-2 text-sm text-gray-600">
            Please enter your profile links for each platform below.
            <br></br>
            If you are not selling on them, please leave the field blank.
          </p>
        </div>
        <form className="mt-8 space-y-6" action="/onboard" method="POST">
          <div className="space-y-4">
            <div>
              <Label htmlFor="shopee" className="block text-sm font-medium text-gray-700">
                Shopee
              </Label>
              <Input
                id="shopee"
                name="shopee"
                type="url"
                placeholder="https://shopee.sg/your-profile"
                className="mt-1 block w-full"
              />
            </div>
            <div>
              <Label htmlFor="lazada" className="block text-sm font-medium text-gray-700">
                Lazada
              </Label>
              <Input
                id="lazada"
                name="lazada"
                type="url"
                placeholder="https://lazada.sg/your-profile"
                className="mt-1 block w-full"
              />
            </div>
            <div>
              <Label htmlFor="carousell" className="block text-sm font-medium text-gray-700">
                Carousell
              </Label>
              <Input
                id="carousell"
                name="carousell"
                type="url"
                placeholder="https://carousell.sg/your-profile"
                className="mt-1 block w-full"
              />
            </div>
          </div>
          <div>
            <Button type="submit" className="w-full">
              Submit
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
