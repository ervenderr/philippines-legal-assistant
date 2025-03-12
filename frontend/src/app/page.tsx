"use client";

import { useState, useEffect } from "react";
import {
  BookOpen,
  Scale,
  AlertCircle,
  Search,
  FileText,
  Upload,
  Trash2,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileUpload } from "@/components/ui/file-upload";
import { v4 as uuidv4 } from "uuid";

interface Answer {
  answer: string;
  relevant_chunks: {
    text: string;
    source: string;
    similarity: number;
  }[];
}

interface Document {
  id: string;
  filename: string;
  status: string;
  metadata: {
    sections?: Record<string, number>;
    total_length?: number;
  };
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string>("");
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [activeTab, setActiveTab] = useState("search");
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(
    null
  );

  // Initialize user ID on first load
  useEffect(() => {
    // Check if user ID exists in local storage
    const storedUserId = localStorage.getItem("legal_assistant_user_id");
    if (storedUserId) {
      setUserId(storedUserId);
    } else {
      // Generate a new user ID
      const newUserId = uuidv4();
      localStorage.setItem("legal_assistant_user_id", newUserId);
      setUserId(newUserId);
    }
  }, []);

  // Load user documents when user ID is available
  useEffect(() => {
    if (userId) {
      loadUserDocuments();
    }
  }, [userId]);

