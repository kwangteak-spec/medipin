import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Welcome from "./pages/Welcome/Welcome";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import SearchMain from "./pages/Search_main/Search_main";
import { Search } from "./pages/Search/Search";
import SearchDetail from "./pages/Search_detail/search_detail";
import SearchResultInfo from "./pages/Search_result_info/Search_result_info";


import "./styles/global.css";

createRoot(document.getElementById("app")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
  <Route path="/" element={<Welcome />} />
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  {/* 검색 진입 */}
  <Route path="/search_main" element={<SearchMain />} />

  {/* 검색어 입력 */}
  <Route path="/search" element={<Search />} />

  {/* 🔹 검색 결과 리스트 */}
  <Route path="/search/detail" element={<SearchDetail />} />

  {/* 🔹 약 상세 정보 (⭐ 핵심) */}
  <Route
    path="/search/result/:drugId"
    element={<SearchResultInfo />}
  />

  {/* 404 */}
  <Route path="*" element={<div>페이지를 찾을 수 없습니다.</div>} />
</Routes>
    </BrowserRouter>
  </React.StrictMode>
);
