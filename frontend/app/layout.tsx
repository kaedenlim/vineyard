"use client";

import { usePathname } from "next/navigation";
import localFont from "next/font/local";
import "./globals.css";
import Nav from "@/components/Nav";

import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
  useUser
} from "@clerk/nextjs";

// Create a separate component for the profile button
function ProfileButton() {
  const { user } = useUser();
  
  return (
    <div className="absolute top-4 right-6 z-10 flex items-center gap-3">
      <div className="text-sm text-right">
        <div className="font-medium">Welcome,</div>
        <div className="text-gray-700">{user?.firstName || 'User'}</div>
      </div>
      <UserButton afterSignOutUrl="/" />
    </div>
  );
}

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
  const pathname = usePathname();
  const noSideBar = ["/" , "/sign-up" , "/sign-in"]
  const hideSideBar = noSideBar.includes(pathname)

  return (
    <ClerkProvider>
      <html lang="en">
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        >
          {hideSideBar ? (
            // if no side bar
            <main>{children}</main>
          ) : (
            // Non-landing pages - apply flex layout to both Nav and content
            <main className="relative">
              {/* Profile icon in top right corner */}
              <SignedIn>
                <ProfileButton />
              </SignedIn>
              
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
    </ClerkProvider>
  );
}
