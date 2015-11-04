# Methods for anonymizing data for public distribution

This QGIS Processing provider plugin implements different methods for the
anonymization of spatial data (typically point samples) with the goal of making
the data publicly available, while preserving the privacy of the individuals
whose information the dataset contains (see [3]).

The differential privacy algorithm is based on the algorithm outlined in [1]
and implemented by Konstantinos Chatzikokolakis in the Location Guard
browser extension [2].

## Credits

[1] Andrés, M.E., Bordenabe, N.E., Chatzikokolakis, K., and Palamidessi, P.
2013. 'Geo-indistinguishability: Differential Privacy for Location-Based
Systems', *In the Proceedings of the 2013 ACM SIGSAC conference on Computer
and Communications Security (CCS'13)*. New York, New York, USA: ACM Press,
pp. 901–914. Online at http://arxiv.org/abs/1212.1984v3

[2] https://github.com/chatziko/location-guard

[3] https://en.wikipedia.org/wiki/Differential_privacy

Toucan by Lane F. Kinkade from the Noun Project
https://github.com/SpatialVision/differential_privacy

## Changelog

* 0.1.0 (3rd November 2015): Initial version with independent anonymization of 
  points only.
