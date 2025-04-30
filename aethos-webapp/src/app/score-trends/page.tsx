"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart } from "recharts"; // Replace with your actual Score Trends component
import Layout from "@/components/layout";

const ScoreTrendsPage: React.FC = () => {
  return (
    <Layout>
      <Card>
        <CardHeader>
          <CardTitle>Score Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div>Score Trends Content</div>
        </CardContent>
      </Card>
    </Layout>
  );
};

export default ScoreTrendsPage;
