# HoVer Notes:

**Basics:**
- [Paper](https://arxiv.org/abs/2011.03088)
- [Site](https://hover-nlp.github.io/)
- Dataset for multi-hop fact verification
- Facts are extracted from Wikipedia articles
    - Up to 4 articles are necessary for extraction
    - Q: does this require that many hops in WikiData?
- Up to 4 hops are necessary for wikipedia
- Claims are either "supported" or "not supported"
- 26K claims
- E.g. claim: "The Ford Fusion was introduced for model year 2006. The Rookie of The Year in the 1997 CART season drives it in the series held by the group that held an event at the Saugus Speedway."

**Claims:**
- Produced by taking a single-page claim and replacing an object, so that another hop is necessary
- This method is repeated to create up to 4-hop examples
