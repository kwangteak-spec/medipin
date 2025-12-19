// src/pages/Login/Login.jsx

import React, { useState } from "react";
import { Button } from "../../components/Button";
import { Element } from "../../components/Element";
import { Warning } from "../../components/Warning/Warning";
import { useNavigate } from "react-router-dom";
import "./style.css";

export const Login = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // ✅ Warning 상태
  const [warningType, setWarningType] = useState("hidden");

  const handleLogin = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem("authToken", data.access_token);
        navigate("/search_main");
      } else {
        // 🔴 비밀번호 불일치
        setWarningType("incorrect-password");
      }
    } catch {
      // 🔴 서버 오류도 로그인 실패로 처리
      setWarningType("incorrect-password");
    }
  };

  return (
    <div className="login">
      {/* ✅ Warning (클릭 시 닫힘) */}
      {warningType !== "hidden" && (
        <Warning
          one={warningType}
          onClose={() => setWarningType("hidden")}
        />
      )}

      {/* Header */}
      <Element variant="simple" />

      {/* Login Form */}
      <div className="frame-2">
        <div className="frame-3">
          <div className="text-wrapper-2">Welcome</div>

          <div className="frame-4">
            <div className="div-wrapper">
              <input
                className="input-field"
                placeholder="ID"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="div-wrapper">
              <input
                type="password"
                className="input-field"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>
        </div>

        <Button
          one="login"
          className="button-instance"
          onClick={handleLogin}
        />

        <div className="frame-5">
          <p
            className="don-t-have-an"
            onClick={() => navigate("/register")}
          >
            <span className="span">Don’t have an account?</span>
            <span className="text-wrapper-4"> Sign Up</span>
          </p>

          {/* 🔵 forget password → 안내 경고 */}
          <div
            className="text-wrapper-5"
            onClick={() => setWarningType("forget-password")}
          >
            forget password?
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
