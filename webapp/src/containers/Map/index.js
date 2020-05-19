import React, { Component } from "react";
import { bindActionCreators } from "redux";
import { connect } from "react-redux";
import ReactMapboxGl from "react-mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

import * as AppActions from "../../actions";

import MapSources from "../../components/MapSources";
// import LayerCostPoints from "./layers-costpoints";
import {
  CostPointsLayer,
  OriginPathLayer,
  POILayer,
  SidewalksLayer,
  SidewalkScoreLayer,
  WalkshedLayer,
  WalkshedStreetsLayer,
} from "../../components/MapLayers";
import travelModes from "../../travel-modes";

const center = [-122.333592, 47.605628];
const zoom = [15];

const MapboxGL = ReactMapboxGl({
  accessToken: process.env.REACT_APP_MAPBOX_TOKEN,
  minZoom: 10,
  maxZoom: 20,
  bearing: [0],
  pitch: [0],
});

const getTravelLayerString = (travelMode, widthRestricted) => {
  const widthString = widthRestricted ? "_width" : "";

  switch (travelMode) {
    case "Manual wheelchair":
      return `sidewalkscore_manual_wheelchair${widthString}`;
    case "Powered wheelchair":
      return `sidewalkscore_powered_wheelchair${widthString}`;
    case "Cane":
      return `sidewalkscore_cane${widthString}`;
    case "Walking (normative)":
      return `sidewalkscore_walking${widthString}`;
    default:
      return `sidewalkscore_wheelchair${widthString}`;
  }
};

class Map extends Component {
  render() {
    const {
      costPoints,
      poi,
      travelMode,
      viewMode,
      walkshed,
      walkshedStreets,
      walkshedOrigin,
      widthRestricted,
    } = this.props;

    const profile = travelModes[travelMode];

    let layers;

    if (viewMode === "walksheds") {
      layers = (
        <>
          <SidewalksLayer
            uphill={profile.uphill}
            avoid_curbs={profile.avoid_curbs}
            width={widthRestricted ? 2 : 0}
          />
        </>
      );
    } else {
      layers = (
        <>
          <SidewalkScoreLayer
            layerName={getTravelLayerString(travelMode, widthRestricted)}
          />
          <WalkshedStreetsLayer walkshed={walkshedStreets} />
          <WalkshedLayer walkshed={walkshed} />
          { (poi && walkshedOrigin) && <OriginPathLayer poi={poi} origin={walkshedOrigin} /> }
          { poi &&
              <POILayer
                poi={poi}
                fillColor={walkshedOrigin ? "#77f" : "#f77" }
                borderColor={walkshedOrigin ? "#00f" : "#f00" }
              />
          }
          { costPoints && <CostPointsLayer costPoints={costPoints} /> }
        </>
      );
    }

    return (
      <MapboxGL
        className="map"
        center={center}
        zoom={zoom}
        maxBounds={[[-122.714460, 47.406897], [-121.907342, 47.809213]]}
        style="mapbox://styles/mapbox/dark-v9"  // eslint-disable-line react/style-prop-object
        onMouseMove={(m, e) => {
          m.getCanvas().style.cursor = "pointer";
        }}
        onDrag={m => {
          m.getCanvas().style.cursor = "grabbing";
        }}
        onClick={(m, e) => {
          if (viewMode === "sidewalkscore") {
            return this.props.actions.clickMap(e.lngLat.lng, e.lngLat.lat)
          }
        }}
      >
      <MapSources />
        {layers}
      </MapboxGL>
    );
  }
}

const mapStateToProps = (state) => {
  return {
    poi: state.walkshed ? [state.walkshed.lon, state.walkshed.lat] : null,
    travelMode: state.travelMode,
    viewMode: state.viewMode,
    // costPoints: state.walkshed ? state.walkshed.reachable.node_costs : null,
    walkshed: state.walkshed ? state.walkshed.reachable.edges : null,
    walkshedStreets: state.walkshedStreets ? state.walkshedStreets.reachable.edges : null,
    walkshedOrigin: state.walkshed ? state.walkshed.reachable.origin : null,
    widthRestricted: state.widthRestricted
  };
}

const mapDispatchToProps = dispatch => ({
  actions: bindActionCreators(AppActions, dispatch),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(Map);
