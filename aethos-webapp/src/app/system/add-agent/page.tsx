'use client';

import React, {useState} from 'react';
import Layout from '@/components/layout';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Textarea} from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {useRouter} from 'next/navigation';
import {useToast} from '@/hooks/use-toast';

interface Agent {
  name: string;
  description: string;
  llmModel: string;
  agentFramework: string;
  version: string;
  usage: string;
}

const AddAgentPage: React.FC = () => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [llmModel, setLlmModel] = useState('');
  const [agentFramework, setAgentFramework] = useState('');
  const [version, setVersion] = useState('');
  const [usage, setUsage] = useState('');

  const router = useRouter();
  const {toast} = useToast();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const newAgent: Agent = {
      name,
      description,
      llmModel,
      agentFramework,
      version,
      usage,
    };

    // Simulate adding the agent to a data store (e.g., a database)
    // In a real application, you would send this data to your backend
    console.log('New Agent Added:', newAgent);

    // Show toast notification
    toast({
      title: 'Agent Added',
      description: `Agent "${name}" has been added successfully.`,
    });

    // Reset the form fields
    setName('');
    setDescription('');
    setLlmModel('');
    setAgentFramework('');
    setVersion('');
    setUsage('');

    // Redirect to the system page after adding the agent
    router.push('/system');
  };

  return (
    <Layout>
      <Card>
        <CardHeader>
          <CardTitle>Add New Agent</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="Agent Name"
                value={name}
                onChange={e => setName(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Agent Description"
                value={description}
                onChange={e => setDescription(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="llmModel">LLM Model</Label>
              <Select onValueChange={value => setLlmModel(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select LLM Model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="GPT-3.5">GPT-3.5</SelectItem>
                  <SelectItem value="GPT-4">GPT-4</SelectItem>
                  <SelectItem value="Gemini">Gemini</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="agentFramework">Agent Framework</Label>
              <Select onValueChange={value => setAgentFramework(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Agent Framework" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Langchain">Langchain</SelectItem>
                  <SelectItem value="AutoGen">AutoGen</SelectItem>
                  <SelectItem value="None">None</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="version">Version</Label>
              <Input
                id="version"
                placeholder="Agent Version"
                value={version}
                onChange={e => setVersion(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="usage">Usage</Label>
              <Input
                id="usage"
                placeholder="Agent Usage"
                value={usage}
                onChange={e => setUsage(e.target.value)}
                required
              />
            </div>
            {/* Add more input fields as necessary */}
            <div className="flex justify-end">
              <Button type="submit">Add</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </Layout>
  );
};

export default AddAgentPage;
