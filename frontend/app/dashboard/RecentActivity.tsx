"use client"
import { RecentActivityInfo } from "@/types"
 
 import React from "react"
 import {
   Table,
   TableBody,
   TableCell,
   TableHead,
   TableHeader,
   TableRow,
 } from "@/components/ui/table"
 
 interface RecentActivityProps {
    data: RecentActivityInfo[]
 }
 
 export function RecentActivity({ data }: RecentActivityProps) {
   return (
     <div className="max-w-full max-h-[30vh]">
         <div className="py-4 text-lg font-semibold">Recent Activity</div>
         <div className="w-full overflow-auto">
             <Table>
                 <TableHeader>
                 <TableRow>
                     <TableHead>Activity</TableHead>
                     <TableHead className="text-right">Date</TableHead>
                 </TableRow>
                 </TableHeader>
                 <TableBody>
                 {data.map((item, index) => (
                     <TableRow key={index}>
                     <TableCell>{item.activity}</TableCell>
                     <TableCell className="text-right">{item.date}</TableCell>
                     </TableRow>
                 ))}
                 </TableBody>
             </Table>
         </div>
     </div>
   )
 }