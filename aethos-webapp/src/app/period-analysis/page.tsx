"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PeriodWiseAnalysis } from "@/components/dashboard/period-wise-analysis";
import Layout from "@/components/layout";

const PeriodAnalysisPage: React.FC = () => {
  return (
    <Layout>
      <Card>
        <CardHeader>
          <CardTitle>Period-wise Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <PeriodWiseAnalysis />
        </CardContent>
      </Card>
    </Layout>
  );
};

export default PeriodAnalysisPage;
