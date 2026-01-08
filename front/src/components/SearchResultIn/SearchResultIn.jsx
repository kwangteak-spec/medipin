import React from "react";
import addIcon from "./add_icon.svg";
import "./style.css";

export const SearchResultIn = ({
  className,
  imageUrl,
  title,
  onPlusClick,
  onImageClick,
}) => {
  return (
    <div className={`search-result-in ${className}`}>
      <div className="search-result">
        <div className="frame">
          <div className="image-icon" style={{ cursor: "pointer", position: "relative" }}>
            <div onClick={onImageClick} style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {imageUrl ? (
                <img
                  src={imageUrl}
                  alt={title}
                  className="drug-db-image"
                />
              ) : (
                <div className="image-placeholder">NO IMAGE</div>
              )}
            </div>
            <img
              className="frame-2"
              alt="add"
              src={addIcon}
              onClick={(e) => {
                e.stopPropagation();
                onPlusClick();
              }}
            />
          </div>

          <div className="text-wrapper">{title}</div>
        </div>
      </div>

    </div>
  );
};
