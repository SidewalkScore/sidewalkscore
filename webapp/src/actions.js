const travelModeMap = {
  "Manual wheelchair": "manual_wheelchair",
  "Powered wheelchair": "powered_wheelchair",
  "Cane": "cane",
  "Walking (normative)": "walking",
};

const routeServer = process.env.REACT_APP_ROUTESERVER;
const routeStreetsServer = process.env.REACT_APP_ROUTESTREETSSERVER;

export const ENABLE_WIDTH_RESTRICTION = "ENABLE_WIDTH_RESTRICTION";
export const DISABLE_WIDTH_RESTRICTION = "DISABLE_WIDTH_RESTRICTION";
export const SET_TRAVEL_MODE = "SET_TRAVEL_MODE";
export const GET_REACHABLE = "GET_REACHABLE";
export const RECEIVED_REACHABLE_BOTH = "RECEIVED_REACHABLE_BOTH";
export const FAILED_REACHABLE_BOTH = "FAILED_REACHABLE_BOTH";
export const GET_REACHABLE_STREETS = "GET_REACHABLE_STREETS";
export const SET_WALKDISTANCE = "SET_WALKDISTANCE";
export const CLICK_MAP = "CLICK_MAP";

export const enableWidthRestriction = () => (dispatch, getState) => {
  dispatch({
    type: ENABLE_WIDTH_RESTRICTION
  });
  fetchWalkshed({min_width: 2}, dispatch, getState);
};

export const disableWidthRestriction = () => (dispatch, getState) => {
  dispatch({
    type: DISABLE_WIDTH_RESTRICTION
  });
  fetchWalkshed({min_width: 0}, dispatch, getState);
};


export const setTravelMode = (travelMode) => (dispatch, getState) => {
  dispatch({
    type: SET_TRAVEL_MODE,
    payload: { travelMode }
  });
  fetchWalkshed({}, dispatch, getState);
};

let walkdistanceTimeout;
export const setWalkdistance = walkdistance => (dispatch, getState) => {
  dispatch({
    type: SET_WALKDISTANCE,
    payload: walkdistance,
  });

  clearTimeout(walkdistanceTimeout);
  walkdistanceTimeout = setTimeout(
    () => {
      fetchWalkshed({ walkdistance }, dispatch, getState);
    },
    50
  );
};

export const clickMap = (lon, lat) => (dispatch, getState) => {
  dispatch({
    type: CLICK_MAP,
    payload: { lon, lat }
  });
  fetchWalkshed({ lon, lat }, dispatch, getState);
};

export const getReachable = (lon, lat, reachable) => ({
  type: GET_REACHABLE,
  payload: {lon, lat, reachable},
});

export const getReachableStreets = (lon, lat, reachable) => ({
  type: GET_REACHABLE_STREETS,
  payload: {lon, lat, reachable},
});

export const getReachableBoth = (lon, lat, reachable, reachableStreets) => (dispatch, getState) => {
  const invalidPedestrianStart = reachable.status === "InvalidWaypoint";
  const invalidStreetStart = reachableStreets.status === "InvalidWaypoint";

  if (invalidPedestrianStart || invalidStreetStart) {
    dispatch({
      type: FAILED_REACHABLE_BOTH,
      payload: {
        pedestrianStart: invalidPedestrianStart,
        streetStart: invalidStreetStart
      },
    });
  } else {
    dispatch({
      type: RECEIVED_REACHABLE_BOTH,
      payload: {lon, lat, reachable, reachableStreets},
    });
  }
};

export const fetchWalkshed  = (newParams, dispatch, getState) => {
  const state = getState();
  const { travelMode, widthRestricted } = state;
  const queryParams = {
    lon: state.walkshed ? state.walkshed.lon : null,
    lat: state.walkshed ? state.walkshed.lat : null,
    max_cost: state.walkdistance,
    min_width: widthRestricted ? 2 : 0,
    ...newParams,
  }

  // Check if all necessary params are set (namely, lon and lat)
  if (!queryParams.lon || !queryParams.lat) return;

  const esc = encodeURIComponent;
  const queryURL = Object.keys(queryParams)
    .map(k => `${esc(k)}=${esc(queryParams[k])}`)
    .join("&");

  const profile = widthRestricted ? travelModeMap[travelMode] + "_width" : travelModeMap[travelMode];

  const swWalkshedURL = `${routeServer}/reachable/${profile}.json?${queryURL}`;
  const stWalkshedURL = `${routeStreetsServer}/reachable/walking.json?${queryURL}`;

  const swWalkshedFetch = fetch(swWalkshedURL)
  const stWalkshedFetch = fetch(stWalkshedURL)

  Promise.all([swWalkshedFetch, stWalkshedFetch])
    .then(responses =>
      Promise.all(responses.map(res => res.ok ? res.json() : null))
    )
    .then(jsons => {
      for (let json of jsons) {
        if (json === null) {
          throw Error("no route!")
        }
      }
      dispatch(getReachableBoth(queryParams.lon, queryParams.lat, jsons[0], jsons[1]));
    })
    .catch(error => {});
}
