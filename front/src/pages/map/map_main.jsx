// src/pages/map/map_main.jsx
import React, { useState } from "react";
import Sidebar from "./Sidebar";
import KakaoMap from "../../components/Map";

import "./style.css";

export const MapMain = () => {
  // ✅ 지도 제어 상태들 (모두 필요)
  const [radius, setRadius] = useState(1000);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentCity, setCurrentCity] = useState("");
  const [filterType, setFilterType] = useState("all");

  const [results, setResults] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);

  return (
    <div className="map-main">
      {/* ✅ 사이드바 */}
      <Sidebar
        radius={radius}
        setRadius={setRadius}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        currentCity={currentCity}
        onCityChange={setCurrentCity}
        filterType={filterType}
        setFilterType={setFilterType}
        results={results}
        onSelectResult={setSelectedItem}
      />

      {/* ✅ 실제 카카오 지도 */}
      <div className="kakao-map-layer">
        <KakaoMap
          filterType={filterType}
          radius={radius}
          searchQuery={searchQuery}
          currentCity={currentCity}
          onResultsChange={setResults}
          selectedItem={selectedItem}
        />
      </div>
    </div>
  );
};
