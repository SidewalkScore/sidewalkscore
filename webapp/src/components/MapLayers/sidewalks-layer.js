import React from "react";

import { Layer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";
// import inclineColorScale from "../../incline-color-scale";

const PATH_WIDTH = 4;  // width of path lines in meters
const PATH_WIDTH_EXPRESSION = realWidthExpression(PATH_WIDTH);

// const INCLINE_BREAKS = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12];
// const INCLINE_COLOR_EXPRESSION = [
//   "case",
//   ["has", "incline"],
//   [
//     "interpolate",
//     ["linear"],
//     ["abs", ["to-number", ["get", "incline"]]],
//     ...INCLINE_BREAKS.map(b => [b, inclineColorScale(b / Math.max(...INCLINE_BREAKS)).hex()]).reduce((a, b) => a.concat(b))
//   ],
//   "#eee"
// ];

const SidewalksLayer = ({uphill, avoid_curbs, width}) => (
  <>
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
        "line-color": [
          "case",
          ["all",
            ["==", ["get", "footway"], ["literal", "crossing"]],
            ["==", ["get", "curbramps"], 0],
            ["literal", avoid_curbs === 1],
          ],
          "#000000",
          ["case",
            ["all",
              ["==", ["get", "footway"], ["literal", "sidewalk"]],
              ["any",
                [">", ["abs", ["get", "incline"]], ["literal", uphill]],
                ["<", ["get", "width"], ["literal", width]],
              ],
            ],
            "#000000",
            "#FCA635",
          ],
        ],
        "line-opacity": 1,
        "line-width": PATH_WIDTH_EXPRESSION
      }}
      before="bridge-street"
    />
  </>
);
            // ["all",  ["to-boolean", ["get", "curbramps"]], ["!", ["to-boolean", ["literal", avoid_curbs]]]],

export default SidewalksLayer;
