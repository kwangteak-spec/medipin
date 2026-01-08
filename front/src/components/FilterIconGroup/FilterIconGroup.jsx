import React, { useRef, useState } from "react";
import PropTypes from "prop-types";

import HospitalIcon from "./Hospital_icon.svg";
import PharmacyIcon from "./Pharmacy_icon.svg";
import SosIcon from "./Sos_icon.svg";
import ConStoreIcon from "./Constore_icon.svg";
import NowIcon from "./Now_icon.svg";
import FavoritesIcon from "./Favorites_icon.svg";

import "./style.css";

const FilterIconGroup = ({ filters, onToggle, className = "" }) => {
  const scrollRef = useRef(null);
  const [isDrag, setIsDrag] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const onDragStart = (e) => {
    e.preventDefault();
    setIsDrag(true);
    setStartX(e.pageX - scrollRef.current.offsetLeft);
    setScrollLeft(scrollRef.current.scrollLeft);
  };

  const onDragEnd = () => {
    setIsDrag(false);
  };

  const onDragMove = (e) => {
    if (!isDrag) return;
    e.preventDefault();
    const x = e.pageX - scrollRef.current.offsetLeft;
    const walk = (x - startX) * 2; // 스크롤 속도 배율
    scrollRef.current.scrollLeft = scrollLeft - walk;
  };

  return (
    <div
      className={`filter-icon-group ${className}`}
      ref={scrollRef}
      onMouseDown={onDragStart}
      onMouseMove={onDragMove}
      onMouseUp={onDragEnd}
      onMouseLeave={onDragEnd}
    >
      {/* 병원 */}
      <div
        className={`filter-item ${filters.hospital ? "active" : ""}`}
        onClick={() => onToggle("hospital")}
      >
        <img src={HospitalIcon} alt="병원" className="icon" />
        <span className="label">병원</span>
      </div>

      {/* 약국 */}
      <div
        className={`filter-item ${filters.pharmacy ? "active" : ""}`}
        onClick={() => onToggle("pharmacy")}
      >
        <img src={PharmacyIcon} alt="약국" className="icon" />
        <span className="label">약국</span>
      </div>

      {/* 응급 */}
      <div
        className={`filter-item ${filters.sos ? "active" : ""}`}
        onClick={() => onToggle("sos")}
      >
        <img src={SosIcon} alt="응급실" className="icon" />
        <span className="label">응급실</span>
      </div>

      {/* 편의점 */}
      <div
        className={`filter-item ${filters.constore ? "active" : ""}`}
        onClick={() => onToggle("constore")}
      >
        <img src={ConStoreIcon} alt="편의점 약국" className="icon" />
        <span className="label">편의점 약국</span>
      </div>

      {/* 현재 */}
      <div
        className={`filter-item ${filters.now ? "active" : ""}`}
        onClick={() => onToggle("now")}
      >
        <img src={NowIcon} alt="운영중" className="icon" />
        <span className="label">운영중</span>
      </div>

      {/* 즐겨찾기 - 로그인 시에만 표시 */}
      {!!localStorage.getItem("authToken") && (
        <div
          className={`filter-item ${filters.favorites ? "active" : ""}`}
          onClick={() => onToggle("favorites")}
        >
          <img src={FavoritesIcon} alt="즐겨찾기" className="icon" />
          <span className="label">즐겨찾기</span>
        </div>
      )}
    </div>
  );
};

FilterIconGroup.propTypes = {
  filters: PropTypes.object.isRequired,
  onToggle: PropTypes.func.isRequired,
  className: PropTypes.string,
};

export default FilterIconGroup;
