"use client";

import React, { useState, useEffect } from "react";
import {
  getContentScoresForPeriod,
  ContentScore,
} from "@/services/aethos";
import {
  Chart,
  ChartContainer,
  ChartLegend,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegendContent,
} from "@/components/ui/chart";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Skeleton } from "@/components/ui/skeleton";

const chartConfig = {
  score: {
    label: "Score",
    color: "hsl(var(--chart-1))",
  },
};

export function PeriodWiseAnalysis() {
  const [contentScores, setContentScores] = useState<ContentScore[] | null>(
    null
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadContentScores() {
      setLoading(true);
      try {
        const scores = await getContentScoresForPeriod("weekly");
        setContentScores(scores);
      } catch (error) {
        console.error("Failed to load content scores:", error);
        setContentScores([]);
      } finally {
        setLoading(false);
      }
    }

    loadContentScores();
  }, []);

  if (loading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-4 w-[250px]" />
        <Skeleton className="h-[200px] w-full" />
      </div>
    );
  }

  const chartData = contentScores
    ? contentScores.map((score) => ({
        name: score.contentId,
        score: score.score,
      }))
    : [];

  return (
    <ChartContainer config={chartConfig} className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip content={<ChartTooltipContent />} />
          <Legend content={<ChartLegendContent />} />} />
          <Bar dataKey="score" fill="hsl(var(--chart-1))" />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
