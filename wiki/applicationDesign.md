# Application Design

### Problem / Goal

- Need a way to keep track of events, places, people, and interactions.
- Should be able to look up these items by:
   - people looked up by name, should give back the timeline the person has
   traversed including events, places been to, interactions, etc.
   - places should be looked up by name, and should include the people who
   come and go, the interactions in the city, and the events
- Need to be able to detect similarities/collisions. For example, it should
be easy to identify interactions _(both past and possible future)_ between
two people. If a person travels with another, the relation with the other
person should be evident by querying either person's timeline.

### See Also

- [**API Design**](./apiDesign.md)
- [**Domain Design**](./domainDesign.md)
