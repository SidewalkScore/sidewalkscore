import React from "react";

import { Source } from "react-mapbox-gl";

const tileserver = process.env.REACT_APP_TILESERVER;

const MapSources = () => (
  <>
    <Source
      id="pedestrian"
      tileJsonSource={{
        type: "vector",
        url: `${tileserver}/tilejson/pedestrian.json`,
      }}
    />
    <Source
      id="sidewalkscore"
      tileJsonSource={{
        type: "vector",
        url: `${tileserver}/tilejson/sidewalkscore.json`,
      }}
    />
  </>
);

export default MapSources;
