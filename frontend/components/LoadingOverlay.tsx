// components/LoadingOverlay.tsx
import React from "react";
import { Loader2 } from "lucide-react"; // Ensure you have lucide-react installed: npm install lucide-react

interface LoadingOverlayProps {
    text: string;
}
  
export default function LoadingOverlay({ text }: LoadingOverlayProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white bg-opacity-50">
      <div className="flex flex-col items-center">
        <Loader2 className="animate-spin h-16 w-16 text-black" />
        <p className="mt-4 text-black text-xl">
          {text}
        </p>
      </div>
    </div>
  );
}
