"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  LayoutDashboard,
} from "lucide-react";
import {
  TotalContentScored
} from "@/components/dashboard/total-content-scored";
import {
  UserStatistics
} from "@/components/dashboard/user-statistics";
import {
  PeriodWiseAnalysis
} from "@/components/dashboard/period-wise-analysis";
import {
  UserScoreTimeline
} from "@/components/dashboard/user-score-timeline";
import Layout from "@/components/layout";

const DashboardPage: React.FC = () => {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader>
          <CardTitle>Total Content Scored</CardTitle>
        </CardHeader>
        <CardContent>
          <TotalContentScored />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>User Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <UserStatistics />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Period-wise Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <PeriodWiseAnalysis />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>User Score Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <UserScoreTimeline userId="user1" />
        </CardContent>
      </Card>
    </div>
  );
};

export default function Home() {
  return (
    <Layout>
      <DashboardPage />
    </Layout>
  );
}
