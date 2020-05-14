import chroma from "chroma-js";

// Maps travel speed to color
const inclineColorScale = chroma
  .scale(
    [chroma("lime"), chroma("yellow"), chroma("red")].map(c => c.brighten(2.5))
  )
  .mode("lab");

export default inclineColorScale;
