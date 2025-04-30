"use client";

import React, { useState, useEffect } from "react";
import { getUserStats, UserStats } from "@/services/aethos";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

export function UserStatistics() {
  const [userStats, setUserStats] = useState<UserStats[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUserStats() {
      setLoading(true);
      try {
        const stats = await getUserStats();
        setUserStats(stats);
      } catch (error) {
        console.error("Failed to load user stats:", error);
        setUserStats([]);
      } finally {
        setLoading(false);
      }
    }

    loadUserStats();
  }, []);

  if (loading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-4 w-[250px]" />
        <Skeleton className="h-4 w-[200px]" />
        <Skeleton className="h-4 w-[220px]" />
      </div>
    );
  }

  return (
    <div className="w-full">
      <Table>
        <TableCaption>A list of your user statistics.</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">User ID</TableHead>
            <TableHead>Average Score</TableHead>
            <TableHead>Total Content Scored</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {userStats && userStats.length > 0 ? (
            userStats.map((user) => (
              <TableRow key={user.userId}>
                <TableCell className="font-medium">{user.userId}</TableCell>
                <TableCell>{user.averageScore}</TableCell>
                <TableCell>{user.totalContentScored}</TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={3} className="text-center">
                No user stats available.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
