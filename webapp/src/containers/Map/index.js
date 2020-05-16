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

const center = [-122.333592, 47.605628];
const zoom = [15];

const MapboxGL = ReactMapboxGl({
  accessToken: process.env.REACT_APP_MAPBOX_TOKEN,
  minZoom: 10,
  maxZoom: 20,
  bearing: [0],
  pitch: [0],
});

class Map extends Component {
  render() {
    const {
      costPoints,
      poi,
      travelMode,
      walkshed,
      walkshedStreets,
      walkshedOrigin
    } = this.props;

    let travelLayerString;
    switch (travelMode) {
      case "Manual wheelchair":
        travelLayerString = "sidewalkscore_wheelchair";
        break;
      case "Powered wheelchair":
        travelLayerString = "sidewalkscore_electric";
        break;
      case "Cane":
        travelLayerString = "sidewalkscore_cane";
        break;
      case "Walk":
        travelLayerString = "sidewalkscore_walk";
        break;
      default:
        travelLayerString = "sidewalkscore_wheelchair";
        break;
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
          return this.props.actions.clickMap(e.lngLat.lng, e.lngLat.lat)
        }}
      >
        <MapSources />
        <SidewalksLayer />
        <SidewalkScoreLayer layerName={travelLayerString}/>
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
      </MapboxGL>
    );
  }
}

const mapStateToProps = (state) => {
  return {
    poi: state.walkshed ? [state.walkshed.lon, state.walkshed.lat] : null,
    travelMode: state.travelMode,
    // costPoints: state.walkshed ? state.walkshed.reachable.node_costs : null,
    walkshed: state.walkshed ? state.walkshed.reachable.edges : null,
    walkshedStreets: state.walkshedStreets ? state.walkshedStreets.reachable.edges : null,
    walkshedOrigin: state.walkshed ? state.walkshed.reachable.origin : null
  };
}

const mapDispatchToProps = dispatch => ({
  actions: bindActionCreators(AppActions, dispatch),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(Map);
