import React from "react";
import { Search } from "./Search";
import { SearchResultIn } from "./SearchResultIn";
import fill4 from "./fill-4.svg";
import frame8681 from "./frame-8681.svg";
import "./style.css";

export const SearchList = () => {
  return (
    <div className="search-list">
      <div className="handle-wrapper">
        <div className="handle">
          <div className="handle-2" />
        </div>
      </div>

      <img className="frame-5" alt="Frame" src={frame8681} />

      <div className="frame-6">
        <div className="fill-wrapper">
          <img className="fill" alt="Fill" src={fill4} />
        </div>

        <div className="text-wrapper-5">
          가스디알정50밀리그램(디메크로틴산마그네슘)
        </div>
      </div>

      <div className="frame-7">
        <div className="frame-8">
          <SearchResultIn
            className="search-result-in-instance"
            frame="frame-8825-2.svg"
            img="vector-4.svg"
            vector="vector-3.svg"
            vector1="vector-5.svg"
          />
          <SearchResultIn
            className="search-result-in-instance"
            frame="frame-8825-3.svg"
            img="vector-7.svg"
            vector="vector-6.svg"
            vector1="vector-8.svg"
          />
        </div>

        <div className="frame-8">
          <SearchResultIn
            className="search-result-in-instance"
            frame="frame-8825-4.svg"
            img="vector-10.svg"
            vector="vector-9.svg"
            vector1="vector-11.svg"
          />
          <SearchResultIn
            className="search-result-in-instance"
            frame="frame-8825-5.svg"
            img="vector-13.svg"
            vector="vector-12.svg"
            vector1="vector-14.svg"
          />
        </div>

        <div className="frame-8">
          <SearchResultIn
            className="search-result-in-instance"
            frame="frame-8825-6.svg"
            img="vector-16.svg"
            vector="vector-15.svg"
            vector1="vector-17.svg"
          />
          <SearchResultIn
            className="search-result-in-instance"
            frame="frame-8825-7.svg"
            img="vector-19.svg"
            vector="vector-18.svg"
            vector1="vector-20.svg"
          />
        </div>
      </div>

      <Search
        calendarIcon="calendar-icon-2.svg"
        className="under-bar"
        ellipse="ellipse-138-2.svg"
        iconStroke="icon-stroke-2.svg"
        mapIcon="map-icon-2.svg"
        rectangle="rectangle-15-2.svg"
        rectangleClassName="search-instance"
        searchIcon="search-icon-2.svg"
      />
    </div>
  );
};
