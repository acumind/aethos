"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Layout from "@/components/layout";

const SettingsPage: React.FC = () => {
  return (
    <Layout>
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div>Settings Content</div>
        </CardContent>
      </Card>
    </Layout>
  );
};

export default SettingsPage;
