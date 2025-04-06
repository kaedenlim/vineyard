'use client'

import React from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from 'next/link';

export default function Nav() {
    const pathname = usePathname();
    return (
        <div className="h-vh w-[15%] min-w-[150px] bg-[#f8f8f8] flex-col gap-0 px-6">
            <div className="h-[15vh] font-bold text-2xl py-6">Vineyard</div>
            <div className="h-[60vh] flex flex-col justify-center items-start gap-6 flex-grow py-6">
                <Link href="/search">
                    <div className={`text-lg ${pathname.startsWith("/search") ? "font-bold" : ""}`}>Search</div>
                </Link>
                <Link href="/dashboard">
                    <div className={`text-lg ${pathname.startsWith("/dashboard") ? "font-bold" : ""}`}>Dashboard</div>
                </Link>
                <Link href="/history">
                    <div className={`text-lg ${pathname.startsWith("/history") ? "font-bold" : ""}`}>History</div>
                </Link>
            </div>
        </div>
    )
}