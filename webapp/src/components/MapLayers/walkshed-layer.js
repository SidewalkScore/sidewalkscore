import React from "react";
import { GeoJSONLayer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";

const PATH_WIDTH = 16;  // width of path lines in meters
const PATH_WIDTH_EXPRESSION = realWidthExpression(PATH_WIDTH);

const WalkshedLayer = (props) => {
  const { walkshed } = props;

  if (walkshed === null) return null;

  return (
    <>
      <GeoJSONLayer
        data={walkshed}
        lineLayout={{ "line-cap": "round" }}
        linePaint={{
          "line-color": "#888",
          "line-opacity": 1,
          "line-width": ["interpolate", ["linear"], ["zoom"], 8, 1, 21, 2],
          "line-gap-width": PATH_WIDTH_EXPRESSION,
        }}
        before="sidewalkscore-outline"
      />
      <GeoJSONLayer
        data={walkshed}
        lineLayout={{ "line-cap": "round" }}
        linePaint={{
          "line-color": "deepskyblue",
          "line-width": PATH_WIDTH_EXPRESSION,
        }}
        before="sidewalkscore-outline"
      />
    </>
  );
}


export default WalkshedLayer;
