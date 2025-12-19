import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "../pages/Login/Login";
import Register from "../pages/Register/Register";
import SearchMain from "../pages/Search_main/Search_main";
import { Search } from "../pages/Search/Search";
import SearchDetail from "../pages/Search_detail/search_detail";

function AppRouter() {
  return (
    <Router>
      <Routes>
        {/* 메인 경로 */}
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/search_main" element={<SearchMain />} />
        <Route path="/search" element={<Search />} />

        {/* ✅ 검색 상세 (query는 state로만 전달) */}
        <Route path="/search_detail" element={<SearchDetail />} />

        {/* 404 */}
        <Route
          path="*"
          element={
            <div style={{ textAlign: "center", marginTop: "50px" }}>
              페이지를 찾을 수 없습니다.
            </div>
          }
        />
      </Routes>
    </Router>
  );
}

export default AppRouter;
