"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UserStatistics } from "@/components/dashboard/user-statistics";
import Layout from "@/components/layout";

const UserStatsPage: React.FC = () => {
  return (
    <Layout>
      <Card>
        <CardHeader>
          <CardTitle>User Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <UserStatistics />
        </CardContent>
      </Card>
    </Layout>
  );
};

export default UserStatsPage;
