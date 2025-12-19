import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Element } from "../../components/Element/Element";
import "./style.css";

export const Search = () => {
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [history, setHistory] = useState([]);

  /* 🔹 최근 검색어 로드 */
  useEffect(() => {
    const saved = JSON.parse(
      localStorage.getItem("search_history") || "[]"
    );
    setHistory(saved);
  }, []);

  /* 🔹 검색 실행 */
const handleSearch = () => {
  if (!query.trim()) return;

  const updatedHistory = [
    query,
    ...history.filter((item) => item !== query),
  ].slice(0, 5);

  localStorage.setItem(
    "search_history",
    JSON.stringify(updatedHistory)
  );
  setHistory(updatedHistory);

  // ✅ 경로 통일 (중요)
  navigate("/search/detail", {
    state: { query },
  });
};


  /* 🔹 개별 검색어 삭제 */
  const handleDelete = (item, e) => {
    e.stopPropagation();

    const updated = history.filter((h) => h !== item);
    localStorage.setItem(
      "search_history",
      JSON.stringify(updated)
    );
    setHistory(updated);
  };

  return (
    <div className="search">
      <Element className="header" />

      {/* 🔍 검색 입력 영역 */}
      <div className="search-input-area">
        <input
          className="search-input"
          type="text"
          placeholder="검색"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <button className="search-button" onClick={handleSearch}>
          검색
        </button>
      </div>

      {/* 🕘 최근 검색어 */}
      <div className="frame-7">
        {history.length === 0 && (
          <div className="frame-8">
            <div className="text-wrapper-4">
              최근 검색어가 없습니다
            </div>
          </div>
        )}

        {history.map((item, idx) => (
          <div
            key={idx}
            className="frame-8"
            onClick={() =>
              navigate("/search/detail", {
                state: { query },
              })
            }
            style={{ cursor: "pointer" }}
          >
            <div className="text-wrapper-4">{item}</div>

            <div
              className="text-wrapper-5"
              onClick={(e) => handleDelete(item, e)}
            >
              ●●●
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
