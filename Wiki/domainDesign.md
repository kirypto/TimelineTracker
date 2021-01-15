# Domain Design

### Domain Objects

- `Position`: a multi-dimensional point. Positions are currently intended to
support up to the 5th dimension:
   - Dimensions 1-3: typical coordinate system consisting of longitude,
   latitude, and altitude.
   - Dimension 4: 'time' or 'duration', the time that the position is tied to
   - Dimension 5: 'decision space' or 'alternate realities' which may be
   jumped between
- `PositionalRange`: a multi-dimensional range, with a lower and higher point
in each dimension.
- `Journey`: a sequence of positions. Iterating along the sequence of positions
does not necessarily imply increasing in along the 4th dimension _(as would be
expected with 'real-world' 3 dimensional positions)_. Instead, two adjacent
points in a journey may move in the 4th or even 5th dimension.
  - A journey has a sequence of one or more positions, which represent the
  travel or movement of something.
  - A journey has a sequence of transition rules, which represent how the
  movement between positions occurs. Examples are:
     - Interpolated: the position smoothly interpolates the position in each of
     the 1st through 4th.
     - Immediate: the earlier position is used to 'infill' between two points
     in a sequence until the latter position is reached, then the latter
     position is instantaneously used.
- `Traveler`: a person or thing which has a journey consisting of the positions
it visits. A traveler can interact with other travelers and locations.
   - A traveler has a description, which provides details about the traveler.
   - A Traveler has a journey consisting of the positions it visits starting at
   the beginning of its existence and continuing until the end of its existence.
   - A traveler can have zero or more tags, which are strings to allow easy
   identification and other utilities such as filtering and querying.
- `Location`: a place of significance that traveler's can come to and leave
from.
   - A location has a description, which provides details about the location.
   - A location has a span, which is the positional range that specifies what
   area the location exists within.
   in each dimension. Most locations will consist of an area that spans 4 of the
   5 dimensions: it's 3-dimensional area, and the time range from when it was
   constructed to when it will be no more. It's range in the 5th dimension is
   still a range but is likely only one point in that dimension _(the low and
   high values are equal)_.
   - A location can have zero or more tags, which are strings to allow easy
   identification and other utilities such as filtering and querying.
- `Event`: An interaction, connection, or other thing which happens at a place
to and optionally includes travelers.
   - An event has a description, which summarizes the details of what occurs.
   - An event has a span, which is the positional range that specifies what area
   the event effects.
   - An event has a set of zero or more traveler ids that identify which _(if
   any)_ travelers were affected by the event. To be valid, the referenced
   travelers must have a position in their respective journeys within the span
   of the event. Some events may not affect any travelers at all, for example
   a natural disaster in a remote area.
   - An event has a set of zero or more location ids what identify which _(if
   any)_ location were affected by the event. To be valid, the referenced
   locations' spans must intersect with the span of the event. Some events may
   not affect any locations, such as meeting between travelers out in the
   wilderness.
   - An event can have zero or more tags, which are strings to allow easy
   identification and other utilities such as filtering and querying.

### Domain Usages

- `Tags`: can be added to travelers, locations, and events to categorize and
assist in retrieving desired items. 
   - Tags can be filtered as follows:
      - `All`: Only items which have each of the given tags will be returned.
      - `Any`: Items which have at least one of the given tags will be returned.
      - `Only`: Items which have only the given tags will be returned. Items 
      with a subset of the given tags will be returned.
      - `None`: Items which do not have any of the given tags will be returned.
   - Multiple filters can be used simultaneously. Non-intersecting filters
   _(such as combining `only=A` and `none=A`)_ will result in an empty list.
   - Because having an empty tag set is valid, the `Only` filters treats
   untagged items as 'passing' the filter. This allows:
      - To filter to only untagged items, use: `Only={}`.
      - To filter to items tagged with 'A' and/or 'B' _(but not untagged items)_
      combine the `Only` and `Any` filters: `Only={A,B}&Any{A,B}`.
   

- `Timeline`: a series of positions and events which show what has happened to
a Traveler or Location throughout its existence.
   - A timeline does not exist as a domain object on its own. It is an aggregate
   of travelers, positions, locations, and/or events.
   - The timeline of a location would contain only events, as a location is
   unable to move. These events can reference travelers, but the timeline itself
   would not.
   - The timeline of a traveler would certainly include positions and events, as
   each position in a traveler's journey would be included.
      - Events referenced in a traveler's timeline will be listed at the
      earliest position that the event is applicable. This means the event may
      show in the timeline immediately prior to the journeyed position, which
      would be the case whenever the movement type to that position is
      interpolated. If the movement type is immediate _(for example some form of
      teleportation)_, then the event would appear immediately after the
      journeyed location.
      - Events may also appear multiple times in a traveler's timeline, as a
      traveler could leave and re-enter the event's span.
      - A traveler's timeline will always begin with a position, as events 
      cannot affect a traveler which has not yet been anywhere.
      - A traveler's timeline may end with either an event or a position. This
      is because the movement type (immediate vs interpolated) affects whether
      the event appears before or after the journeyed position _(see above)_. 
   - Events included in a retrieved timeline can be filtered according to the
   event's tags.

### See Also

- [**Application Design**](./applicationDesign.md)
- [**API Design**](./apiDesign.md)
