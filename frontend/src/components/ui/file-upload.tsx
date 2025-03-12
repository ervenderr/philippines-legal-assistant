import React, { useState } from "react";
import { Button } from "./button";
import { Card, CardContent } from "./card";
import { Upload, File, X, CheckCircle, AlertCircle } from "lucide-react";

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  acceptedFileTypes?: string;
  maxSizeMB?: number;
}

export function FileUpload({
  onUpload,
  acceptedFileTypes = ".pdf",
  maxSizeMB = 10,
}: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    // Check file type
    if (acceptedFileTypes && !selectedFile.name.endsWith(".pdf")) {
      setErrorMessage(`Only ${acceptedFileTypes} files are accepted`);
      setUploadStatus("error");
      return;
    }

    // Check file size
    if (selectedFile.size > maxSizeBytes) {
      setErrorMessage(`File size exceeds the maximum limit of ${maxSizeMB}MB`);
      setUploadStatus("error");
      return;
    }

    setFile(selectedFile);
    setErrorMessage(null);
    setUploadStatus("idle");
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("idle");

    try {
      await onUpload(file);
      setUploadStatus("success");
    } catch (error) {
      setUploadStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setUploadStatus("idle");
    setErrorMessage(null);
  };

  return (
    <Card className="border-2 border-dashed border-slate-300 dark:border-slate-700 bg-white/50 dark:bg-gray-950/50">
      <CardContent className="p-6">
        {!file ? (
          <div
            className={`flex flex-col items-center justify-center p-6 rounded-lg transition-colors ${
              isDragging
                ? "bg-primary/10 border-primary"
                : "bg-slate-100 dark:bg-slate-900"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="h-10 w-10 text-slate-400 dark:text-slate-500 mb-4" />
            <h3 className="text-lg font-medium mb-2">Upload Legal Document</h3>
            <p className="text-sm text-muted-foreground text-center mb-4">
              Drag and drop your PDF file here, or click to browse
            </p>
            <Button
              variant="outline"
              onClick={() => document.getElementById("file-upload")?.click()}
              className="relative"
            >
              Browse Files
              <input
                id="file-upload"
                type="file"
                className="sr-only"
                accept={acceptedFileTypes}
                onChange={handleFileChange}
              />
            </Button>
            <p className="text-xs text-muted-foreground mt-4">
              Accepted file types: PDF (Max size: {maxSizeMB}MB)
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center p-4 bg-slate-100 dark:bg-slate-900 rounded-lg">
              <File className="h-8 w-8 text-primary mr-3" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={handleRemoveFile}
                className="p-1 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full"
              >
                <X className="h-5 w-5 text-muted-foreground" />
              </button>
            </div>

            {uploadStatus === "error" && errorMessage && (
              <div className="flex items-center p-3 text-sm bg-destructive/10 text-destructive rounded-lg">
                <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
                {errorMessage}
              </div>
            )}

            {uploadStatus === "success" && (
              <div className="flex items-center p-3 text-sm bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-lg">
                <CheckCircle className="h-4 w-4 mr-2 flex-shrink-0" />
                Document uploaded successfully!
              </div>
            )}

            <div className="flex justify-end">
              <Button
                onClick={handleUpload}
                disabled={isUploading || uploadStatus === "success"}
                className="w-full sm:w-auto"
              >
                {isUploading ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Uploading...
                  </>
                ) : uploadStatus === "success" ? (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Uploaded
                  </>
                ) : (
                  "Upload Document"
                )}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
