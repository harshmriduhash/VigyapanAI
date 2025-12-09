import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Loader, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";
import { authFetch } from "@/lib/api";

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
  const [isLoading, setIsLoading] = useState(false);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setProgress(10);

    try {
      const response = await authFetch("/analyze", {
        method: "POST",
        body: JSON.stringify(formData),
      });

      setProgress(50);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const jobId = data.job_id;

      const resultUrl = await pollJob(jobId);
      setProgress(100);
      setReport(`Report ready. Download: ${resultUrl}`);
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
    } finally {
      setIsLoading(false);
    }
  };

  const pollJob = async (jobId: string): Promise<string> => {
    let attempts = 0;
    while (attempts < 60) {
      const res = await authFetch(`/jobs/${jobId}`);
      const data = await res.json();
      if (data.status === "finished" && data.result_url) return data.result_url;
      if (data.error) throw new Error(data.error);
      await new Promise((r) => setTimeout(r, 3000));
      attempts += 1;
    }
    throw new Error("Timed out waiting for analysis");
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

                    {/* Video URL */}
                    <div>
                      <Label htmlFor="videoUrl">Video URL *</Label>
                      <Input
                        id="videoUrl"
                        required
                        placeholder="https://..."
                        value={formData.videoUrl}
                        onChange={(e) =>
                          setFormData({ ...formData, videoUrl: e.target.value })
                        }
                        className="transition-all duration-300 focus:ring-2 focus:ring-emerald-500"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Provide a direct URL to your MP4 (S3/R2 or public link).
                      </p>
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