import { combineReducers } from "redux";
import {
  CLEAR_SIDEWALKSCORE,
  ENABLE_WIDTH_RESTRICTION,
  DISABLE_WIDTH_RESTRICTION,
  FAILED_REACHABLE_BOTH,
  RECEIVED_REACHABLE_BOTH,
  SET_TRAVEL_MODE,
  SET_VIEW_MODE_SIDEWALKSCORE,
  SET_VIEW_MODE_WALKSHEDS,
  SET_WALKDISTANCE,
} from "./actions";

const defaults = {
  failure: null,
  sidewalkScore: null,
  travelMode: "Manual wheelchair",
  viewMode: "sidewalkscore",
  walkshed: null,
  walkshedStreets: null,
  walkdistance: 400,
  widthRestricted: false,
};

const handleFailure = (state = defaults.failure, action) => {
  let networks;
  switch (action.type) {
    case FAILED_REACHABLE_BOTH:
      if (action.payload.pedestrianStart) {
          networks = "pedestrian";
        if (action.payload.streetStart) {
          networks = "pedestrian and street";
        }
      } else {
        if (action.payload.streetStart) {
          networks = "street";
        }
      }
      return `No valid start point on ${networks} network(s)`;
    case RECEIVED_REACHABLE_BOTH:
      return null;
    default:
      return state;
  }
};

const handleSidewalkScore = (state = defaults.sidewalkScore, action) => {
  switch (action.type) {
    case FAILED_REACHABLE_BOTH:
      return null;
    case RECEIVED_REACHABLE_BOTH:
      const pedestrianTotalDistance = action.payload.reachable.edges.features.reduce((a, v) => a + v.properties.length, 0);
      const streetsTotalDistance = action.payload.reachableStreets.edges.features.reduce((a, v) => a + v.properties.length, 0);
      return pedestrianTotalDistance / streetsTotalDistance / 2;
    case CLEAR_SIDEWALKSCORE:
      return null;
    default:
      return state;
  }
};

const handleTravelMode = (state = defaults.travelMode, action) => {
  switch (action.type) {
    case SET_TRAVEL_MODE:
      return action.payload.travelMode;
    default:
      return state;
  }
};

const handleViewMode = (state = defaults.viewMode, action) => {
  switch (action.type) {
    case SET_VIEW_MODE_SIDEWALKSCORE:
      return "sidewalkscore";
    case SET_VIEW_MODE_WALKSHEDS:
      return "walksheds";
    default:
      return state;
  }
};

const handleWalkshed = (state = defaults.walkshed, action) => {
  switch (action.type) {
    case RECEIVED_REACHABLE_BOTH:
      return {
        ...state,
        lon: action.payload.lon,
        lat: action.payload.lat,
        reachable: action.payload.reachable,
      };
    case CLEAR_SIDEWALKSCORE:
    case FAILED_REACHABLE_BOTH:
      return null;
    default:
      return state;
  }
};

const handleWalkshedStreets = (state = defaults.walkshedStreets, action) => {
  switch (action.type) {
    case RECEIVED_REACHABLE_BOTH:
      return {
        ...state,
        lon: action.payload.lon,
        lat: action.payload.lat,
        reachable: action.payload.reachableStreets,
      };
    case CLEAR_SIDEWALKSCORE:
    case FAILED_REACHABLE_BOTH:
      return null;
    default:
      return state;
  }
};

const handleWalkdistance = (state = defaults.walkdistance, action) => {
  switch (action.type) {
    case SET_WALKDISTANCE:
      return action.payload;
    default:
      return state;
  }
};

const handleWidthRestricted = (state = defaults.widthRestricted, action) => {
  switch (action.type) {
    case ENABLE_WIDTH_RESTRICTION:
      return true;
    case DISABLE_WIDTH_RESTRICTION:
      return false;
    default:
      return state;
  }
};

export default combineReducers({
  failure: handleFailure,
  travelMode: handleTravelMode,
  sidewalkScore: handleSidewalkScore,
  viewMode: handleViewMode,
  walkshed: handleWalkshed,
  walkshedStreets: handleWalkshedStreets,
  walkdistance: handleWalkdistance,
  widthRestricted: handleWidthRestricted,
});
