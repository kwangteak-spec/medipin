// backup\front\src\pages\Register\Register.jsx
import React, { useState } from "react";
import { Button } from "../../components/Button/Button";
import { Element } from "../../components/Element/Element";
import { useNavigate } from "react-router-dom";
import line from "./line.svg";
import "./style.css";

// ✅ docs 기준 실제 엔드포인트
const API_URL = "http://127.0.0.1:8000/register";

const Register = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [name, setName] = useState("");
  const [phoneNum, setPhoneNum] = useState("");
  const [age, setAge] = useState("");

  const handleRegister = async () => {
    // 간단 검증
    if (!email || !password || !confirmPassword || !name || !phoneNum || !age) {
      alert("모든 항목을 입력해주세요.");
      return;
    }
    if (password !== confirmPassword) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }

    const ageNum = Number(age);
    if (!Number.isInteger(ageNum) || ageNum <= 0) {
      alert("나이를 올바르게 입력해주세요.");
      return;
    }

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          name,
          phone_num: phoneNum,
          age: ageNum,
        }),
      });

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        // FastAPI 422 등에서 detail이 배열로 오는 케이스 대응
        const msg =
          data?.detail
            ? Array.isArray(data.detail)
              ? data.detail.map((d) => d.msg).join(", ")
              : String(data.detail)
            : "회원가입에 실패했습니다.";
        alert(msg);
        return;
      }

      alert("회원가입이 완료되었습니다. 로그인해주세요.");
      navigate("/login");
    } catch (err) {
      console.error(err);
      alert("네트워크 오류로 회원가입에 실패했습니다.");
    }
  };

  return (
    <div className="register">
      <div className="frame-2">
        <div className="frame-3">
          <div className="frame-wrapper">
            <div className="div-wrapper">
              <div className="text-wrapper-2">Join our PIN!</div>
            </div>
          </div>

          <div className="frame-4">
            <div className="frame-5">
              <div className="input-wrap">
                <input value={email} onChange={(e) => setEmail(e.target.value)} />
                {!email && <span>ID (E-mail)</span>}
              </div>
              <img className="line" src={line} alt="" />
            </div>

            <div className="frame-5">
              <div className="input-wrap">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                {!password && <span>Password</span>}
              </div>
              <img className="line" src={line} alt="" />
            </div>

            <div className="frame-5">
              <div className="input-wrap">
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
                {!confirmPassword && <span>Confirm Password</span>}
              </div>
              <img className="line" src={line} alt="" />
            </div>

            <div className="frame-5">
              <div className="input-wrap">
                <input value={name} onChange={(e) => setName(e.target.value)} />
                {!name && <span>Name</span>}
              </div>
              <img className="line" src={line} alt="" />
            </div>

            <div className="frame-5">
              <div className="input-wrap">
                <input
                  value={phoneNum}
                  onChange={(e) => setPhoneNum(e.target.value)}
                />
                {!phoneNum && <span>Phone-number</span>}
              </div>
              <img className="line" src={line} alt="" />
            </div>

            <div className="frame-5">
              <div className="input-wrap">
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                />
                {!age && <span>Age</span>}
              </div>
              <img className="line" src={line} alt="" />
            </div>
          </div>
        </div>

        <div className="register-button-wrapper" onClick={handleRegister}>
          <Button className="button-instance" one="register" />
        </div>
      </div>

      <Element className="header" />
    </div>
  );
};

export default Register;
