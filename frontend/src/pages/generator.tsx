import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Loader, Download, BarChart  } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";

interface FormData {
  productName: string;
  tagline: string;
  duration: string;
  callToAction: string;
  logoUrl: string;
  targetAudience: string;
  campaignGoal: string;
  brandColors: string;
}

interface FormErrors {
  [key: string]: string;
}

const ResultsSection = ({ videoUrl, onNewVideo }) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isDownloading, setIsDownloading] = useState(false);
  
  const handleDownload = async () => {
    try {
      setIsDownloading(true);
      const response = await fetch(videoUrl);
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'generated-video.mp4';
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      
      toast({
        title: "Success",
        description: "Video downloaded successfully!"
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Unable to download the video. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsDownloading(false);
    }
  };

  const handleAnalysis = () => {
    navigate('/analysis', { state: { videoUrl } });
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <Card className="p-6 bg-white shadow-md">
        <CardContent>
          <div className="text-center">
            <div className="mt-4">
              <div className="relative w-full max-w-2xl mx-auto rounded-lg shadow-lg overflow-hidden">
                <video 
                  controls 
                  className="w-full h-full"
                  src={videoUrl}
                  preload="metadata"
                >
                  Your browser does not support the video tag.
                </video>
              </div>
              <div className="mt-4 space-x-4">
                <Button
                  onClick={handleDownload}
                  disabled={isDownloading}
                  className="hover:scale-105 transition-transform"
                >
                  {isDownloading ? (
                    <>
                      <Loader className="mr-2 h-4 w-4 animate-spin" />
                      Downloading...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      Download Video
                    </>
                  )}
                </Button>
                <Button
                  onClick={handleAnalysis}
                  className="hover:scale-105 transition-transform bg-emerald-600 hover:bg-emerald-700"
                >
                  <BarChart className="mr-2 h-4 w-4" />
                  Do Advertisement Analysis
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      <div className="flex justify-center mt-6">
        <Button
          variant="ghost"
          className="hover:bg-emerald-50"
          onClick={onNewVideo}
        >
          Create Another Video
        </Button>
      </div>
    </div>
  );
};


const Generator = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [formData, setFormData] = useState<FormData>({
    productName: "",
    tagline: "",
    duration: "",
    callToAction: "",
    logoUrl: "",
    targetAudience: "",
    campaignGoal: "",
    brandColors: "",
  });

  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.productName.trim()) {
      newErrors.productName = "Product name is required";
    }

    if (!formData.tagline.trim()) {
      newErrors.tagline = "Tagline is required";
    }

    if (!formData.duration.trim()) {
      newErrors.duration = "Duration is required";
    } else {
      const duration = Number(formData.duration);
      if (isNaN(duration) || duration <= 0 || duration > 300) {
        newErrors.duration = "Duration must be between 1 and 300 seconds";
      }
    }

    if (!formData.callToAction.trim()) {
      newErrors.callToAction = "Call to action is required";
    }

    if (!formData.logoUrl.trim()) {
      newErrors.logoUrl = "Logo URL is required";
    } else if (!isValidUrl(formData.logoUrl)) {
      newErrors.logoUrl = "Please enter a valid URL";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast({
        title: "Validation Error",
        description: "Please check the form for errors",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setProgress(10);

    try {
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setProgress(50);

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setProgress(100);
      setVideoUrl(data.video_url);
      setShowResults(true);

      toast({
        title: "Success",
        description: "Video generated successfully!",
      });
    } catch (error) {
      console.error('Error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate video",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewVideo = () => {
    setShowResults(false);
    setProgress(0);
    setVideoUrl(null);
    setFormData({
      productName: "",
      tagline: "",
      duration: "",
      callToAction: "",
      logoUrl: "",
      targetAudience: "",
      campaignGoal: "",
      brandColors: "",
    });
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
                AI Advertisement Generator
              </h1>
              <p className="text-lg text-emerald-700">
                Create Engaging Video Content with AI Technology
              </p>
            </div>

            <Card className="max-w-2xl mx-auto backdrop-blur-sm bg-white/80">
              <CardHeader>
                <CardTitle>Create New Advertisement</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Form fields remain the same */}
                  <div className="space-y-4">
                    {/* Product Name */}
                    <div>
                      <Label htmlFor="productName">Product Name *</Label>
                      <Input
                        id="productName"
                        value={formData.productName}
                        onChange={(e) => {
                          setFormData({ ...formData, productName: e.target.value });
                          if (errors.productName) {
                            setErrors({ ...errors, productName: "" });
                          }
                        }}
                        className={`transition-all duration-300 focus:ring-2 focus:ring-emerald-500 ${
                          errors.productName ? 'border-red-500' : ''
                        }`}
                      />
                      {errors.productName && (
                        <p className="text-sm text-red-500 mt-1">{errors.productName}</p>
                      )}
                    </div>

                    {/* Tagline */}
                    <div>
                      <Label htmlFor="tagline">Tagline *</Label>
                      <Input
                        id="tagline"
                        value={formData.tagline}
                        onChange={(e) => {
                          setFormData({ ...formData, tagline: e.target.value });
                          if (errors.tagline) {
                            setErrors({ ...errors, tagline: "" });
                          }
                        }}
                        className={`transition-all duration-300 focus:ring-2 focus:ring-emerald-500 ${
                          errors.tagline ? 'border-red-500' : ''
                        }`}
                      />
                      {errors.tagline && (
                        <p className="text-sm text-red-500 mt-1">{errors.tagline}</p>
                      )}
                    </div>

                    {/* Duration */}
                    <div>
                      <Label htmlFor="duration">Video Duration (seconds) *</Label>
                      <Input
                        id="duration"
                        type="number"
                        value={formData.duration}
                        onChange={(e) => {
                          setFormData({ ...formData, duration: e.target.value });
                          if (errors.duration) {
                            setErrors({ ...errors, duration: "" });
                          }
                        }}
                        className={`transition-all duration-300 focus:ring-2 focus:ring-emerald-500 ${
                          errors.duration ? 'border-red-500' : ''
                        }`}
                      />
                      {errors.duration && (
                        <p className="text-sm text-red-500 mt-1">{errors.duration}</p>
                      )}
                    </div>

                    {/* Call to Action */}
                    <div>
                      <Label htmlFor="callToAction">Call to Action Text *</Label>
                      <Input
                        id="callToAction"
                        value={formData.callToAction}
                        onChange={(e) => {
                          setFormData({ ...formData, callToAction: e.target.value });
                          if (errors.callToAction) {
                            setErrors({ ...errors, callToAction: "" });
                          }
                        }}
                        className={`transition-all duration-300 focus:ring-2 focus:ring-emerald-500 ${
                          errors.callToAction ? 'border-red-500' : ''
                        }`}
                      />
                      {errors.callToAction && (
                        <p className="text-sm text-red-500 mt-1">{errors.callToAction}</p>
                      )}
                    </div>

                    {/* Logo URL */}
                    <div>
                      <Label htmlFor="logoUrl">Logo URL *</Label>
                      <Input
                        id="logoUrl"
                        value={formData.logoUrl}
                        onChange={(e) => {
                          setFormData({ ...formData, logoUrl: e.target.value });
                          if (errors.logoUrl) {
                            setErrors({ ...errors, logoUrl: "" });
                          }
                        }}
                        className={`transition-all duration-300 focus:ring-2 focus:ring-emerald-500 ${
                          errors.logoUrl ? 'border-red-500' : ''
                        }`}
                        placeholder="Enter a publicly accessible image URL"
                      />
                      {errors.logoUrl && (
                        <p className="text-sm text-red-500 mt-1">{errors.logoUrl}</p>
                      )}
                    </div>

                    {/* Optional fields */}
                    <div>
                      <Label htmlFor="targetAudience">Target Audience (optional)</Label>
                      <Input
                        id="targetAudience"
                        value={formData.targetAudience}
                        onChange={(e) => setFormData({ ...formData, targetAudience: e.target.value })}
                        className="transition-all duration-300 focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>

                    <div>
                      <Label htmlFor="campaignGoal">Campaign Goal (optional)</Label>
                      <Input
                        id="campaignGoal"
                        value={formData.campaignGoal}
                        onChange={(e) => setFormData({ ...formData, campaignGoal: e.target.value })}
                        className="transition-all duration-300 focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>

                    <div>
                      <Label htmlFor="brandColors">
                        Brand Colors (comma-separated hex codes, optional)
                      </Label>
                      <Input
                        id="brandColors"
                        placeholder="e.g., #FF0000, #00FF00, #0000FF"
                        value={formData.brandColors}
                        onChange={(e) => setFormData({ ...formData, brandColors: e.target.value })}
                        className="transition-all duration-300 focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>
                  </div>

                  {isLoading && (
                    <div className="w-full">
                      <Progress value={progress} className="w-full" />
                      <p className="text-sm text-center mt-2 text-gray-600">
                        Generating your video... {progress}%
                      </p>
                    </div>
                  )}

                  <Button
                    type="submit"
                    className="w-full hover:scale-105 transition-transform"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader className="mr-2 h-4 w-4 animate-spin" />
                        Generating Video...
                      </>
                    ) : (
                      "Generate Video"
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </>
        ) : (
          <ResultsSection
            videoUrl={videoUrl}
            onNewVideo={handleNewVideo}
          />
        )}
      </div>
    </div>
  );
};

export default Generator;