// src/layouts/MainLayout.jsx
import React from "react";
import { Outlet } from "react-router-dom";
import HomeBar from "../components/HomeBar/HomeBar";

function MainLayout() {
  return (
    <>
      <Outlet />
      <HomeBar />
    </>
  );
}

export default MainLayout;
