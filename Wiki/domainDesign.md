# Domain Design

### Domain Objects

- `Position`: a multi-dimensional point. Currently intended to support up to
the 5th dimension:
   - Dimensions 1-3: typical coordinate system consisting of longitude,
   latitude, and height relative to sea level
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
   - A location has a positional range that covers specified what area it covers
   in each dimension. Most locations will consist of an area that spans 4 of the
   5 dimensions: it's 3-dimensional area and the time range from when it was
   constructed to when it will be no more. It's range in the 5th dimension is
   still a range but is likely only one point in that dimension _(the low and
   high values are equal)_.
   - A location can have zero or more tags, which are strings to allow easy
   identification and other utilities such as filtering and querying.
- `Event`: An interaction, connection, or other thing which happens at a place
to and optionally includes travelers.
   - An event has a description, which summarizes the details of what occurs.
   - An event has either a positional range, which is the multi-dimensional span
   over which the event occurs.
   - An event has a set of travelers. Most events have at least one traveler,
indicating that the event affected or included those travelers. Events without
any travelers are supported but must still have a position or location _(for
example a natural disaster in a remote area)_.
   - An event has a set of locations showing which locations were affected by
   the event. This set can have 0 or more locations, but each location's span
   must intersect with the event's span at least partially.
   - An event can have zero or more tags, which are strings to allow easy
   identification and other utilities such as filtering and querying.

### Domain Usages

- `Tags`: can be added to travelers, locations, and events to categorize and
assist in retrieving desired items. Tags can be filtered as follows:
   - `All`: Only items which have each of the given tags will be returned.
   - `Any`: Items which have at least one of the given tags will be returned.
   - `Only`: Items which have only the given tags will be returned.
   - `None`: Items which do not have any of the of the given tags will be
   returned.
   - Multiple filters can be used simultaneously. Non-intersecting filters
   _(such as combining `only=A` and `none=A`)_ will result in an empty list.

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
      earliest position that the event is applicable.
      - Events may also appear multiple times in a traveler's timeline, as a
      traveler could leave and re-enter the event's span.
      - A traveler's timeline will always begin and end positions, with a
      combination of events and positions between.
   - Events included in a retrieved timeline can be filtered according to those
   event's tags.

### See Also

- [**Application Design**](./applicationDesign.md)
- [**API Design**](./apiDesign.md)
