import React from "react";
import { SearchSwitcher } from "./SearchSwitcher";
import arrowTriangle2Circlepath from "./arrow-triangle-2-circlepath.svg";
import shutter from "./shutter.svg";
import "./style.css";

export const SearchCamera = () => {
  return (
    <div className="search-camera">
      <div className="rectangle" />

      <div className="bottom-drawer">
        <img className="icon-shutter" alt="Icon shutter" src={shutter} />

        <div className="action-rotate">
          <img
            className="arrow-triangle"
            alt="Arrow triangle"
            src={arrowTriangle2Circlepath}
          />
        </div>
      </div>

      <SearchSwitcher className="search-switcher-instance" one="one" />
    </div>
  );
};
