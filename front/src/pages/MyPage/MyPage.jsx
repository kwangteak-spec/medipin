import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./Button"; 
import "./style.css";

// 누락된 이미지/아이콘 컴포넌트 임시 대체
const User = () => <div style={{width: 30, height: 30, backgroundColor: '#ccc', borderRadius: '50%'}} />;
const SearchOutline = () => <div style={{width: 30, height: 30, backgroundColor: '#ccc'}} />;
const Pill = () => <div style={{width: 30, height: 30, backgroundColor: '#ccc'}} />;

export const MyPageScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="my-page-screen">
      <div className="rectangle-2" />

      {/* 상단 헤더 영역 */}
      <div className="frame-3">
        <div className="group" onClick={() => navigate("/search_main")} style={{cursor: 'pointer'}}>
          <div className="fill">🏠</div>
        </div>
        <div className="my-page-2" style={{textAlign: 'center', fontWeight: 'bold'}}>MY PAGE</div>
        <div className="trailing-icon">
          <div className="container">
            <div className="state-layer">
              <div className="icon-notification" />
            </div>
          </div>
        </div>
      </div>

      {/* 메뉴 리스트 영역 */}
      <div className="frame-4">
        {/* 1. 내 정보 수정 -> Editmypage.jsx 연결 예정 */}
        <div 
          className="frame-5" 
          style={{cursor: 'pointer'}} 
          onClick={() => navigate("/edit-mypage")}
        >
          <User className="icon-feathericons" />
          <div className="frame-6">
            <span className="edit-profile">내 정보 수정</span>
            <span className="ic-baseline-greater">&gt;</span>
          </div>
        </div>
        
        {/* 2. 검색 기록 */}
        <div 
          className="frame-5" 
          style={{cursor: 'pointer', marginTop: '20px'}}
          onClick={() => navigate("/search_detail")}
        >
          <SearchOutline className="icon-instance-node" />
          <div className="frame-6">
            <span className="search-list">검색 기록</span>
            <span className="ic-baseline-greater">&gt;</span>
          </div>
        </div>

        {/* 3. 복용 약 관리 */}
        <div 
          className="frame-5" 
          style={{cursor: 'pointer', marginTop: '20px'}}
          onClick={() => navigate("/pill-management")}
        >
          <Pill className="icon-instance-node" />
          <div className="frame-6">
            <span className="pill-list">복용 약 관리</span>
            <span className="ic-baseline-greater">&gt;</span>
          </div>
        </div>
      </div>

      {/* 프로필 정보 영역 */}
      <div className="frame-7">
        <div className="my-page-wrapper">
          <div className="frame-wrapper">
            <div className="frame-8">
              <div className="frame-9">
                <div className="text-wrapper-5">MediPin User</div>
                <div className="text-wrapper-9">medipin@gmail.com</div>
              </div>
              <div className="change-user-wrapper" style={{cursor: 'pointer'}}>
                <div className="change-user">Change</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 임시 하단 바 삭제됨 (MainLayout의 하단바가 적용됨) */}
    </div>
  );
};