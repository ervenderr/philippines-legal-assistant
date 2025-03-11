"use client";

import { useState } from "react";
import { BookOpen, Scale, AlertCircle, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface Answer {
  answer: string;
  relevant_chunks: {
    text: string;
    source: string;
  }[];
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setAnswer(null);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      const data = await response.json();
      setAnswer(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-100 via-slate-200 to-slate-300 dark:from-gray-900 dark:via-gray-900 dark:to-black">
      {/* Header */}
      <header className="w-full bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary rounded-lg">
                <Scale className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-slate-100 dark:to-slate-300">
                  Philippine Legal Assistant
                </h1>
                <p className="text-sm text-muted-foreground">
                  Your AI-powered legal research companion
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-slate-100 dark:to-slate-300">
            Legal Research Made Simple
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Ask questions about Philippine Supreme Court decisions and get
            accurate answers with relevant citations.
          </p>
        </div>

        {/* Search Card */}
        <Card className="border-2 border-slate-200 dark:border-slate-800 shadow-xl bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl mb-8">
          <CardContent className="p-6">
            <form onSubmit={handleSubmit}>
              <div className="relative flex items-center">
                <Input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Enter your legal question..."
                  className="pr-36 h-14 text-lg bg-white dark:bg-gray-950 border-2 focus:ring-2 focus:ring-primary/20"
                />
                <Button
                  type="submit"
                  size="lg"
                  className="absolute right-1 h-12 px-6 bg-primary hover:bg-primary/90"
                  disabled={isLoading || !question.trim()}
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-foreground border-t-transparent" />
                      <span>Searching...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Search className="w-4 h-4" />
                      <span>Search</span>
                    </div>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {error && (
          <Alert
            variant="destructive"
            className="mb-8 border-2 animate-in fade-in slide-in-from-top-4"
          >
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {isLoading && (
          <Card className="border-2 border-slate-200 dark:border-slate-800 shadow-lg animate-pulse">
            <CardHeader className="space-y-4 pb-4">
              <Skeleton className="h-6 w-1/4" />
              <Skeleton className="h-4 w-2/4" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-[90%]" />
              <Skeleton className="h-4 w-[80%]" />
            </CardContent>
          </Card>
        )}

        {answer && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4">
            <Card className="border-2 border-slate-200 dark:border-slate-800 shadow-xl bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl">
              <CardHeader className="space-y-4">
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <BookOpen className="w-6 h-6 text-primary" />
                  </div>
                  Answer
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose dark:prose-invert max-w-none">
                  <p className="text-lg leading-relaxed">{answer.answer}</p>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-6">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Scale className="w-5 h-5 text-primary" />
                </div>
                Supporting Evidence
              </h3>
              {answer.relevant_chunks.map((chunk, index) => (
                <Card
                  key={index}
                  className="border-2 border-slate-200 dark:border-slate-800 shadow-md bg-white/60 dark:bg-gray-950/60 backdrop-blur-xl hover:shadow-lg transition-all hover:bg-white/80 dark:hover:bg-gray-950/80"
                >
                  <CardContent className="p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <Badge
                        variant="outline"
                        className="px-3 py-1 text-xs font-medium border-2"
                      >
                        {chunk.source}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {chunk.text}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-slate-200 dark:border-slate-800 mt-12 py-8 text-center text-sm text-muted-foreground bg-white/50 dark:bg-gray-950/50 backdrop-blur-sm">
        <p>Philippine Legal Assistant - AI-powered legal research tool</p>
      </footer>
    </div>
  );
}
