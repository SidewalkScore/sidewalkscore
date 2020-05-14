import { combineReducers } from "redux";
import {
//  GET_REACHABLE,
//  GET_REACHABLE_STREETS,
  GET_REACHABLE_BOTH,
  SET_TRAVEL_MODE,
  SET_WALKDISTANCE,
} from "./actions";

const defaults = {
  travelMode: "Manual wheelchair",
  sidewalkScore: null,
  walkshed: null,
  walkshedStreets: null,
  walkdistance: 400,
};

const handleWalkshed = (state = defaults.walkshed, action) => {
  switch (action.type) {
    case GET_REACHABLE_BOTH:
      return {
        ...state,
        lon: action.payload.lon,
        lat: action.payload.lat,
        reachable: action.payload.reachable,
      };
    default:
      return state;
  }
};

const handleWalkshedStreets = (state = defaults.walkshedStreets, action) => {
  switch (action.type) {
    case GET_REACHABLE_BOTH:
      return {
        ...state,
        lon: action.payload.lon,
        lat: action.payload.lat,
        reachable: action.payload.reachableStreets,
      };
    default:
      return state;
  }
};

const handleSidewalkScore = (state = defaults.sidewalkScore, action) => {
  switch (action.type) {
    case GET_REACHABLE_BOTH:
      const pedestrianTotalDistance = action.payload.reachable.edges.features.reduce((a, v) => a + v.properties.length, 0);
      const streetsTotalDistance = action.payload.reachableStreets.edges.features.reduce((a, v) => a + v.properties.length, 0);
      return pedestrianTotalDistance / streetsTotalDistance / 2;
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

const handleTravelMode = (state = defaults.travelMode, action) => {
  switch (action.type) {
    case SET_TRAVEL_MODE:
      return action.payload.travelMode;
    default:
      return state;
  }
};

export default combineReducers({
  travelMode: handleTravelMode,
  sidewalkScore: handleSidewalkScore,
  walkshed: handleWalkshed,
  walkshedStreets: handleWalkshedStreets,
  walkdistance: handleWalkdistance,
});
