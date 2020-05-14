const ZOOMS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22];

const pixelsPerMeter = (zoom) => {
  const EARTH_RADIUS = 6378137;
  const LAT = 47.6;
  const TILESIZE = 512;

  const scale = 2 ** zoom;
  const worldSize = TILESIZE * scale;
  const rest =
    2 * Math.PI * EARTH_RADIUS * Math.abs(Math.cos(LAT * (Math.PI / 180)));
  return worldSize / rest;
};

export default (width) => ([
  "interpolate",
  ["exponential", 2],
  ["zoom"],
  ...ZOOMS.map(z => [z, width * pixelsPerMeter(z)]).reduce((a, b) => a.concat(b))
]);
