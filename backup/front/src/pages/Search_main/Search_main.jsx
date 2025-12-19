import React from "react";
import { useNavigate } from "react-router-dom";
import { Element } from "../../components/Element/Element";
import "./style.css";

const SearchMain = () => {
  const navigate = useNavigate();

  return (
    <div className="search-main">
      <Element className="header" />

      {/* 🔍 검색창 영역 (UI 유지) */}
      <div className="search-input-area">
        <input
          type="text"
          className="search-input"
          placeholder="검색"
          readOnly              // ✅ 키 입력 방지 (Search.jsx에서만 입력)
          onFocus={() => navigate("/search")}  // ✅ 포커스 시 이동
        />
        <button className="search-button">검색</button>
      </div>
    </div>
  );
};

export default SearchMain;
