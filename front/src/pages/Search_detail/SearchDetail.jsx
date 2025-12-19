import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Element } from "../../components/Element/Element";
import { SearchResultIn } from "../../components/SearchResultIn/SearchResultIn";
import { HomeBar } from "../../components/HomeBar/HomeBar";

import preIcon from "./pre_icon.svg";

import "./style.css";

const SearchDetail = () => {
  const navigate = useNavigate();
  const { query } = useParams(); // ✅ 검색어 URL 파라미터

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!query) {
      setLoading(false);
      return;
    }

    const fetchResults = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/drugs/search?q=${encodeURIComponent(query)}`
        );
        const data = await res.json();
        setResults(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("검색 실패", err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query]);

  return (
    <div className="search-detail">
      {/* 헤더 */}
      <Element className="header" />

      {/* 검색어 표시 영역 */}
      <div className="frame-6">
        <div className="fill-wrapper" onClick={() => navigate("/search_main")}>
          <img className="fill" alt="back" src={preIcon} />
        </div>

        <div className="text-wrapper-6">{query}</div>
      </div>

      {/* 결과 영역 */}
      <div className="search-result-2">
        {!loading && results.length === 0 && (
          <p>검색 결과가 없습니다.</p>
        )}

        {!loading && results.length > 0 && (
          <div className="frame-7">
            {results.map((item) => (
              <SearchResultIn
                key={item.id}
                imageUrl={item.item_image}
                title={item.drug_name}
                onPlusClick={() => alert("추후 구현 예정입니다")}
                onImageClick={() => navigate(`/search/result/${item.id}`)}
              />
            ))}
          </div>
        )}
      </div>

      {/* 하단 네비게이션 */}
      <div className="bottom-nav-container">
        <HomeBar />
      </div>
    </div>
  );
};

export default SearchDetail;
