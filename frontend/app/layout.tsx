"use client"

import { usePathname } from 'next/navigation'
import localFont from "next/font/local";
import "./globals.css";
import Nav from "@/components/Nav";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname()
  const isLandingPage = pathname === '/'
  
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {isLandingPage ? (
          // Landing page - no flex layout needed
          <main>
            {children}
          </main>
        ) : (
          // Non-landing pages - apply flex layout to both Nav and content
          <main>
            <div className="flex">
              <Nav />
              <div className="flex-1">
                {children}
              </div>
            </div>
          </main>
        )}
      </body>
    </html>
  );
}
