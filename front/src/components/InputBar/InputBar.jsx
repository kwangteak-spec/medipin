import React from "react";
import searchIcon from "./search_icon.svg";
import "./style.css";

export const InputBar = ({ className, value, onChange, onSearch, placeholder = "검색" }) => {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && onSearch) {
      onSearch();
    }
  };

  return (
    <div className={`input-bar ${className}`}>
      <input
        className="text-input"
        type="text"
        value={value}
        onChange={onChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
      />
      <div className="icon-stroke-wrapper" onClick={onSearch}>
        <img
          className="icon-stroke"
          alt="Search icon"
          src={searchIcon}
        />
      </div>
    </div>
  );
};
