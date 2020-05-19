import React from "react";

import { Layer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";
// import inclineColorScale from "../../incline-color-scale";

const PATH_WIDTH = 4;  // width of path lines in meters
const PATH_WIDTH_EXPRESSION = realWidthExpression(PATH_WIDTH, 2);

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

const PLASMA = [
  "#6A00A7",
  "#B02A8F",
  "#E06461",
  "#FCA635",
  "#EFF821",
];

const SidewalkScoreLayer = ({layerName}) => {
  const palette = PLASMA;
  const SIDEWALKSCORE_EXPRESSION = [
    "interpolate",
    ["linear"],
    ["to-number", ["get", layerName]],
    0, "#000000",
    0.0000000001, palette[0],
    0.25, palette[1],
    0.5, palette[2],
    0.75, palette[3],
    1, palette[4],
  ];

  return (
    <React.Fragment>
      <Layer
        id="sidewalkscore"
        type="line"
        sourceId="sidewalkscore"
        sourceLayer="sidewalkscore"
        layout={{
          "line-cap": "round",
        }}
        paint={{
          "line-color": SIDEWALKSCORE_EXPRESSION,
          "line-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            10, 0.0,
            13, 1
          ],
          "line-width": PATH_WIDTH_EXPRESSION
        }}
        before="bridge-street"
      />
    </React.Fragment>
  );
};

export default SidewalkScoreLayer;
