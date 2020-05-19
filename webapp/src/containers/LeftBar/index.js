import React, { Component } from "react";
import { bindActionCreators } from "redux";
import { connect } from "react-redux";

import { Box, Button, CheckBox, FormField, Heading, RadioButtonGroup, RangeInput } from "grommet";

import * as AppActions from "../../actions";


class ControlBar extends Component {
  render() {
    const {
      actions,
      failure,
      sidewalkScore,
      travelMode,
      viewMode,
      walkdistance,
      widthRestricted,
    } = this.props;

    const viewLabel = viewMode === "sidewalkscore" ? "SidewalkScore" : "Walksheds";

    return (
      <Box direction="column">
        <Box direction="column">
          <Button
            primary
            large
            label={`Switch to ${viewMode === "sidewalkscore" ? "Walksheds" : "SidewalkScore"}`}
            onClick={() => {
              if (viewMode === "sidewalkscore") {
                actions.setViewModeWalksheds();
              } else {
                actions.setViewModeSidewalkScore();
              }
            }}
          />
        </Box>
        <Heading level={2}>
          { viewMode === "sidewalkscore" ?
            `${viewLabel}: ${sidewalkScore ? sidewalkScore.toFixed(2) : ""}` :
            `${viewLabel}`
          }
        </Heading>
        { viewMode === "sidewalkscore" &&
          <>
          <Box direction="column">
            <Button
              secondary
              large
              label="Clear SidewalkScore"
              onClick={actions.clearSidewalkScore}
            />
          </Box>
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
          </>
        }
        <Box direction="column">
          <FormField label="Travel mode" pad>
            <RadioButtonGroup
              name="Travel Mode"
              options={["Manual wheelchair", "Powered wheelchair", "Cane", "Walking (normative)"]}
              value={travelMode}
              onChange={(e) => {
                const target = e.target || null;
                if (target === null) return;
                actions.setTravelMode(target.value);
              }}
            />
          </FormField>
        </Box>
        <Box direction="column">
          <FormField label="Width restriction" pad>
            <CheckBox
              label="Minimum width of 2 meters"
              checked={widthRestricted}
              onChange={(e) => {
                if (widthRestricted) {
                  actions.disableWidthRestriction();
                } else {
                  actions.enableWidthRestriction();
                }
              }}
            />
          </FormField>
        </Box>
        <Box direction="column" style={{color: "#FF0000"}}>
          { failure && failure }
        </Box>
      </Box>
    );
  }
}

const mapStateToProps = state => ({
  failure: state.failure,
  travelMode: state.travelMode,
  viewMode: state.viewMode,
  sidewalkScore: state.sidewalkScore,
  walkdistance: state.walkdistance,
  widthRestricted: state.widthRestricted,
});

const mapDispatchToProps = dispatch => ({
  actions: bindActionCreators(AppActions, dispatch),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(ControlBar);
