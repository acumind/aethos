'use client';

import React from 'react';
import {useRouter} from 'next/navigation';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import Layout from '@/components/layout';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface AgentDetailsProps {
  params: { agentName: string };
}

const AgentDetailsPage: React.FC<AgentDetailsProps> = ({params}) => {
  const {agentName} = params;
  const router = useRouter();

  // Dummy data - replace with actual data fetching
  const agentDetails = {
    name: agentName,
    configuration: {
      setting1: 'value1',
      setting2: 'value2',
    },
    usage: 'High',
    version: '1.0.0',
    llmModel: 'GPT-4',
    agentFramework: 'Langchain',
    averageResponseTime: '200ms',
    requestsPerMinute: 60,
    errorRate: '0.5%',
  };

  const usageData = [
    {time: '00:00', requests: 50},
    {time: '03:00', requests: 100},
    {time: '06:00', requests: 150},
    {time: '09:00', requests: 200},
    {time: '12:00', requests: 180},
    {time: '15:00', requests: 150},
    {time: '18:00', requests: 120},
    {time: '21:00', requests: 80},
    {time: '24:00', requests: 40},
  ];

  const formattedAgentName = agentName.replace('%20', ' '); // Decode URI encoded spaces

  return (
    <Layout>
      <Card>
        <CardHeader>
          <CardTitle>{formattedAgentName} Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <p>
              <strong>Configuration:</strong>
            </p>
            <ul>
              {Object.entries(agentDetails.configuration).map(
                ([key, value]) => (
                  <li key={key}>
                    {key}: {value}
                  </li>
                )
              )}
            </ul>
            <p>
              <strong>Usage:</strong> {agentDetails.usage}
            </p>
            <p>
              <strong>Version:</strong> {agentDetails.version}
            </p>
            <p>
              <strong>LLM Model:</strong> {agentDetails.llmModel}
            </p>
            <p>
              <strong>Agent Framework:</strong> {agentDetails.agentFramework}
            </p>
            <p>
              <strong>Average Response Time:</strong> {agentDetails.averageResponseTime}
            </p>
            <p>
              <strong>Requests Per Minute:</strong> {agentDetails.requestsPerMinute}
            </p>
            <p>
              <strong>Error Rate:</strong> {agentDetails.errorRate}
            </p>

            <Card>
              <CardHeader>
                <CardTitle>Agent Usage (Requests/Hour)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart
                    data={usageData}
                    margin={{
                      top: 10,
                      right: 30,
                      left: 0,
                      bottom: 0,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="requests"
                      stroke="#8884d8"
                      fill="#8884d8"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    </Layout>
  );
};

export default AgentDetailsPage;
