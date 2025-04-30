
"use client";

import type { ChangeEvent } from "react";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { ShieldCheck, Paperclip, X, FileAudio, FileVideo } from "lucide-react"; // Added icons
import { getRaiMetrics, RaiMetrics, RaiInput } from "@/services/rai-metrics";
import { Badge } from "@/components/ui/badge";
import { Toaster } from "@/components/ui/toaster";
import { useToast } from "@/hooks/use-toast";
import Image from 'next/image';

// Define content types
type TextContent = { type: "text"; text: string };
type ImageContent = { type: "image"; url: string; alt?: string; name?: string };
type AudioContent = { type: "audio"; url: string; name?: string };
type VideoContent = { type: "video"; url: string; name?: string };
type MessageContent = TextContent | ImageContent | AudioContent | VideoContent;

// Define message structure
interface Message {
  id: string;
  sender: "user" | "ai";
  content: MessageContent;
  metrics?: RaiMetrics;
  expanded?: boolean;
}

// Mock URLs for simulation
const MOCK_AUDIO_URL = "https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3";
const MOCK_VIDEO_URL = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.webm";


const AIChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setFilePreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
      // Clear the input value to allow selecting the same file again
      if (event.target) {
        event.target.value = "";
      }
    }
  };

  const removeSelectedFile = () => {
    setSelectedFile(null);
    setFilePreviewUrl(null);
     if (fileInputRef.current) {
       fileInputRef.current.value = ""; // Clear the actual input element
     }
  };

 const handleSend = async () => {
     if (!input.trim() && !selectedFile) return;

     setLoading(true); // Start loading indicator

     let userMessageContent: MessageContent | null = null; // Initialize as potentially null
     const userMessagesToSend: Message[] = []; // Array to hold messages being sent

     // Handle file upload first
     if (selectedFile && filePreviewUrl) {
         const fileType = selectedFile.type.split("/")[0];
         const fileName = selectedFile.name;
         let content: MessageContent | null = null;
         switch (fileType) {
             case "image":
                 content = { type: "image", url: filePreviewUrl, alt: fileName, name: fileName };
                 break;
             case "audio":
                 content = { type: "audio", url: filePreviewUrl, name: fileName };
                 break;
             case "video":
                 content = { type: "video", url: filePreviewUrl, name: fileName };
                 break;
             default:
                 toast({ title: "Unsupported File Type", description: "This file type is not supported for direct display.", variant: "destructive"});
                 setLoading(false);
                 return;
         }
         if (content) {
             userMessageContent = content; // Set the primary content if file exists
             const fileMessage: Message = {
                 id: Date.now().toString() + '-file',
                 sender: "user",
                 content: content,
             };
             userMessagesToSend.push(fileMessage);
         }
     }

     // Handle text input, always send if present
     if (input.trim()) {
         const textContent: TextContent = { type: "text", text: input };
         if (!userMessageContent) {
             userMessageContent = textContent; // Set as primary if no file
         }
         const textMessage: Message = {
             id: Date.now().toString() + '-text',
             sender: "user",
             content: textContent,
         };
         userMessagesToSend.push(textMessage);
     }


     if (userMessagesToSend.length === 0) {
       setLoading(false); // Stop loading
       return; // Should not happen if button is disabled correctly
     }

     // Add all prepared user messages to state
     setMessages((prev) => [...prev, ...userMessagesToSend]);
     setInput("");
     removeSelectedFile();


     // Simulate AI response with a delay. Replace with your actual backend call.
     setTimeout(async () => {
        // AI Response logic based on the *last* message sent by the user in this turn
        const lastUserMessage = userMessagesToSend[userMessagesToSend.length - 1];
        let aiResponseText = "";
        let aiResponseContent: MessageContent; // Needs to be defined

        const randomResponseType = Math.random();

        if (lastUserMessage.content.type === 'text') {
            aiResponseText = `Simulated AI response to: "${lastUserMessage.content.text}".`;
        } else if (lastUserMessage.content.type === 'image' || lastUserMessage.content.type === 'audio' || lastUserMessage.content.type === 'video') {
            aiResponseText = `Simulated AI processing the uploaded ${lastUserMessage.content.type}: "${lastUserMessage.content.name}".`;
        }

        // Randomly choose AI response type
        if (randomResponseType < 0.4) { // 40% chance of text
            aiResponseContent = { type: "text", text: aiResponseText };
        } else if (randomResponseType < 0.7) { // 30% chance of image
            const width = Math.floor(Math.random() * 200) + 200;
            const height = Math.floor(Math.random() * 150) + 150;
            aiResponseContent = { type: "image", url: `https://picsum.photos/${width}/${height}`, alt: "AI Generated Image", name: `ai-image-${Date.now()}.jpg` };
        } else if (randomResponseType < 0.85) { // 15% chance of audio
             aiResponseContent = { type: "audio", url: MOCK_AUDIO_URL, name: "simulated-audio.mp3" };
        } else { // 15% chance of video
             aiResponseContent = { type: "video", url: MOCK_VIDEO_URL, name: "simulated-video.webm" };
        }


       const aiMessage: Message = {
         id: Date.now().toString() + "-ai",
         sender: "ai",
         content: aiResponseContent,
       };
       setMessages((prev) => [...prev, aiMessage]);
       setLoading(false); // Stop loading after AI response
     }, 1500); // Simulate a 1.5-second delay.
   };

  const handleRaiCheck = async (messageId: string) => {
    const messageToCheck = messages.find(m => m.id === messageId);
    if (!messageToCheck || messageToCheck.sender !== 'ai') {
        toast({ title: "Cannot Check RAI", description: "RAI metrics can only be generated for AI responses.", variant: "destructive" });
        return;
    }

    // If metrics already exist, just toggle the view
    if (messageToCheck.metrics) {
        toggleRaiMetrics(messageId);
        return;
    }

    setLoading(true); // Start loading for RAI check
    try {
      // Prepare input for the RAI service based on content type
      let raiInput: RaiInput;
      // Use the actual content type from the message
      if (messageToCheck.content.type === 'text') {
        raiInput = { type: 'text', value: messageToCheck.content.text };
      } else if (messageToCheck.content.type === 'image' || messageToCheck.content.type === 'audio' || messageToCheck.content.type === 'video') {
        // Pass the correct type and the URL as the value
        raiInput = { type: messageToCheck.content.type, value: messageToCheck.content.url };
      } else {
        // Handle potential future content types or errors
        const exhaustiveCheck: never = messageToCheck.content; // Ensures all types handled
        toast({ title: "Unsupported Content", description: "Cannot generate RAI for this content type.", variant: "destructive" });
        setLoading(false);
        return;
      }

      // Call the service with the prepared input
      const metrics = await getRaiMetrics(raiInput);

      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId ? { ...m, metrics: metrics, expanded: true } : m
        )
      );
      toast({
        title: "RAI Metrics Generated",
        description: `Successfully fetched RAI metrics for this ${messageToCheck.content.type} response.`,
      });
    } catch (error) {
      console.error("Error fetching RAI metrics:", error);
      toast({
        title: "Error",
        description: "Failed to fetch RAI metrics. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false); // Stop loading after RAI check attempt
    }
  };

  const toggleRaiMetrics = (messageId: string) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId ? { ...m, expanded: !m.expanded } : m
      )
    );
  };

  const getShieldColorClass = (raiScore: number | undefined) => {
    if (raiScore === undefined) {
      return "text-muted-foreground"; // Default color if RAI score is not available
    }
    // Explicit Tailwind classes for colors based on score
    return raiScore > 0.7 ? "text-green-500 dark:text-green-400" : "text-yellow-500 dark:text-yellow-400";
  };


  // Render message content based on type
  const renderMessageContent = (content: MessageContent) => {
    switch (content.type) {
      case "text":
        return <p className="text-sm break-words">{content.text}</p>;
      case "image":
        // Use next/image for optimization, ensure width/height or layout='fill'
        return <Image src={content.url} alt={content.alt || 'Uploaded image'} width={200} height={200} className="rounded-md max-w-full h-auto object-cover" />;
      case "audio":
        return <audio controls src={content.url} className="w-full max-w-xs">Your browser does not support the audio element.</audio>;
      case "video":
        return <video controls src={content.url} className="rounded-md max-w-xs h-auto" width="300">Your browser does not support the video tag.</video>;
      default:
         const exhaustiveCheck: never = content; // Ensures all types handled
        return null;
    }
  };


  return (
     <div className="flex flex-col h-[calc(100vh-4rem)] bg-muted"> {/* Adjust height for navbar */}

      <div className="flex-grow p-4 space-y-4 overflow-y-auto">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`flex flex-col rounded-lg p-3 max-w-[80%] shadow-sm ${
                message.sender === "user"
                  ? "bg-secondary ml-auto" // User messages appear on the right
                  : "bg-card mr-auto" // AI messages appear on the left
              }`}
            >
              {/* Render Content */}
               <div className="mb-1"> {/* Add margin below content */}
                 {renderMessageContent(message.content)}
               </div>

              {/* RAI Icon - Only for AI messages */}
              {message.sender === "ai" && (
                <div className="relative mt-1 self-end"> {/* Position RAI relative to the bubble, bottom right */}
                    <Button
                      variant="ghost"
                      size="icon"
                      className={`h-6 w-6 hover:text-accent ${getShieldColorClass(message.metrics?.raiScore)}`}
                      onClick={() => handleRaiCheck(message.id)} // Always call handleRaiCheck for AI messages
                      disabled={loading && !message.metrics} // Disable only if loading *new* metrics
                      title={message.metrics ? "Toggle RAI Score Details" : `Check RAI Score for this ${message.content.type}`}
                    >
                      <ShieldCheck className="h-4 w-4" />
                    </Button>
                 </div>
              )}

               {/* Expanded RAI Metrics Card - Only for AI messages */}
               {message.sender === 'ai' && message.metrics && message.expanded && (
                <Card className="mt-2 w-full bg-background border-border">
                  <CardContent className="p-3">
                    <h4 className="text-sm font-semibold mb-2 text-foreground">RAI Metrics:</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                      <div>
                        RAI Score:{" "}
                        <Badge variant="secondary" className={`font-medium ${
                          message.metrics.raiScore > 0.7 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
                        }`}>
                          {message.metrics.raiScore.toFixed(2)}
                        </Badge>
                      </div>
                      <div>Biasness: <span className="font-medium">{message.metrics.biasness.toFixed(2)}</span></div>
                      <div>
                        Truthfulness: <span className="font-medium">{message.metrics.truthfulness.toFixed(2)}</span>
                      </div>
                      <div>Fairness: <span className="font-medium">{message.metrics.fairness.toFixed(2)}</span></div>
                      <div>
                        Groundedness: <span className="font-medium">{message.metrics.groundedness.toFixed(2)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        ))}
        {/* Loading indicator inside the chat area */}
        {loading && <div className="flex justify-center"><p className="text-sm text-muted-foreground">Loading...</p></div>}
         <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t bg-background">
         {/* File Preview */}
         {filePreviewUrl && selectedFile && (
             <div className="mb-2 p-2 border rounded-md relative flex items-center gap-2 bg-muted">
               {selectedFile.type.startsWith('image/') && (
                 <Image src={filePreviewUrl} alt="Preview" width={40} height={40} className="rounded object-cover" />
               )}
                {selectedFile.type.startsWith('audio/') && (
                    <div className="w-10 h-10 bg-secondary rounded flex items-center justify-center text-muted-foreground">
                        <FileAudio className="h-5 w-5" />
                    </div>
                )}
                 {selectedFile.type.startsWith('video/') && (
                    <div className="w-10 h-10 bg-secondary rounded flex items-center justify-center text-muted-foreground">
                        <FileVideo className="h-5 w-5" />
                    </div>
                )}
               <span className="text-sm text-muted-foreground truncate flex-grow">{selectedFile.name}</span>
               <Button variant="ghost" size="icon" className="h-6 w-6 text-muted-foreground hover:text-destructive" onClick={removeSelectedFile}>
                 <X className="h-4 w-4" />
               </Button>
             </div>
           )}

        <div className="flex gap-2 items-end"> {/* Use items-end for better alignment with Textarea */}
          {/* File Input Button */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            title="Attach file"
            className="shrink-0"
          >
            <Paperclip className="h-4 w-4" />
          </Button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept="image/*,audio/*,video/*" // Specify acceptable file types
            disabled={loading}
          />

          {/* Text Input */}
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={selectedFile ? "Add a caption..." : "Type your message..."}
            className="flex-grow rounded-md resize-none min-h-[40px] max-h-[120px]" // Adjust height constraints
            rows={1} // Start with 1 row, auto-expands
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault(); // Prevent newline on Enter
                if(!loading) handleSend(); // Only send if not loading
              }
            }}
            disabled={loading} // Disable textarea while loading
          />

          {/* Send Button */}
          <Button onClick={handleSend} disabled={loading || (!input.trim() && !selectedFile)} className="shrink-0">
            Send
          </Button>
        </div>
      </div>
      <Toaster />
    </div>
  );
};

export default AIChat;
