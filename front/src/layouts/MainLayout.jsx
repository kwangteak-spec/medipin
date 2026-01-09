// src/layouts/MainLayout.jsx
import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import HomeBar from "../components/HomeBar/HomeBar";
import AlarmOverlay from "../components/AlarmOverlay/AlarmOverlay";

function MainLayout() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const isHistoryDetail = location.pathname === "/chat" && searchParams.get("history") === "true";

  return (
    <div className={isHistoryDetail ? "history-detail-view" : ""}>
      <AlarmOverlay />
      <Outlet />
      {!isHistoryDetail && <HomeBar />}
    </div>
  );
}

export default MainLayout;
