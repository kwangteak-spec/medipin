import React, { useEffect, useRef, useState } from "react";
import { InputBar } from "../../components/InputBar/InputBar";
import FilterIconGroup from "../../components/FilterIconGroup/FilterIconGroup";
import MapList from "../../components/MapList/MapList";
import { HomeBar } from "../../components/HomeBar/HomeBar";
import { API_BASE_URL } from "../../api/config";

import hospitalIcon from "../../components/FilterIconGroup/Hospital_marker.svg";
import pharmacyIcon from "../../components/FilterIconGroup/Pharmacy_marker.svg";
import convIcon from "../../components/FilterIconGroup/Constore_marker.svg";
import sosIcon from "../../components/FilterIconGroup/Sos_marker.svg";

import "./style.css";

const SHEET = {
  CLOSED: "CLOSED",
  MIN: "MIN",
  FULL: "FULL",
};

const MyLocationIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="8" />
    <line x1="12" y1="2" x2="12" y2="5" />
    <line x1="12" y1="19" x2="12" y2="22" />
    <line x1="2" y1="12" x2="5" y2="12" />
    <line x1="19" y1="12" x2="22" y2="12" />
    <circle cx="12" cy="12" r="1.5" fill="currentColor" />
  </svg>
);

export const MapMain = () => {
  const mapContainerRef = useRef(null);
  const mapInstance = useRef(null);
  const clustererRef = useRef(null);
  const DEFAULT_CENTER = { lat: 37.5665, lng: 126.978 }; // 서울시청 기준
  const markersRef = useRef({
    hospital: [],
    pharmacy: [],
    convenience: [],
    emergency: [], // 응급실
  });
  const myLocationOverlayRef = useRef(null); // 내 위치 오버레이
  const addressOverlayRef = useRef(null); // 주소 검색 결과 오버레이
  const selectedMarkerRef = useRef(null); // 현재 확대된 마커
  const timerRef = useRef(null); // 디바운스 타이머 Refs

  const iconMap = {
    hospital: hospitalIcon,
    pharmacy: pharmacyIcon,
    convenience: convIcon,
    emergency: sosIcon,
  };

  // 데이터 상태
  const [searchText, setSearchText] = useState(""); // 검색창 입력값
  const [keyword, setKeyword] = useState("");      // 실제 필터링 키워드
  const [sheetState, setSheetState] = useState(SHEET.CLOSED);
  const [visiblePlaces, setVisiblePlaces] = useState([]); // 리스트에 보여줄 데이터
  const [selectedPlace, setSelectedPlace] = useState(null); // 선택된 장소 상세 정보

  // 필터 상태
  const [filters, setFilters] = useState({
    hospital: true,
    pharmacy: true,
    sos: false,
    constore: false, // 편의점
    now: false,
    favorites: false,
  });

  const [radius, setRadius] = useState(1000);
  const geocoderRef = useRef(null);
  const radiusCircleRef = useRef(null); // 반경 원 Overlay

  // 클로저 문제 해결을 위한 Refs
  const filtersRef = useRef(filters);
  const keywordRef = useRef(keyword);
  const sheetStateRef = useRef(sheetState);

  // 상태 동기화
  useEffect(() => { filtersRef.current = filters; }, [filters]);
  useEffect(() => { keywordRef.current = keyword; }, [keyword]);
  useEffect(() => { sheetStateRef.current = sheetState; }, [sheetState]);

  const API_URL = `${API_BASE_URL}/map`;

  const toggleFilter = (key) => {
    setFilters((prev) => {
      const isTurningOn = !prev[key];
      const next = { ...prev, [key]: isTurningOn };

      if (isTurningOn) {
        setSheetState(SHEET.MIN);
      } else {
        // 모든 주요 필터가 꺼졌는지 확인
        const isAnyActive = next.hospital || next.pharmacy || next.sos || next.constore;
        if (!isAnyActive) {
          setSheetState(SHEET.CLOSED);
          setSelectedPlace(null);
        }
      }
      return next;
    });
  };

  /* ------------------------------------------------------------------
     Kakao Map 초기화
     ------------------------------------------------------------------ */
  const waitForKakao = () =>
    new Promise((resolve, reject) => {
      if (window.kakao && window.kakao.maps) {
        return resolve(window.kakao);
      }
      let count = 0;
      const timer = setInterval(() => {
        if (window.kakao && window.kakao.maps) {
          clearInterval(timer);
          resolve(window.kakao);
        }
        if (count++ > 50) {
          clearInterval(timer);
          reject(new Error("Kakao SDK load timeout"));
        }
      }, 100);
    });

  useEffect(() => {
    let isMounted = true;

    waitForKakao()
      .then((kakao) => {
        if (!isMounted) return;

        const container = mapContainerRef.current;
        kakao.maps.load(() => {
          const options = {
            center: new kakao.maps.LatLng(37.5665, 126.978),
            level: 4,
          };
          const map = new kakao.maps.Map(container, options);
          mapInstance.current = map;

          // 지오코더 초기화
          geocoderRef.current = new kakao.maps.services.Geocoder();

          clustererRef.current = new kakao.maps.MarkerClusterer({
            map: map,
            averageCenter: true,
            minLevel: 5,
            disableClickZoom: false,
            styles: [{
              width: '40px', height: '40px',
              background: 'rgba(51, 204, 255, .8)',
              borderRadius: '20px',
              color: '#000',
              textAlign: 'center',
              fontWeight: 'bold',
              lineHeight: '40px'
            }]
          });

          const handleMapIdle = () => {
            if (timerRef.current) clearTimeout(timerRef.current);
            timerRef.current = setTimeout(() => {
              if (keywordRef.current && keywordRef.current.trim()) return;
              fetchMarkersInBounds();
            }, 100);
          };

          kakao.maps.event.addListener(map, 'dragend', handleMapIdle);
          kakao.maps.event.addListener(map, 'zoom_changed', handleMapIdle);

          kakao.maps.event.addListener(map, 'idle', () => {
            const center = map.getCenter();
            localStorage.setItem("last_map_lat", center.getLat());
            localStorage.setItem("last_map_lng", center.getLng());
          });

          kakao.maps.event.addListener(map, 'click', () => {
            // FULL 상태에서 지도 클릭 시 MIN으로 먼저 내리고, 
            // MIN 상태일 때 클릭해야 완전히 사라지게 수정
            if (sheetStateRef.current === SHEET.FULL) {
              setSheetState(SHEET.MIN);
            } else {
              setSheetState(SHEET.CLOSED);
              setSelectedPlace(null);
            }
          });

          const initUserLocation = async () => {
            await moveToMyLocation();
          };

          initUserLocation();
          updateRadiusCircle();
        });
      })
      .catch((err) => {
        console.error("Kakao SDK loading failed", err);
      });

    return () => {
      isMounted = false;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  /* ------------------------------------------------------------------
     데이터 Fetching (Viewport Based)
     ------------------------------------------------------------------ */
  const fetchMarkersInBounds = async () => {
    if (!mapInstance.current) return;

    const bounds = mapInstance.current.getBounds();
    const sw = bounds.getSouthWest();
    const ne = bounds.getNorthEast();
    const params = `?north=${ne.getLat()}&south=${sw.getLat()}&east=${ne.getLng()}&west=${sw.getLng()}`;

    const urls = [
      `${API_URL}/hospitals${params}`,
      `${API_URL}/pharmacies${params}`,
      `${API_URL}/convenience-stores${params}`,
      `${API_URL}/hospitals/emergency${params}`,
    ];

    try {
      const responses = await Promise.all(urls.map(u => fetch(u, {
        headers: { "Accept": "application/json" }
      }).catch(err => {
        console.error(`Fetch failed for ${u}:`, err);
        return { ok: false };
      })));

      const data = await Promise.all(responses.map(r => {
        if (r.ok) return r.json();
        return [];
      }));

      const [hospitals, pharmacies, stores, emergencies] = data;
      clearMarkers();

      const newMarkers = {
        hospital: createMarkerObjects(hospitals, "hospital"),
        pharmacy: createMarkerObjects(pharmacies, "pharmacy"),
        convenience: createMarkerObjects(stores, "convenience"),
        emergency: createMarkerObjects(emergencies, "emergency"),
      };

      markersRef.current = newMarkers;
      applyFilter();

    } catch (err) {
      console.error("Map Data Fetch Error:", err);
    }
  };

  /* 마커 객체 생성 헬퍼 */
  const getPlaceId = (item) => `${item.name}-${item.lat}-${item.lng}`;

  const createMarkerObjects = (data, type) => {
    if (!Array.isArray(data) || !window.kakao || !window.kakao.maps) return [];

    return data.map((item) => {
      const pId = getPlaceId(item);
      const isSelected = selectedPlace && getPlaceId(selectedPlace) === pId && selectedPlace.type === type;

      const size = isSelected ? 28 : 18;
      const offset = isSelected ? 14 : 9;

      const markerImage = new window.kakao.maps.MarkerImage(
        iconMap[type],
        new window.kakao.maps.Size(size, size),
        { offset: new window.kakao.maps.Point(offset, offset) }
      );

      const marker = new window.kakao.maps.Marker({
        position: new window.kakao.maps.LatLng(item.lat, item.lng),
        image: markerImage,
      });
      // 데이터 식별을 위해 pId와 type 저장
      marker.data = { ...item, type, pId };

      if (isSelected) {
        selectedMarkerRef.current = marker;
      }

      window.kakao.maps.event.addListener(marker, 'click', () => {
        setSelectedPlace({ ...item, type });
        setSheetState(SHEET.MIN);
      });

      return marker;
    });
  };

  /* 마커 초기화 */
  const clearMarkers = () => {
    if (clustererRef.current) {
      clustererRef.current.clear();
    }
    clearAddressOverlay();
  };

  const clearAddressOverlay = () => {
    if (addressOverlayRef.current) {
      addressOverlayRef.current.setMap(null);
      addressOverlayRef.current = null;
    }
  };

  /* ------------------------------------------------------------------
     필터링 & 렌더링
     ------------------------------------------------------------------ */
  const applyFilter = () => {
    if (!clustererRef.current) return;
    clustererRef.current.clear();

    let targets = [];
    const currentFilters = filtersRef.current;

    if (currentFilters.hospital) targets.push(...markersRef.current.hospital);
    if (currentFilters.pharmacy) targets.push(...markersRef.current.pharmacy);
    if (currentFilters.constore) targets.push(...markersRef.current.convenience);
    if (currentFilters.sos) targets.push(...markersRef.current.emergency);

    const currentKeyword = keywordRef.current;
    if (currentKeyword && currentKeyword.trim()) {
      targets = targets.filter(m => m.data.name.includes(currentKeyword) || (m.data.address && m.data.address.includes(currentKeyword)));
    }

    clustererRef.current.addMarkers(targets);
    const visibleData = targets.map(m => m.data);
    setVisiblePlaces(visibleData);
  };

  useEffect(() => {
    if (!keyword && !searchText) {
      if (mapInstance.current) fetchMarkersInBounds();
    }
    applyFilter();
  }, [filters, keyword]);

  /* ------------------------------------------------------------------
     검색 핸들러 (API 호출)
     ------------------------------------------------------------------ */
  const handleSearch = async () => {
    const kw = searchText.trim();
    if (!kw) {
      setKeyword("");
      return;
    }

    let searchLat = DEFAULT_CENTER.lat;
    let searchLng = DEFAULT_CENTER.lng;
    if (mapInstance.current) {
      const center = mapInstance.current.getCenter();
      searchLat = center.getLat();
      searchLng = center.getLng();
    }

    geocoderRef.current.addressSearch(kw, async (result, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        const addrData = result[0];
        const moveLatLon = new window.kakao.maps.LatLng(addrData.y, addrData.x);

        clearMarkers();
        clearAddressOverlay();

        let roadAddr = "";
        if (addrData.road_address) {
          const { road_name, main_building_no, sub_building_no } = addrData.road_address;
          roadAddr = `${road_name} ${main_building_no}${sub_building_no ? '-' + sub_building_no : ''}`;
        } else {
          roadAddr = addrData.address_name;
        }

        const content = `
          <div class="address-search-marker">
            <div class="pin">
              <div class="dot"></div>
            </div>
            <div class="label">${roadAddr}</div>
          </div>
        `;

        addressOverlayRef.current = new window.kakao.maps.CustomOverlay({
          position: moveLatLon,
          content: content,
          yAnchor: 1.1
        });
        addressOverlayRef.current.setMap(mapInstance.current);

        mapInstance.current.setCenter(moveLatLon);
        mapInstance.current.setLevel(3);

        setKeyword(kw);
        return;
      }

      try {
        const res = await fetch(`${API_URL}/search?keyword=${encodeURIComponent(kw)}&lat=${searchLat}&lng=${searchLng}&radius=5000`);
        if (res.ok) {
          const data = await res.json();
          if (data.length === 0) {
            alert(`'${kw}' 주변 검색 결과가 없습니다.\n지도를 이동하거나 검색어를 변경해보세요.`);
            return;
          }

          const hospitals = data.filter(d => d.type === 'hospital');
          const pharmacies = data.filter(d => d.type === 'pharmacy');
          const stores = data.filter(d => d.type === 'convenience');

          clearMarkers();
          markersRef.current = {
            hospital: createMarkerObjects(hospitals, 'hospital'),
            pharmacy: createMarkerObjects(pharmacies, 'pharmacy'),
            convenience: createMarkerObjects(stores, 'convenience'),
            emergency: []
          };

          setKeyword(kw);
          setSheetState(SHEET.MIN);
          if (data.length > 0 && mapInstance.current) {
            const first = data[0];
            const moveLatLon = new window.kakao.maps.LatLng(first.lat, first.lng);
            mapInstance.current.panTo(moveLatLon);
          }
        }
      } catch (err) {
        console.error("Search Error:", err);
        alert("검색 중 오류가 발생했습니다.");
      }
    });
  };

  const moveToMyLocation = () => {
    const handleLocationSuccess = (lat, lng) => {
      const loc = new window.kakao.maps.LatLng(lat, lng);
      if (mapInstance.current) {
        mapInstance.current.setCenter(loc);
        mapInstance.current.setLevel(4);

        if (myLocationOverlayRef.current) {
          myLocationOverlayRef.current.setMap(null);
        }
        const content = `<div class="my-location-dot"></div>`;
        myLocationOverlayRef.current = new window.kakao.maps.CustomOverlay({
          position: loc,
          content: content,
          zIndex: 5
        });
        myLocationOverlayRef.current.setMap(mapInstance.current);
        fetchMarkersInBounds();
      }
    };

    const handleLocationError = (error) => {
      console.warn("Geolocation failed or denied. Using fallback center.", error);
      const lastLat = localStorage.getItem("last_map_lat");
      const lastLng = localStorage.getItem("last_map_lng");
      let fallbackLoc;
      if (lastLat && lastLng) {
        fallbackLoc = new window.kakao.maps.LatLng(Number(lastLat), Number(lastLng));
      } else {
        fallbackLoc = new window.kakao.maps.LatLng(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng);
      }
      if (mapInstance.current) {
        mapInstance.current.setCenter(fallbackLoc);
        mapInstance.current.setLevel(4);
        fetchMarkersInBounds();
      }
    };

    if (!window.isSecureContext && window.location.hostname !== 'localhost') {
      handleLocationError(new Error("Insecure Context"));
      return;
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => handleLocationSuccess(pos.coords.latitude, pos.coords.longitude),
        (err) => handleLocationError(err),
        { timeout: 5000, enableHighAccuracy: true, maximumAge: 0 }
      );
    } else {
      handleLocationError(new Error("Not supported"));
    }
  };

  /* 반경 원 그리기 */
  const updateRadiusCircle = () => {
    if (!mapInstance.current) return;
    if (radiusCircleRef.current) {
      radiusCircleRef.current.setMap(null);
    }
    const center = mapInstance.current.getCenter();
    radiusCircleRef.current = new window.kakao.maps.Circle({
      center: center,
      radius: radius,
      strokeWeight: 1,
      strokeColor: '#75B8FA',
      strokeOpacity: 0.8,
      strokeStyle: 'solid',
      fillColor: '#CFE7FF',
      fillOpacity: 0.3
    });
    radiusCircleRef.current.setMap(mapInstance.current);
  };

  useEffect(() => {
    updateRadiusCircle();
  }, [radius]);

  useEffect(() => {
    if (selectedPlace && mapInstance.current) {
      const moveLatLon = new window.kakao.maps.LatLng(selectedPlace.lat, selectedPlace.lng);
      mapInstance.current.panTo(moveLatLon);
    }

    // 마커 확대/축소 효과
    // 1. 이전 선택된 마커 축소
    if (selectedMarkerRef.current) {
      const prev = selectedMarkerRef.current;
      const type = prev.data.type;
      const normalImage = new window.kakao.maps.MarkerImage(
        iconMap[type],
        new window.kakao.maps.Size(18, 18),
        { offset: new window.kakao.maps.Point(9, 9) }
      );
      prev.setImage(normalImage);
      selectedMarkerRef.current = null;
    }

    // 2. 새로운 선택된 마커 확대
    if (selectedPlace) {
      const allMarkers = [
        ...markersRef.current.hospital,
        ...markersRef.current.pharmacy,
        ...markersRef.current.convenience,
        ...markersRef.current.emergency
      ];

      const targetPId = getPlaceId(selectedPlace);
      const target = allMarkers.find(
        m => m.data.pId === targetPId && m.data.type === selectedPlace.type
      );

      if (target) {
        const bigImage = new window.kakao.maps.MarkerImage(
          iconMap[selectedPlace.type],
          new window.kakao.maps.Size(28, 28),
          { offset: new window.kakao.maps.Point(14, 14) }
        );
        target.setImage(bigImage);
        selectedMarkerRef.current = target;
      }
    }
  }, [selectedPlace]);

  return (
    <div className="map-main">
      <div className="map-top-ui">
        <div className="map-ui-inner">
          <InputBar
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onSearch={handleSearch}
            placeholder="병원, 약국 검색"
          />
          <FilterIconGroup
            filters={filters}
            onToggle={toggleFilter}
          />
        </div>
      </div>

      <button
        onClick={moveToMyLocation}
        style={{
          position: 'absolute',
          bottom: '180px',
          right: '20px',
          zIndex: 20,
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          backgroundColor: 'white',
          border: '1px solid #ddd',
          boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: '24px'
        }}
        title="내 위치로 이동"
      >
        <MyLocationIcon />
      </button>

      <div ref={mapContainerRef} className="kakao-map-layer" />

      {sheetState !== SHEET.CLOSED && (
        <MapList
          sheetState={sheetState}
          setSheetState={setSheetState}
          places={visiblePlaces}
          selectedPlace={selectedPlace}
          setSelectedPlace={setSelectedPlace}
        />
      )}
    </div>
  );
};

export default MapMain;
