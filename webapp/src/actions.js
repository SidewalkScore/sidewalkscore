const travelModeMap = {
  "Manual wheelchair": "wheelchair",
  "Powered wheelchair": "electric",
  "Cane": "cane",
  "Walk": "walk",
};

const routeServer = process.env.REACT_APP_ROUTESERVER;
const routeStreetsServer = process.env.REACT_APP_ROUTESTREETSSERVER;

export const SET_TRAVEL_MODE = "SET_TRAVEL_MODE";
export const GET_REACHABLE = "GET_REACHABLE";
export const GET_REACHABLE_BOTH = "GET_REACHABLE_BOTH";
export const GET_REACHABLE_STREETS = "GET_REACHABLE_STREETS";
export const SET_WALKDISTANCE = "SET_WALKDISTANCE";
export const CLICK_MAP = "CLICK_MAP";

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

export const getReachableBoth = (lon, lat, reachable, reachableStreets) => ({
  type: GET_REACHABLE_BOTH,
  payload: {lon, lat, reachable, reachableStreets},
});

export const fetchWalkshed  = (newParams, dispatch, getState) => {
  const state = getState();
  const { travelMode } = state;
  const queryParams = {
    lon: state.walkshed ? state.walkshed.lon : null,
    lat: state.walkshed ? state.walkshed.lat : null,
    max_cost: state.walkdistance,
    ...newParams,
  }

  // Check if all necessary params are set (namely, lon and lat)
  if (!queryParams.lon || !queryParams.lat) return;

  const esc = encodeURIComponent;
  const queryURL = Object.keys(queryParams)
    .map(k => `${esc(k)}=${esc(queryParams[k])}`)
    .join("&");

  const profile = travelModeMap[travelMode];

  const swWalkshedURL = `${routeServer}/reachable/${profile}.json?${queryURL}`;
  const stWalkshedURL = `${routeStreetsServer}/reachable/dynamic.json?${queryURL}`;

  // const swWalkshedURL = `${routeServer}/reachable/dynamic.json?${queryURL}`;
  // const stWalkshedURL = `${routeStreetsServer}/reachable/dynamic.json?${queryURL}`;

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
      // dispatch(getReachable(queryParams.lon, queryParams.lat, jsons[0]));
      // dispatch(getReachableStreets(queryParams.lon, queryParams.lat, jsons[1]));
    })
    .catch(error => {});
}
