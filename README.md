# About FireGUARD

## Overview

FireGUARD (Fire Growth under Uncertainty for Appropriate Response Decision Support) is designed to support wildland fire response decicion-making. FireGUARD contains four core elements:

1. generation of weather forecast scenarios
2. generation of a burn probability map from replicated simulation of fire growth, smouldering, and natural extinction under the weather scenarios and stochastic fire behaviour scenarios
3. assessment of 'risk' (i.e., likelihood-weighted impacts) by multiplying the spatial burn probability by a spatial rating of potential socio-economic impact, and
4. (in progress for future implementation) estimation of the cost of response alternatives

## Additional License Condition

All covered works (e.g., copies of this work, derived works) must include a copy of the file (or an updated version of it) that details credits for work up to the time of the original open source release. That file is available [here](ORIGIN.md).

## Active Forks

Please note that:
- This repository is the original open source version that originated from proprietary, internal work
- Our intention is to maintain this repository (1) as a record of the original open source version and (2) as a discoverable pointer to the active fork
- The project is being actively developed in another fork
- As of 2024-09-24, the active fork is [https://github.com/CWFMF/FireSTARR](https://github.com/CWFMF/FireSTARR)
- We anticipate that the active fork will soon be split into separate repositories for various components

## Publications

FireGUARD is published at the following locations:

- [Weather forecast model](https://doi.org/10.3390/fire3020016)
- Burn probability model (In progress)
- [Impact and likelihood-weighted impact model](https://doi.org/10.1071/WF18189)


## Documentation

FireGUARD is the overall suite of products for creating probabilistic fire growth outputs.

Subcomponents include:

[FireSTARR](FireSTARR)

[GIS](GIS)

[WeatherSHIELD](WeatherSHIELD)

<!-- @diafile DataFlow.dia -->
