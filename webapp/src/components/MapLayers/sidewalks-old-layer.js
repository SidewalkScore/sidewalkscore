import React from "react";

import { Layer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";
import inclineColorScale from "../../incline-color-scale";

const PATH_WIDTH = 4;  // width of path lines in meters
const PATH_WIDTH_EXPRESSION = realWidthExpression(PATH_WIDTH);

const INCLINE_BREAKS = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12];
const INCLINE_COLOR_EXPRESSION = [
  "case",
  ["has", "incline"],
  [
    "interpolate",
    ["linear"],
    ["abs", ["to-number", ["get", "incline"]]],
    ...INCLINE_BREAKS.map(b => [b, inclineColorScale(b / Math.max(...INCLINE_BREAKS)).hex()]).reduce((a, b) => a.concat(b))
  ],
  "#eee"
];

const SidewalksLayer = () => {
  return (
    <React.Fragment>
      <Layer
        id="sidewalks-outline"
        type="line"
        sourceId="pedestrian"
        sourceLayer="transportation"
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
      <Layer
        id="sidewalks"
        type="line"
        sourceId="pedestrian"
        sourceLayer="transportation"
        layout={{ "line-cap": "round" }}
        paint={{
          "line-color": INCLINE_COLOR_EXPRESSION,
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

export default SidewalksLayer;
