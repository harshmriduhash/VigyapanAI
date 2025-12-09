import React from 'react';
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Sparkles } from "lucide-react";

export const Hero = () => {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-emerald-50 via-white to-emerald-100">
      {/* Animated background elements */}
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

      {/* Main content */}
      <div className="relative z-10 mx-auto max-w-6xl px-4 text-center">
        <div className="rounded-3xl backdrop-blur-lg bg-white/40 p-8 lg:p-12 shadow-2xl border border-emerald-200">
          <div className="inline-flex items-center gap-2 bg-emerald-200 px-4 py-2 rounded-full mb-8">
            <Sparkles className="w-4 h-4 text-emerald-700" />
            <span className="text-emerald-800 font-medium">AI-Powered Advertising Platform</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-emerald-950 mb-6 leading-tight">
            Transform Your Advertising Journey with{' '}
            <span className="text-emerald-700">VigyapanAI</span>
          </h1>

          <p className="text-xl md:text-2xl text-emerald-900 mb-8 max-w-3xl mx-auto leading-relaxed">
            Where cutting-edge technology meets creativity to revolutionize your marketing. 
            Analyze, optimize, and generate impactful advertisements effortlessly.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              size="lg"
              className="bg-emerald-700 hover:bg-emerald-800 text-white px-8 py-6 text-lg rounded-full transition-all duration-300 transform hover:scale-105"
              onClick={() => navigate('/get-started')}
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button 
              variant="outline"
              size="lg"
              className="border-emerald-300 text-emerald-800 hover:bg-emerald-100 px-8 py-6 text-lg rounded-full"
              onClick={() => (window.location.href = 'https://youtu.be/6xzC4GWnOhU')}
            >
              Watch Demo
            </Button>
          </div>

          <p className="mt-8 text-emerald-700 font-medium">
             Smart. Engaging. AI-Driven
          </p>
        </div>
      </div>
    </div>
  );
};

export default Hero;
