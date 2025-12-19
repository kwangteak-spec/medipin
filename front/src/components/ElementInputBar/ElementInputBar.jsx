import React from "react";
import iconStroke from "./search_icon.svg";
import "./style.css";

export const ElementInputBar = ({
  className,
  value,
  onChange,
  onKeyDown,
  onSearch,
}) => {
  return (
    <div className={`element-input-bar ${className}`}>
      <div className="frame">
        <input
          className="text-wrapper"
          type="text"
          placeholder="검색"
          value={value}
          onChange={onChange}
          onKeyDown={onKeyDown}
        />

        <div
          className="icon-stroke-wrapper"
          onClick={onSearch}
        >
          <img
            className="icon-stroke"
            alt="search icon"
            src={iconStroke}
          />
        </div>
      </div>
    </div>
  );
};
