import React from "react";
import "./style.css";

export const Button = ({
  buttonText = "login",
  one,
  className,
  onClick,          // ✅ 추가
  type = "button", // ✅ 기본값
}) => {
  return (
    <button
      type={type}
      className={`button ${className || ""}`}
      onClick={onClick}   // ✅ 핵심
    >
      <div className="div">{buttonText}</div>
    </button>
  );
};
