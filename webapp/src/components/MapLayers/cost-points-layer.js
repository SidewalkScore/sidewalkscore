import React from "react";
import { GeoJSONLayer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";

const CIRCLE_RADIUS = 4.5;  // Radius of cost circles in meters
const COST_RADIUS_EXPRESSION = realWidthExpression(CIRCLE_RADIUS);

const CostPointsLayer = (props) => {
  const { costPoints } = props;
  let maxCost = 0;
  for (let feature of costPoints.features) {
    if (!isNaN(feature.properties.cost)) {
      maxCost = Math.max(maxCost, feature.properties.cost);
    }
  }
  return (
    <GeoJSONLayer
      data={costPoints}
      circlePaint={{
        "circle-radius": COST_RADIUS_EXPRESSION,
        "circle-color": [
          "interpolate",
          ["linear"],
          ["number", ["get", "cost"], 0],
          0, "#8856a7",
          600, "#e0ecf4"
        ]
      }}
    />
  );
};

export default CostPointsLayer;
