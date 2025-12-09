import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Evaluation from "./pages/Evaluation";
import Generator from "./pages/generator";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Main Home Page */}
          <Route path="/" element={<Index />} />
          
          {/* Evaluation Page */}
          <Route path="/evaluation" element={<Evaluation />} />

          {/* Generator Page */}
          <Route path="/generator" element={<Generator />} />
          
          {/* Analysis Page (separated from home) */}
          <Route path="/analysis" element={<Evaluation />} />
          
          {/* Optional: Add a Fallback Route */}
          <Route path="*" element={<div>Page Not Found</div>} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;