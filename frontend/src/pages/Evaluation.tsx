import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Upload, Loader, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";

interface FormData {
  productName: string;
  brandName: string;
  tagline: string;
  colorPalette: string;
  videoUrl: string;
}

const Evaluation = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  // Form state
  const [formData, setFormData] = useState<FormData>({
    productName: "",
    brandName: "",
    tagline: "",
    colorPalette: "#34D399",
    videoUrl: "",
  });

  // UI states
  const [progress, setProgress] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [report, setReport] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>("No video selected");
  const [isLoading, setIsLoading] = useState(false);

  // Handle video file selection
  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        toast({
          title: "File too large",
          description: "Please select a video file smaller than 100MB",
          variant: "destructive"
        });
        return;
      }
      setUploadStatus(`Selected file: ${file.name}`);
    } else {
      setUploadStatus("No video selected");
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setProgress(10);

    const formDataObj = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      formDataObj.append(key, value);
    });

    const videoInput = document.getElementById("video-upload") as HTMLInputElement;
    if (videoInput?.files?.[0]) {
      formDataObj.append("video_file", videoInput.files[0]);
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        body: formDataObj,
      });

      setProgress(50);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setProgress(100);
      setReport(data.report);
      setShowResults(true);
      
      toast({
        title: "Analysis Complete",
        description: "Your advertisement analysis is ready to view",
      });
    } catch (error) {
      console.error("Analysis error:", error);
      toast({
        title: "Analysis Failed",
        description: "There was an error analyzing your advertisement. Please try again.",
        variant: "destructive"
      });
      setUploadStatus("Upload failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Reset form to initial state
  const resetForm = () => {
    setFormData({
      productName: "",
      brandName: "",
      tagline: "",
      colorPalette: "#34D399",
      videoUrl: "",
    });
    setUploadStatus("No video selected");
    setShowResults(false);
    setReport(null);
    setProgress(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 to-white">
      <div className="container mx-auto px-4 py-6">
        <Button
          variant="ghost"
          onClick={() => navigate("/")}
          className="mb-6 hover:bg-emerald-50"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Button>

        {!showResults ? (
          <>
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-emerald-400 bg-clip-text text-transparent mb-4">
                AI-Powered Advertisement Analyzer
              </h1>
              <p className="text-lg text-emerald-700">
                Revolutionize Your Marketing Campaigns with AI Precision
              </p>
            </div>

            <Card className="max-w-2xl mx-auto backdrop-blur-sm bg-white/80">
              <CardHeader>
                <CardTitle>Advertisement Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-4">
                    {/* Product Name Input */}
                    <div>
                      <Label htmlFor="productName">Product Name *</Label>
                      <Input
                        id="productName"
                        required
                        placeholder="Enter product name"
                        value={formData.productName}
                        onChange={(e) =>
                          setFormData({ ...formData, productName: e.target.value })
                        }
                        className="transition-all duration-300 focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>

                    {/* Brand Name Input */}
                    <div>
                      <Label htmlFor="brandName">Brand Name *</Label>
                      <Input
                        id="brandName"
                        required
                        placeholder="Enter brand name"
                        value={formData.brandName}
                        onChange={(e) =>
                          setFormData({ ...formData, brandName: e.target.value })
                        }
                        className="transition-all duration-300 focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>

                    {/* Tagline Input */}
                    <div>
                      <Label htmlFor="tagline">Tagline *</Label>
                      <Input
                        id="tagline"
                        required
                        placeholder="Enter tagline"
                        value={formData.tagline}
                        onChange={(e) =>
                          setFormData({ ...formData, tagline: e.target.value })
                        }
                        className="transition-all duration-300 focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>

                    {/* Color Palette Input */}
                    <div>
                      <Label htmlFor="colorPalette">Color Palette</Label>
                      <Input
                        id="colorPalette"
                        type="color"
                        value={formData.colorPalette}
                        onChange={(e) =>
                          setFormData({ ...formData, colorPalette: e.target.value })
                        }
                        className="h-12 cursor-pointer"
                      />
                    </div>

                    {/* Video Upload Section */}
                    <div className="space-y-2">
                      <Label>Video Upload</Label>
                      <div className="grid gap-4">
                        <Input
                          type="file"
                          accept="video/*"
                          className="hidden"
                          id="video-upload"
                          onChange={handleVideoChange}
                        />
                        <Label
                          htmlFor="video-upload"
                          className="cursor-pointer flex flex-col items-center gap-2 p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-emerald-500 transition-colors"
                        >
                          <Upload className="h-8 w-8 text-gray-400" />
                          <span className="text-sm text-gray-600">
                            Drag and drop or click to upload
                          </span>
                        </Label>
                        <p className="text-sm text-gray-500 text-center">{uploadStatus}</p>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    {progress > 0 && (
                      <Progress value={progress} className="w-full" />
                    )}
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    className="w-full hover:scale-105 transition-transform"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      "Start Evaluating"
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </>
        ) : (
          // Results View
          <div className="container mx-auto px-4 py-12">
            <h1 className="text-4xl font-bold text-center text-emerald-600 mb-6">
              Analysis Results
            </h1>
            <Card className="max-w-4xl mx-auto bg-white shadow-md">
              <CardHeader>
                <CardTitle>Generated Report</CardTitle>
              </CardHeader>
              <CardContent>
                {report ? (
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm">{report}</pre>
                  </div>
                ) : (
                  <div className="flex items-center justify-center p-6">
                    <Loader className="h-8 w-8 animate-spin text-emerald-500" />
                  </div>
                )}
              </CardContent>
            </Card>
            <div className="flex justify-center mt-6">
              <Button
                variant="outline"
                className="hover:bg-emerald-50"
                onClick={resetForm}
              >
                Start a New Analysis
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Evaluation;