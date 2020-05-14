import React, { Component } from "react";
import { Provider } from "react-redux";
import dotenv from "dotenv";

import { Box, Grid, Grommet } from "grommet";

import "./App.css";

import createStore from "./store.js";

import Map from "./containers/Map";
import LeftBar from "./containers/LeftBar";

// Initialize dotenv - retrieve environment variables from .env file
dotenv.config();

const store = createStore();

const theme = {
  global: {
    font: {
      family: "Roboto",
      size: "14px",
      height: "20px"
    }
  },
  formField: {
    border: false
  }
};

class App extends Component {
  render() {
    return (
      <Provider store={store}>
        <Grommet theme={theme} full>
          <Grid
            fill
            rows={["100%"]}
            columns={["medium", "flex"]}
            gap="none"
            areas={[
              { name: "control-bar", start: [0, 0], end: [0, 0] },
              { name: "map", start: [1, 0], end: [1, 0] },
            ]}
          >
            <Box gridArea="control-bar" pad="medium">
              <LeftBar />
            </Box>
            <Box gridArea="map">
              <Map />
            </Box>
          </Grid>
        </Grommet>
      </Provider>
    );
  }
}

export default App;
