import React from "react";
import { GeoJSONLayer } from "react-mapbox-gl";

import realWidthExpression from "./real-width-expression";

const PATH_WIDTH = 12;  // width of path lines in meters
const PATH_WIDTH_EXPRESSION = realWidthExpression(PATH_WIDTH);

const WalkshedStreetsLayer = (props) => {
  const { walkshed } = props;

  return (
    <>
      <GeoJSONLayer
        data={walkshed}
        lineLayout={{ "line-cap": "round" }}
        linePaint={{
          "line-color": "#000",
          "line-width": PATH_WIDTH_EXPRESSION,
        }}
        before="sidewalkscore-outline"
      />
    </>
  );
}


export default WalkshedStreetsLayer;
