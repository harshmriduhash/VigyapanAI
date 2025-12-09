import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Check, Sparkles, LineChart, Video, ArrowRight } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export const Features = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const features = [
    {
      title: "AI-Powered Analysis",
      description: "Advanced algorithms for comprehensive ad evaluation",
      icon: LineChart
    },
    {
      title: "Real-time Feedback",
      description: "Instant insights on visual elements and messaging",
      icon: Sparkles
    },
    {
      title: "Color Optimization",
      description: "Smart palette suggestions for maximum impact",
      icon: Check
    },
    {
      title: "Engagement Prediction",
      description: "AI-driven audience response forecasting",
      icon: Check
    }
  ];

  const handleFeatureClick = (feature: string) => {
    toast({
      title: "Coming Soon",
      description: `${feature} will be available soon!`,
      duration: 3000,
    });
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-emerald-50 via-white to-emerald-100">
      {/* Animated background */}
      <div className="absolute inset-0">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full mix-blend-multiply filter blur-xl animate-float opacity-5"
            style={{
              width: `${Math.random() * 200 + 100}px`,
              height: `${Math.random() * 200 + 100}px`,
              backgroundColor: i % 2 ? '#34D399' : '#10B981',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDuration: `${Math.random() * 10 + 20}s`,
              animationDelay: `${Math.random() * 10}s`,
            }}
          />
        ))}
      </div>

      {/* Services Section */}
      <div className="relative z-10 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <div className="inline-flex items-center gap-2 bg-emerald-200 px-4 py-2 rounded-full mb-8">
              <Sparkles className="w-4 h-4 text-emerald-700" />
              <span className="text-emerald-800 font-medium">Powerful Solutions</span>
            </div>
            <h2 className="text-4xl font-bold text-emerald-950 mb-4">
              Transform Your Marketing Strategy
            </h2>
            <p className="text-lg text-emerald-900">
              Choose from our AI-powered advertising solutions
            </p>
          </div>

          {/* Main service cards */}
          <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 lg:grid-cols-2">
            {/* Analysis Card */}
            <Card className="backdrop-blur-lg bg-white/40 border border-emerald-200 hover:shadow-2xl transition-all duration-500 p-8">
              <CardHeader className="space-y-4">
                <div className="h-12 w-12 rounded-full bg-emerald-200 flex items-center justify-center mb-4">
                  <LineChart className="h-6 w-6 text-emerald-700" />
                </div>
                <CardTitle className="text-2xl font-bold text-emerald-950">AI-Powered Advertisement Analyzer</CardTitle>
                <p className="text-emerald-900 text-lg">
                  Upload your advertisement content and get detailed AI-driven analysis on effectiveness,
                  engagement potential, and recommendations for improvement.
                </p>
              </CardHeader>
              <CardContent className="pt-6">
                <Button
                  size="lg"
                  onClick={() => navigate("/analysis")}
                  className="w-full bg-emerald-700 hover:bg-emerald-800 text-white text-lg py-6 rounded-full transition-all duration-300 transform hover:scale-105"
                >
                  Start Analyzing
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </CardContent>
            </Card>

            {/* Generator Card */}
            <Card className="backdrop-blur-lg bg-white/40 border border-emerald-200 hover:shadow-2xl transition-all duration-500 p-8">
              <CardHeader className="space-y-4">
                <div className="h-12 w-12 rounded-full bg-emerald-200 flex items-center justify-center mb-4">
                  <Video className="h-6 w-6 text-emerald-700" />
                </div>
                <CardTitle className="text-2xl font-bold text-emerald-950">AI-driven Advertisement Generator</CardTitle>
                <p className="text-emerald-900 text-lg">
                  Create compelling video advertisements automatically using AI. Input your brand details
                  and let our AI craft engaging content tailored to your needs.
                </p>
              </CardHeader>
              <CardContent className="pt-6">
                <Button
                  size="lg"
                  onClick={() => navigate("/generator")}
                  className="w-full bg-emerald-700 hover:bg-emerald-800 text-white text-lg py-6 rounded-full transition-all duration-300 transform hover:scale-105"
                >
                  Start Creating
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="relative z-10 py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-3xl font-bold text-center text-emerald-950 mb-12">
              Powerful Features
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {features.map((feature, index) => (
                <div
                  key={index}
                  onClick={() => handleFeatureClick(feature.title)}
                  className="group p-6 rounded-xl backdrop-blur-lg bg-white/40 border border-emerald-200
                           hover:shadow-2xl transition-all duration-500 cursor-pointer
                           hover:scale-105"
                >
                  <feature.icon className="h-8 w-8 text-emerald-700 mb-4 group-hover:text-emerald-800 transition-colors" />
                  <h4 className="text-xl font-semibold text-emerald-950 mb-2">{feature.title}</h4>
                  <p className="text-emerald-900">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;