# Methods for anonymizing data for public distribution

This plugin implements different methods for the anonymization of spatial
data (typically point samples) with the goal of making the data publically
available, while preserving the privacy of the individuals whose information
the dataset contains.

The differential privacy algorithm is based on the algorithm outlined in [1]
and implemented by Konstantinos Chatzikokolakis in the Location Guard
browser extension [2].

## Credits

[1] Andrés, M.E. et al., 2013. Geo-indistinguishability. In the 2013 ACM
SIGSAC conference. New York, New York, USA: ACM Press, pp. 901–914.

[2] https://github.com/chatziko/location-guard

Toucan by Lane F. Kinkade from the Noun Project

## Changelog

* 0.1.0 (3rd November 2015): Initial version with independent anonymization of 
  points only.
