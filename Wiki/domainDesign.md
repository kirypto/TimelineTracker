# Domain Design

- `Position`: a multi-dimensional point. Currently intended to support up to
the 5th dimension:
   - Dimensions 1-3: typical coordinate system consisting of longitude,
   latitude, and height relative to sea level
   - Dimension 4: 'time' or 'duration', the time that the position is tied to
   - Dimension 5: 'decision space' or 'alternate realities' which may be
   jumped between
- `PositionalRange`: a multi-dimensional range, with a lower and higher point
in each dimension.
- `Timeline`: a sequence of positions. Iterating along the sequence of positions
does not necessarily imply increasing in along the 4th dimension _(as would be
expected with 'real-world' 3 dimensional positions)_. Instead, two adjacent
points in a timeline may move in the 4th or even 5th dimension.
  - A timeline has a sequence of positions, which represent the travel or
  movement of something.
  - A timeline has a sequence of transition rules, which represent how the
  movement between positions occurs. Examples are:
     - Interpolation: the position smoothly interpolates the position in
     specific dimensions depending on the query dimension.
     - Jump: the earlier position is used to 'infill' all possible queries
     between two points in a sequence until the latter position is reached, at
     which time the latter position is instantaneously used.
- `Traveler`: a person or thing which has a timeline consisting of the positions
it visits. A traveler can interact with other travelers and locations.
   - A traveler has a timeline, which is a sequence of positions.
   - A traveler has a description, which is tied to it's timeline. The
   traveler's description will change as it experiences it's timeline.
- `Location`: a place of significance that traveler's can come to and leave
from.
   - A location has a positional range that covers specified what area it covers
   in each dimension. Most locations will consist of an area that spans 4 of the
   5 dimensions: it's 3-dimensional area and the time range from when it was
   constructed to when it will be no more. It's range in the 5th dimension is
   still a range but is likely only one point in that dimension _(the low and
   high values are equal)_.
- `Interaction`: a link, connection, or event which occurs somewhere and may
include zero or more travelers.
   - An interaction has a description, which summarized the interaction or event
   that occurs.
   - An interaction has either a position or a location _(which implies a
   positional range)_. This is the position or place at which the interaction
   occurs.
   - An interaction has a set of travelers. This may be empty, meaning it is
   likely a natural event of one form or another. It may have only a single
   traveler, meaning it is likely an event or something which happened to that
   traveler. It may have multiple travelers, meaning it is likely an interaction
   or connection between multiple travelers.
- `Group`: an alias for a set of one or more travelers.
   - A group has a set of travelers. This can be used to represent a the
   ownership of an important object or objects, listing the object travelers and
   the possessor traveler.

### See Also

- [**Application Design**](./applicationDesign.md)
- [**API Design**](./apiDesign.md)