  const loadUserDocuments = async () => {
    if (!userId) return;

    setIsLoadingDocuments(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/documents/${userId}`
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Error response:", errorData);
        throw new Error(
          errorData.detail ||
            `Failed to load documents: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();
      console.log("Documents loaded:", data);
      setDocuments(data.documents || []);
    } catch (err) {
      console.error("Error loading documents:", err);
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setIsLoadingDocuments(false);
    }
  };

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
        body: JSON.stringify({
          question,
          user_id: userId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Query error response:", errorData);
        throw new Error(
          errorData.detail ||
            `Failed to get answer: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();
      setAnswer(data);
    } catch (err) {
      console.error("Error getting answer:", err);
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    try {
      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Upload error response:", errorData);
        throw new Error(
          errorData.detail ||
            `Upload failed: ${response.status} ${response.statusText}`
        );
      }

      // Reload documents after successful upload
      const result = await response.json();
      console.log("Upload successful:", result);

      await loadUserDocuments();

      // Switch to search tab after upload
      setActiveTab("search");

      return result;
    } catch (error) {
      console.error("Upload error:", error);
      throw error;
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!userId) return;

    setIsDeleting(documentId);

    try {
      const response = await fetch(
        `http://localhost:8000/api/documents/${userId}/${documentId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Delete error response:", errorData);
        throw new Error(
          errorData.detail ||
            `Failed to delete document: ${response.status} ${response.statusText}`
        );
      }

      // Reload documents after successful deletion
      await loadUserDocuments();
      setShowDeleteConfirm(null);
    } catch (err) {
      console.error("Error deleting document:", err);
      setError(
        err instanceof Error ? err.message : "Failed to delete document"
      );
    } finally {
      setIsDeleting(null);
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
            Upload your legal documents and ask questions to get accurate
            answers with relevant citations.
          </p>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="search" className="text-base py-3">
              <Search className="w-4 h-4 mr-2" />
              Ask Questions
            </TabsTrigger>
            <TabsTrigger value="upload" className="text-base py-3">
              <Upload className="w-4 h-4 mr-2" />
              Upload Documents
            </TabsTrigger>
          </TabsList>

          {/* Search Tab */}
          <TabsContent value="search" className="mt-6">
            {/* Document List */}
            {documents.length > 0 ? (
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-3 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-primary" />
                  Your Documents ({documents.length})
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {documents.map((doc) => (
                    <Card
                      key={doc.id}
                      className="bg-white/60 dark:bg-gray-950/60 backdrop-blur-sm"
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center">
                          <FileText className="w-5 h-5 mr-3 text-primary" />
                          <div className="truncate flex-1">
                            <p className="font-medium truncate">
                              {doc.filename}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {doc.metadata.total_length
                                ? `${Math.round(
                                    doc.metadata.total_length / 1000
                                  )}K characters`
                                : "Processing..."}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive hover:bg-destructive/10"
                            onClick={() => setShowDeleteConfirm(doc.id)}
                            title="Delete document"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ) : isLoadingDocuments ? (
              <div className="mb-6">
                <Skeleton className="h-6 w-48 mb-3" />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              </div>
            ) : (
              <Alert className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>No documents found</AlertTitle>
                <AlertDescription>
                  Please upload documents first to ask questions about them.
                </AlertDescription>
              </Alert>
            )}

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
                      disabled={documents.length === 0}
                    />
                    <Button
                      type="submit"
                      size="lg"
                      className="absolute right-1 h-12 px-6 bg-primary hover:bg-primary/90"
                      disabled={
                        isLoading || !question.trim() || documents.length === 0
                      }
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
                      <p className="text-lg leading-relaxed whitespace-pre-line">
                        {answer.answer}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {answer.relevant_chunks.length > 0 && (
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
                            {chunk.similarity && (
                              <Badge className="px-3 py-1 text-xs font-medium bg-primary/10 text-primary border border-primary/20">
                                Relevance: {Math.round(chunk.similarity * 100)}%
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {chunk.text}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          {/* Upload Tab */}
          <TabsContent value="upload" className="mt-6">
            <Card className="border-2 border-slate-200 dark:border-slate-800 shadow-xl bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Upload Legal Documents
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FileUpload onUpload={handleUpload} />

                <div className="mt-6 text-sm text-muted-foreground">
                  <h4 className="font-medium mb-2">Supported Documents:</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Supreme Court decisions (PDF)</li>
                    <li>Philippine laws and regulations (PDF)</li>
                    <li>Legal opinions and memoranda (PDF)</li>
                  </ul>
                  <p className="mt-4">
                    After uploading, your documents will be processed and made
                    available for questions. This may take a few moments
                    depending on the document size.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Document List */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <FileText className="w-5 h-5 text-primary" />
                </div>
                Your Documents
              </h3>

              {isLoadingDocuments ? (
                <div className="space-y-3">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              ) : documents.length > 0 ? (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <Card
                      key={doc.id}
                      className="bg-white/60 dark:bg-gray-950/60 backdrop-blur-sm"
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center">
                          <FileText className="w-8 h-8 mr-4 text-primary" />
                          <div className="flex-1">
                            <p className="font-medium">{doc.filename}</p>
                            <div className="flex items-center text-xs text-muted-foreground mt-1">
                              <Badge variant="outline" className="mr-2">
                                {doc.status}
                              </Badge>
                              {doc.metadata.total_length && (
                                <span>
                                  {Math.round(doc.metadata.total_length / 1000)}
                                  K characters
                                </span>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive hover:bg-destructive/10"
                            onClick={() => setShowDeleteConfirm(doc.id)}
                            title="Delete document"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="bg-slate-100 dark:bg-slate-900 border-dashed border-2">
                  <CardContent className="p-6 text-center">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                    <p className="text-muted-foreground">
                      No documents uploaded yet
                    </p>
                    <Button
                      variant="outline"
                      className="mt-4"
                      onClick={() => setActiveTab("upload")}
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Your First Document
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-slate-200 dark:border-slate-800 mt-12 py-8 text-center text-sm text-muted-foreground bg-white/50 dark:bg-gray-950/50 backdrop-blur-sm">
        <p>Philippine Legal Assistant - AI-powered legal research tool</p>
      </footer>

      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-destructive" />
                Confirm Deletion
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4">
                Are you sure you want to delete this document? This action
                cannot be undone.
              </p>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowDeleteConfirm(null)}
                  disabled={isDeleting !== null}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => handleDeleteDocument(showDeleteConfirm)}
                  disabled={isDeleting !== null}
                >
                  {isDeleting === showDeleteConfirm ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      Deleting...
                    </>
                  ) : (
                    "Delete"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
