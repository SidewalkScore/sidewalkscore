import React from "react";
import { GeoJSONLayer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";

const PATH_WIDTH = 3;  // width of path lines in meters
const PATH_WIDTH_EXPRESSION = realWidthExpression(PATH_WIDTH);

const OriginPathLayer = (props) => {
  const { poi, origin } = props;

  return (
    <GeoJSONLayer
      data={{
        type: "FeatureCollection",
        features: [{
          type: "Feature",
          geometry: {
            type: "LineString",
            coordinates: [poi, origin.geometry.coordinates],
          },
        }]
      }}
      lineLayout={{
        "line-cap": "round"
      }}
      linePaint={{
        "line-color": "#000",
        "line-width": PATH_WIDTH_EXPRESSION,
        "line-dasharray": [
          0, 2
        ]
      }}
      before="bridge-street"
    />
  );
};


export default OriginPathLayer;
