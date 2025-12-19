// src/pages/Login/Login.jsx

import React, { useState, useEffect } from "react";
import { Button } from "../../components/Button";
import { Element } from "../../components/Element";
import { Warning } from "../../components/Warning/Warning";
import { useNavigate } from "react-router-dom";
import "./style.css";

export const Login = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (showWarning) {
      const timer = setTimeout(() => {
        setShowWarning(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [showWarning]);

  const handleForgetPassword = () => {
    setShowWarning(true);
  };

  const goToRegister = () => {
    navigate("register");
  };

  const handleLogin = async () => {
    setError("");
    const API_URL = "http://127.0.0.1:8000/login";

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("authToken", data.access_token);
        navigate("/search_main");
      } else {
        let errorMessage = "이메일 또는 비밀번호가 올바르지 않습니다.";

        if (response.status === 422 && Array.isArray(data.detail)) {
          errorMessage =
            "입력 오류: " +
            data.detail
              .map((err) => {
                const field = err.loc.length > 1 ? err.loc[1] : "입력";
                return `[${field}] ${err.msg}`;
              })
              .join(", ");
        } else if (typeof data.detail === "string") {
          errorMessage = data.detail;
        }

        setError(errorMessage);
      }
    } catch (err) {
      setError("서버 연결 실패. FastAPI 서버를 확인하세요.");
    }
  };

  return (
    <div className="login" data-model-id="2:127">
      {showWarning && <Warning one="forget-password" />}

      <Element className="header" />

      <div className="frame-2">
        <div className="frame-3">
          <div className="text-wrapper-2">Welcome</div>

          <div className="frame-4">
            <div className="div-wrapper">
              <input
                type="email"
                placeholder="Email"
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="div-wrapper">
              <input
                type="password"
                placeholder="Password"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && (
              <div style={{ color: "red", marginTop: "10px" }}>{error}</div>
            )}
          </div>
        </div>

        <div onClick={handleLogin}>
          <Button className="button-instance" one="login" />
        </div>

        <div className="frame-5">
          <p
            className="don-t-have-an"
            onClick={goToRegister}
            style={{ cursor: "pointer" }}
          >
            <span className="span">Don’t have an account? </span>
            <span className="text-wrapper-4">Sign Up</span>
          </p>

          <div
            className="text-wrapper-5"
            onClick={handleForgetPassword}
            style={{ cursor: "pointer" }}
          >
            forget password?
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
