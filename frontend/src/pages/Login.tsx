import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { AetheraSignIn } from "@/components/blocks/aethera-sign-in";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      if (isRegister) {
        await register(email, password, name);
        await login(email, password);
      } else {
        await login(email, password);
      }
      setLoading(false);
      setSuccess(true);
      setTimeout(() => navigate("/dashboard"), 1800);
    } catch (err: any) {
      setLoading(false);
      setError(err.response?.data?.detail || "Erro ao conectar");
    }
  }, [email, password, name, isRegister, login, register, navigate]);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSubmit();
  };

  return (
    <AetheraSignIn
      isRegister={isRegister}
      onSubmit={handleFormSubmit}
      onToggleMode={() => { setIsRegister(!isRegister); setError(""); }}
      error={error}
      email={email}
      onEmailChange={(e) => setEmail(e.target.value)}
      password={password}
      onPasswordChange={(e) => setPassword(e.target.value)}
      name={name}
      onNameChange={(e) => setName(e.target.value)}
      loading={loading}
      success={success}
    />
  );
}
