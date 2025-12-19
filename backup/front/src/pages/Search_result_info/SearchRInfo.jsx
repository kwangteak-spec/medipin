import React from "react";
import { Frame } from "./Frame";
import { HomeBar } from "./HomeBar";
import fill4 from "./pre_icon.svg";
import frame8681 from "./pill_pic.svg";
import "./style.css";

export const SearchResultFinal = () => {
  return (
    <div className="search-result-final">
      <div className="frame-5">
        <div className="frame-6">
          <div className="group">
            <img className="fill" alt="Fill" src={fill4} />
          </div>

          <div className="text-wrapper-10">
            가스디알정50밀리그램(디메크로틴산마그네슘)
          </div>
        </div>

        <img className="frame-7" alt="Frame" src={frame8681} />
      </div>

      <Frame />
      <HomeBar />
    </div>
  );
};
