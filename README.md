# SidewalkScore

SidewalkScore is a pedestrian accessibility / walkability metric laser-focused on
sidewalk usability.

# Table of Contents

  * [SidewalkScore](#sidewalkscore)
  * [Table of contents](#table-of-contents)
  * [Technical overview](#technical-overview)
  * [SidewalkScore tools](#sidewalkscore-tools)
  * [Installation](#installation)
    * [Python package](#python-package)
    * [Web app](#web-app)
  * [Usage](#Usage)

# Technical Overview

# SidewalkScore Tools

# Installation

## Python package

The Python package in this repo is the current implementation reference. See its
[README](sidewalkscore) for instructions. This tool can be used to:

1. Construct a graph from GDAL-compatible pedestrian and street networks.

2. Compute SidewalkScores for every street in the graph.

3. Generate a web API that dynamically produces SidewalkScores and their associated
walksheds from location inputs.

## Web app

This repo comes with a React-based single page web application for dynamically
investigating SidewalkScore results. See the [web app's README](webapp) for details.

# Usage
