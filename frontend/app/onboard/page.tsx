// app/page.tsx
'use client'
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ProfileLinkInfo, ProfileScrapeResponse } from "@/types";
import { getProfileProducts } from "@/services/onboardAPI";
import LoadingOverlay from "@/components/LoadingOverlay";
import OnboardProductsPage from "./OnboardProductsPage";
import { testProfileScrapeResponse } from "@/testdata";

export default function Page() {
  const [loading, setLoading] = useState(false);
  const [profileLinks, setProfileLinks] = useState<ProfileLinkInfo>({
    shopee_url: "",
    lazada_url: "",
    carousell_url: "",
  });
  const [responseData, setResponseData] = useState<ProfileScrapeResponse | null>(null);

  // Set test data only once on mount
//   useEffect(() => {
//     setResponseData(testProfileScrapeResponse);
//   }, []);

  // Update state as the user types in the inputs.
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileLinks({
      ...profileLinks,
      [name]: value,
    });
  };

  // Handle form submission: call getProfileProducts and update response state.
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await getProfileProducts(profileLinks);
      console.log(data);
      setResponseData(data);
    } catch (error) {
      console.error("Error getting profile products", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative max-w-[80%] mx-auto">
      {loading && <LoadingOverlay text={"Hold on while we set up your profile..."} />}
      <div className={loading ? "blur-sm pointer-events-none select-none" : ""}>
      {!responseData && (
        <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8 w-full">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">Let's get you set up</h1>
            <p className="mt-2 text-sm text-gray-600">
              Please enter your profile links for each platform below.
              <br />
              If you are not selling on them, please leave the field blank.
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <Label htmlFor="shopee_url" className="block text-sm font-medium text-gray-700">
                  Shopee
                </Label>
                <Input
                  id="shopee_url"
                  name="shopee_url"
                  type="url"
                  placeholder="https://shopee.sg/your-profile"
                  className="mt-1 block w-full"
                  value={profileLinks.shopee_url}
                  onChange={handleChange}
                />
              </div>
              <div>
                <Label htmlFor="lazada_url" className="block text-sm font-medium text-gray-700">
                  Lazada
                </Label>
                <Input
                  id="lazada_url"
                  name="lazada_url"
                  type="url"
                  placeholder="https://lazada.sg/your-profile"
                  className="mt-1 block w-full"
                  value={profileLinks.lazada_url}
                  onChange={handleChange}
                />
              </div>
              <div>
                <Label htmlFor="carousell_url" className="block text-sm font-medium text-gray-700">
                  Carousell
                </Label>
                <Input
                  id="carousell_url"
                  name="carousell_url"
                  type="url"
                  placeholder="https://carousell.sg/your-profile"
                  className="mt-1 block w-full"
                  value={profileLinks.carousell_url}
                  onChange={handleChange}
                />
              </div>
            </div>
            <div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Getting Products..." : "Get Products"}
              </Button>
            </div>
          </form>
        </div>
      </div>
      )}
      </div>
      {responseData && (
        <div className="w-full flex flex-col items-center justify-center min-h-screen py-6 px-8 sm:px-12 lg:px-16">
            <OnboardProductsPage products={responseData} />
        </div>
      )}
    </div>
  );
}
