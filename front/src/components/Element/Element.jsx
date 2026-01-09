import React from "react";
import { useAlarm } from "../../context/AlarmContext";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../Icons";
import { InputBar } from "../InputBar/InputBar";
import "./style.css";

/**
 * variant
 * - "simple" : 로고만 (로그인)
 * - "alarm"  : 로고 + 알림
 * - "search" : 로고 + 알림 + 검색
 * - "chat-list" : 로고 + 알람 + 검색바 (채팅 목록용)
 * - "back" : 뒤로가기 + 로고 + 알림
 */

export const Element = ({ variant = "simple", className = "", onBackClick, title }) => {
  const { toggleOverlay } = useAlarm();
  const navigate = useNavigate();

  const handleBack = onBackClick || (() => navigate(-1));

  return (
    <div className={`element element--${variant} ${className}`}>
      <div className="header-top">
        {variant === "back" ? (
          <div style={{ width: 56, display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
            <button onClick={handleBack} className="header-back-btn">
              <BackIcon />
            </button>
          </div>
        ) : title ? (
          <div style={{ width: 56 }}></div>
        ) : null}

        {title !== undefined ? (
          <div className="header-title">{title}</div>
        ) : (
          <div className="logo">MediPIN</div>
        )}

        {(variant === "alarm" || variant === "search" || variant === "chat-list" || variant === "back") && (
          <div className="icon-wrapper" onClick={toggleOverlay}>
            <div className="icon-alarm" />
          </div>
        )}
      </div>

      {(variant === "search" || variant === "chat-list") && (
        <InputBar className="header-search" iconStroke="search_icon.svg" />
      )}
    </div>
  );
};

export default Element;
