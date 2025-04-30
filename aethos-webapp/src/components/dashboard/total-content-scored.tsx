"use client";

import React, { useState, useEffect } from "react";
import { getTotalContentScored } from "@/services/aethos";
import { Skeleton } from "@/components/ui/skeleton";

export function TotalContentScored() {
  const [total, setTotal] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTotal() {
      setLoading(true);
      try {
        const totalContent = await getTotalContentScored();
        setTotal(totalContent);
      } catch (error) {
        console.error("Failed to load total content scored:", error);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    }

    loadTotal();
  }, []);

  if (loading) {
    return <Skeleton className="h-4 w-[100px]" />;
  }

  return <div className="text-2xl font-bold">{total}</div>;
}
