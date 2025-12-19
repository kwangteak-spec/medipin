import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./style.css";

/* 헤더 컴포넌트 (기존 유지) */
const Element = ({ className }) => (
  <div className={`element ${className}`}>
    <div className="frame">
      <div className="text-wrapper">MediPIN</div>
    </div>
  </div>
);

const SearchDetail = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const query = location.state?.query;

  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!query) {
      setLoading(false);
      return;
    }

    const fetchList = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/drugs/search?q=${encodeURIComponent(query)}`
        );
        const data = await res.json();
        setList(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("검색 실패", err);
      } finally {
        setLoading(false);
      }
    };

    fetchList();
  }, [query]);

  return (
    <div className="search-detail-page">
      <Element className="header" />

      {/* 뒤로가기 버튼 (위치 유지) */}
      <div className="detail-content">
        <button className="back-button" onClick={() => navigate(-1)}>
          &lt; 뒤로가기
        </button>
      </div>

      {/* 🔹 검색 결과 카드 영역 */}
      <div className="search-result-area">
        {loading && <p>검색 중입니다...</p>}

        {!loading && list.length === 0 && (
          <p>검색 결과가 없습니다.</p>
        )}

        {!loading &&
          list.map((drug) => (
            <div
              key={drug.id}
              className="drug-summary-card"
              onClick={() =>
                navigate(`/search/result/${drug.id}`)
              }
              style={{ cursor: "pointer" }}
            >
              {drug.item_image && (
                <img
                  src={drug.item_image}
                  alt={drug.drug_name}
                  style={{ maxWidth: "100px", borderRadius: "8px", marginBottom: "10px" }}
                />
              )}
              <h3>{drug.drug_name}</h3>
              <p>제조사: {drug.manufacturer}</p>
              <p>제형: {drug.form_type}</p>
            </div>
          ))}
      </div>
    </div>
  );
};

export default SearchDetail;
