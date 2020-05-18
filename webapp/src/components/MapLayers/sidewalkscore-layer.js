import React from "react";

import { Layer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";
// import inclineColorScale from "../../incline-color-scale";

const PATH_WIDTH = 4;  // width of path lines in meters
const PATH_WIDTH_EXPRESSION = realWidthExpression(PATH_WIDTH);

// const SWS_BREAKS = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4];
// const INCLINE_COLOR_EXPRESSION = [
//   "case",
//   ["has", "sidewalkscore_wheelchair"],
//   [
//     "interpolate",
//     ["linear"],
//     ["abs", ["to-number", ["get", "sidewalkscore"]]],
//     ...SWS_BREAKS.map(b => [b, inclineColorScale(b / Math.max(...SWS_BREAKS)).hex()]).reduce((a, b) => a.concat(b))
//   ],
//   "#eee"
// ];

const SidewalkScoreLayer = ({layerName}) => {
  const SIDEWALKSCORE_EXPRESSION = [
    "interpolate",
    ["linear"],
    ["to-number", ["get", layerName]],
    0, "#440154",
    0.25, "#3b528b",
    0.5, "#21918c",
    0.75, "#3b528b",
    1, "#440154",
  ];

  return (
    <React.Fragment>
      { /*
      <Layer
        id="sidewalkscore-outline"
        type="line"
        sourceId="sidewalkscore"
        sourceLayer="sidewalkscore"
        layout={{ "line-cap": "round" }}
        paint={{
          "line-color": "#999",
          "line-opacity": {
            stops: [[14, 0.0], [18, 1]],
          },
          "line-gap-width": PATH_WIDTH_EXPRESSION
        }}
        before="bridge-street"
      />
      */ }
      <Layer
        id="sidewalkscore"
        type="line"
        sourceId="sidewalkscore"
        sourceLayer="sidewalkscore"
        layout={{ "line-cap": "round" }}
        paint={{
          "line-color": SIDEWALKSCORE_EXPRESSION,
          "line-opacity": {
            stops: [[10, 0.0], [13, 1]],
          },
          "line-width": PATH_WIDTH_EXPRESSION
        }}
        before="bridge-street"
      />
    </React.Fragment>
  );
};

export default SidewalkScoreLayer;
