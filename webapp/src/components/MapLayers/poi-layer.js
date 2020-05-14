import React from "react";
import { GeoJSONLayer } from "react-mapbox-gl";

const POILayer = (props) => {
  const { fillColor, borderColor, poi } = props;

  return (
    <GeoJSONLayer
      data={{
        type: "FeatureCollection",
        features: [{
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: poi,
          },
        }]
      }}
      circlePaint={{
        "circle-color": fillColor,
        "circle-color-transition": { "duration": 0 },
        "circle-stroke-color": borderColor,
        "circle-stroke-color-transition": { "duration": 0 },
        "circle-stroke-width": [
          "interpolate",
          ["linear"],
          ["zoom"],
          12, 1,
          16, 2,
          22, 3
        ],
        "circle-radius": [
          "interpolate",
          ["linear"],
          ["zoom"],
          12, 1,
          16, 6,
          22, 50
        ]
      }}
      before="bridge-street"
    />
  );
}

POILayer.defaultProps = {
  fillColor: "#fff",
  borderColor: "#000"
};

export default POILayer;
