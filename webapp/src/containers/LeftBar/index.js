import React, { Component } from "react";
import { bindActionCreators } from "redux";
import { connect } from "react-redux";

import { Box, FormField, Heading, RadioButtonGroup, RangeInput } from "grommet";

import * as AppActions from "../../actions";


class ControlBar extends Component {
  render() {
    const {
      actions,
      sidewalkScore,
      travelMode,
      walkdistance,
    } = this.props;

    return (
      <Box direction="column">
        <Heading level={2}>SidewalkScore: {sidewalkScore ? sidewalkScore.toFixed(2) : ""}</Heading>
        <Box direction="column" margin={{ bottom: "medium" }}>
          <FormField label={`Distance of travel: ${walkdistance}`} pad>
            <RangeInput
              min={200}
              max={600}
              step={50}
              name="Select distance of travel"
              value={walkdistance}
              label="Distance of travel (meters)"
              onChange={(e) => {
                // TODO: this is a messed-up way to handle state (global variable). Use
                // component state?
                const target = e.target || null;
                if (target === null) return;
                actions.setWalkdistance(target.value);
              }}
            />
          </FormField>
        </Box>
        <Box direction="column">
          <FormField label="Select travel mode" pad>
            <RadioButtonGroup
              name="Select Travel Mode"
              options={["Manual wheelchair", "Powered wheelchair", "Cane", "Walk"]}
              value={travelMode}
              onChange={(e) => {
                const target = e.target || null;
                if (target === null) return;
                actions.setTravelMode(target.value);
              }}
            />
          </FormField>
        </Box>
      </Box>
    );
  }
}

const mapStateToProps = state => ({
  travelMode: state.travelMode,
  sidewalkScore: state.sidewalkScore,
  walkdistance: state.walkdistance,
});

const mapDispatchToProps = dispatch => ({
  actions: bindActionCreators(AppActions, dispatch),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(ControlBar);
