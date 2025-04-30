'use client';

import React, {useState, useEffect} from 'react';
import {useRouter} from 'next/navigation';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import Layout from '@/components/layout';
import {Button} from '@/components/ui/button';
import Link from 'next/link';

interface Agent {
  name: string;
  status: 'active' | 'inactive';
  description: string;
  llmModel: string;
  agentFramework: string;
  version: string;
  usage: string;
}

const SystemPage: React.FC = () => {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    // Load agents from local storage on component mount
    const storedAgents = localStorage.getItem('agents');
    if (storedAgents) {
      setAgents(JSON.parse(storedAgents));
    } else {
      // Initialize with some default agents if local storage is empty
      const initialAgents: Agent[] = [
        {
          name: 'Content Scorer',
          status: 'active',
          description: 'Scores AI-generated content for responsibility.',
          llmModel: 'GPT-4',
          agentFramework: 'Langchain',
          version: '1.0.0',
          usage: 'High',
        },
        {
          name: 'User Analyzer',
          status: 'inactive',
          description: 'Analyzes user behavior and content interaction.',
          llmModel: 'GPT-3.5',
          agentFramework: 'None',
          version: '0.5.0',
          usage: 'Medium',
        },
        {
          name: 'Trend Detector',
          status: 'active',
          description: 'Detects trends in user content scores.',
          llmModel: 'Gemini',
          agentFramework: 'AutoGen',
          version: '1.2.0',
          usage: 'Low',
        },
        {
          name: 'Compliance Monitor',
          status: 'active',
          description: 'Ensures compliance with AI ethics guidelines.',
          llmModel: 'GPT-4',
          agentFramework: 'Langchain',
          version: '1.1.0',
          usage: 'High',
        },
        {
          name: 'Bias Auditor',
          status: 'inactive',
          description: 'Audits AI models for bias and fairness.',
          llmModel: 'GPT-3.5',
          agentFramework: 'None',
          version: '0.6.0',
          usage: 'Medium',
        },
        {
          name: 'Explainability Engine',
          status: 'active',
          description: 'Provides explanations for AI decision-making processes.',
          llmModel: 'Gemini',
          agentFramework: 'AutoGen',
          version: '1.3.0',
          usage: 'Low',
        },
        {
          name: 'Data Validator',
          status: 'active',
          description: 'Validates the integrity and quality of input data.',
          llmModel: 'GPT-4',
          agentFramework: 'Langchain',
          version: '1.4.0',
          usage: 'High',
        },
        {
          name: 'Feedback Collector',
          status: 'inactive',
          description: 'Collects user feedback to improve AI models.',
          llmModel: 'GPT-3.5',
          agentFramework: 'None',
          version: '0.7.0',
          usage: 'Medium',
        },
        {
          name: 'Risk Assessor',
          status: 'active',
          description: 'Assesses potential risks associated with AI deployment.',
          llmModel: 'Gemini',
          agentFramework: 'AutoGen',
          version: '1.5.0',
          usage: 'Low',
        },
        {
          name: 'Model Trainer',
          status: 'active',
          description: 'Trains and updates AI models using new data.',
          llmModel: 'GPT-4',
          agentFramework: 'Langchain',
          version: '1.6.0',
          usage: 'High',
        },
      ];
      localStorage.setItem('agents', JSON.stringify(initialAgents));
      setAgents(initialAgents);
    }
  }, []);

  const handleAgentClick = (agentName: string) => {
    router.push(`/system/${encodeURIComponent(agentName)}`);
  };

  return (
    <Layout>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">System Agents</h1>
        <Link href="/system/add-agent">
          <Button>Add Agent</Button>
        </Link>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {agents.map(agent => (
          <Card
            key={agent.name}
            className="cursor-pointer"
            onClick={() => handleAgentClick(agent.name)}
          >
            <CardHeader>
              <CardTitle>{agent.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{agent.description}</p>
              <p>
                Status:{' '}
                <span
                  className={
                    agent.status === 'active' ? 'text-green-500' : 'text-red-500'
                  }
                >
                  {agent.status}
                </span>
              </p>
              <p>Version: {agent.version}</p>
              <p>LLM Model: {agent.llmModel}</p>
              <p>Agent Framework: {agent.agentFramework}</p>
              <p>Usage: {agent.usage}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </Layout>
  );
};

export default SystemPage;
