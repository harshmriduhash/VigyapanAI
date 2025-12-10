import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/components/ui/use-toast";

const Login = () => {
  const { signIn, signUp, loading } = useAuth();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleAuth = async (mode: "signin" | "signup") => {
    try {
      if (mode === "signin") {
        await signIn(email, password);
        toast({ title: "Signed in" });
      } else {
        await signUp(email, password);
        toast({ title: "Check your email to confirm sign-up" });
      }
    } catch (err) {
      toast({
        title: "Auth error",
        description:
          err instanceof Error ? err.message : "Authentication failed",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-emerald-50 to-white px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Sign in to continue</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <div className="flex gap-2">
            <Button
              className="w-full"
              disabled={loading}
              onClick={() => handleAuth("signin")}
            >
              Sign In
            </Button>
            <Button
              variant="outline"
              className="w-full"
              disabled={loading}
              onClick={() => handleAuth("signup")}
            >
              Sign Up
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;