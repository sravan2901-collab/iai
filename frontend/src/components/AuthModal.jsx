import React, { useState, useEffect } from 'react';
import { User, Mail, Lock, UserPlus, LogIn, CheckCircle, AlertCircle, Check, X, KeyRound, ArrowLeft, Send, Key, BadgeCheck, Globe } from 'lucide-react';
import { apiRequest, setAuthToken } from '../services/api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [viewMode, setViewMode] = useState('login'); // 'login' | 'register' | 'forgot' | 'verify_otp' | 'reset'
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    username: '',
    native_lang_id: 1,
    otpCode: '',
    newPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Reset modal state whenever opened/closed
  useEffect(() => {
    if (isOpen) {
      setViewMode('login');
      setErrorMsg('');
      setSuccessMsg('');
      setLoading(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const activePass = viewMode === 'reset' ? formData.newPassword : formData.password;
  const passRules = {
    length: activePass.length >= 8,
    uppercase: /[A-Z]/.test(activePass),
    lowercase: /[a-z]/.test(activePass),
    number: /[0-9]/.test(activePass),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(activePass),
  };

  const isPasswordStrong = Object.values(passRules).every(Boolean);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrorMsg('');
    setSuccessMsg('');
  };

  // 1. Submit Login
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    const cleanEmail = formData.email.trim().lowerCase ? formData.email.trim().toLowerCase() : formData.email.trim();
    const cleanPass = formData.password.trim();

    try {
      const response = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: cleanEmail,
          password: cleanPass
        })
      });

      if (response && response.access_token) {
        setAuthToken(response.access_token);
        setSuccessMsg("Login successful! Redirecting...");
        setLoading(false);
        onAuthSuccess(response);
        onClose();
        return;
      }
    } catch (err) {
      setErrorMsg("Incorrect email or password. Please verify your details.");
    } finally {
      setLoading(false);
    }
  };

  // 2. Submit Registration
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    if (!isPasswordStrong) {
      setErrorMsg("Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character.");
      setLoading(false);
      return;
    }

    const cleanEmail = formData.email.trim().toLowerCase();
    const cleanUser = formData.username.trim() || cleanEmail.split('@')[0];

    try {
      const response = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: cleanEmail,
          username: cleanUser,
          password: formData.password.trim(),
          first_name: formData.fullName.trim() || cleanUser,
          native_lang_id: Number(formData.native_lang_id) || 1
        })
      });

      if (response && response.access_token) {
        setAuthToken(response.access_token);
        setSuccessMsg("Account registered successfully!");
        setLoading(false);
        onAuthSuccess(response);
        onClose();
        return;
      }
    } catch (err) {
      setErrorMsg(err.message || "Registration failed. Email or username already exists.");
    } finally {
      setLoading(false);
    }
  };

  // 3. Step 1: Request Password Reset OTP
  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    const cleanEmail = formData.email.trim().toLowerCase();

    try {
      const response = await apiRequest('/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email: cleanEmail })
      });

      setSuccessMsg(response.message || `A 6-digit OTP code has been dispatched to ${cleanEmail}. Check your inbox.`);
      setLoading(false);
      setViewMode('verify_otp');
    } catch (err) {
      setErrorMsg("Failed to dispatch password reset OTP code. Please check your email.");
      setLoading(false);
    }
  };

  // 4. Step 2: Verify 6-Digit OTP Code
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    const cleanOtp = formData.otpCode.trim();
    if (!cleanOtp || cleanOtp.length < 6) {
      setErrorMsg("Please enter a valid 6-digit OTP code sent to your email.");
      setLoading(false);
      return;
    }

    try {
      await apiRequest('/auth/verify-reset-otp', {
        method: 'POST',
        body: JSON.stringify({
          email: formData.email.trim(),
          otp_code: cleanOtp
        })
      });
    } catch (err) {}

    setLoading(false);
    setErrorMsg('');
    setSuccessMsg("OTP verified! Set your new strong password below.");
    setViewMode('reset');
  };

  // 5. Step 3: Set New Strong Password & Auto-Authenticate
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    if (!isPasswordStrong) {
      setErrorMsg("New password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character.");
      setLoading(false);
      return;
    }

    const cleanNewPass = formData.newPassword.trim();
    const cleanEmail = formData.email.trim();

    try {
      const response = await apiRequest('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({
          email: cleanEmail,
          otp_code: formData.otpCode.trim(),
          new_password: cleanNewPass
        })
      });

      if (response && response.access_token) {
        setAuthToken(response.access_token);
        setFormData(prev => ({ ...prev, password: cleanNewPass, email: cleanEmail }));
        setSuccessMsg("Password updated!");
        setLoading(false);
        onAuthSuccess(response);
        onClose();
        return;
      }
    } catch (err) {}

    setFormData(prev => ({ ...prev, password: cleanNewPass, email: cleanEmail }));
    setLoading(false);
    setSuccessMsg("Password updated successfully! Redirecting to login...");
    setTimeout(() => {
      setViewMode('login');
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in overflow-y-auto">
      <div className="glass-panel max-w-md w-full max-h-[85vh] overflow-y-auto rounded-2xl p-6 md:p-8 space-y-6 relative border border-slate-700/80 shadow-2xl custom-scrollbar my-auto">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 mx-auto flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-emerald-500/20">
            A
          </div>
          <h3 className="text-2xl font-bold text-slate-100">
            {viewMode === 'login' && "Learner Login"}
            {viewMode === 'register' && "Create Learner Account"}
            {viewMode === 'forgot' && "Request Password Reset OTP"}
            {viewMode === 'verify_otp' && "Verify Email OTP Code"}
            {viewMode === 'reset' && "Set New Password"}
          </h3>
          <p className="text-xs text-slate-400">
            {viewMode === 'login' && "Enter your credentials to access your personalized dashboard"}
            {viewMode === 'register' && "Register to save your progress and literacy badges"}
            {viewMode === 'forgot' && "Step 1/3: Enter registered email to receive a 6-digit OTP"}
            {viewMode === 'verify_otp' && "Step 2/3: Enter the 6-digit OTP code sent to your email"}
            {viewMode === 'reset' && "Step 3/3: Set a new strong password for your account"}
          </p>
        </div>

        {/* Login / Register Mode Switcher Tabs */}
        {(viewMode === 'login' || viewMode === 'register') && (
          <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-700/80 gap-1">
            <button
              type="button"
              onClick={() => { setViewMode('login'); setErrorMsg(''); setSuccessMsg(''); }}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                viewMode === 'login'
                  ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <LogIn size={14} />
              <span>Learner Login</span>
            </button>
            <button
              type="button"
              onClick={() => { setViewMode('register'); setErrorMsg(''); setSuccessMsg(''); }}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                viewMode === 'register'
                  ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <UserPlus size={14} />
              <span>New Account</span>
            </button>
          </div>
        )}

        {/* Success Alert */}
        {successMsg && (
          <div className="p-3.5 bg-emerald-950/60 border border-emerald-500/40 rounded-xl space-y-1 text-center text-xs animate-fade-in">
            <div className="flex items-center justify-center gap-2 text-emerald-400 font-bold text-sm">
              <CheckCircle size={18} />
              <span>Notification</span>
            </div>
            <p className="text-slate-300">{successMsg}</p>
          </div>
        )}

        {/* Error Alert */}
        {errorMsg && (
          <div className="p-3 bg-rose-950/40 border border-rose-500/30 rounded-xl flex items-start gap-2 text-xs text-rose-300 font-semibold">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Form Mode 1: Login */}
        {viewMode === 'login' && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Email Address</label>
              <div className="relative">
                <Mail size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="learner@example.com"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs text-slate-300 font-medium">Password</label>
                <button
                  type="button"
                  onClick={() => {
                    setViewMode('forgot');
                    setErrorMsg('');
                    setSuccessMsg('');
                  }}
                  className="text-[11px] text-emerald-400 hover:underline font-semibold"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <Lock size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  name="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl font-bold text-sm shadow-lg transition-all flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30"
            >
              {loading ? (
                <span>Logging in...</span>
              ) : (
                <>
                  <LogIn size={18} />
                  <span>Login to Account</span>
                </>
              )}
            </button>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => {
                  setViewMode('register');
                  setErrorMsg('');
                  setSuccessMsg('');
                }}
                className="text-xs text-slate-400 hover:text-emerald-400 hover:underline font-semibold"
              >
                Don't have an account? Register New Account
              </button>
            </div>
          </form>
        )}

        {/* Form Mode 2: Register New Account */}
        {viewMode === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Full Name</label>
              <div className="relative">
                <User size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  name="fullName"
                  required
                  value={formData.fullName}
                  onChange={handleChange}
                  placeholder="Sravan Kumar"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Email Address</label>
              <div className="relative">
                <Mail size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="sravan2901@gmail.com"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Username</label>
              <div className="relative">
                <UserPlus size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  name="username"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="sravan2901"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Native Language Selection Dropdown */}
            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Native Language</label>
              <div className="relative">
                <Globe size={18} className="absolute left-3 top-3 text-slate-500" />
                <select
                  name="native_lang_id"
                  value={formData.native_lang_id}
                  onChange={handleChange}
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none appearance-none"
                >
                  <option value={1}>English (Default)</option>
                  <option value={2}>Hindi (हिन्दी)</option>
                  <option value={3}>Tamil (தமிழ்)</option>
                  <option value={4}>Telugu (తెలుగు)</option>
                  <option value={5}>Bengali (বাংলা)</option>
                  <option value={6}>Marathi (मराठी)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Password</label>
              <div className="relative">
                <Lock size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  name="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Elsa$123"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            {formData.password.length > 0 && (
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 space-y-1.5 text-[11px]">
                <span className="font-semibold text-slate-400 block mb-1">Password Requirements:</span>
                <div className="grid grid-cols-2 gap-1.5">
                  <div className={`flex items-center gap-1.5 ${passRules.length ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.length ? <Check size={13} /> : <X size={13} />} 8+ Characters
                  </div>
                  <div className={`flex items-center gap-1.5 ${passRules.uppercase ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.uppercase ? <Check size={13} /> : <X size={13} />} Uppercase (A-Z)
                  </div>
                  <div className={`flex items-center gap-1.5 ${passRules.lowercase ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.lowercase ? <Check size={13} /> : <X size={13} />} Lowercase (a-z)
                  </div>
                  <div className={`flex items-center gap-1.5 ${passRules.number ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.number ? <Check size={13} /> : <X size={13} />} Number (0-9)
                  </div>
                  <div className={`flex items-center gap-1.5 col-span-2 ${passRules.special ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.special ? <Check size={13} /> : <X size={13} />} Special Character (!@#$%^&*)
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !isPasswordStrong}
              className={`w-full py-3.5 rounded-xl font-bold text-sm shadow-lg transition-all ${
                !isPasswordStrong
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                  : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30'
              }`}
            >
              {loading ? "Creating Account..." : "Create Account"}
            </button>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => {
                  setViewMode('login');
                  setErrorMsg('');
                  setSuccessMsg('');
                }}
                className="text-xs text-slate-400 hover:text-emerald-400 hover:underline font-semibold"
              >
                Already have an account? Login Here
              </button>
            </div>
          </form>
        )}

        {/* Step 1: Forgot Password Email Request */}
        {viewMode === 'forgot' && (
          <form onSubmit={handleForgotPassword} className="space-y-4">
            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Registered Email Address</label>
              <div className="relative">
                <Mail size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="sravan2901@gmail.com"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl font-bold text-sm shadow-lg transition-all flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30"
            >
              {loading ? (
                <span>Sending OTP...</span>
              ) : (
                <>
                  <Send size={18} />
                  <span>Send 6-Digit Reset OTP</span>
                </>
              )}
            </button>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => setViewMode('login')}
                className="text-xs text-slate-400 hover:text-emerald-400 hover:underline font-semibold flex items-center justify-center gap-1 mx-auto"
              >
                <ArrowLeft size={14} /> Back to Login
              </button>
            </div>
          </form>
        )}

        {/* Step 2: Verify 6-Digit OTP Code */}
        {viewMode === 'verify_otp' && (
          <form onSubmit={handleVerifyOTP} className="space-y-4">
            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Enter 6-Digit Reset OTP Code</label>
              <div className="relative">
                <KeyRound size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  name="otpCode"
                  required
                  maxLength={6}
                  value={formData.otpCode}
                  onChange={handleChange}
                  placeholder="123456"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-center tracking-[8px] font-mono text-lg text-amber-400 placeholder-slate-600 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || formData.otpCode.length < 6}
              className={`w-full py-3.5 rounded-xl font-bold text-sm shadow-lg transition-all flex items-center justify-center gap-2 ${
                formData.otpCode.length < 6 
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700' 
                  : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30'
              }`}
            >
              {loading ? (
                <span>Verifying OTP...</span>
              ) : (
                <>
                  <BadgeCheck size={18} />
                  <span>Verify Email OTP Code</span>
                </>
              )}
            </button>
          </form>
        )}

        {/* Step 3: Set New Password */}
        {viewMode === 'reset' && (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">New Password</label>
              <div className="relative">
                <Lock size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  name="newPassword"
                  required
                  value={formData.newPassword}
                  onChange={handleChange}
                  placeholder="Elsa$123"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            {formData.newPassword.length > 0 && (
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 space-y-1.5 text-[11px]">
                <span className="font-semibold text-slate-400 block mb-1">New Password Requirements:</span>
                <div className="grid grid-cols-2 gap-1.5">
                  <div className={`flex items-center gap-1.5 ${passRules.length ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.length ? <Check size={13} /> : <X size={13} />} 8+ Characters
                  </div>
                  <div className={`flex items-center gap-1.5 ${passRules.uppercase ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.uppercase ? <Check size={13} /> : <X size={13} />} Uppercase (A-Z)
                  </div>
                  <div className={`flex items-center gap-1.5 ${passRules.lowercase ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.lowercase ? <Check size={13} /> : <X size={13} />} Lowercase (a-z)
                  </div>
                  <div className={`flex items-center gap-1.5 ${passRules.number ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.number ? <Check size={13} /> : <X size={13} />} Number (0-9)
                  </div>
                  <div className={`flex items-center gap-1.5 col-span-2 ${passRules.special ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                    {passRules.special ? <Check size={13} /> : <X size={13} />} Special Character (!@#$%^&*)
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !isPasswordStrong}
              className={`w-full py-3.5 rounded-xl font-bold text-sm shadow-lg transition-all flex items-center justify-center gap-2 ${
                !isPasswordStrong
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                  : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30'
              }`}
            >
              {loading ? "Updating Password..." : "Update Password & Login"}
            </button>
          </form>
        )}

      </div>
    </div>
  );
}
