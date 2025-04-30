"use client";

import React, { useState, useEffect } from "react";
import {
  getContentScoreTimeline,
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
  LineChart,
  Line,
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
    color: "hsl(var(--chart-2))",
  },
};

interface UserScoreTimelineProps {
  userId: string;
}

export function UserScoreTimeline({ userId }: UserScoreTimelineProps) {
  const [scoreTimeline, setScoreTimeline] = useState<ContentScore[] | null>(
    null
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadScoreTimeline() {
      setLoading(true);
      try {
        const timeline = await getContentScoreTimeline(userId);
        setScoreTimeline(timeline);
      } catch (error) {
        console.error("Failed to load score timeline:", error);
        setScoreTimeline([]);
      } finally {
        setLoading(false);
      }
    }

    loadScoreTimeline();
  }, [userId]);

  if (loading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-4 w-[250px]" />
        <Skeleton className="h-[200px] w-full" />
      </div>
    );
  }

  const chartData = scoreTimeline
    ? scoreTimeline.map((score) => ({
        name: score.contentId,
        score: score.score,
      }))
    : [];

  return (
    <ChartContainer config={chartConfig} className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip content={<ChartTooltipContent />} />
          <Legend content={<ChartLegendContent />} />} />
          <Line type="monotone" dataKey="score" stroke="hsl(var(--chart-2))" />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
